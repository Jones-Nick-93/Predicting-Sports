from __future__ import annotations

import numpy as np

from uncertainty_gates.data import chronological_split, generate_dataset
from uncertainty_gates.experiment import run_experiment
from uncertainty_gates.models import MapieIntervalModel, NGBoostIntervalModel


def _assert_valid_prediction(prediction: object, rows: int) -> None:
    assert prediction.point.shape == (rows,)
    assert prediction.lower.shape == (rows,)
    assert prediction.upper.shape == (rows,)
    assert np.isfinite(prediction.point).all()
    assert np.all(prediction.lower <= prediction.point)
    assert np.all(prediction.point <= prediction.upper)


def test_mapie_adapter_produces_finite_ordered_intervals() -> None:
    split = chronological_split(generate_dataset(n_samples=360, seed=7))
    model = MapieIntervalModel.fit(
        split.train.X,
        split.train.y,
        split.conformalization.X,
        split.conformalization.y,
        seed=7,
        max_iter=30,
    )

    _assert_valid_prediction(model.predict(split.test.X), len(split.test.y))


def test_ngboost_adapter_produces_finite_ordered_intervals() -> None:
    split = chronological_split(generate_dataset(n_samples=360, seed=7))
    model = NGBoostIntervalModel.fit(
        split.train.X,
        split.train.y,
        seed=7,
        n_estimators=20,
    )

    _assert_valid_prediction(model.predict(split.test.X), len(split.test.y))


def test_experiment_reports_regime_metrics_and_gate_states() -> None:
    report = run_experiment(n_samples=400, seed=11, ngboost_estimators=20)

    assert report["experiment_schema_version"] == "1.0.0"
    assert report["split"]["train_rows"] == 240
    assert report["split"]["conformalization_rows"] == 80
    assert report["split"]["test_rows"] == 80
    assert report["feature_shift"]["out_of_domain_rows"] > 0
    for model_report in report["models"].values():
        assert set(model_report["regimes"]) == {"stable", "shifted"}
        assert 0.0 <= model_report["overall"]["empirical_coverage"] <= 1.0
        assert model_report["overall"]["mean_width"] > 0.0
        assert "blocked_invalid" not in model_report["gate"]["counts"]
