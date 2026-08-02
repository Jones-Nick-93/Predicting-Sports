"""Pure, model-independent betting math helpers.

This module implements standard market arithmetic only. It contains no model
inputs, selection rules, bankroll values, production thresholds, or limits.
"""

from math import isfinite
from numbers import Real


def _finite_number(value: Real, *, name: str) -> float:
    """Return ``value`` as a finite float, rejecting ambiguous booleans."""
    if isinstance(value, bool) or not isinstance(value, Real):
        raise TypeError(f"{name} must be a real number")
    result = float(value)
    if not isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


def probability_to_decimal(probability: Real) -> float:
    """Convert a probability in ``(0, 1]`` to gross decimal odds.

    The result is not rounded. Callers should round only for display so later
    calculations do not accumulate presentation error.
    """
    probability = _finite_number(probability, name="probability")
    if not 0.0 < probability <= 1.0:
        raise ValueError("probability must be greater than 0 and at most 1")
    return 1.0 / probability


def decimal_to_probability(decimal_odds: Real) -> float:
    """Convert gross decimal odds of at least ``1.0`` to probability."""
    decimal_odds = _finite_number(decimal_odds, name="decimal_odds")
    if decimal_odds < 1.0:
        raise ValueError("decimal_odds must be at least 1")
    return 1.0 / decimal_odds


def american_to_decimal(american_odds: Real) -> float:
    """Convert nonzero American odds to gross decimal odds.

    For example, ``-110`` converts to approximately ``1.9091`` and ``+150``
    converts to ``2.5``. The leading stake is included in the decimal return.
    """
    american_odds = _finite_number(american_odds, name="american_odds")
    if american_odds == 0.0:
        raise ValueError("american_odds cannot be zero")
    if american_odds < 0.0:
        return 1.0 + (100.0 / abs(american_odds))
    return 1.0 + (american_odds / 100.0)


def decimal_to_american(decimal_odds: Real) -> float:
    """Convert gross decimal odds greater than ``1.0`` to American odds."""
    decimal_odds = _finite_number(decimal_odds, name="decimal_odds")
    if decimal_odds <= 1.0:
        raise ValueError("decimal_odds must be greater than 1")
    if decimal_odds >= 2.0:
        return (decimal_odds - 1.0) * 100.0
    return -100.0 / (decimal_odds - 1.0)


def probability_to_american(probability: Real) -> float:
    """Convert a probability in ``(0, 1)`` to unrounded American odds."""
    probability = _finite_number(probability, name="probability")
    if not 0.0 < probability < 1.0:
        raise ValueError("probability must be strictly between 0 and 1")
    return decimal_to_american(probability_to_decimal(probability))


def american_to_probability(american_odds: Real) -> float:
    """Convert nonzero American odds to implied probability."""
    return decimal_to_probability(american_to_decimal(american_odds))


def fractional_kelly(
    win_probability: Real,
    decimal_odds: Real,
    *,
    multiplier: Real,
) -> float:
    """Return a nonnegative fractional-Kelly bankroll proportion.

    ``decimal_odds`` are gross returns, while the Kelly equation uses net
    profit per unit staked internally. ``multiplier`` must be supplied by the
    caller and lie in ``[0, 1]``; for example, ``0.25`` demonstrates quarter
    Kelly. A non-positive raw Kelly value returns zero because this helper
    models a bet fraction, not a short position.
    """
    win_probability = _finite_number(win_probability, name="win_probability")
    decimal_odds = _finite_number(decimal_odds, name="decimal_odds")
    multiplier = _finite_number(multiplier, name="multiplier")

    if not 0.0 <= win_probability <= 1.0:
        raise ValueError("win_probability must be between 0 and 1")
    if decimal_odds <= 1.0:
        raise ValueError("decimal_odds must be greater than 1")
    if not 0.0 <= multiplier <= 1.0:
        raise ValueError("multiplier must be between 0 and 1")

    net_odds = decimal_odds - 1.0
    lose_probability = 1.0 - win_probability
    full_kelly = (net_odds * win_probability - lose_probability) / net_odds
    return max(0.0, multiplier * full_kelly)


def prob_to_american(probability: Real) -> int:
    """Return a display-ready whole-number American price."""
    return int(round(probability_to_american(probability)))


def american_to_prob(american_odds: Real) -> float:
    """Compatibility alias for :func:`american_to_probability`."""
    return american_to_probability(american_odds)


def format_american(american_odds: Real) -> str:
    """Format whole-number American odds with a sign for positive prices."""
    american_odds = _finite_number(american_odds, name="american_odds")
    if not american_odds.is_integer():
        raise ValueError("american_odds must be a whole number for formatting")
    value = int(american_odds)
    return f"+{value}" if value > 0 else str(value)
