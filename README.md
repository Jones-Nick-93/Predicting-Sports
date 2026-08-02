# Predicting Sports

Public-safe sports analytics projects built to demonstrate software engineering,
testing, and quantitative reasoning without publishing private forecasting IP.

## Projects

### Soccer

- [`soccer/market-math`](soccer/market-math) — tested American-odds conversion and
  push-aware Asian-handicap settlement using fabricated probability grids.

### Odds infrastructure

- [`odds/clv-tracker`](odds/clv-tracker) — idempotent synthetic odds ingestion,
  market normalization, feed-health checks, entry-versus-close reporting, and a
  static HTML dashboard.

### Evaluation

- [`backtesting/leakage-safe-lab`](backtesting/leakage-safe-lab) — expanding
  walk-forward splits, embargoes, as-of feature joins, calibration diagnostics,
  bootstrap uncertainty, and realistic execution filters.

### Data engineering

- [`data/production-pipeline`](data/production-pipeline) — immutable payload
  checksums, row quarantine, idempotent SQLite writes, bounded retries, structured
  run telemetry, deduplicated alerts, and health/readiness API behavior.

## Publication boundary

Every project in this repository is intended for public portfolio use. It must exclude
credentials, private or licensed data, live projections, production parameters,
selection and staking rules, private-system architecture, and performance claims that
cannot be reproduced from included public-safe materials.

Project-specific publication policies and development instructions live alongside each
project.
