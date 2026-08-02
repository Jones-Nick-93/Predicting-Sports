# Soccer Market Math

A deliberately limited portfolio sample containing generic soccer market arithmetic.
It demonstrates validated odds conversion, fractional-Kelly arithmetic, and push-aware
Asian-handicap settlement using fabricated inputs.

This repository does **not** describe or implement a forecasting model. It contains no
data pipeline, features, model architecture, fitted parameters, validation process,
selection criteria, bankroll values, production staking policy, live prices,
projections, or performance results.

## Included

- `src/asian_handicap.py` - generic whole-, half-, and quarter-line settlement logic
- `src/odds_utils.py` - probability, decimal-odds, American-odds, and fractional-Kelly helpers
- `src/test_asian_handicap.py` - hand-built synthetic settlement tests
- `src/test_odds_utils.py` - known-value, boundary, and round-trip conversion tests
- `examples/run_market_math.py` - a fabricated arithmetic-only example
- `docs/publication-scope.md` - the explicit public/private boundary
- `docs/legacy-migration.md` - how the interactive legacy helpers were rehabilitated

## Run

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python examples/run_market_math.py
```

Repository-specific Codex instructions live in `AGENTS.md`. A public-readiness,
model-validity, and hiring-manager audit is in `docs/codex-review.md`.

Odds conversions retain full precision internally and round only for display. The
Kelly helper exposes the textbook equation with a caller-supplied multiplier; it does
not encode a real bankroll, cap, minimum edge, market filter, or operating policy.

All example values are invented for software demonstration. Nothing in this repository
should be interpreted as a recommendation, forecast, or representation of a private
production system.
