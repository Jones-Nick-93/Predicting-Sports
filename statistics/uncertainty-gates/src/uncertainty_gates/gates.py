from __future__ import annotations

from collections import Counter
from dataclasses import dataclass

import numpy as np

from .models import IntervalPrediction


@dataclass(frozen=True)
class FeatureEnvelope:
    lower: np.ndarray
    upper: np.ndarray

    @classmethod
    def fit(
        cls,
        X_train: np.ndarray,
        *,
        lower_quantile: float = 0.01,
        upper_quantile: float = 0.99,
        buffer_fraction: float = 0.10,
    ) -> FeatureEnvelope:
        features = np.asarray(X_train, dtype=float)
        if features.ndim != 2 or len(features) == 0 or not np.isfinite(features).all():
            raise ValueError("X_train must be a nonempty finite feature matrix")
        if not 0.0 <= lower_quantile < upper_quantile <= 1.0:
            raise ValueError("feature quantiles are invalid")
        if buffer_fraction < 0.0 or not np.isfinite(buffer_fraction):
            raise ValueError("buffer_fraction must be finite and nonnegative")
        lower = np.quantile(features, lower_quantile, axis=0)
        upper = np.quantile(features, upper_quantile, axis=0)
        span = np.maximum(upper - lower, 1e-12)
        return cls(
            lower=lower - buffer_fraction * span,
            upper=upper + buffer_fraction * span,
        )

    def outside(self, X: np.ndarray) -> np.ndarray:
        features = np.asarray(X, dtype=float)
        if features.ndim != 2 or features.shape[1] != len(self.lower):
            raise ValueError("feature matrix does not match fitted envelope")
        if not np.isfinite(features).all():
            raise ValueError("features must be finite")
        return np.any((features < self.lower) | (features > self.upper), axis=1)


@dataclass(frozen=True)
class GateReport:
    statuses: tuple[str, ...]

    @property
    def counts(self) -> dict[str, int]:
        return dict(sorted(Counter(self.statuses).items()))

    @property
    def eligible_fraction(self) -> float:
        return self.statuses.count("eligible") / len(self.statuses)


@dataclass(frozen=True)
class UncertaintyGate:
    max_interval_width: float
    block_out_of_domain: bool = True

    def __post_init__(self) -> None:
        if not np.isfinite(self.max_interval_width) or self.max_interval_width <= 0.0:
            raise ValueError("max_interval_width must be finite and positive")

    @classmethod
    def from_reference_predictions(
        cls,
        prediction: IntervalPrediction,
        *,
        width_quantile: float = 0.90,
        expansion: float = 1.10,
        block_out_of_domain: bool = True,
    ) -> UncertaintyGate:
        if not 0.0 < width_quantile <= 1.0:
            raise ValueError("width_quantile must lie in (0, 1]")
        if expansion < 1.0 or not np.isfinite(expansion):
            raise ValueError("expansion must be finite and at least one")
        width_limit = float(np.quantile(prediction.width, width_quantile) * expansion)
        return cls(width_limit, block_out_of_domain=block_out_of_domain)

    def evaluate(
        self, prediction: IntervalPrediction, *, out_of_domain: np.ndarray
    ) -> GateReport:
        outside = np.asarray(out_of_domain, dtype=bool)
        if outside.shape != prediction.point.shape:
            raise ValueError("out_of_domain must align with predictions")
        statuses: list[str] = []
        for width, shifted in zip(prediction.width, outside):
            if not np.isfinite(width) or width < 0.0:
                statuses.append("blocked_invalid")
            elif self.block_out_of_domain and shifted:
                statuses.append("review_shift")
            elif width > self.max_interval_width:
                statuses.append("review_width")
            else:
                statuses.append("eligible")
        return GateReport(tuple(statuses))

