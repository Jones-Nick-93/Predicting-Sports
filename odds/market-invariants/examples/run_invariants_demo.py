from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from market_invariants import (  # noqa: E402
    additive_devig,
    apply_uniform_overround,
    multiplicative_devig,
    odds_ratio_devig,
    power_devig,
    require_nonincreasing_ladder,
)


def mean_absolute_error(actual: tuple[float, ...], expected: tuple[float, ...]) -> float:
    return sum(abs(left - right) for left, right in zip(actual, expected)) / len(actual)


def main() -> None:
    truth = (0.52, 0.30, 0.18)
    implied = apply_uniform_overround(truth, overround=0.07)
    methods = {
        "multiplicative": multiplicative_devig,
        "additive": additive_devig,
        "power": power_devig,
        "odds_ratio": odds_ratio_devig,
    }

    print("Synthetic three-way market")
    print(f"truth={truth}")
    print(f"posted_implied={tuple(round(value, 6) for value in implied)}")
    for name, method in methods.items():
        recovered = method(implied)
        print(
            f"{name:>14}  probabilities="
            f"{tuple(round(value, 6) for value in recovered)}  "
            f"mae={mean_absolute_error(recovered, truth):.8f}"
        )

    ladder = require_nonincreasing_ladder(
        lines=(45.5, 46.5, 47.5, 48.5),
        probabilities=(0.57, 0.53, 0.48, 0.43),
    )
    print(f"validated_ladder={ladder}")
    print("Synthetic demonstration only; no real market or forecasting claim.")


if __name__ == "__main__":
    main()
