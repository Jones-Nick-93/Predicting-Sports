# Codex Working Agreement

## Purpose

Maintain a public-safe uncertainty and abstention laboratory for time-ordered
predictive systems. Prefer calibrated uncertainty, explicit failure states, and
honest negative results over narrow intervals or impressive point estimates.

## Boundaries

- Use generated data only.
- Never add real fixtures, prices, predictions, wagers, bankrolls, proprietary
  features, fitted private parameters, credentials, or licensed data.
- Never random-split time-ordered evaluation data.
- Fit models on training data, conformalize on later calibration data, and
  evaluate once on still-later test data.
- Derive gate thresholds without consulting test outcomes.
- Report interval coverage together with width and regime segments.
- Conformal coverage assumptions must be stated; distribution shift may break
  nominal coverage.
- No result grants wagering or production authority.

## Commands

```text
python -m pip install -r requirements-dev.txt
python -m pytest
python examples/run_uncertainty_demo.py
```

## Definition of done

- Time and split invariants pass.
- MAPIE and NGBoost adapters produce finite ordered intervals.
- Coverage, width, and abstention results are segmented by regime.
- The synthetic demo is deterministic.
- Public-scope and model-card limitations remain accurate.

