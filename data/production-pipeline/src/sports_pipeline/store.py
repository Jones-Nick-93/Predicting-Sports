from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime
from pathlib import Path

from .domain import Snapshot


SCHEMA = """
PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS payloads (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    checksum TEXT NOT NULL,
    received_at_utc TEXT NOT NULL,
    body BLOB NOT NULL,
    UNIQUE(source, checksum)
);
CREATE TABLE IF NOT EXISTS snapshots (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    payload_id INTEGER NOT NULL REFERENCES payloads(id),
    captured_at_utc TEXT NOT NULL,
    event_id TEXT NOT NULL,
    starts_at_utc TEXT NOT NULL,
    sportsbook TEXT NOT NULL,
    market_type TEXT NOT NULL,
    selection TEXT NOT NULL,
    line TEXT NOT NULL,
    american_odds INTEGER NOT NULL,
    snapshot_role TEXT NOT NULL,
    UNIQUE(source, captured_at_utc, event_id, starts_at_utc, sportsbook,
           market_type, selection, line, american_odds, snapshot_role)
);
CREATE TABLE IF NOT EXISTS quarantine (
    id INTEGER PRIMARY KEY,
    payload_id INTEGER NOT NULL REFERENCES payloads(id),
    row_index INTEGER NOT NULL,
    reason TEXT NOT NULL,
    row_json TEXT NOT NULL,
    UNIQUE(payload_id, row_index)
);
CREATE TABLE IF NOT EXISTS runs (
    run_id TEXT PRIMARY KEY,
    source TEXT NOT NULL,
    started_at_utc TEXT NOT NULL,
    ended_at_utc TEXT,
    status TEXT NOT NULL,
    attempts INTEGER NOT NULL DEFAULT 0,
    payload_checksum TEXT,
    rows_seen INTEGER NOT NULL DEFAULT 0,
    rows_written INTEGER NOT NULL DEFAULT 0,
    rows_quarantined INTEGER NOT NULL DEFAULT 0,
    error_class TEXT,
    error_message TEXT
);
CREATE TABLE IF NOT EXISTS alerts (
    id INTEGER PRIMARY KEY,
    alert_key TEXT NOT NULL UNIQUE,
    first_seen_at_utc TEXT NOT NULL,
    last_seen_at_utc TEXT NOT NULL,
    run_id TEXT NOT NULL,
    message TEXT NOT NULL,
    occurrences INTEGER NOT NULL DEFAULT 1,
    resolved INTEGER NOT NULL DEFAULT 0
);
"""


class PipelineStore:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.initialize()

    def connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    def start_run(self, run_id: str, source: str, started_at_utc: str) -> None:
        with self.connect() as connection:
            connection.execute(
                "INSERT INTO runs(run_id, source, started_at_utc, status) VALUES (?, ?, ?, 'running')",
                (run_id, source, started_at_utc),
            )

    def finish_run(self, run_id: str, ended_at_utc: str, **fields: object) -> None:
        allowed = {
            "status", "attempts", "payload_checksum", "rows_seen", "rows_written",
            "rows_quarantined", "error_class", "error_message",
        }
        unknown = set(fields).difference(allowed)
        if unknown:
            raise ValueError(f"unsupported run fields: {', '.join(sorted(unknown))}")
        assignments = ["ended_at_utc = ?", *[f"{name} = ?" for name in fields]]
        values = [ended_at_utc, *fields.values(), run_id]
        with self.connect() as connection:
            connection.execute(
                f"UPDATE runs SET {', '.join(assignments)} WHERE run_id = ?",
                values,
            )

    def process_payload(
        self,
        source: str,
        body: bytes,
        received_at_utc: str,
    ) -> dict[str, object]:
        checksum = hashlib.sha256(body).hexdigest()
        with self.connect() as connection:
            existing = connection.execute(
                "SELECT id FROM payloads WHERE source = ? AND checksum = ?",
                (source, checksum),
            ).fetchone()
            if existing:
                return {
                    "checksum": checksum,
                    "duplicate_payload": True,
                    "rows_seen": 0,
                    "rows_written": 0,
                    "rows_quarantined": 0,
                }

            cursor = connection.execute(
                "INSERT INTO payloads(source, checksum, received_at_utc, body) VALUES (?, ?, ?, ?)",
                (source, checksum, received_at_utc, body),
            )
            payload_id = int(cursor.lastrowid)
            try:
                document = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                connection.execute(
                    "INSERT INTO quarantine(payload_id, row_index, reason, row_json) VALUES (?, -1, ?, ?)",
                    (payload_id, f"invalid_json: {exc}", "null"),
                )
                return {
                    "checksum": checksum,
                    "duplicate_payload": False,
                    "rows_seen": 0,
                    "rows_written": 0,
                    "rows_quarantined": 1,
                }

            rows = document.get("snapshots") if isinstance(document, dict) else None
            schema_version = document.get("schema_version") if isinstance(document, dict) else None
            if schema_version != 1 or not isinstance(rows, list):
                reason = (
                    "unsupported schema_version"
                    if schema_version != 1
                    else "document must contain a snapshots list"
                )
                connection.execute(
                    "INSERT INTO quarantine(payload_id, row_index, reason, row_json) VALUES (?, -1, ?, ?)",
                    (payload_id, reason, json.dumps(document, sort_keys=True)),
                )
                return {
                    "checksum": checksum,
                    "duplicate_payload": False,
                    "rows_seen": 0,
                    "rows_written": 0,
                    "rows_quarantined": 1,
                }

            written = 0
            quarantined = 0
            insert_sql = """
                INSERT OR IGNORE INTO snapshots(
                    source, payload_id, captured_at_utc, event_id, starts_at_utc,
                    sportsbook, market_type, selection, line, american_odds, snapshot_role
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            for index, row in enumerate(rows):
                try:
                    if not isinstance(row, dict):
                        raise ValueError("snapshot row must be an object")
                    snapshot = Snapshot.from_mapping(row)
                except ValueError as exc:
                    quarantined += 1
                    connection.execute(
                        "INSERT INTO quarantine(payload_id, row_index, reason, row_json) VALUES (?, ?, ?, ?)",
                        (payload_id, index, str(exc), json.dumps(row, sort_keys=True)),
                    )
                    continue
                cursor = connection.execute(
                    insert_sql,
                    (source, payload_id, *snapshot.to_dict().values()),
                )
                written += int(cursor.rowcount == 1)
            return {
                "checksum": checksum,
                "duplicate_payload": False,
                "rows_seen": len(rows),
                "rows_written": written,
                "rows_quarantined": quarantined,
            }

    def upsert_alert(self, key: str, now_utc: str, run_id: str, message: str) -> None:
        with self.connect() as connection:
            connection.execute(
                """
                INSERT INTO alerts(alert_key, first_seen_at_utc, last_seen_at_utc, run_id, message)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(alert_key) DO UPDATE SET
                    last_seen_at_utc = excluded.last_seen_at_utc,
                    run_id = excluded.run_id,
                    message = excluded.message,
                    occurrences = alerts.occurrences + 1,
                    resolved = 0
                """,
                (key, now_utc, now_utc, run_id, message),
            )

    def latest_successful_run(self, source: str) -> dict[str, object] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT * FROM runs WHERE source = ? AND status = 'succeeded' "
                "ORDER BY ended_at_utc DESC, rowid DESC LIMIT 1",
                (source,),
            ).fetchone()
        return dict(row) if row else None

    def latest_snapshot(self, source: str) -> dict[str, object] | None:
        with self.connect() as connection:
            row = connection.execute(
                "SELECT captured_at_utc, event_id, starts_at_utc, sportsbook, market_type, "
                "selection, line, american_odds, snapshot_role FROM snapshots "
                "WHERE source = ? ORDER BY captured_at_utc DESC, id DESC LIMIT 1",
                (source,),
            ).fetchone()
        return dict(row) if row else None

    def counts(self) -> dict[str, int]:
        with self.connect() as connection:
            return {
                table: int(connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0])
                for table in ("payloads", "snapshots", "quarantine", "runs", "alerts")
            }
