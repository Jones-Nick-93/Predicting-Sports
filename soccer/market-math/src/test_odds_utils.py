"""Tests for public, model-independent betting math."""

import math

import pytest

from odds_utils import (
    american_to_decimal,
    american_to_prob,
    american_to_probability,
    decimal_to_american,
    decimal_to_probability,
    format_american,
    fractional_kelly,
    prob_to_american,
    probability_to_american,
    probability_to_decimal,
)


@pytest.mark.parametrize(
    ("probability", "expected"),
    [(0.25, 4.0), (0.5, 2.0), (1.0, 1.0), (0.53, 1.0 / 0.53)],
)
def test_probability_to_decimal_preserves_precision(probability, expected):
    assert probability_to_decimal(probability) == pytest.approx(expected)


@pytest.mark.parametrize(
    ("american", "decimal"),
    [(-200, 1.5), (-110, 1.0 + 100.0 / 110.0), (-100, 2.0), (100, 2.0), (150, 2.5)],
)
def test_american_decimal_known_values_and_round_trip(american, decimal):
    assert american_to_decimal(american) == pytest.approx(decimal)
    expected_american = 100.0 if american == -100 else float(american)
    assert decimal_to_american(decimal) == pytest.approx(expected_american)


@pytest.mark.parametrize("probability", [0.1, 0.4, 0.5, 0.6, 0.9])
def test_probability_american_round_trip(probability):
    american = probability_to_american(probability)
    assert american_to_probability(american) == pytest.approx(probability)


def test_quarter_kelly_uses_net_profit_odds():
    assert fractional_kelly(0.55, 2.0, multiplier=0.25) == pytest.approx(0.025)
    decimal_odds = american_to_decimal(-110)
    assert fractional_kelly(0.55, decimal_odds, multiplier=0.25) == pytest.approx(0.01375)


def test_kelly_returns_zero_when_there_is_no_positive_edge():
    assert fractional_kelly(0.50, american_to_decimal(-110), multiplier=0.25) == 0.0


def test_compatibility_helpers_use_validated_conversions():
    assert prob_to_american(0.6) == -150
    assert prob_to_american(0.4) == 150
    assert american_to_prob(-150) == pytest.approx(0.6)
    assert format_american(150) == "+150"
    assert format_american(-110) == "-110"


@pytest.mark.parametrize("probability", [0, -0.1, 1.1, math.inf, math.nan])
def test_invalid_probabilities_are_rejected(probability):
    with pytest.raises(ValueError):
        probability_to_decimal(probability)


@pytest.mark.parametrize("probability", [0, 1, -0.1, 1.1, math.inf, math.nan])
def test_boundaries_without_finite_american_prices_are_rejected(probability):
    with pytest.raises(ValueError):
        probability_to_american(probability)


@pytest.mark.parametrize("american", [0, math.inf, -math.inf, math.nan])
def test_invalid_american_odds_are_rejected(american):
    with pytest.raises(ValueError):
        american_to_decimal(american)


@pytest.mark.parametrize("decimal", [0, 0.99, -1, math.inf, math.nan])
def test_invalid_decimal_odds_are_rejected(decimal):
    with pytest.raises(ValueError):
        decimal_to_probability(decimal)


@pytest.mark.parametrize(
    ("probability", "decimal", "multiplier"),
    [(-0.1, 2.0, 0.25), (1.1, 2.0, 0.25), (0.5, 1.0, 0.25), (0.5, 2.0, -0.1), (0.5, 2.0, 1.1)],
)
def test_kelly_rejects_invalid_inputs(probability, decimal, multiplier):
    with pytest.raises(ValueError):
        fractional_kelly(probability, decimal, multiplier=multiplier)


@pytest.mark.parametrize("value", [True, False, "-110", None])
def test_non_numeric_or_boolean_inputs_are_rejected(value):
    with pytest.raises(TypeError):
        american_to_decimal(value)


def test_formatting_rejects_fractional_prices():
    with pytest.raises(ValueError):
        format_american(100.5)
