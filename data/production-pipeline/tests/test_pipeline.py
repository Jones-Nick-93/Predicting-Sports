import json
from datetime import datetime, timezone

from sports_pipeline import PipelineService, PipelineStore


NOW = datetime(2026, 7, 10, 18, 50, tzinfo=timezone.utc)


def payload(odds=105, include_invalid=False):
    rows = [
        {
            "captured_at_utc": "2026-07-10T18:45:00Z",
            "event_id": "SYN-1",
            "starts_at_utc": "2026-07-10T19:00:00Z",
            "sportsbook": "Book Alpha",
            "market_type": "moneyline",
            "selection": "Metro FC",
            "line": "",
            "american_odds": odds,
            "snapshot_role": "close",
        }
    ]
    if include_invalid:
        rows.append({"event_id": "broken"})
    return json.dumps({"schema_version": 1, "snapshots": rows}, sort_keys=True).encode()


def service(tmp_path):
    store = PipelineStore(tmp_path / "pipeline.sqlite3")
    return store, PipelineService(store, clock=lambda: NOW)


def test_replayed_payload_is_a_noop_success(tmp_path):
    store, pipeline = service(tmp_path)
    first = pipeline.run("demo", lambda: payload(), run_id="run-1")
    second = pipeline.run("demo", lambda: payload(), run_id="run-2")
    assert first.rows_written == 1
    assert second.status == "succeeded" and second.rows_written == 0
    assert store.counts()["payloads"] == 1
    assert store.counts()["snapshots"] == 1


def test_changed_payload_is_versioned(tmp_path):
    store, pipeline = service(tmp_path)
    pipeline.run("demo", lambda: payload(105), run_id="run-1")
    pipeline.run("demo", lambda: payload(110), run_id="run-2")
    counts = store.counts()
    assert counts["payloads"] == 2 and counts["snapshots"] == 2


def test_bad_row_is_quarantined_without_poisoning_good_row(tmp_path):
    store, pipeline = service(tmp_path)
    result = pipeline.run("demo", lambda: payload(include_invalid=True), run_id="run-1")
    assert result.status == "partial"
    assert result.rows_written == 1 and result.rows_quarantined == 1
    assert store.counts()["alerts"] == 1


def test_alert_is_deduplicated_across_repeated_condition(tmp_path):
    store, pipeline = service(tmp_path)
    pipeline.run("demo", lambda: payload(105, True), run_id="run-1")
    pipeline.run("demo", lambda: payload(110, True), run_id="run-2")
    assert store.counts()["alerts"] == 1


def test_unsupported_schema_version_is_quarantined(tmp_path):
    store, pipeline = service(tmp_path)
    body = json.dumps({"schema_version": 2, "snapshots": []}).encode()
    result = pipeline.run("demo", lambda: body, run_id="run-1")
    assert result.status == "partial" and result.rows_quarantined == 1
