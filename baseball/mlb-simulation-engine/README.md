# MLB Multi-Market Simulation Engine

A public-safe Python project demonstrating how one MLB-style game simulation
can price multiple market families from a shared event ledger.

The simulator uses deterministic synthetic player profiles. It contains no
vendor feeds, live projections, private wagers, production parameters, account
information, or selection and staking rules.

## Why one shared simulation?

Independent market-specific models can contradict one another: a game-total
model may imply one run environment while hitter and pitcher prop models imply
another. This project simulates each game once and derives every market from
the same collection of game results.

```text
synthetic matchup configuration
             |
             v
plate appearances -> ordered event ledger -> game results
                                               |
                          +--------------------+-------------------+
                          |                    |                   |
                      sides/totals       team markets        player props
```

## Implemented mechanics

- Seeded plate-appearance simulation with explicit strikeout, walk, hit, and
  out outcomes
- Regulation innings, skipped bottom ninth when appropriate, walk-offs, and
  extra innings so moneyline outcomes do not retain tie mass
- Starter workload limits followed by an aggregate bullpen profile
- Stable player IDs kept separate from display names
- Ordered event ledger with inning half, outs, bases, pitcher, batter, and runs
- Push-aware pricing for moneylines, totals, team totals, run lines, hitter
  total bases, hitter home runs, and starting-pitcher strikeouts
- Fair American odds calculated from resolved outcomes after pushes are removed

## Quick start

Python 3.10 or newer is required. The project has no third-party runtime
dependencies.

```powershell
python -m pip install -e .
python -m unittest discover -v
python scripts/run_demo.py
```

The demo runs 1,000 simulations from a fixed seed and prints a small market
board. Integer totals intentionally demonstrate the difference between raw win
probability, push probability, and the conditional probability used for fair
odds.

## Repository layout

```text
src/predicting_sports/mlb/
  simulation.py      validated profiles, game state, and event ledger
  markets.py         push-aware market extraction from shared results
  fixtures.py        deterministic fictional teams
scripts/
  run_demo.py        reproducible multi-market board
docs/
  codex-context.md   project decision and public boundary
  data-contracts.md  market schema and time semantics
  model-card.md      intended use, evaluation plan, and limitations
tests/
  test_simulation_markets.py
```

## Validation evidence

The included tests verify:

- deterministic replay from a fixed seed;
- complete two-way moneyline probability with no simulated ties;
- explicit push accounting for integer lines;
- starter-to-bullpen workload transitions;
- stable IDs when display names collide;
- event-ledger sequencing and score accounting;
- consistent market extraction from one result collection; and
- fair-odds boundary behavior and input validation.

These are software and accounting checks, not evidence of predictive accuracy
or profitability.

## Public-release boundary

Included: source code, synthetic fixtures, tests, documentation, and CI.

Excluded: raw or licensed baseball data, paid-feed payloads, live projections,
private features, calibrated production parameters, wager history, account
metadata, infrastructure details, execution logic, and bankroll rules.

## Limitations

- Synthetic profiles are illustrative and are not estimates for real players.
- Batted-ball advancement is simplified and does not model errors, steals,
  substitutions, handedness, park, weather, umpire, or defense effects.
- Starter workload is a fixed batters-faced limit rather than a sampled hook.
- The bullpen is represented by one aggregate profile per team.
- Extra innings do not implement every season-specific automatic-runner rule.
- No predictive calibration, walk-forward evaluation, market availability,
  limits, latency, slippage, or closing-line comparison is claimed.

See the [model card](docs/model-card.md) and
[data contracts](docs/data-contracts.md) for the evaluation requirements that
would precede any real-world use.

## License

Released under the [MIT License](LICENSE).
