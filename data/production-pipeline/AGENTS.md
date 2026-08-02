# Codex Working Agreement

- Start with synthetic/public inputs and a documented schema.
- Preserve raw payloads by checksum; never silently overwrite source evidence.
- Every write must be idempotent or protected by a deterministic uniqueness key.
- Classify errors as validation, transient, permanent, or operator action required.
- Bound retries; add jitter; never retry invalid data forever.
- Use structured logs without credentials or full private payloads.
- Separate liveness from readiness and test both.
- Add failure-path tests before adding another integration.
- Keep forecasting, selection, and staking logic outside this repository.
