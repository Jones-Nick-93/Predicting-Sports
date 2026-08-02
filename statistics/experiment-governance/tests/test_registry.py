import pytest

from experiment_governance import ExperimentRegistry, Trial


def trial(name, p_value, guardrail=True):
    return Trial(name, p_value, 20, "loss", 1.0, guardrail)


def test_registry_rejects_undeclared_and_duplicate_trials():
    registry = ExperimentRegistry(("a", "b"))
    with pytest.raises(ValueError, match="undeclared"):
        registry.record(trial("c", 0.01))
    registry.record(trial("a", 0.01))
    with pytest.raises(ValueError, match="duplicate"):
        registry.record(trial("a", 0.02))


def test_decisions_require_complete_registered_family():
    registry = ExperimentRegistry(("a", "b"))
    registry.record(trial("a", 0.01))
    with pytest.raises(ValueError, match="missing: b"):
        registry.decisions()


def test_bonferroni_uses_full_family_size():
    registry = ExperimentRegistry(("a", "b", "c"), family_alpha=0.06)
    registry.record(trial("a", 0.019))
    registry.record(trial("b", 0.021))
    registry.record(trial("c", 0.001, guardrail=False))
    decisions = {decision.name: decision for decision in registry.decisions("bonferroni")}
    assert decisions["a"].adjusted_alpha == pytest.approx(0.02)
    assert decisions["a"].significant
    assert not decisions["b"].significant
    assert not decisions["c"].significant


def test_holm_stops_after_first_failure():
    registry = ExperimentRegistry(("a", "b", "c"), family_alpha=0.05)
    registry.record(trial("a", 0.01))
    registry.record(trial("b", 0.03))
    registry.record(trial("c", 0.04))
    decisions = {decision.name: decision for decision in registry.decisions("holm")}
    assert decisions["a"].significant
    assert not decisions["b"].significant
    assert not decisions["c"].significant


def test_failed_guardrail_does_not_change_holm_math_for_other_trials():
    registry = ExperimentRegistry(("a", "b", "c"), family_alpha=0.05)
    registry.record(trial("a", 0.001, guardrail=False))
    registry.record(trial("b", 0.01))
    registry.record(trial("c", 0.5))
    decisions = {decision.name: decision for decision in registry.decisions("holm")}
    assert not decisions["a"].significant
    assert decisions["b"].significant
    assert not decisions["c"].significant
