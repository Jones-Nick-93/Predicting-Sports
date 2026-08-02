# Legacy Betting Tools Migration

This project replaces a small interactive utility script with import-safe, tested
functions. The migration intentionally keeps only generic market arithmetic.

| Legacy behavior | Public replacement | Change |
| --- | --- | --- |
| Probability to rounded decimal price | `probability_to_decimal` | Preserves full precision and rejects zero/non-finite values. |
| American price to a value labeled decimal odds | `american_to_decimal` | Returns gross decimal odds, including returned stake. |
| Interactive probability-to-price loop | `probability_to_american` | Pure, composable function with explicit validation. |
| Interactive hard-coded quarter-Kelly output | `fractional_kelly` | Pure function with an explicit caller-supplied multiplier. |

The old script mixed input/output with arithmetic and executed prompts during import.
The migrated module has no import-time side effects. Its tests use only fabricated
values and cover known prices, round trips, invalid boundaries, and no-edge Kelly
behavior.

The public version does not include bankroll amounts, production multipliers, caps,
minimum-edge rules, market selection, data sources, projections, or wager history.
