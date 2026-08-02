from __future__ import annotations

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from backtest_lab import brier_score, brier_score_interval, calibration_bins, evaluate_execution, walk_forward_folds


def main() -> None:
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)
    timestamps = [start + timedelta(days=index) for index in range(14)]
    folds = walk_forward_folds(timestamps, min_train_size=6, test_size=2, embargo_size=1)
    probabilities = [0.42, 0.55, 0.63, 0.48, 0.71, 0.36, 0.59, 0.66]
    outcomes = [0, 1, 1, 0, 1, 0, 0, 1]
    interval = brier_score_interval(probabilities, outcomes, samples=500)
    execution = evaluate_execution(
        decision_at=start,
        market_available_at=start - timedelta(minutes=5),
        event_starts_at=start + timedelta(seconds=2),
        requested_stake=75,
        available_limit=40,
        assumed_latency_ms=250,
    )
    print(f"folds={len(folds)} first_fold={folds[0]}")
    print(f"brier={brier_score(probabilities, outcomes):.4f} interval=({interval[0]:.4f}, {interval[1]:.4f})")
    print(f"calibration_bins={calibration_bins(probabilities, outcomes)}")
    print(f"execution={execution}")


if __name__ == "__main__":
    main()
