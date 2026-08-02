"""Generic American-odds conversion helpers.

These functions contain only standard market arithmetic. They do not contain
model inputs, projections, selection rules, or production parameters.
"""


def prob_to_american(p: float) -> int:
    """Convert a probability to American odds."""
    p = max(0.001, min(0.999, p))
    if p >= 0.5:
        return int(round(-(p / (1 - p)) * 100))
    return int(round(((1 - p) / p) * 100))


def american_to_prob(odds: int) -> float:
    """Convert American odds to implied probability."""
    if odds < 0:
        return abs(odds) / (abs(odds) + 100)
    return 100 / (odds + 100)


def format_american(odds: int) -> str:
    """Format American odds with an explicit plus sign when positive."""
    return f"+{odds}" if odds > 0 else str(odds)
