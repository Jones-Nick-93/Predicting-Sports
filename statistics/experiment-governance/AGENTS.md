# Codex Working Agreement

## Purpose

Maintain a public-safe statistical experiment-governance toolkit. Prefer explicit
contracts, complete trial retention, and defensible uncertainty over impressive claims.

## Public/private boundary

- Use fabricated data in repository examples and tests.
- Never add forecasting features, model architecture, private performance, real
  positions, position-sizing ladders, bankroll caps, execution rules, credentials, or
  paid/licensed data.
- Never manufacture or infer a p-value from whether a metric crossed a threshold.
- Base family-wise corrections on the full pre-registered family, not the number of
  favorable or completed trials.
- Document assumptions and reject malformed, incomplete, or selectively logged input.

## Commands

```bash
python -m pip install -r requirements-dev.txt
python -m pytest -q
python examples/run_governance_demo.py
python -m compileall -q src examples tests
```
