from __future__ import annotations

from datetime import timedelta

import numpy as np
import pytest

from asof_news_nlp.data import NewsCorpus, NewsItem, generate_corpus, temporal_split
from asof_news_nlp.experiment import run_experiment
from asof_news_nlp.features import build_documents
from asof_news_nlp.metrics import evaluate
from asof_news_nlp.models import CalibratedTextClassifier


def test_generator_is_deterministic_and_bitemporal() -> None:
    first = generate_corpus(n_events=200, seed=4); second = generate_corpus(n_events=200, seed=4)
    np.testing.assert_array_equal(first.labels, second.labels)
    assert first.items == second.items
    assert all(item.publication_time <= item.ingestion_time <= item.feature_available_time for item in first.items)


def test_split_requires_prior_labels_to_settle() -> None:
    split = temporal_split(generate_corpus(n_events=400))
    assert (len(split.train.event_ids), len(split.calibration.event_ids), len(split.test.event_ids)) == (280, 60, 60)
    assert max(split.train.settlement_times) < min(split.calibration.prediction_times)
    assert max(split.calibration.settlement_times) < min(split.test.prediction_times)


def test_safe_builder_excludes_future_revisions() -> None:
    corpus = generate_corpus(n_events=200)
    safe = build_documents(corpus, as_of_safe=True); leaky = build_documents(corpus, as_of_safe=False)
    assert np.all(safe.included_items == 1)
    assert np.all(safe.excluded_future_items == 2)
    assert np.all(leaky.included_items == 3)


def test_post_prediction_append_cannot_change_safe_text() -> None:
    corpus = generate_corpus(n_events=200)
    before = build_documents(corpus, as_of_safe=True)
    future = NewsItem("ADVERSARIAL", corpus.event_ids[0], 99, "TARGET LEAK", corpus.prediction_times[0] + timedelta(minutes=1), corpus.prediction_times[0] + timedelta(minutes=2), corpus.prediction_times[0] + timedelta(minutes=3))
    modified = NewsCorpus(corpus.event_ids, corpus.labels, corpus.prediction_times, corpus.event_times, corpus.settlement_times, corpus.items + (future,))
    assert build_documents(modified, as_of_safe=True).texts == before.texts
    assert build_documents(modified, as_of_safe=False).texts != build_documents(corpus, as_of_safe=False).texts


def test_calibrated_model_returns_valid_probabilities() -> None:
    split = temporal_split(generate_corpus(n_events=300))
    train = build_documents(split.train, as_of_safe=True); calibration = build_documents(split.calibration, as_of_safe=True); test = build_documents(split.test, as_of_safe=True)
    probabilities = CalibratedTextClassifier.fit(train, calibration).predict_proba(test)
    assert probabilities.shape == test.labels.shape
    assert np.all((probabilities >= 0) & (probabilities <= 1))


def test_registered_leaky_join_is_suspiciously_perfect() -> None:
    report = run_experiment(n_events=400)
    safe = report["pipelines"]["asof_safe"]["metrics"]; leaky = report["pipelines"]["leaky_event_join"]["metrics"]
    assert leaky["roc_auc"] == 1.0
    assert leaky["log_loss"] < safe["log_loss"]
    assert report["pipelines"]["asof_safe"]["documents"]["future_items_excluded"] == 120


def test_metrics_reject_invalid_probabilities() -> None:
    with pytest.raises(ValueError, match="valid vectors"):
        evaluate(np.asarray([0, 1]), np.asarray([0.2, 1.2]))
