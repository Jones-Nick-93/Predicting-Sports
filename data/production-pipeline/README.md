# Production Sports Data Pipeline

A public-safe reference implementation focused on reliable data engineering rather
than prediction. It processes only fabricated snapshots and uses the Python standard
library plus SQLite so the operational behavior is easy to inspect.

## Implemented vertical slice

```text
scheduled synthetic/public pull
  -> raw payload checksum
  -> idempotent ingestion key
  -> normalized event/market tables
  -> schema and freshness checks
  -> retry with bounded backoff
  -> structured run log + metrics
  -> health/readiness API
  -> alert on stale, partial, or failed runs
```

## Acceptance criteria for the first implementation

- Replaying the same payload creates no duplicate facts.
- A changed source payload is versioned rather than overwritten silently.
- Schema violations are quarantined with a reason and do not poison good rows.
- Retries happen only for classified transient failures and stop after a fixed budget.
- Every run records start/end time, source, row counts, checksum, status, and error.
- `/health` proves the service process is alive; `/ready` proves required data is fresh.
- Alerts are deduplicated and contain a run ID plus a direct diagnostic.
- Secrets come from environment/service configuration and never appear in Git or logs.

## Run

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python scripts/demo.py
```

The demo is deterministic and writes only ignored artifacts. The service exposes a
small WSGI-compatible API surface through `PipelineApi`, with `/health`, `/ready`, and
`/latest-snapshot` kept intentionally separate.
