import pytest

from experiment_governance import effective_sample_size, paired_sign_flip_test, weighted_mean


def test_effective_sample_size_equal_weights_matches_count():
    assert effective_sample_size([1, 1, 1, 1]) == pytest.approx(4)


def test_effective_sample_size_exposes_concentrated_weights():
    assert effective_sample_size([10, 0.1, 0.1, 0.1]) < 2


@pytest.mark.parametrize("weights", [[], [0, 0], [1, -1], [1, float("nan")]])
def test_effective_sample_size_rejects_invalid_weights(weights):
    with pytest.raises(ValueError):
        effective_sample_size(weights)


def test_weighted_mean_validates_and_calculates():
    assert weighted_mean([1, 3], [1, 3]) == pytest.approx(2.5)
    with pytest.raises(ValueError):
        weighted_mean([1], [1, 2])


def test_exact_sign_flip_all_four_pairs_improve():
    result = paired_sign_flip_test([2, 2, 2, 2], [1, 1, 1, 1])
    assert result.method == "exact"
    assert result.mean_improvement == pytest.approx(1)
    assert result.p_value_one_sided == pytest.approx(1 / 16)


def test_sign_flip_identical_losses_returns_one():
    result = paired_sign_flip_test([1, 2, 3], [1, 2, 3])
    assert result.p_value_one_sided == 1


def test_monte_carlo_sign_flip_is_deterministic():
    baseline = [2.0] * 21
    candidate = [1.0] * 21
    first = paired_sign_flip_test(baseline, candidate, monte_carlo_draws=500, seed=11)
    second = paired_sign_flip_test(baseline, candidate, monte_carlo_draws=500, seed=11)
    assert first == second and first.method == "monte_carlo"
