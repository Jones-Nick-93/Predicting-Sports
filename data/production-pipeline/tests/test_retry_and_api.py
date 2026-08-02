from datetime import datetime, timedelta, timezone

from sports_pipeline import (
    PermanentSourceError,
    PipelineApi,
    PipelineService,
    PipelineStore,
    RetryPolicy,
    TransientSourceError,
)

from test_pipeline import NOW, payload


def test_transient_failure_retries_with_fixed_budget(tmp_path):
    attempts = 0

    def fetcher():
        nonlocal attempts
        attempts += 1
        if attempts < 3:
            raise TransientSourceError("temporary")
        return payload()

    store = PipelineStore(tmp_path / "pipeline.sqlite3")
    service = PipelineService(store, retry_policy=RetryPolicy(3, 0, 0), clock=lambda: NOW)
    result = service.run("demo", fetcher, run_id="run-1")
    assert result.status == "succeeded" and attempts == 3 and result.attempts == 3


def test_permanent_failure_does_not_retry_and_alerts(tmp_path):
    attempts = 0

    def fetcher():
        nonlocal attempts
        attempts += 1
        raise PermanentSourceError("bad configuration")

    store = PipelineStore(tmp_path / "pipeline.sqlite3")
    result = PipelineService(store, clock=lambda: NOW).run("demo", fetcher, run_id="run-1")
    assert result.status == "failed" and result.error_class == "permanent"
    assert attempts == 1 and store.counts()["alerts"] == 1


def test_unexpected_failure_is_closed_for_operator_action(tmp_path):
    store = PipelineStore(tmp_path / "pipeline.sqlite3")

    def fetcher():
        raise RuntimeError("unexpected detail that should not leak into the result")

    result = PipelineService(store, clock=lambda: NOW).run("demo", fetcher, run_id="run-1")
    assert result.status == "failed" and result.error_class == "operator_action"
    assert store.counts()["alerts"] == 1


def test_health_readiness_and_latest_snapshot_are_separate(tmp_path):
    store = PipelineStore(tmp_path / "pipeline.sqlite3")
    service = PipelineService(store, clock=lambda: NOW)
    api = PipelineApi(store, "demo", freshness=timedelta(minutes=30), clock=lambda: NOW)
    assert api.handle("/health") == (200, {"status": "ok"})
    assert api.handle("/ready")[0] == 503
    service.run("demo", lambda: payload(), run_id="run-1")
    assert api.handle("/ready") == (200, {"status": "ready", "run_id": "run-1"})
    assert api.handle("/latest-snapshot")[0] == 200

    stale_api = PipelineApi(
        store,
        "demo",
        freshness=timedelta(minutes=30),
        clock=lambda: NOW + timedelta(hours=1),
    )
    assert stale_api.handle("/health")[0] == 200
    assert stale_api.handle("/ready") == (503, {"status": "not_ready", "reason": "stale_success"})


def test_new_noop_run_does_not_make_old_data_ready(tmp_path):
    store = PipelineStore(tmp_path / "pipeline.sqlite3")
    PipelineService(store, clock=lambda: NOW).run("demo", lambda: payload(), run_id="run-1")
    later = NOW + timedelta(hours=2)
    PipelineService(store, clock=lambda: later).run("demo", lambda: payload(), run_id="run-2")
    api = PipelineApi(store, "demo", freshness=timedelta(minutes=30), clock=lambda: later)
    assert api.handle("/ready") == (503, {"status": "not_ready", "reason": "stale_data"})
