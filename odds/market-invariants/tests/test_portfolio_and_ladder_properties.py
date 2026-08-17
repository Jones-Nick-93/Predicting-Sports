from __future__ import annotations

import pytest
from hypothesis import given, strategies as st

from market_invariants.consistency import require_nonincreasing_ladder
from market_invariants.domain import MarketMathError
from market_invariants.portfolio import kelly_fraction


@given(
    st.floats(min_value=1.01, max_value=20.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
)
def test_kelly_is_bounded_and_nondecreasing_in_probability(
    decimal_odds: float, first: float, second: float
) -> None:
    lower, upper = sorted((first, second))
    lower_fraction = kelly_fraction(lower, decimal_odds)
    upper_fraction = kelly_fraction(upper, decimal_odds)
    assert 0.0 <= lower_fraction <= upper_fraction <= 1.0


@given(st.floats(min_value=1.01, max_value=20.0, allow_nan=False, allow_infinity=False))
def test_kelly_is_zero_at_breakeven(decimal_odds: float) -> None:
    assert kelly_fraction(1.0 / decimal_odds, decimal_odds) == pytest.approx(0.0, abs=1e-12)


@given(
    st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
    st.floats(min_value=1.01, max_value=20.0, allow_nan=False, allow_infinity=False),
)
def test_zero_multiplier_always_returns_zero(
    probability: float, decimal_odds: float
) -> None:
    assert kelly_fraction(probability, decimal_odds, multiplier=0.0) == 0.0


@given(
    st.lists(
        st.integers(min_value=-100, max_value=100),
        min_size=2,
        max_size=20,
        unique=True,
    ),
    st.lists(
        st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        min_size=2,
        max_size=20,
    ),
)
def test_sorted_ladder_accepts_nonincreasing_probabilities(
    raw_lines: list[int], raw_probabilities: list[float]
) -> None:
    size = min(len(raw_lines), len(raw_probabilities))
    lines = sorted(raw_lines[:size])
    probabilities = sorted(raw_probabilities[:size], reverse=True)
    validated = require_nonincreasing_ladder(lines, probabilities)
    assert len(validated) == size


def test_incoherent_ladder_is_rejected() -> None:
    with pytest.raises(MarketMathError, match="nonincreasing"):
        require_nonincreasing_ladder((45.5, 46.5, 47.5), (0.52, 0.55, 0.40))


@pytest.mark.parametrize("multiplier", [-0.01, 1.01])
def test_invalid_kelly_multiplier_is_rejected(multiplier: float) -> None:
    with pytest.raises(MarketMathError, match="multiplier"):
        kelly_fraction(0.55, 2.0, multiplier=multiplier)

