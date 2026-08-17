from __future__ import annotations

import math

import pytest
from hypothesis import given, strategies as st

from market_invariants.domain import (
    MarketMathError,
    american_to_decimal,
    decimal_to_american,
    decimal_to_probability,
    probability_to_decimal,
    require_probability_simplex,
)

from .strategies import probability_simplexes


@given(st.floats(min_value=0.001, max_value=0.999, allow_nan=False, allow_infinity=False))
def test_probability_decimal_round_trip(probability: float) -> None:
    assert decimal_to_probability(probability_to_decimal(probability)) == pytest.approx(
        probability, rel=1e-12, abs=1e-12
    )


@given(st.floats(min_value=1.001, max_value=1_000.0, allow_nan=False, allow_infinity=False))
def test_decimal_american_round_trip(decimal_odds: float) -> None:
    assert american_to_decimal(decimal_to_american(decimal_odds)) == pytest.approx(
        decimal_odds, rel=1e-12, abs=1e-12
    )


@given(probability_simplexes())
def test_generated_simplex_passes_validation(probabilities: tuple[float, ...]) -> None:
    assert require_probability_simplex(probabilities) == probabilities


@pytest.mark.parametrize(
    "values",
    [
        [0.7, 0.4],
        [math.nan, 1.0],
        [-0.1, 1.1],
        [1.0],
    ],
)
def test_invalid_simplex_is_rejected(values: list[float]) -> None:
    with pytest.raises(MarketMathError):
        require_probability_simplex(values)


@pytest.mark.parametrize("odds", [1.0, 0.0, math.inf, math.nan])
def test_invalid_decimal_odds_are_rejected(odds: float) -> None:
    with pytest.raises(MarketMathError):
        decimal_to_probability(odds)

