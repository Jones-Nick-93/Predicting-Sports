# Betting project context

## Decision and market

This project validates generic arithmetic for synthetic two-way and multiway
markets. It makes no forecast or wagering decision.

## Time semantics

V1 contains only timeless generated snapshots. Event, publication, ingestion,
feature-availability, prediction, entry, close, and settlement timestamps become
mandatory before any longitudinal extension.

## Data sources and rights

All test cases and examples are generated in memory from fabricated probability
vectors. No external or licensed data are used.

## Normalization contract

- Probabilities must be finite and lie in `[0, 1]`.
- A probability simplex must sum to one within explicit tolerance.
- Decimal odds must exceed one.
- American odds must be at least `+100` or at most `-100`.
- Devig output must be finite, nonnegative, and normalized.

## Leakage controls

No learned model or time-indexed data exist in V1. A future evaluation must
separate generation, method selection, validation, and final holdout seeds and
must define every as-of timestamp.

## Backtest and execution assumptions

There is no backtest, executable-price assumption, fill model, limit, or wager.

## Evaluation and calibration

V1 evaluates mathematical properties. The next phase may evaluate recovery
error against known synthetic truth under multiple vig and bias generators.

## Public/private boundary

Public: methods, contracts, generated fixtures, tests, and negative results.
Excluded: real prices, predictions, wagers, bankrolls, private parameters,
licensed feeds, selection rules, and private infrastructure.

