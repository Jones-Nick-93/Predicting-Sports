from __future__ import annotations

import math

from .domain import MarketMathError, require_probability


def kelly_fraction(
    win_probability: float,
    decimal_odds: float,
    *,
    multiplier: float = 1.0,
) -> float:
    """Return nonnegative generic Kelly fraction with a caller-supplied multiplier."""
    probability = require_probability(win_probability)
    odds = float(decimal_odds)
    scale = float(multiplier)
    if not math.isfinite(odds) or odds <= 1.0:
        raise MarketMathError("decimal odds must be finite and greater than one")
    if not math.isfinite(scale) or not 0.0 <= scale <= 1.0:
        raise MarketMathError("multiplier must lie in [0, 1]")
    net_odds = odds - 1.0
    full_kelly = (net_odds * probability - (1.0 - probability)) / net_odds
    return max(0.0, min(1.0, full_kelly * scale))

