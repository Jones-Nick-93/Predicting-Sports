# Codex Review: Public Portfolio Readiness

## Executive read

In roughly 60 seconds, this repository proves that the author can implement and
test push-aware Asian-handicap arithmetic, validated odds conversions, and generic
fractional-Kelly math while maintaining a deliberate boundary between public
portfolio code and private production IP.

The publication boundary is unusually clear. The README and
`docs/publication-scope.md` explicitly exclude live data, model design, parameters,
selection logic, production staking settings, prices, projections, results, and credentials. A
basic text scan found no obvious embedded secrets or connection strings.

## What is already credible

- Fabricated grids and examples instead of disguised production data.
- Tests for pick'em, whole, half, and quarter lines.
- Known-value and round-trip tests for probability, decimal, and American odds.
- An explicit Kelly multiplier rather than a hard-coded production setting.
- A clear `.gitignore` covering secrets, environments, data, outputs, and model
  artifacts.
- A small enough code surface for a reviewer to understand quickly.
- Explicit language that this is market mechanics, not a forecasting product.

## Model-validity cautions

These are review findings, not claims that the private model is wrong.

1. `cover_prob` is not always a literal cover probability. On whole lines it
   returns `win probability + 0.5 * push probability`. That can be a useful
   push-adjusted settlement score, but it should not be converted directly to a
   fair price without stating the pricing convention. A push-refund market is
   normally priced using win and loss mass separately.
2. Probability-grid inputs are not validated for dimensionality, finite values,
   non-negativity, or total mass. Silent bad inputs could produce plausible output.
3. `max_goals` can silently truncate probability mass. Any truncation should be
   explicit and checked.
4. The odds helpers now fail fast on invalid and non-finite values, but the suite
   does not yet include property-based testing across a generated price range.
5. The suite still lacks tests for rectangular grids, truncated grids, or
   floating-point line normalization.

## Hiring-manager gaps, in priority order

1. Add explicit input contracts and negative tests for invalid probability grids.
2. Separate `win`, `push`, `loss`, `half-win`, and `half-loss` settlement outcomes;
   calculate a quoted fair price only in a separately documented pricing function.
3. Add property-based odds tests across generated valid prices.
4. Move toward a conventional importable package plus a top-level `tests/` folder.
5. Add one small benchmark or property-based test showing invariants across many
   synthetic grids.

## Public-safe next step

The safest improvement is to strengthen contracts and tests without adding any
forecasting logic. Keep the repository narrow. Use the separate portfolio projects
for CLV tracking, leakage-safe backtesting, and production pipeline work.
