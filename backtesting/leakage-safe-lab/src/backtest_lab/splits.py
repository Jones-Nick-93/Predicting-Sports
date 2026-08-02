from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Sequence


@dataclass(frozen=True)
class WalkForwardFold:
    fold: int
    train_indices: tuple[int, ...]
    embargo_indices: tuple[int, ...]
    test_indices: tuple[int, ...]


def walk_forward_folds(
    timestamps: Sequence[datetime],
    min_train_size: int,
    test_size: int,
    step_size: int | None = None,
    embargo_size: int = 0,
) -> list[WalkForwardFold]:
    if min_train_size < 1 or test_size < 1:
        raise ValueError("min_train_size and test_size must be positive")
    if embargo_size < 0:
        raise ValueError("embargo_size cannot be negative")
    step = test_size if step_size is None else step_size
    if step < 1:
        raise ValueError("step_size must be positive")
    if any(timestamp.tzinfo is None or timestamp.utcoffset() is None for timestamp in timestamps):
        raise ValueError("timestamps must be timezone-aware")
    if list(timestamps) != sorted(timestamps):
        raise ValueError("timestamps must be sorted ascending")
    if len(set(timestamps)) != len(timestamps):
        raise ValueError("timestamps must be unique for index-based folds")

    folds: list[WalkForwardFold] = []
    train_end = min_train_size
    fold_number = 1
    while True:
        test_start = train_end + embargo_size
        test_end = test_start + test_size
        if test_end > len(timestamps):
            break
        train = tuple(range(0, train_end))
        embargo = tuple(range(train_end, test_start))
        test = tuple(range(test_start, test_end))
        if timestamps[train[-1]] >= timestamps[test[0]]:
            raise AssertionError("training time must precede test time")
        folds.append(WalkForwardFold(fold_number, train, embargo, test))
        fold_number += 1
        train_end += step
    return folds
