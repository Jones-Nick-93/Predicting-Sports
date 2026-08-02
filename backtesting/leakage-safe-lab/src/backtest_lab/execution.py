from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
import math


@dataclass(frozen=True)
class ExecutionDecision:
    eligible: bool
    filled_stake: float
    reason: str


def evaluate_execution(
    decision_at: datetime,
    market_available_at: datetime,
    event_starts_at: datetime,
    requested_stake: float,
    available_limit: float,
    assumed_latency_ms: int,
) -> ExecutionDecision:
    timestamps = (decision_at, market_available_at, event_starts_at)
    if any(value.tzinfo is None or value.utcoffset() is None for value in timestamps):
        raise ValueError("execution timestamps must be timezone-aware")
    if not math.isfinite(requested_stake) or not math.isfinite(available_limit):
        raise ValueError("stake and limit must be finite")
    if requested_stake <= 0 or available_limit < 0 or assumed_latency_ms < 0:
        raise ValueError("stake must be positive; limit and latency cannot be negative")
    if market_available_at >= event_starts_at:
        raise ValueError("market availability must precede event lock")
    if decision_at < market_available_at:
        return ExecutionDecision(False, 0.0, "market_not_yet_available")
    arrival = decision_at + timedelta(milliseconds=assumed_latency_ms)
    if arrival >= event_starts_at:
        return ExecutionDecision(False, 0.0, "arrives_after_market_lock")
    if available_limit == 0:
        return ExecutionDecision(False, 0.0, "no_available_limit")
    filled = min(requested_stake, available_limit)
    reason = "fully_filled" if filled == requested_stake else "limited_fill"
    return ExecutionDecision(True, filled, reason)
