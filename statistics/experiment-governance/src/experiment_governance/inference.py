from __future__ import annotations

import itertools
import math
import random
from dataclasses import dataclass
from typing import Sequence


def _finite_values(values: Sequence[float], field: str) -> list[float]:
    converted = [float(value) for value in values]
    if not converted or any(not math.isfinite(value) for value in converted):
        raise ValueError(f"{field} must contain finite values")
    return converted


def effective_sample_size(weights: Sequence[float]) -> float:
    """Kish effective sample size, used only as a weight-concentration diagnostic."""
    checked = _finite_values(weights, "weights")
    if any(weight < 0 for weight in checked) or sum(checked) <= 0:
        raise ValueError("weights must be non-negative with positive total weight")
    return sum(checked) ** 2 / sum(weight * weight for weight in checked)


def weighted_mean(values: Sequence[float], weights: Sequence[float]) -> float:
    checked_values = _finite_values(values, "values")
    checked_weights = _finite_values(weights, "weights")
    if len(checked_values) != len(checked_weights):
        raise ValueError("values and weights must have equal length")
    if any(weight < 0 for weight in checked_weights) or sum(checked_weights) <= 0:
        raise ValueError("weights must be non-negative with positive total weight")
    return sum(value * weight for value, weight in zip(checked_values, checked_weights)) / sum(checked_weights)


@dataclass(frozen=True)
class PairedTestResult:
    n_pairs: int
    mean_improvement: float
    p_value_one_sided: float
    method: str
    draws: int


def paired_sign_flip_test(
    baseline_losses: Sequence[float],
    candidate_losses: Sequence[float],
    *,
    exact_max_pairs: int = 20,
    monte_carlo_draws: int = 20_000,
    seed: int = 7,
) -> PairedTestResult:
    """Test whether candidate loss is lower using paired sign-flip inference.

    Positive differences (`baseline - candidate`) favor the candidate. Callers are
    responsible for supplying defensible paired evaluation units.
    """
    baseline = _finite_values(baseline_losses, "baseline_losses")
    candidate = _finite_values(candidate_losses, "candidate_losses")
    if len(baseline) != len(candidate) or len(baseline) < 2:
        raise ValueError("paired losses must have equal length with at least two pairs")
    if exact_max_pairs < 1 or monte_carlo_draws < 100:
        raise ValueError("exact_max_pairs must be positive and monte_carlo_draws at least 100")

    differences = [base - challenger for base, challenger in zip(baseline, candidate)]
    observed = sum(differences) / len(differences)
    if all(difference == 0 for difference in differences):
        return PairedTestResult(len(differences), 0.0, 1.0, "degenerate_equal", 1)

    tolerance = 1e-15
    if len(differences) <= exact_max_pairs:
        extreme = 0
        total = 0
        for signs in itertools.product((-1.0, 1.0), repeat=len(differences)):
            permuted = sum(sign * difference for sign, difference in zip(signs, differences)) / len(differences)
            extreme += int(permuted >= observed - tolerance)
            total += 1
        p_value = extreme / total
        return PairedTestResult(len(differences), observed, p_value, "exact", total)

    rng = random.Random(seed)
    extreme = 0
    for _ in range(monte_carlo_draws):
        permuted = sum(
            (1.0 if rng.random() < 0.5 else -1.0) * difference
            for difference in differences
        ) / len(differences)
        extreme += int(permuted >= observed - tolerance)
    p_value = (extreme + 1) / (monte_carlo_draws + 1)
    return PairedTestResult(len(differences), observed, p_value, "monte_carlo", monte_carlo_draws)
