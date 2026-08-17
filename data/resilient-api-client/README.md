# Resilient API Client

A provider-neutral Python transport for API jobs that run unattended. It demonstrates
bounded retries, bearer-token refresh, conflict-aware creates, and guarded deletion
without embedding a real provider's endpoints, payload schema, or credentials.

## What it demonstrates

- One token refresh and request replay after an HTTP 401
- Retries for connection failures, HTTP 429, and selected 5xx responses
- `Retry-After` support plus bounded exponential backoff and jitter
- HTTP 409 as an optional, explicit conflict outcome
- Dry-run defaults and a second confirmation gate for bulk deletion
- Relative-path enforcement so bearer tokens cannot be sent to another host
- Error messages that omit tokens, payloads, and provider exception text

## Synthetic example

```python
import os

from resilient_client import ResilientApiClient

client = ResilientApiClient(
    base_url="https://api.example.invalid",
    token_provider=lambda: os.environ["DEMO_API_TOKEN"],
    dry_run=True,
)

items = client.list_resources("/v1/items", result_field="items")

created, conflicted = client.create_resource(
    "/v1/items",
    {"external_id": "sample-001", "label": "Synthetic item"},
)
```

`example.invalid` is a reserved non-production domain. All resource names, paths, and
payloads in this project are fabricated.

## Authentication boundary

The caller supplies a zero-argument `token_provider`. It may read an environment
variable, call an OAuth library, or obtain a short-lived credential from a secret
manager. This project deliberately does not prescribe an authentication endpoint,
credential payload, token response field, tenant identifier, or vendor SDK.

## Destructive-operation boundary

`dry_run` defaults to `True`. Bulk deletion requires both `dry_run=False` and
`confirm=True`. Callers remain responsible for authorization, audit logging,
environment controls, and any provider-specific recovery process.

## Run

```bash
python -m pip install -e ".[dev]"
python -m pytest -q
python -m compileall -q resilient_client.py test_resilient_client.py
python examples/run_demo.py
```

## Limitations

- This is a synchronous demonstration client, not a complete SDK.
- It does not implement pagination, distributed rate limiting, circuit breaking, or
  idempotency-key generation.
- A 409 is treated as a conflict only when the caller explicitly allows it.
- Retry safety still depends on the remote operation being idempotent or protected by
  a provider-supported idempotency key.

## Publication boundary

No real hosts, endpoints, payload fields, account identifiers, credentials, vendor
responses, or production retry settings are included.

Released under the MIT License. See `LICENSE`.
