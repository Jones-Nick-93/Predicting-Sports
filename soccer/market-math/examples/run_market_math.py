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


def main() -> None:
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
