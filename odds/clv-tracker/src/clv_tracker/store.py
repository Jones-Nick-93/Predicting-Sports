from __future__ import annotations

import csv
import sqlite3
from collections import defaultdict
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

from .domain import OddsSnapshot, parse_utc


SCHEMA = """
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY,
    captured_at_utc TEXT NOT NULL,
    event_id TEXT NOT NULL,
    starts_at_utc TEXT NOT NULL,
    sportsbook TEXT NOT NULL,
    market_type TEXT NOT NULL,
    selection TEXT NOT NULL,
    line TEXT NOT NULL,
    american_odds INTEGER NOT NULL,
    snapshot_role TEXT NOT NULL CHECK(snapshot_role IN ('entry', 'close')),
    UNIQUE (
        captured_at_utc, event_id, starts_at_utc, sportsbook, market_type,
        selection, line, american_odds, snapshot_role
    )
);
CREATE INDEX IF NOT EXISTS idx_snapshots_market
ON snapshots(event_id, sportsbook, market_type, selection, line, snapshot_role);
CREATE INDEX IF NOT EXISTS idx_snapshots_book_time
ON snapshots(sportsbook, captured_at_utc);
"""


class SnapshotStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def ingest(self, snapshots: Iterable[OddsSnapshot]) -> dict[str, int]:
        self.initialize()
        inserted = 0
        skipped = 0
        sql = """
        INSERT OR IGNORE INTO snapshots (
            captured_at_utc, event_id, starts_at_utc, sportsbook,
            market_type, selection, line, american_odds, snapshot_role
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        with self.connect() as connection:
            for snapshot in snapshots:
                cursor = connection.execute(
                    sql,
                    (
                        snapshot.captured_at_utc,
                        snapshot.event_id,
                        snapshot.starts_at_utc,
                        snapshot.sportsbook,
                        snapshot.market_type,
                        snapshot.selection,
                        snapshot.line,
                        snapshot.american_odds,
                        snapshot.snapshot_role,
                    ),
                )
                if cursor.rowcount == 1:
                    inserted += 1
                else:
                    skipped += 1
        return {"inserted": inserted, "skipped": skipped}

    def ingest_csv(self, path: str | Path) -> dict[str, int]:
        with Path(path).open("r", encoding="utf-8", newline="") as handle:
            reader = csv.DictReader(handle)
            snapshots = [OddsSnapshot.from_mapping(row) for row in reader]
        return self.ingest(snapshots)

    def all_snapshots(self) -> list[OddsSnapshot]:
        self.initialize()
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT captured_at_utc, event_id, starts_at_utc, sportsbook, "
                "market_type, selection, line, american_odds, snapshot_role "
                "FROM snapshots ORDER BY captured_at_utc, id"
            ).fetchall()
        return [OddsSnapshot(**dict(row)) for row in rows]

    def feed_health(
        self,
        as_of_utc: str,
        expected_books: set[str],
        stale_after_minutes: int = 30,
    ) -> dict[str, object]:
        if stale_after_minutes < 0:
            raise ValueError("stale_after_minutes cannot be negative")
        as_of = parse_utc(as_of_utc, "as_of_utc")
        latest_by_book: dict[str, datetime] = {}
        roles_by_market: dict[tuple[str, str, str, str, str], set[str]] = defaultdict(set)

        snapshots = self.all_snapshots()
        visible_snapshots = []
        for snapshot in snapshots:
            captured = parse_utc(snapshot.captured_at_utc, "captured_at_utc")
            if captured > as_of:
                continue
            visible_snapshots.append(snapshot)
            current = latest_by_book.get(snapshot.sportsbook)
            if current is None or captured > current:
                latest_by_book[snapshot.sportsbook] = captured
            roles_by_market[snapshot.market_key].add(snapshot.snapshot_role)

        seen_books = set(latest_by_book)
        threshold = as_of - timedelta(minutes=stale_after_minutes)
        stale_books = sorted(book for book, seen_at in latest_by_book.items() if seen_at < threshold)
        missing_close_keys = sorted("|".join(key) for key, roles in roles_by_market.items() if "entry" in roles and "close" not in roles)

        return {
            "as_of_utc": as_of.isoformat(),
            "missing_books": sorted(expected_books - seen_books),
            "stale_books": stale_books,
            "markets_missing_close": missing_close_keys,
            "snapshot_count": len(visible_snapshots),
        }
