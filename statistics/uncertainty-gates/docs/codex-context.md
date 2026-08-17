# Betting project context

## Decision and market

The project makes no market or wagering decision. It decides whether a synthetic
prediction is eligible for downstream consideration or must be reviewed.

## Time semantics

- `event_time`: when the synthetic outcome occurs.
- `publication_time`: when the synthetic source value is published.
- `ingestion_time`: when the pipeline receives it.
- `feature_available_time`: when the derived feature can be used.
- `prediction_time`: the simulated decision timestamp.

The required ordering is publication <= ingestion <= feature availability <=
prediction < event.

## Data sources and rights

All rows are generated deterministically in memory. No external data are used.

## Normalization contract

Features and targets must be finite. Intervals must have equal one-dimensional
shape, finite bounds, and lower <= point <= upper.

## Leakage controls

Splits are chronological. Model fitting uses the earliest block,
conformalization uses the next block, and evaluation uses the final block.
Thresholds are never selected from test outcomes.

## Backtest and execution assumptions

There is no backtest, market availability, entry, fill, limit, close, settlement,
or bankroll assumption.

## Evaluation and calibration

Report empirical coverage, mean width, Winkler interval score, MAE, RMSE, and
gate routing overall and by stable/shifted regime.

## Public/private boundary

Public: generated process, package adapters, metrics, gates, tests, limitations.
Excluded: real data, prices, predictions, parameters, wagers, accounts,
selection rules, and private infrastructure.

