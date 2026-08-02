# Soccer Market Math

A deliberately limited portfolio sample containing generic soccer market arithmetic.
It demonstrates American-odds conversion and push-aware Asian-handicap settlement on
fabricated probability grids.

This repository does **not** describe or implement a forecasting model. It contains no
data pipeline, features, model architecture, fitted parameters, validation process,
selection criteria, staking rules, live prices, projections, or performance results.

## Included

- `src/asian_handicap.py` — generic whole-, half-, and quarter-line settlement logic
- `src/odds_utils.py` — standard American-odds conversion helpers
- `src/test_asian_handicap.py` — tests using hand-built synthetic probability grids
- `examples/run_market_math.py` — a fabricated arithmetic-only example
- `docs/publication-scope.md` — the explicit public/private boundary

## Run

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python examples/run_market_math.py
```

Repository-specific Codex instructions live in `AGENTS.md`. A public-readiness,
model-validity, and hiring-manager audit is in `docs/codex-review.md`.

All example values are invented for software demonstration. Nothing in this repository
should be interpreted as a recommendation, forecast, or representation of a private
production system.
