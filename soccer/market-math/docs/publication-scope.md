# Publication Scope

This repository is intentionally limited to generic market-mechanics code and
fabricated examples. It is not a deployable forecasting or wagering system.

The public repository excludes:

- data sources, schemas, ingestion logic, and feature definitions;
- estimator selection, model architecture, and training code;
- fitted ratings, weights, coefficients, priors, caps, and thresholds;
- validation windows, optimization objectives, and evaluation results;
- production staking multipliers, bankroll values, caps, limits, and execution rules;
- market-selection rules, real fixtures, prices, projections, and recommendations;
- performance records, credentials, endpoints, and serialized state.

Standard probability/price identities and the textbook fractional-Kelly equation are
included as generic arithmetic. The Kelly multiplier is an explicit caller input and
does not represent a private or recommended operating setting.

Values in examples and tests are fabricated solely to exercise generic arithmetic.
They must not be treated as representative of any private system.
