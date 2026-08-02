from __future__ import annotations

import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from typing import Callable

from .retry import PermanentSourceError, RetryPolicy, TransientSourceError, fetch_with_retry
from .store import PipelineStore


@dataclass(frozen=True)
class RunResult:
    run_id: str
    source: str
    status: str
    attempts: int
    payload_checksum: str | None
    rows_seen: int
    rows_written: int
    rows_quarantined: int
    error_class: str | None = None

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True)


class PipelineService:
    def __init__(
        self,
        store: PipelineStore,
        *,
        retry_policy: RetryPolicy | None = None,
        clock: Callable[[], datetime] | None = None,
    ):
        self.store = store
        self.retry_policy = retry_policy or RetryPolicy()
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def _now(self) -> str:
        value = self.clock()
        if value.tzinfo is None or value.utcoffset() is None:
            raise ValueError("service clock must return a timezone-aware datetime")
        return value.astimezone(timezone.utc).isoformat()

    def run(self, source: str, fetcher: Callable[[], bytes], *, run_id: str | None = None) -> RunResult:
        if not source.strip():
            raise ValueError("source is required")
        run_id = run_id or str(uuid.uuid4())
        self.store.start_run(run_id, source, self._now())
        attempts = 0
        try:
            body, attempts = fetch_with_retry(fetcher, self.retry_policy)
            outcome = self.store.process_payload(source, body, self._now())
            quarantined = int(outcome["rows_quarantined"])
            status = "partial" if quarantined else "succeeded"
            result = RunResult(
                run_id=run_id,
                source=source,
                status=status,
                attempts=attempts,
                payload_checksum=str(outcome["checksum"]),
                rows_seen=int(outcome["rows_seen"]),
                rows_written=int(outcome["rows_written"]),
                rows_quarantined=quarantined,
                error_class="validation" if quarantined else None,
            )
            self.store.finish_run(
                run_id,
                self._now(),
                status=status,
                attempts=attempts,
                payload_checksum=result.payload_checksum,
                rows_seen=result.rows_seen,
                rows_written=result.rows_written,
                rows_quarantined=result.rows_quarantined,
                error_class=result.error_class,
            )
            if quarantined:
                self.store.upsert_alert(
                    f"{source}:validation",
                    self._now(),
                    run_id,
                    f"{quarantined} row(s) quarantined; inspect run {run_id}",
                )
            return result
        except (TransientSourceError, PermanentSourceError) as exc:
            error_class = "transient" if isinstance(exc, TransientSourceError) else "permanent"
            attempts = attempts or self.retry_policy.max_attempts if error_class == "transient" else 1
            self.store.finish_run(
                run_id,
                self._now(),
                status="failed",
                attempts=attempts,
                error_class=error_class,
                error_message=str(exc),
            )
            self.store.upsert_alert(
                f"{source}:{error_class}", self._now(), run_id,
                f"{error_class} source failure; inspect run {run_id}",
            )
            return RunResult(run_id, source, "failed", attempts, None, 0, 0, 0, error_class)
        except Exception as exc:
            diagnostic = f"unexpected {type(exc).__name__}"
            self.store.finish_run(
                run_id,
                self._now(),
                status="failed",
                attempts=max(attempts, 1),
                error_class="operator_action",
                error_message=diagnostic,
            )
            self.store.upsert_alert(
                f"{source}:operator_action",
                self._now(),
                run_id,
                f"{diagnostic}; inspect run {run_id}",
            )
            return RunResult(run_id, source, "failed", max(attempts, 1), None, 0, 0, 0, "operator_action")
