# Uncertainty Gates

A public-safe laboratory for adding prediction intervals and explicit abstention
states to time-ordered sports-like regression systems.

The included synthetic process has heteroscedastic noise and a late regime shift.
It compares:

- A point-prediction baseline.
- MAPIE split-conformal intervals.
- NGBoost conditional Normal distributions.
- A gate that routes wide or out-of-domain predictions to review.

## Run

```text
python -m pip install -r requirements-dev.txt
python -m pytest
python examples/run_uncertainty_demo.py
```

## What this project demonstrates

- Chronological train/conformalization/test separation.
- Explicit publication, ingestion, feature-availability, prediction, and event time.
- Coverage, interval width, Winkler score, MAE, and RMSE.
- Stable-versus-shifted regime evaluation.
- Gate thresholds derived without test outcomes.
- Abstention as a first-class model output.

## Reproducible example signal

With the committed demo seed and 90% nominal intervals, the stable synthetic
segment achieved 92.5% MAPIE coverage and 87.5% NGBoost coverage. After the
deliberate late shift, coverage fell to 66.25% and 70.0%, respectively. The gates
routed 25 out-of-domain rows to review, and NGBoost routed another 20 rows for
excessive interval width.

Those values are not performance claims. They are a deliberately visible failure
case: acceptable-looking aggregate uncertainty can conceal severe conditional
miscalibration after a regime change.

## Project map

```text
synthetic rows -> chronological train / conformalization / test
               -> point baseline + MAPIE + NGBoost
               -> coverage, width, Winkler score, regime slices
               -> eligible / review_width / review_shift
```

See [`docs/data-contract.md`](docs/data-contract.md),
[`docs/evaluation-contract.md`](docs/evaluation-contract.md), and
[`docs/model-card.md`](docs/model-card.md) for the enforceable methodology and
limitations.

## What it does not demonstrate

The synthetic results are not evidence about a real sport, market, model, or
wagering process. Nominal conformal coverage is not guaranteed after arbitrary
distribution shift. NGBoost's Normal distribution is deliberately a challenger
assumption rather than accepted truth.
