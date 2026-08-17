# Task brief

## Outcome

Create a public-safe property-based test harness that detects incoherent market
math before it can reach forecasting, reporting, or portfolio layers.

## Known facts

- The monorepo already contains deterministic soccer market arithmetic.
- Existing projects do not use property-based testing.
- The repository's public boundary excludes real prices, wagers, parameters,
  proprietary logic, and unreproducible performance claims.

## Assumptions

- This project is an independent public artifact rather than a production
  dependency in its first release.
- Synthetic markets are sufficient to test mathematical invariants.

## In scope

- Probability and odds validation.
- Four generic devig implementations.
- Alternate-line monotonicity checks.
- Generic Kelly arithmetic.
- Hypothesis strategies and invariant tests.
- A deterministic synthetic demonstration.

## Out of scope

- Forecasting, betting recommendations, execution, bankroll management, CLV,
  real odds, model parameters, or claims that one method is universally best.

## Acceptance criteria

- Generated valid markets always produce finite normalized output for supported
  methods.
- Permuting selections only permutes the output.
- Fair markets are fixed points of compatible devig methods.
- Uniform-overround synthetic markets are exactly recovered by multiplicative
  devig within numerical tolerance.
- Odds round trips, Kelly boundaries, and line monotonicity are property tested.
- Invalid method domains fail explicitly.

## Verification

- Run pytest, the synthetic demo, and Python compilation.
- Review the project for private or misleading content.

## Risks and approval gates

- Synthetic results do not establish real-market superiority.
- Adding longitudinal or real-market validation requires explicit time semantics
  and publication review.

## Finish and handoff

- Report passing properties, generated-example counts, known method limitations,
  and the next experiment without publishing private evidence.

