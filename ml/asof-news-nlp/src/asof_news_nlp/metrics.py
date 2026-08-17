from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.metrics import accuracy_score, brier_score_loss, log_loss, roc_auc_score


@dataclass(frozen=True)
class ClassificationMetrics:
    n: int
    accuracy: float
    roc_auc: float
    log_loss: float
    brier_score: float
    expected_calibration_error: float


def evaluate(labels: np.ndarray, probabilities: np.ndarray, *, bins: int = 10) -> ClassificationMetrics:
    y = np.asarray(labels, dtype=int); p = np.asarray(probabilities, dtype=float)
    if y.shape != p.shape or y.ndim != 1 or len(y) == 0 or not np.isfinite(p).all() or np.any((p < 0) | (p > 1)):
        raise ValueError("labels and probabilities must be aligned valid vectors")
    edges = np.linspace(0, 1, bins + 1); ece = 0.0
    for index in range(bins):
        mask = (p >= edges[index]) & (p < edges[index + 1] if index < bins - 1 else p <= edges[index + 1])
        if mask.any(): ece += float(mask.mean() * abs(p[mask].mean() - y[mask].mean()))
    return ClassificationMetrics(len(y), float(accuracy_score(y, p >= 0.5)), float(roc_auc_score(y, p)), float(log_loss(y, p)), float(brier_score_loss(y, p)), ece)
