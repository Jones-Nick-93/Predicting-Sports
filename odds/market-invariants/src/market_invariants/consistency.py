from __future__ import annotations

import math
from collections.abc import Iterable

from .domain import MarketMathError, require_probability


def require_nonincreasing_ladder(
    lines: Iterable[float], probabilities: Iterable[float], *, tolerance: float = 1e-12
) -> tuple[tuple[float, float], ...]:
    """Validate that harder increasing thresholds never receive higher probability."""
    line_values = tuple(float(value) for value in lines)
    probability_values = tuple(require_probability(value) for value in probabilities)
    if len(line_values) != len(probability_values) or len(line_values) < 2:
        raise MarketMathError("lines and probabilities need equal length of at least two")
    if any(not math.isfinite(value) for value in line_values):
        raise MarketMathError("lines must be finite")
    if tolerance < 0.0 or not math.isfinite(tolerance):
        raise MarketMathError("tolerance must be finite and nonnegative")
    if any(right <= left for left, right in zip(line_values, line_values[1:])):
        raise MarketMathError("lines must be strictly increasing")
    if any(
        right > left + tolerance
        for left, right in zip(probability_values, probability_values[1:])
    ):
        raise MarketMathError("probabilities must be nonincreasing as lines increase")
    return tuple(zip(line_values, probability_values))

