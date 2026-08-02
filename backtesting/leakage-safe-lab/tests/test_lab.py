from datetime import datetime, timedelta, timezone

import pytest

from backtest_lab import (
    FeatureManifest,
    FeatureObservation,
    brier_score,
    brier_score_interval,
    build_as_of_feature_vector,
    calibration_bins,
    evaluate_execution,
    walk_forward_folds,
)


def test_walk_forward_split_preserves_time_and_embargo():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    times = [start + timedelta(days=index) for index in range(12)]
    folds = walk_forward_folds(times, min_train_size=5, test_size=2, embargo_size=1)
    assert len(folds) == 3
    for fold in folds:
        assert max(fold.train_indices) < min(fold.embargo_indices) < min(fold.test_indices)
        assert times[fold.train_indices[-1]] < times[fold.test_indices[0]]


def test_unsorted_timestamps_are_rejected():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError):
        walk_forward_folds([now, now - timedelta(days=1)], 1, 1)


def test_naive_timestamps_are_rejected():
    with pytest.raises(ValueError, match="timezone-aware"):
        walk_forward_folds([datetime(2026, 1, 1), datetime(2026, 1, 2)], 1, 1)


def test_metrics_and_interval_are_bounded():
    probabilities = [0.2, 0.4, 0.6, 0.8]
    outcomes = [0, 0, 1, 1]
    score = brier_score(probabilities, outcomes)
    lower, upper = brier_score_interval(probabilities, outcomes, samples=200)
    assert score == pytest.approx(0.1)
    assert 0 <= lower <= upper <= 1
    assert sum(item.count for item in calibration_bins(probabilities, outcomes, bins=4)) == 4


def test_execution_applies_latency_and_limits():
    now = datetime.now(timezone.utc)
    limited = evaluate_execution(now, now, now + timedelta(seconds=2), 75, 40, 250)
    assert limited.eligible and limited.filled_stake == 40 and limited.reason == "limited_fill"
    locked = evaluate_execution(now, now, now + timedelta(milliseconds=100), 20, 100, 250)
    assert not locked.eligible and locked.reason == "arrives_after_market_lock"


def test_execution_rejects_invalid_time_contract():
    now = datetime.now(timezone.utc)
    with pytest.raises(ValueError, match="availability"):
        evaluate_execution(now, now + timedelta(seconds=2), now + timedelta(seconds=1), 10, 10, 0)


def test_as_of_feature_vector_excludes_future_values():
    now = datetime(2026, 1, 5, tzinfo=timezone.utc)
    manifest = FeatureManifest("v1", ("form", "availability"))
    observations = [
        FeatureObservation("SYN-1", "form", 0.4, now - timedelta(days=2)),
        FeatureObservation("SYN-1", "form", 0.9, now + timedelta(minutes=1)),
        FeatureObservation("SYN-1", "availability", 1.0, now - timedelta(hours=1)),
    ]
    vector = build_as_of_feature_vector("SYN-1", now, manifest, observations)
    assert vector == {"form": 0.4, "availability": 1.0}


def test_as_of_feature_vector_fails_when_required_value_is_missing():
    now = datetime(2026, 1, 5, tzinfo=timezone.utc)
    manifest = FeatureManifest("v1", ("form", "availability"))
    observations = [FeatureObservation("SYN-1", "form", 0.4, now)]
    with pytest.raises(ValueError, match="availability"):
        build_as_of_feature_vector("SYN-1", now, manifest, observations)
