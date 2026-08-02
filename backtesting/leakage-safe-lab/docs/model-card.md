# Model Card Template

## Intended use

What decision is being evaluated? Who should and should not use the result?

## Prediction timestamp

Define the exact `as_of_utc` cutoff and prove every feature existed by that time.

## Data and exclusions

List sources, licenses, missingness, delayed fields, corrections, and excluded rows.

## Evaluation design

- Training window and test window
- Walk-forward cadence
- Embargo duration and why it is sufficient
- Transformations/calibration fit only on training data
- Frozen metrics and decision thresholds

## Execution assumptions

Record availability time, decision latency, market lock, limits, slippage, rejected
orders, and the close definition. State what is simulated versus observed.

## Results with uncertainty

Report sample size, calibration, Brier/log loss, CLV where valid, ROI where valid,
confidence intervals, maximum drawdown, and sensitivity to assumptions.

## Failure modes

Cover feed delays, timestamp mistakes, label leakage, schema drift, stale prices,
selection bias, multiple testing, regime change, and insufficient sample size.

## Promotion rule

Define in advance what evidence promotes, revises, or kills the experiment.
