from __future__ import annotations

from dataclasses import asdict
from importlib.metadata import version

import numpy as np

from .data import chronological_split, generate_dataset
from .gates import FeatureEnvelope, UncertaintyGate
from .metrics import interval_metrics, point_metrics
from .models import (
    IntervalPrediction,
    MapieIntervalModel,
    NGBoostIntervalModel,
    fit_point_baseline,
)


def run_experiment(
    *,
    n_samples: int = 1_200,
    seed: int = 71,
    confidence_level: float = 0.90,
    ngboost_estimators: int = 120,
) -> dict[str, object]:
    dataset = generate_dataset(n_samples=n_samples, seed=seed, shift_fraction=0.90)
    split = chronological_split(dataset)
    baseline = fit_point_baseline(split.train.X, split.train.y, split.test.X, seed=seed)

    mapie = MapieIntervalModel.fit(
        split.train.X,
        split.train.y,
        split.conformalization.X,
        split.conformalization.y,
        confidence_level=confidence_level,
        seed=seed,
    )
    ngboost = NGBoostIntervalModel.fit(
        split.train.X,
        split.train.y,
        confidence_level=confidence_level,
        seed=seed,
        n_estimators=ngboost_estimators,
    )
    mapie_reference = mapie.predict(split.conformalization.X)
    ngboost_reference = ngboost.predict(split.conformalization.X)
    mapie_test = mapie.predict(split.test.X)
    ngboost_test = ngboost.predict(split.test.X)

    envelope = FeatureEnvelope.fit(split.train.X)
    outside = envelope.outside(split.test.X)
    mapie_gate = UncertaintyGate.from_reference_predictions(mapie_reference)
    ngboost_gate = UncertaintyGate.from_reference_predictions(ngboost_reference)
    mapie_gate_report = mapie_gate.evaluate(mapie_test, out_of_domain=outside)
    ngboost_gate_report = ngboost_gate.evaluate(ngboost_test, out_of_domain=outside)

    return {
        "experiment_schema_version": "1.0.0",
        "seed": seed,
        "confidence_level": confidence_level,
        "dependencies": {
            "mapie": version("mapie"),
            "ngboost": version("ngboost"),
            "numpy": version("numpy"),
            "scikit-learn": version("scikit-learn"),
        },
        "split": {
            "train_rows": len(split.train.y),
            "conformalization_rows": len(split.conformalization.y),
            "test_rows": len(split.test.y),
            "trained_through": split.train.event_time[-1].isoformat(),
            "conformalized_through": split.conformalization.event_time[-1].isoformat(),
            "test_started_at": split.test.event_time[0].isoformat(),
        },
        "baseline": asdict(point_metrics(split.test.y, baseline)),
        "models": {
            "mapie_split_conformal": _model_report(
                split.test.y,
                split.test.regime,
                mapie_test,
                mapie_gate_report.statuses,
                mapie_gate.max_interval_width,
            ),
            "ngboost_normal": _model_report(
                split.test.y,
                split.test.regime,
                ngboost_test,
                ngboost_gate_report.statuses,
                ngboost_gate.max_interval_width,
            ),
        },
        "feature_shift": {
            "out_of_domain_rows": int(outside.sum()),
            "out_of_domain_fraction": float(np.mean(outside)),
        },
        "interpretation": (
            "Synthetic methodology result only; no real forecast, market, or wagering authority."
        ),
    }


def _model_report(
    y_true: np.ndarray,
    regimes: np.ndarray,
    prediction: IntervalPrediction,
    statuses: tuple[str, ...],
    width_limit: float,
) -> dict[str, object]:
    report: dict[str, object] = {
        "overall": asdict(
            interval_metrics(
                y_true,
                prediction.point,
                prediction.lower,
                prediction.upper,
                confidence_level=prediction.confidence_level,
            )
        ),
        "gate": {
            "max_interval_width": width_limit,
            "counts": _status_counts(statuses),
            "eligible_fraction": statuses.count("eligible") / len(statuses),
        },
        "regimes": {},
    }
    regime_reports: dict[str, object] = {}
    for regime in sorted(set(str(value) for value in regimes)):
        mask = regimes == regime
        regime_reports[regime] = {
            "metrics": asdict(
                interval_metrics(
                    y_true[mask],
                    prediction.point[mask],
                    prediction.lower[mask],
                    prediction.upper[mask],
                    confidence_level=prediction.confidence_level,
                )
            ),
            "gate_counts": _status_counts(
                tuple(status for status, selected in zip(statuses, mask) if selected)
            ),
        }
    report["regimes"] = regime_reports
    return report


def _status_counts(statuses: tuple[str, ...]) -> dict[str, int]:
    return {
        status: statuses.count(status)
        for status in ("eligible", "review_shift", "review_width", "blocked_invalid")
        if statuses.count(status)
    }

