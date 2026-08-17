# Codex Working Agreement

## Purpose

This is a public-safe market-math reliability lab. It demonstrates invariants,
property-based testing, and synthetic devig evaluation without reproducing a
private forecasting, selection, or staking system.

## Boundaries

- Use only generated or explicitly fabricated markets.
- Never add real prices, wagers, accounts, bankrolls, vendor data, credentials,
  production parameters, selection rules, or private-system architecture.
- Keep functions deterministic and side-effect free.
- Treat probabilities and prices as untrusted inputs.
- A devig method may reject a market whose assumptions it cannot satisfy; it
  must never silently emit negative, non-finite, or unnormalized probabilities.
- Generic Kelly arithmetic must not encode bankroll values, caps, edge gates, or
  operating policy.

## Time semantics

The first release uses generated single-snapshot markets, so publication,
ingestion, feature-availability, prediction, entry, close, and settlement times
are intentionally absent. Add those fields before introducing any longitudinal
fixture, backtest, or market-movement claim.

## Commands

```text
python -m pip install -r requirements-dev.txt
python -m pytest
python examples/run_invariants_demo.py
python -m compileall -q src examples tests
```

## Definition of done

- Deterministic tests and Hypothesis properties pass.
- The synthetic demonstration is reproducible.
- Failure behavior is documented.
- No profit, predictive-accuracy, or production-readiness claim is made.

