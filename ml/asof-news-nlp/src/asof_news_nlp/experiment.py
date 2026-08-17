from __future__ import annotations

from dataclasses import asdict
from importlib.metadata import version

import numpy as np

from .data import generate_corpus, temporal_split
from .features import build_documents
from .metrics import evaluate
from .models import CalibratedTextClassifier


def run_experiment(*, n_events: int = 600, seed: int = 97) -> dict[str, object]:
    split = temporal_split(generate_corpus(n_events=n_events, seed=seed))
    reports = {}
    for name, safe in (("asof_safe", True), ("leaky_event_join", False)):
        train = build_documents(split.train, as_of_safe=safe)
        calibration = build_documents(split.calibration, as_of_safe=safe)
        test = build_documents(split.test, as_of_safe=safe)
        model = CalibratedTextClassifier.fit(train, calibration, seed=seed)
        probabilities = model.predict_proba(test)
        terms = np.asarray(model.vectorizer.get_feature_names_out())
        coefficients = model.classifier.coef_[0]
        reports[name] = {
            "metrics": asdict(evaluate(test.labels, probabilities)),
            "documents": {
                "mean_items_included": float(test.included_items.mean()),
                "future_items_excluded": int(test.excluded_future_items.sum()),
            },
            "strongest_positive_terms": terms[np.argsort(coefficients)[-6:][::-1]].tolist(),
        }
    return {
        "experiment_schema_version": "1.0.0",
        "seed": seed,
        "dependencies": {"numpy": version("numpy"), "scikit-learn": version("scikit-learn")},
        "split": {
            "train_events": len(split.train.event_ids),
            "calibration_events": len(split.calibration.event_ids),
            "test_events": len(split.test.event_ids),
            "trained_through_settlement": max(split.train.settlement_times).isoformat(),
            "test_prediction_started": min(split.test.prediction_times).isoformat(),
        },
        "pipelines": reports,
        "audit": {
            "confirmed_leakage": "Joining all document revisions by event ID admits definitive and post-event text unavailable at prediction time.",
            "affected_estimate": "The leaky pipeline's holdout discrimination and calibration metrics.",
            "prevention_test": "Appending a post-prediction revision must not change the as-of-safe document batch.",
        },
        "interpretation": "Synthetic leakage demonstration only; no real injury forecast, selection, or wager.",
    }
