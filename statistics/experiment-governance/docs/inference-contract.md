# Inference Contract

## Pre-registration

The complete hypothesis family is declared before trial results are recorded. The
registry rejects undeclared names, duplicate results, and decisions on incomplete
families. This makes the correction denominator independent of result order.

## Paired sign-flip test

The test operates on paired losses from the same held-out evaluation units. Positive
`baseline - candidate` differences favor the candidate. For at most 20 pairs, every
sign assignment is enumerated. Larger samples use a deterministic Monte Carlo estimate
with a plus-one correction.

The null requires sign exchangeability. It is not automatically justified for
autocorrelated rows, overlapping windows, repeated observations of the same entity, or
adaptively selected evaluation periods. Aggregate into defensible blocks before using
the test and disclose that choice.

## Multiple comparisons

Bonferroni applies `family_alpha / registered_family_size` to every trial. Holm orders
p-values and uses step-down thresholds. A failed pre-registered guardrail cannot be
overridden by statistical significance.

## Effective sample size

Kish effective sample size reports how concentrated non-negative weights are:

`n_eff = sum(weights)^2 / sum(weight^2)`

It does not correct dependence, validate the weighting scheme, or produce a p-value.
