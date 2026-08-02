from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from typing import Callable, Iterable

from .domain import parse_utc
from .store import PipelineStore


class PipelineApi:
    def __init__(
        self,
        store: PipelineStore,
        source: str,
        *,
        freshness: timedelta = timedelta(hours=1),
        clock: Callable[[], datetime] | None = None,
    ):
        if freshness <= timedelta(0):
            raise ValueError("freshness must be positive")
        self.store = store
        self.source = source
        self.freshness = freshness
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def handle(self, path: str) -> tuple[int, dict[str, object]]:
        if path == "/health":
            return 200, {"status": "ok"}
        if path == "/ready":
            run = self.store.latest_successful_run(self.source)
            if not run:
                return 503, {"status": "not_ready", "reason": "no_successful_run"}
            ended = parse_utc(str(run["ended_at_utc"]), "ended_at_utc")
            now = self.clock()
            if now.tzinfo is None or now.utcoffset() is None:
                raise ValueError("API clock must return a timezone-aware datetime")
            now = now.astimezone(timezone.utc)
            if now - ended > self.freshness:
                return 503, {"status": "not_ready", "reason": "stale_success"}
            snapshot = self.store.latest_snapshot(self.source)
            if not snapshot:
                return 503, {"status": "not_ready", "reason": "no_snapshot"}
            captured = parse_utc(str(snapshot["captured_at_utc"]), "captured_at_utc")
            if now - captured > self.freshness:
                return 503, {"status": "not_ready", "reason": "stale_data"}
            return 200, {"status": "ready", "run_id": run["run_id"]}
        if path == "/latest-snapshot":
            snapshot = self.store.latest_snapshot(self.source)
            if not snapshot:
                return 404, {"status": "not_found"}
            return 200, snapshot
        return 404, {"status": "not_found"}

    def wsgi(self, environ: dict[str, object], start_response: Callable[..., object]) -> Iterable[bytes]:
        status_code, payload = self.handle(str(environ.get("PATH_INFO", "/")))
        body = json.dumps(payload, sort_keys=True).encode("utf-8")
        label = "OK" if status_code == 200 else "Not Found" if status_code == 404 else "Service Unavailable"
        start_response(
            f"{status_code} {label}",
            [("Content-Type", "application/json"), ("Content-Length", str(len(body)))],
        )
        return [body]
