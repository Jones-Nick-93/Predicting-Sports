from __future__ import annotations

import math
from collections.abc import Iterable

from .domain import MarketMathError, require_probability_simplex


def apply_uniform_overround(
    true_probabilities: Iterable[float], overround: float
) -> tuple[float, ...]:
    truth = require_probability_simplex(true_probabilities)
    margin = float(overround)
    if not math.isfinite(margin) or not 0.0 <= margin < 1.0:
        raise MarketMathError("overround must lie in [0, 1)")
    posted = tuple(value * (1.0 + margin) for value in truth)
    if any(value >= 1.0 for value in posted):
        raise MarketMathError("uniform overround would create invalid implied probability")
    return posted

