"""Public-safe statistical experiment-governance primitives."""

from .inference import PairedTestResult, effective_sample_size, paired_sign_flip_test, weighted_mean
from .registry import Decision, ExperimentRegistry, Trial

__all__ = [
    "Decision",
    "ExperimentRegistry",
    "PairedTestResult",
    "Trial",
    "effective_sample_size",
    "paired_sign_flip_test",
    "weighted_mean",
]
