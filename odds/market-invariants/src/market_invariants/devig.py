from __future__ import annotations

import math
from collections.abc import Callable, Iterable

from .domain import (
    DEFAULT_TOLERANCE,
    MarketMathError,
    require_probability_simplex,
    require_probability_vector,
)


def multiplicative_devig(implied_probabilities: Iterable[float]) -> tuple[float, ...]:
    implied = _require_overround_market(implied_probabilities)
    total = sum(implied)
    return _validated_output(value / total for value in implied)


def additive_devig(implied_probabilities: Iterable[float]) -> tuple[float, ...]:
    implied = _require_overround_market(implied_probabilities)
    adjustment = (sum(implied) - 1.0) / len(implied)
    adjusted = tuple(value - adjustment for value in implied)
    if any(value < 0.0 for value in adjusted):
        raise MarketMathError("additive devig would create a negative probability")
    return _validated_output(adjusted)


def power_devig(implied_probabilities: Iterable[float]) -> tuple[float, ...]:
    implied = _require_overround_market(implied_probabilities)
    if math.isclose(sum(implied), 1.0, abs_tol=DEFAULT_TOLERANCE, rel_tol=0.0):
        return require_probability_simplex(implied)

    exponent = _bisect_root(
        lambda value: sum(probability**value for probability in implied) - 1.0,
        lower=1.0,
        upper=128.0,
    )
    return _validated_output(probability**exponent for probability in implied)


def odds_ratio_devig(implied_probabilities: Iterable[float]) -> tuple[float, ...]:
    implied = _require_overround_market(implied_probabilities)
    if math.isclose(sum(implied), 1.0, abs_tol=DEFAULT_TOLERANCE, rel_tol=0.0):
        return require_probability_simplex(implied)

    divisor = _bisect_root(
        lambda value: sum(
            probability / (value + (1.0 - value) * probability)
            for probability in implied
        )
        - 1.0,
        lower=1.0,
        upper=1_000_000.0,
    )
    return _validated_output(
        probability / (divisor + (1.0 - divisor) * probability)
        for probability in implied
    )


def _require_overround_market(values: Iterable[float]) -> tuple[float, ...]:
    probabilities = require_probability_vector(values)
    if any(value <= 0.0 or value >= 1.0 for value in probabilities):
        raise MarketMathError("implied probabilities must lie strictly inside (0, 1)")
    if sum(probabilities) < 1.0 - DEFAULT_TOLERANCE:
        raise MarketMathError("devig methods require total implied mass of at least one")
    return probabilities


def _validated_output(values: Iterable[float]) -> tuple[float, ...]:
    return require_probability_simplex(tuple(values), tolerance=1e-9)


def _bisect_root(
    function: Callable[[float], float],
    *,
    lower: float,
    upper: float,
    iterations: int = 160,
) -> float:
    lower_value = function(lower)
    upper_value = function(upper)
    if lower_value < 0.0 or upper_value > 0.0:
        raise MarketMathError("root is not bracketed for this market")
    for _ in range(iterations):
        midpoint = (lower + upper) / 2.0
        midpoint_value = function(midpoint)
        if abs(midpoint_value) <= 1e-14:
            return midpoint
        if midpoint_value > 0.0:
            lower = midpoint
        else:
            upper = midpoint
    return (lower + upper) / 2.0

