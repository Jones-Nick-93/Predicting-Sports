# Model card

## Intended use

Educational and portfolio demonstration of a coherent sports-simulation
architecture. The project shows how one event ledger can support multiple game
and player market summaries without contradictory market-specific simulations.

## Not intended for

- automated wagering or live trading;
- player evaluation or injury decisions;
- guaranteed-profit or predictive-performance claims; or
- real-money use without independent data, calibration, execution, and risk
  controls.

## Data

The public demo uses deterministic fictional batter, starter, and aggregate
bullpen profiles. It includes no private wagers, paid feeds, account data, raw
production projections, or calibrated operational parameters.

## Method

The engine samples plate appearances, advances a simplified base state, records
an ordered event ledger, resolves regulation ties through extra innings, and
summarizes repeated results into push-aware market probabilities. Starting
pitchers face a configured maximum number of batters before an aggregate
bullpen profile takes over.

## Current evaluation

Automated tests cover deterministic replay, accounting invariants, tie-free
moneylines, push decomposition, workload transitions, stable identifiers,
market-family coverage, and odds conversion boundaries. They do not measure
real-world predictive accuracy.

## Required evaluation before real use

- Chronological walk-forward splits grouped by game or slate
- Calibration curves and proper scoring rules by market family and line band
- Bootstrap uncertainty at the game or slate level
- Feature-availability and revision-time audits
- Comparison with closing prices using realistic availability, limits, latency,
  and slippage assumptions
- Drift monitoring and explicit retirement criteria

## Limitations

- Synthetic fixtures are not predictive of real teams or players.
- Base advancement and plate-appearance outcomes are simplified.
- The simulator omits substitutions, defense, errors, steals, handedness, park,
  weather, umpire, injury, and lineup-confirmation effects.
- Starter workload is fixed and bullpen performance is aggregated.
- Season-specific extra-inning rules are not fully represented.
- Monte Carlo probabilities include sampling uncertainty that is not yet
  reported by the demo.
