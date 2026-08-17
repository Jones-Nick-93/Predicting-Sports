# Evaluation contract

## V1 claim

The implementation satisfies documented mathematical properties over the tested
synthetic domain. V1 does not claim that any devig method is empirically superior.

## Generated domains

- Two through twelve selections.
- Strictly positive normalized probability vectors.
- Uniform overround that keeps every implied probability below one.
- Valid decimal and American prices.
- Increasing synthetic line ladders.
- Generic probabilities and caller-supplied Kelly multipliers.

## Required properties

- Output simplex: finite, nonnegative, sums to one.
- Permutation equivariance: selection order does not change selection results.
- Fair-market fixed point for compatible methods.
- Exact recovery of uniformly scaled truth by multiplicative devig.
- Odds conversion round trips within numerical tolerance.
- Kelly fraction is bounded and nondecreasing in win probability.
- Harder increasing thresholds have nonincreasing probabilities.
- Unsupported inputs fail explicitly.

## Future method-comparison claim

A future comparison must pre-register multiple synthetic vig/bias generators,
reserve untouched generator families and seeds, report proper scores with
uncertainty, and separate synthetic truth recovery from agreement with real
closing markets.

