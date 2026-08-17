from __future__ import annotations

import numpy as np
import pytest

from uncertainty_gates.gates import FeatureEnvelope, UncertaintyGate
from uncertainty_gates.metrics import interval_metrics
from uncertainty_gates.models import IntervalPrediction


def _prediction(lower: list[float], upper: list[float]) -> IntervalPrediction:
    return IntervalPrediction(
        model_name="fixture",
        point=np.zeros(len(lower)),
        lower=np.asarray(lower),
        upper=np.asarray(upper),
        confidence_level=0.90,
    )


def test_interval_metrics_match_hand_calculation() -> None:
    metrics = interval_metrics(
        np.asarray([0.0, 2.0]),
        np.asarray([0.0, 0.0]),
        np.asarray([-1.0, -1.0]),
        np.asarray([1.0, 1.0]),
        confidence_level=0.90,
    )

    assert metrics.empirical_coverage == pytest.approx(0.5)
    assert metrics.mean_width == pytest.approx(2.0)
    assert metrics.median_width == pytest.approx(2.0)
    assert metrics.winkler_score == pytest.approx(12.0)
    assert metrics.mae == pytest.approx(1.0)
    assert metrics.rmse == pytest.approx(np.sqrt(2.0))


def test_feature_envelope_flags_only_outside_rows() -> None:
    training = np.asarray([[0.0, 0.0], [1.0, 1.0], [2.0, 2.0]])
    envelope = FeatureEnvelope.fit(
        training, lower_quantile=0.0, upper_quantile=1.0, buffer_fraction=0.0
    )

    np.testing.assert_array_equal(
        envelope.outside(np.asarray([[1.0, 1.5], [3.0, 1.0]])),
        np.asarray([False, True]),
    )


def test_gate_routes_wide_and_shifted_predictions_to_review() -> None:
    report = UncertaintyGate(max_interval_width=4.0).evaluate(
        _prediction([-1.0, -5.0, -1.0], [1.0, 5.0, 1.0]),
        out_of_domain=np.asarray([False, False, True]),
    )

    assert report.statuses == ("eligible", "review_width", "review_shift")
    assert report.counts == {
        "eligible": 1,
        "review_shift": 1,
        "review_width": 1,
    }
    assert report.eligible_fraction == pytest.approx(1.0 / 3.0)


def test_gate_threshold_is_derived_from_reference_widths() -> None:
    gate = UncertaintyGate.from_reference_predictions(
        _prediction([-1.0, -2.0], [1.0, 2.0]),
        width_quantile=1.0,
        expansion=1.25,
    )

    assert gate.max_interval_width == pytest.approx(5.0)


def test_interval_prediction_normalizes_array_like_inputs() -> None:
    prediction = IntervalPrediction("fixture", [0.0], [-1.0], [1.0], 0.90)

    assert isinstance(prediction.point, np.ndarray)
    np.testing.assert_array_equal(prediction.width, np.asarray([2.0]))


def test_interval_prediction_rejects_point_outside_bounds() -> None:
    with pytest.raises(ValueError, match="inside ordered interval"):
        IntervalPrediction("fixture", [2.0], [-1.0], [1.0], 0.90)
