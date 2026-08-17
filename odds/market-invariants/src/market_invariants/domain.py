from __future__ import annotations

import math
from collections.abc import Iterable


DEFAULT_TOLERANCE = 1e-10


class MarketMathError(ValueError):
    """Raised when market arithmetic cannot satisfy its documented contract."""


def require_probability(value: float, *, inclusive: bool = True) -> float:
    probability = float(value)
    if not math.isfinite(probability):
        raise MarketMathError("probability must be finite")
    valid = 0.0 <= probability <= 1.0 if inclusive else 0.0 < probability < 1.0
    if not valid:
        interval = "[0, 1]" if inclusive else "(0, 1)"
        raise MarketMathError(f"probability must lie in {interval}")
    return probability


def require_probability_vector(values: Iterable[float]) -> tuple[float, ...]:
    probabilities = tuple(require_probability(value) for value in values)
    if len(probabilities) < 2:
        raise MarketMathError("a market requires at least two selections")
    if sum(probabilities) <= 0.0:
        raise MarketMathError("probability vector must have positive mass")
    return probabilities


def require_probability_simplex(
    values: Iterable[float], *, tolerance: float = DEFAULT_TOLERANCE
) -> tuple[float, ...]:
    probabilities = require_probability_vector(values)
    if tolerance < 0.0 or not math.isfinite(tolerance):
        raise MarketMathError("tolerance must be finite and nonnegative")
    if not math.isclose(sum(probabilities), 1.0, abs_tol=tolerance, rel_tol=0.0):
        raise MarketMathError("probabilities must sum to one")
    return probabilities


def probability_to_decimal(probability: float) -> float:
    return 1.0 / require_probability(probability, inclusive=False)


def decimal_to_probability(decimal_odds: float) -> float:
    odds = float(decimal_odds)
    if not math.isfinite(odds) or odds <= 1.0:
        raise MarketMathError("decimal odds must be finite and greater than one")
    return 1.0 / odds


def decimal_to_american(decimal_odds: float) -> float:
    odds = float(decimal_odds)
    probability = decimal_to_probability(odds)
    if probability <= 0.5:
        return 100.0 * (odds - 1.0)
    return -100.0 / (odds - 1.0)


def american_to_decimal(american_odds: float) -> float:
    odds = float(american_odds)
    if not math.isfinite(odds) or (-100.0 < odds < 100.0):
        raise MarketMathError("American odds must be at least +100 or at most -100")
    if odds > 0.0:
        return 1.0 + odds / 100.0
    return 1.0 + 100.0 / abs(odds)

