from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable


def _require_aware(value: datetime, field: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{field} must be timezone-aware")


@dataclass(frozen=True)
class FeatureManifest:
    version: str
    names: tuple[str, ...]

    def __post_init__(self) -> None:
        if not self.version.strip() or not self.names:
            raise ValueError("manifest version and feature names are required")
        if any(not name.strip() for name in self.names) or len(set(self.names)) != len(self.names):
            raise ValueError("feature names must be non-empty and unique")


@dataclass(frozen=True)
class FeatureObservation:
    entity_id: str
    feature_name: str
    value: float
    available_at: datetime

    def __post_init__(self) -> None:
        if not self.entity_id.strip() or not self.feature_name.strip():
            raise ValueError("entity_id and feature_name are required")
        if not math.isfinite(self.value):
            raise ValueError("feature value must be finite")
        _require_aware(self.available_at, "available_at")


def build_as_of_feature_vector(
    entity_id: str,
    decision_at: datetime,
    manifest: FeatureManifest,
    observations: Iterable[FeatureObservation],
) -> dict[str, float]:
    """Return the latest manifest value available by the decision timestamp."""
    _require_aware(decision_at, "decision_at")
    latest: dict[str, FeatureObservation] = {}
    for observation in observations:
        if observation.entity_id != entity_id or observation.feature_name not in manifest.names:
            continue
        if observation.available_at > decision_at:
            continue
        current = latest.get(observation.feature_name)
        if current is None or observation.available_at > current.available_at:
            latest[observation.feature_name] = observation

    missing = [name for name in manifest.names if name not in latest]
    if missing:
        raise ValueError(f"missing as-of features: {', '.join(missing)}")
    return {name: latest[name].value for name in manifest.names}
