# Predicting Sports

Public-safe sports analytics projects built to demonstrate software engineering,
testing, and quantitative reasoning without publishing private forecasting IP.

## Projects

### Baseball

- [`baseball/mlb-simulation-engine`](baseball/mlb-simulation-engine) — seeded
  plate-appearance simulation with regulation and extra-inning accounting,
  starter-to-bullpen workload transitions, a shared event ledger, stable player
  identifiers, and push-aware pricing across game and player markets.

### Soccer

- [`soccer/market-math`](soccer/market-math) — tested American-odds conversion and
  push-aware Asian-handicap settlement using fabricated probability grids.

### Odds infrastructure

- [`odds/clv-tracker`](odds/clv-tracker) — idempotent synthetic odds ingestion,
  market normalization, feed-health checks, entry-versus-close reporting, and a
  static HTML dashboard.

- [`odds/market-invariants`](odds/market-invariants) — property-based tests for
  probability, odds, devig, alternate-line, and generic Kelly arithmetic.

### Evaluation

- [`backtesting/leakage-safe-lab`](backtesting/leakage-safe-lab) — expanding
  walk-forward splits, embargoes, as-of feature joins, calibration diagnostics,
  bootstrap uncertainty, and realistic execution filters.

### Statistical governance

- [`statistics/experiment-governance`](statistics/experiment-governance) — fixed
  experiment-family registration, complete trial retention, Bonferroni/Holm
  corrections, weighted-sample diagnostics, and paired sign-flip inference.

- [`statistics/uncertainty-gates`](statistics/uncertainty-gates) — time-ordered
  prediction intervals, regime-aware coverage diagnostics, and explicit abstention.

### Data engineering

- [`data/production-pipeline`](data/production-pipeline) — immutable payload
  checksums, row quarantine, idempotent SQLite writes, bounded retries, structured
  run telemetry, deduplicated alerts, and health/readiness API behavior.

- [`data/resilient-api-client`](data/resilient-api-client) — bounded retries,
  one-time token refresh, conflict-aware creates, host-safe relative paths, and
  dry-run deletion gates exercised through a fake transport.

## Publication boundary

Every project in this repository is intended for public portfolio use. It must exclude
credentials, private or licensed data, live projections, production parameters,
selection and staking rules, private-system architecture, and performance claims that
cannot be reproduced from included public-safe materials.

Project-specific publication policies and development instructions live alongside each
project.
