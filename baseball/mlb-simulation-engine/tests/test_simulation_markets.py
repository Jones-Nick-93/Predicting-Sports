from __future__ import annotations

import sys
import unittest
from dataclasses import replace
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from predicting_sports.mlb.fixtures import synthetic_game
from predicting_sports.mlb.markets import fair_american, price_markets
from predicting_sports.mlb.simulation import simulate_many


class SimulationMarketTests(unittest.TestCase):
    def test_simulation_is_deterministic_with_seed(self) -> None:
        config = synthetic_game()
        first = simulate_many(config, n=20, seed=123)
        second = simulate_many(config, n=20, seed=123)
        self.assertEqual(
            [(result.away_runs, result.home_runs) for result in first],
            [(result.away_runs, result.home_runs) for result in second],
        )

    def test_moneyline_has_no_unpriced_tie_mass(self) -> None:
        results = simulate_many(synthetic_game(), n=500, seed=9)
        self.assertTrue(all(r.away_runs != r.home_runs for r in results))
        moneylines = [
            price for price in price_markets(results) if price.market == "moneyline"
        ]
        self.assertEqual(len(moneylines), 2)
        self.assertAlmostEqual(sum(price.probability for price in moneylines), 1.0)
        self.assertTrue(all(price.push_probability == 0 for price in moneylines))

    def test_integer_total_reports_push_probability(self) -> None:
        results = simulate_many(synthetic_game(), n=500, seed=12)
        totals = [
            price
            for price in price_markets(results, total_line=8.0)
            if price.market == "total"
        ]
        over, under = totals
        self.assertGreater(over.push_probability, 0)
        self.assertEqual(over.push_probability, under.push_probability)
        self.assertAlmostEqual(
            over.probability + under.probability + over.push_probability,
            1.0,
        )

    def test_starter_workload_cap_moves_later_batters_to_bullpen(self) -> None:
        config = synthetic_game()
        result = simulate_many(config, n=1, seed=5)[0]
        for team in (config.away, config.home):
            starter = result.pitcher_lines[team.starter.player_id]
            bullpen = result.pitcher_lines[team.bullpen.player_id]
            self.assertLessEqual(
                starter.batters_faced, team.starter.expected_batters_faced
            )
            self.assertGreater(bullpen.batters_faced, 0)

    def test_stable_ids_preserve_duplicate_display_names(self) -> None:
        config = synthetic_game()
        away_lineup = (
            replace(config.away.lineup[0], name="Shared Display Name"),
            *config.away.lineup[1:],
        )
        home_lineup = (
            replace(config.home.lineup[0], name="Shared Display Name"),
            *config.home.lineup[1:],
        )
        duplicate_names = replace(
            config,
            away=replace(config.away, lineup=away_lineup),
            home=replace(config.home, lineup=home_lineup),
        )
        result = simulate_many(duplicate_names, n=1, seed=7)[0]
        self.assertIn("away-b1", result.batter_lines)
        self.assertIn("home-b1", result.batter_lines)
        self.assertEqual(result.player_names["away-b1"], "Shared Display Name")
        self.assertEqual(result.player_names["home-b1"], "Shared Display Name")

    def test_event_ledger_and_accounting_are_populated(self) -> None:
        result = simulate_many(synthetic_game(), n=1, seed=5)[0]
        self.assertGreater(len(result.event_ledger), 0)
        self.assertEqual(result.total_runs, result.away_runs + result.home_runs)
        self.assertTrue(
            all(line.plate_appearances > 0 for line in result.batter_lines.values())
        )
        self.assertEqual(
            [event["sequence"] for event in result.event_ledger],
            list(range(1, len(result.event_ledger) + 1)),
        )
        self.assertTrue(
            all(
                "batter_id" in event and "pitcher_id" in event
                for event in result.event_ledger
            )
        )

    def test_market_layer_reads_shared_results(self) -> None:
        results = simulate_many(synthetic_game(), n=50, seed=9)
        markets = {price.market for price in price_markets(results)}
        self.assertEqual(
            markets,
            {
                "moneyline",
                "total",
                "run_line",
                "team_total",
                "hitter_total_bases",
                "hitter_home_run",
                "pitcher_strikeouts",
            },
        )

    def test_fair_american_prices_and_boundaries(self) -> None:
        self.assertEqual(fair_american(0.5), -100)
        self.assertEqual(fair_american(0.25), 300)
        self.assertEqual(fair_american(0.75), -300)
        self.assertIsNone(fair_american(0.0))
        self.assertIsNone(fair_american(1.0))

    def test_simulation_count_must_be_positive(self) -> None:
        with self.assertRaises(ValueError):
            simulate_many(synthetic_game(), n=0)


if __name__ == "__main__":
    unittest.main()
