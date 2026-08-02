from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Literal, Sequence


@dataclass(frozen=True)
class Trial:
    name: str
    p_value: float
    sample_size: int
    metric_name: str
    metric_value: float
    guardrail_passed: bool = True
    note: str = ""

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.metric_name.strip():
            raise ValueError("trial name and metric name are required")
        if not math.isfinite(self.p_value) or not 0 <= self.p_value <= 1:
            raise ValueError("p_value must be finite and in [0, 1]")
        if self.sample_size < 1 or not math.isfinite(self.metric_value):
            raise ValueError("sample_size must be positive and metric_value finite")


@dataclass(frozen=True)
class Decision:
    name: str
    p_value: float
    adjusted_alpha: float
    significant: bool
    guardrail_passed: bool
    reason: str


class ExperimentRegistry:
    def __init__(self, hypotheses: Sequence[str], family_alpha: float = 0.05):
        names = tuple(hypothesis.strip() for hypothesis in hypotheses)
        if not names or any(not name for name in names) or len(set(names)) != len(names):
            raise ValueError("hypotheses must be a non-empty unique family")
        if not math.isfinite(family_alpha) or not 0 < family_alpha < 1:
            raise ValueError("family_alpha must be in (0, 1)")
        self.hypotheses = names
        self.family_alpha = family_alpha
        self._trials: dict[str, Trial] = {}

    def record(self, trial: Trial) -> None:
        if trial.name not in self.hypotheses:
            raise ValueError(f"undeclared hypothesis: {trial.name}")
        if trial.name in self._trials:
            raise ValueError(f"duplicate trial: {trial.name}")
        self._trials[trial.name] = trial

    @property
    def missing(self) -> tuple[str, ...]:
        return tuple(name for name in self.hypotheses if name not in self._trials)

    def decisions(self, method: Literal["bonferroni", "holm"] = "bonferroni") -> list[Decision]:
        if self.missing:
            raise ValueError(f"incomplete family; missing: {', '.join(self.missing)}")
        if method == "bonferroni":
            threshold = self.family_alpha / len(self.hypotheses)
            return [self._decision(self._trials[name], threshold) for name in self.hypotheses]
        if method != "holm":
            raise ValueError("method must be bonferroni or holm")

        ordered = sorted(self._trials.values(), key=lambda trial: (trial.p_value, trial.name))
        results: dict[str, Decision] = {}
        stopped = False
        family_size = len(ordered)
        for rank, trial in enumerate(ordered):
            threshold = self.family_alpha / (family_size - rank)
            statistically_rejected = not stopped and trial.p_value <= threshold
            if trial.p_value > threshold:
                stopped = True
            passes = statistically_rejected and trial.guardrail_passed
            results[trial.name] = self._decision(trial, threshold, significant=passes)
        return [results[name] for name in self.hypotheses]

    @staticmethod
    def _decision(trial: Trial, threshold: float, significant: bool | None = None) -> Decision:
        passes = trial.guardrail_passed and trial.p_value <= threshold if significant is None else significant
        if not trial.guardrail_passed:
            reason = "failed pre-registered guardrail"
        elif passes:
            reason = "passed adjusted threshold"
        else:
            reason = "did not pass adjusted threshold"
        return Decision(trial.name, trial.p_value, threshold, passes, trial.guardrail_passed, reason)

    def summary(self, method: Literal["bonferroni", "holm"] = "bonferroni") -> str:
        lines = [
            f"family={len(self.hypotheses)} method={method} family_alpha={self.family_alpha:.4f}"
        ]
        for decision in self.decisions(method):
            trial = self._trials[decision.name]
            if decision.significant:
                status = "REJECT_NULL"
            elif not decision.guardrail_passed:
                status = "BLOCKED"
            else:
                status = "NOT_REJECTED"
            lines.append(
                f"[{status}] {trial.name}: {trial.metric_name}={trial.metric_value:.4f} "
                f"n={trial.sample_size} p={trial.p_value:.6f} "
                f"adjusted_alpha={decision.adjusted_alpha:.6f}"
            )
        return "\n".join(lines)
