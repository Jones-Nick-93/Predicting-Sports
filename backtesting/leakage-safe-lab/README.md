# Leakage-Safe Backtesting Lab

A public-safe starter for demonstrating time-aware evaluation, walk-forward splits,
calibration, uncertainty, and realistic execution filters on synthetic predictions.

The starter contains no forecasting model and no real wagers. Its job is to make
invalid evaluation harder.

## Run

```bash
python scripts/demo.py
python -m pytest -q
```

## Current vertical slice

- Expanding walk-forward splits
- Configurable embargo rows between training and testing
- Assertions that every training timestamp precedes every test timestamp
- Frozen feature manifests with as-of joins that exclude future values
- Brier score and reliability bins
- Deterministic bootstrap confidence interval for Brier score
- Execution eligibility based on availability time, event lock, latency, and limits
- A model-card template centered on failure modes

All timestamps used for splitting, feature availability, and execution must be
timezone-aware. The lab deliberately contains evaluation infrastructure rather than a
forecasting model or selection strategy.
