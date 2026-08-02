import csv

import pytest

from clv_tracker.domain import OddsSnapshot
from clv_tracker.report import build_clv_rows
from clv_tracker.store import SnapshotStore


def snapshots():
    common = {
        "event_id": "SYN-1",
        "starts_at_utc": "2026-07-10T19:00:00Z",
        "sportsbook": "Book Alpha",
        "market_type": "moneyline",
        "selection": "Metro FC",
        "line": "",
    }
    return [
        OddsSnapshot.from_mapping({**common, "captured_at_utc": "2026-07-10T12:00:00Z", "american_odds": "+120", "snapshot_role": "entry"}),
        OddsSnapshot.from_mapping({**common, "captured_at_utc": "2026-07-10T18:45:00Z", "american_odds": "+100", "snapshot_role": "close"}),
    ]


def test_ingestion_is_idempotent(tmp_path):
    store = SnapshotStore(tmp_path / "test.sqlite3")
    first = store.ingest(snapshots())
    second = store.ingest(snapshots())
    assert first == {"inserted": 2, "skipped": 0}
    assert second == {"inserted": 0, "skipped": 2}
    assert len(store.all_snapshots()) == 2


def test_clv_is_positive_when_entry_price_beats_close():
    row = build_clv_rows(snapshots())[0]
    assert row.implied_probability_clv_pp == pytest.approx(4.545)
    assert row.decimal_price_improvement_pct == pytest.approx(10.0)


def test_pairing_uses_latest_entry_that_precedes_close():
    values = snapshots()
    common = values[0]
    later_entry = OddsSnapshot.from_mapping(
        {
            "captured_at_utc": "2026-07-10T18:50:00Z",
            "event_id": common.event_id,
            "starts_at_utc": common.starts_at_utc,
            "sportsbook": common.sportsbook,
            "market_type": common.market_type,
            "selection": common.selection,
            "line": common.line,
            "american_odds": "+130",
            "snapshot_role": "entry",
        }
    )
    row = build_clv_rows([*values, later_entry])[0]
    assert row.entry_odds == 120


def test_feed_health_flags_missing_stale_and_unclosed(tmp_path):
    store = SnapshotStore(tmp_path / "test.sqlite3")
    only_entry = snapshots()[0]
    store.ingest([only_entry])
    health = store.feed_health(
        "2026-07-10T18:50:00Z",
        expected_books={"Book Alpha", "Book Beta"},
        stale_after_minutes=30,
    )
    assert health["missing_books"] == ["Book Beta"]
    assert health["stale_books"] == ["Book Alpha"]
    assert len(health["markets_missing_close"]) == 1


def test_feed_health_excludes_snapshots_after_as_of(tmp_path):
    store = SnapshotStore(tmp_path / "test.sqlite3")
    store.ingest(snapshots())
    health = store.feed_health(
        "2026-07-10T12:30:00Z",
        expected_books={"Book Alpha"},
        stale_after_minutes=60,
    )
    assert health["snapshot_count"] == 1
    assert health["markets_missing_close"]


def test_feed_health_rejects_negative_staleness_window(tmp_path):
    store = SnapshotStore(tmp_path / "test.sqlite3")
    with pytest.raises(ValueError, match="stale_after_minutes"):
        store.feed_health("2026-07-10T12:30:00Z", set(), stale_after_minutes=-1)


def test_changed_start_time_is_versioned_not_silently_skipped(tmp_path):
    store = SnapshotStore(tmp_path / "test.sqlite3")
    original = snapshots()[0]
    changed = OddsSnapshot.from_mapping(
        {
            "captured_at_utc": original.captured_at_utc,
            "event_id": original.event_id,
            "starts_at_utc": "2026-07-10T20:00:00Z",
            "sportsbook": original.sportsbook,
            "market_type": original.market_type,
            "selection": original.selection,
            "line": original.line,
            "american_odds": str(original.american_odds),
            "snapshot_role": original.snapshot_role,
        }
    )
    result = store.ingest([original, changed])
    assert result == {"inserted": 2, "skipped": 0}
