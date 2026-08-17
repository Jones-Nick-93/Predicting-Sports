from __future__ import annotations

import numpy as np
import pytest

from uncertainty_gates.data import chronological_split, generate_dataset


def test_generator_is_deterministic_for_a_fixed_seed() -> None:
    first = generate_dataset(n_samples=300, seed=19)
    second = generate_dataset(n_samples=300, seed=19)

    np.testing.assert_array_equal(first.X, second.X)
    np.testing.assert_array_equal(first.y, second.y)
    np.testing.assert_array_equal(first.regime, second.regime)
    assert first.event_time == second.event_time


def test_every_row_obeys_feature_availability_ordering() -> None:
    dataset = generate_dataset(n_samples=300)

    for published, ingested, available, predicted, event in zip(
        dataset.publication_time,
        dataset.ingestion_time,
        dataset.feature_available_time,
        dataset.prediction_time,
        dataset.event_time,
    ):
        assert published <= ingested <= available <= predicted < event


def test_chronological_split_is_ordered_and_has_expected_sizes() -> None:
    split = chronological_split(generate_dataset(n_samples=500))

    assert (len(split.train.y), len(split.conformalization.y), len(split.test.y)) == (
        300,
        100,
        100,
    )
    assert split.train.event_time[-1] < split.conformalization.event_time[0]
    assert split.conformalization.event_time[-1] < split.test.event_time[0]
    assert set(split.test.regime) == {"stable", "shifted"}


@pytest.mark.parametrize("shift_fraction", [0.79, 1.0])
def test_generator_rejects_shift_outside_declared_range(shift_fraction: float) -> None:
    with pytest.raises(ValueError, match="shift_fraction"):
        generate_dataset(n_samples=300, shift_fraction=shift_fraction)


def test_split_rejects_configuration_without_a_test_block() -> None:
    with pytest.raises(ValueError, match="leave a test block"):
        chronological_split(
            generate_dataset(n_samples=300),
            train_fraction=0.80,
            conformalization_fraction=0.20,
        )
