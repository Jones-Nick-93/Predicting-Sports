# Model card

## Intended use

Educational and portfolio demonstration of uncertainty measurement and
abstention under chronological evaluation.

## Models

- Histogram gradient boosting point baseline.
- MAPIE split-conformal wrapper around the point model.
- NGBoost Normal conditional distribution challenger.

## Data

Deterministic synthetic rows with strength, pace, volatility, and trend features.
The final portion introduces a known covariate and noise-regime shift.

## Timing

Training, conformalization, and testing are strictly chronological. All feature
availability timestamps precede prediction time.

## Evaluation

- MAE and RMSE for point accuracy.
- Empirical interval coverage.
- Mean interval width.
- Winkler interval score.
- Eligible/review routing rates.
- Stable and shifted test segments.

## Limitations

- Synthetic structure may favor or penalize particular models.
- Split-conformal marginal coverage relies on exchangeability assumptions that
  the late regime shift intentionally stresses.
- NGBoost assumes a conditional Normal distribution in this demonstration.
- Marginal coverage does not guarantee useful conditional coverage for every group.
- No betting, profit, or production-readiness conclusion is supported.

## Promotion criteria

No model is promoted. A real extension would require frozen point-in-time data,
pre-registered metrics, walk-forward evaluation, calibration by important
segments, and operational monitoring.

