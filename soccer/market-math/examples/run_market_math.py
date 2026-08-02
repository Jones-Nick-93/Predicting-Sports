"""Demonstrate public, model-independent market arithmetic.

The score grid below is fabricated. It is not produced by a forecasting model
and does not represent a real team, match, price, or production configuration.

Run: python examples/run_market_math.py
"""

import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from asian_handicap import cover_prob, spread_labels
from odds_utils import american_to_decimal, fractional_kelly, probability_to_american


def main() -> None:
    synthetic_probability = 0.55
    synthetic_american_odds = -110
    decimal_odds = american_to_decimal(synthetic_american_odds)
    fair_price = probability_to_american(synthetic_probability)
    demonstration_fraction = fractional_kelly(
        synthetic_probability,
        decimal_odds,
        multiplier=0.25,
    )
    print(
        "Synthetic conversion: "
        f"p={synthetic_probability:.2f}, fair={fair_price:+.1f}, "
        f"market_decimal={decimal_odds:.4f}, "
        f"quarter-Kelly example={demonstration_fraction:.4f}"
    )

    grid = np.array(
        [
            [0.18, 0.12, 0.05],
            [0.20, 0.16, 0.07],
            [0.10, 0.08, 0.04],
        ],
        dtype=float,
    )
    grid /= grid.sum()

    for line in (-0.5, 0.0, 0.5):
        home_label, _ = spread_labels(line)
        settlement_score = cover_prob(grid, line)
        print(f"Synthetic home {home_label:>4}: settlement score={settlement_score:.3f}")


if __name__ == "__main__":
    main()
