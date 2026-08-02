# Odds + Closing-Line-Value Tracker

A public-safe portfolio project that ingests fabricated odds snapshots, normalizes
market keys, stores snapshots idempotently in SQLite, detects stale or incomplete
feeds, compares entry prices with closing prices, and generates a small HTML
dashboard.

This starter intentionally uses synthetic soccer events and prices. It contains no
book credentials, private data-source details, real wagers, staking rules, or claims
of predictive edge.

## What the first vertical slice proves

- A documented snapshot data contract
- Validation and normalization at the ingestion boundary
- Canonical UTC storage and strict as-of filtering for health reports
- Idempotent storage with database uniqueness constraints
- Explicit feed-health checks for staleness, missing books, and missing closes
- Two clearly labeled CLV measures:
  - implied-probability movement in percentage points;
  - decimal-price improvement versus the close
- A generated, dependency-free HTML dashboard
- Automated tests and GitHub Actions CI

## Run the demo

```bash
python scripts/demo.py
```

The command creates `artifacts/clv_demo.sqlite3` and
`artifacts/clv_dashboard.html`, prints an ingestion/health summary, and can be run
again without duplicating rows.

## Run tests

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
```

## Important limitations

- The demo compares raw single-selection implied probabilities; it does not remove
  the sportsbook margin. A production-grade no-vig CLV measure requires complete,
  synchronized prices for every outcome in the market.
- `snapshot_role=close` is supplied by the input. A real pipeline needs a documented
  close policy such as the last valid snapshot before market lock.
- This is tracking infrastructure, not a forecasting or recommendation system.

See `docs/data-contract.md` and `docs/architecture.md` for the exact boundaries.
