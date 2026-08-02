from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from predicting_sports.mlb.fixtures import synthetic_game
from predicting_sports.mlb.markets import price_markets
from predicting_sports.mlb.simulation import simulate_many


def main() -> None:
    results = simulate_many(synthetic_game(), n=1000, seed=42)
    prices = price_markets(results, total_line=8.0)

    print("Demo board from one shared simulation")
    print("----------------------------------------------------------")
    for price in prices[:20]:
        odds = "n/a" if price.fair_american is None else f"{price.fair_american:+d}"
        print(
            f"{price.market:22} {price.selection:24} "
            f"win={price.probability:6.1%} push={price.push_probability:5.1%} "
            f"fair={odds}"
        )


if __name__ == "__main__":
    main()
