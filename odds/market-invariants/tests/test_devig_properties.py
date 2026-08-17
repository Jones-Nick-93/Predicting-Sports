from __future__ import annotations

import math

import pytest
from hypothesis import given

from market_invariants.devig import (
    additive_devig,
    multiplicative_devig,
    odds_ratio_devig,
    power_devig,
)
from market_invariants.domain import MarketMathError, require_probability_simplex
from market_invariants.synthetic import apply_uniform_overround

from .strategies import overround_markets, probability_simplexes


METHODS = (multiplicative_devig, power_devig, odds_ratio_devig)


@given(overround_markets())
def test_supported_devig_methods_return_probability_simplex(
    market: tuple[tuple[float, ...], float, tuple[float, ...]],
) -> None:
    _, _, implied = market
    for method in METHODS:
        result = method(implied)
        assert all(math.isfinite(value) and value >= 0.0 for value in result)
        require_probability_simplex(result, tolerance=1e-9)


@given(overround_markets())
def test_selection_permutation_only_permutes_devig_output(
    market: tuple[tuple[float, ...], float, tuple[float, ...]],
) -> None:
    _, _, implied = market
    for method in METHODS:
        forward = method(implied)
        reversed_result = method(tuple(reversed(implied)))
        assert tuple(reversed(reversed_result)) == pytest.approx(forward, abs=1e-9)


@given(probability_simplexes())
def test_fair_market_is_fixed_point(probabilities: tuple[float, ...]) -> None:
    for method in METHODS:
        assert method(probabilities) == pytest.approx(probabilities, abs=1e-9)


@given(overround_markets())
def test_multiplicative_devig_recovers_uniform_overround_truth(
    market: tuple[tuple[float, ...], float, tuple[float, ...]],
) -> None:
    truth, margin, _ = market
    implied = apply_uniform_overround(truth, margin)
    assert multiplicative_devig(implied) == pytest.approx(truth, abs=1e-12)


def test_additive_method_rejects_negative_output_instead_of_clipping() -> None:
    with pytest.raises(MarketMathError, match="negative"):
        additive_devig((0.98, 0.01, 0.21))


def test_underround_market_is_rejected() -> None:
    for method in (*METHODS, additive_devig):
        with pytest.raises(MarketMathError, match="at least one"):
            method((0.45, 0.45))
