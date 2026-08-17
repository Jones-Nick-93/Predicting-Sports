# Market Invariants Lab

A public-safe reliability harness for probability, odds, devig, alternate-line,
and generic Kelly arithmetic. The project uses property-based tests to generate
large families of synthetic markets and search for violations that hand-written
examples often miss.

## What it demonstrates

- Strict probability and price validation.
- American/decimal/probability round trips.
- Multiplicative, additive, power, and odds-ratio devig methods.
- Probability-simplex, permutation, idempotence, and recovery properties.
- Monotonic alternate-line validation.
- Generic Kelly boundary and monotonicity properties.
- Explicit rejection when a method cannot return a coherent probability set.

## Run

```text
python -m pip install -r requirements-dev.txt
python -m pytest
python examples/run_invariants_demo.py
```

## Interpretation

Passing these invariants does not prove that a devig method recovers real-world
probabilities. It proves that the implementation obeys its mathematical contract
over the generated domain. Method quality requires a separate synthetic
ground-truth experiment and time-aware validation on public or privately held
data.

All inputs in this project are fabricated. Nothing here is a forecast, wager,
selection rule, bankroll policy, or claim of profitability.

