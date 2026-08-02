# Production Pipeline Architecture

## Components

1. **Scheduler** triggers a source-specific job with a unique run ID.
2. **Fetcher** retrieves one bounded payload with timeout and response metadata.
3. **Raw ledger** stores checksum, capture time, source, and immutable payload location.
4. **Validator** enforces schema, timestamps, ranges, and required relationships.
   The public payload contract currently accepts only `schema_version: 1`.
5. **Normalizer** maps source fields into the public snapshot contract.
6. **Writer** performs transactional, idempotent upserts.
7. **Observer** emits structured run metrics and freshness state.
8. **API** exposes liveness, readiness, and the latest safe snapshot. Readiness checks
   both successful-run recency and source-data freshness so a recent no-op run cannot
   make old data appear current.
9. **Alerter** sends one actionable event per unresolved failure condition.

## Failure policy

| Failure | Retry? | Result |
|---|---:|---|
| Timeout / 429 / selected 5xx | Bounded | Backoff with jitter |
| Authentication failure | No | Operator alert; redact credential |
| Schema violation | No | Quarantine payload and alert |
| Duplicate payload | No | Record no-op success |
| Partial source response | Policy-based | Mark incomplete; do not claim readiness |

## Deployment target

Begin with one Docker container or one Python service managed by systemd on the
DigitalOcean Droplet. Use a non-root service account, read-only deploy artifact,
environment-provided secrets, log rotation, monitoring, and tested backups. Add a
message queue only after measured load or failure isolation requires one.
