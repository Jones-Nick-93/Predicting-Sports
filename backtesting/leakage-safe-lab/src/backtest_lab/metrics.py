from __future__ import annotations

import math
import random
from dataclasses import dataclass


def _validate(probabilities: list[float], outcomes: list[int]) -> None:
    if not probabilities or len(probabilities) != len(outcomes):
        raise ValueError("probabilities and outcomes must be non-empty and equal length")
    if any(not math.isfinite(p) or p < 0 or p > 1 for p in probabilities):
        raise ValueError("probabilities must be finite values in [0, 1]")
    if any(y not in {0, 1} for y in outcomes):
        raise ValueError("outcomes must be binary")


def brier_score(probabilities: list[float], outcomes: list[int]) -> float:
    _validate(probabilities, outcomes)
    return sum((p - y) ** 2 for p, y in zip(probabilities, outcomes)) / len(outcomes)


@dataclass(frozen=True)
class CalibrationBin:
    lower: float
    upper: float
    count: int
    mean_prediction: float
    observed_rate: float


def calibration_bins(probabilities: list[float], outcomes: list[int], bins: int = 5) -> list[CalibrationBin]:
    _validate(probabilities, outcomes)
    if bins < 1:
        raise ValueError("bins must be positive")
    buckets: list[list[tuple[float, int]]] = [[] for _ in range(bins)]
    for probability, outcome in zip(probabilities, outcomes):
        index = min(int(probability * bins), bins - 1)
        buckets[index].append((probability, outcome))

    result = []
    for index, values in enumerate(buckets):
        if not values:
            continue
        result.append(
            CalibrationBin(
                lower=index / bins,
                upper=(index + 1) / bins,
                count=len(values),
                mean_prediction=sum(value[0] for value in values) / len(values),
                observed_rate=sum(value[1] for value in values) / len(values),
            )
        )
    return result


def brier_score_interval(
    probabilities: list[float],
    outcomes: list[int],
    confidence: float = 0.95,
    samples: int = 2000,
    seed: int = 7,
) -> tuple[float, float]:
    _validate(probabilities, outcomes)
    if not 0 < confidence < 1 or samples < 100:
        raise ValueError("confidence must be in (0, 1) and samples must be at least 100")
    rng = random.Random(seed)
    scores = []
    size = len(outcomes)
    for _ in range(samples):
        indices = [rng.randrange(size) for _ in range(size)]
        scores.append(
            sum((probabilities[i] - outcomes[i]) ** 2 for i in indices) / size
        )
    scores.sort()
    tail = (1.0 - confidence) / 2.0
    lower_index = max(0, int(tail * samples))
    upper_index = min(samples - 1, int((1.0 - tail) * samples) - 1)
    return scores[lower_index], scores[upper_index]
