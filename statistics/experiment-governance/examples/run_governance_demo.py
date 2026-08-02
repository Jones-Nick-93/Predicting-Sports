"""Synthetic demonstration of complete experiment-family retention."""

from __future__ import annotations

import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from experiment_governance import ExperimentRegistry, Trial, paired_sign_flip_test


def main() -> None:
    baseline = [1.08, 1.12, 1.04, 1.15, 1.09, 1.11, 1.06, 1.14, 1.10, 1.07, 1.13, 1.05]
    candidates = {
        "stable_improvement": [0.98, 1.01, 0.95, 1.04, 1.00, 1.02, 0.96, 1.03, 1.01, 0.97, 1.02, 0.96],
        "mixed_result": [1.02, 1.16, 1.01, 1.10, 1.12, 1.07, 1.09, 1.11, 1.06, 1.10, 1.15, 1.02],
        "no_change": baseline,
    }
    registry = ExperimentRegistry(tuple(candidates), family_alpha=0.05)

    for name, losses in candidates.items():
        test = paired_sign_flip_test(baseline, losses)
        registry.record(
            Trial(
                name=name,
                p_value=test.p_value_one_sided,
                sample_size=test.n_pairs,
                metric_name="mean_loss",
                metric_value=sum(losses) / len(losses),
                guardrail_passed=test.n_pairs >= 8,
                note=f"{test.method} sign-flip test",
            )
        )

    print(registry.summary("bonferroni"))


if __name__ == "__main__":
    main()
