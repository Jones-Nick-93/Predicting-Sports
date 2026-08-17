from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class PointMetrics:
    n: int
    mae: float
    rmse: float


@dataclass(frozen=True)
class IntervalMetrics:
    n: int
    nominal_coverage: float
    empirical_coverage: float
    mean_width: float
    median_width: float
    winkler_score: float
    mae: float
    rmse: float


def point_metrics(y_true: np.ndarray, point: np.ndarray) -> PointMetrics:
    actual, predicted = _aligned_vectors(y_true, point)
    errors = actual - predicted
    return PointMetrics(
        n=len(actual),
        mae=float(np.mean(np.abs(errors))),
        rmse=float(np.sqrt(np.mean(errors**2))),
    )


def interval_metrics(
    y_true: np.ndarray,
    point: np.ndarray,
    lower: np.ndarray,
    upper: np.ndarray,
    *,
    confidence_level: float,
) -> IntervalMetrics:
    if not 0.0 < confidence_level < 1.0:
        raise ValueError("confidence_level must lie in (0, 1)")
    actual, predicted, low, high = _aligned_vectors(y_true, point, lower, upper)
    if np.any(low > high):
        raise ValueError("lower interval bounds cannot exceed upper bounds")
    widths = high - low
    covered = (actual >= low) & (actual <= high)
    alpha = 1.0 - confidence_level
    winkler = widths.copy()
    below = actual < low
    above = actual > high
    winkler[below] += (2.0 / alpha) * (low[below] - actual[below])
    winkler[above] += (2.0 / alpha) * (actual[above] - high[above])
    errors = actual - predicted
    return IntervalMetrics(
        n=len(actual),
        nominal_coverage=confidence_level,
        empirical_coverage=float(np.mean(covered)),
        mean_width=float(np.mean(widths)),
        median_width=float(np.median(widths)),
        winkler_score=float(np.mean(winkler)),
        mae=float(np.mean(np.abs(errors))),
        rmse=float(np.sqrt(np.mean(errors**2))),
    )


def _aligned_vectors(*values: np.ndarray) -> tuple[np.ndarray, ...]:
    arrays = tuple(np.asarray(value, dtype=float) for value in values)
    if not arrays or any(array.ndim != 1 for array in arrays):
        raise ValueError("metric inputs must be one-dimensional")
    if len({len(array) for array in arrays}) != 1 or len(arrays[0]) == 0:
        raise ValueError("metric inputs must be nonempty and equally sized")
    if any(not np.isfinite(array).all() for array in arrays):
        raise ValueError("metric inputs must be finite")
    return arrays

