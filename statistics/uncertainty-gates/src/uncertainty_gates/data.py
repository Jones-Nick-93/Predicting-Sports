from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np


@dataclass(frozen=True)
class TemporalRegressionDataset:
    X: np.ndarray
    y: np.ndarray
    publication_time: tuple[datetime, ...]
    ingestion_time: tuple[datetime, ...]
    feature_available_time: tuple[datetime, ...]
    prediction_time: tuple[datetime, ...]
    event_time: tuple[datetime, ...]
    regime: np.ndarray

    def __post_init__(self) -> None:
        rows = len(self.y)
        if self.X.ndim != 2 or self.X.shape[0] != rows:
            raise ValueError("X must be a two-dimensional matrix aligned with y")
        if self.y.ndim != 1 or self.regime.shape != (rows,):
            raise ValueError("y and regime must be one-dimensional and aligned")
        if not np.isfinite(self.X).all() or not np.isfinite(self.y).all():
            raise ValueError("features and targets must be finite")
        timestamp_fields = (
            self.publication_time,
            self.ingestion_time,
            self.feature_available_time,
            self.prediction_time,
            self.event_time,
        )
        if any(len(values) != rows for values in timestamp_fields):
            raise ValueError("all timestamp fields must align with y")
        for values in timestamp_fields:
            if any(value.tzinfo is None or value.utcoffset() is None for value in values):
                raise ValueError("timestamps must be timezone-aware")
        for published, ingested, available, predicted, event in zip(*timestamp_fields):
            if not published <= ingested <= available <= predicted < event:
                raise ValueError("timestamp availability ordering is invalid")
        if any(right <= left for left, right in zip(self.event_time, self.event_time[1:])):
            raise ValueError("event_time must be strictly increasing")

    def subset(self, start: int, stop: int) -> TemporalRegressionDataset:
        return TemporalRegressionDataset(
            X=self.X[start:stop].copy(),
            y=self.y[start:stop].copy(),
            publication_time=self.publication_time[start:stop],
            ingestion_time=self.ingestion_time[start:stop],
            feature_available_time=self.feature_available_time[start:stop],
            prediction_time=self.prediction_time[start:stop],
            event_time=self.event_time[start:stop],
            regime=self.regime[start:stop].copy(),
        )


@dataclass(frozen=True)
class TemporalSplit:
    train: TemporalRegressionDataset
    conformalization: TemporalRegressionDataset
    test: TemporalRegressionDataset

    def __post_init__(self) -> None:
        if not (
            self.train.event_time[-1]
            < self.conformalization.event_time[0]
            <= self.conformalization.event_time[-1]
            < self.test.event_time[0]
        ):
            raise ValueError("temporal splits must be ordered and nonoverlapping")


def generate_dataset(
    *, n_samples: int = 1_200, seed: int = 71, shift_fraction: float = 0.90
) -> TemporalRegressionDataset:
    if n_samples < 300:
        raise ValueError("n_samples must be at least 300")
    if not 0.80 <= shift_fraction < 1.0:
        raise ValueError("shift_fraction must lie in [0.80, 1.0)")

    rng = np.random.default_rng(seed)
    positions = np.arange(n_samples, dtype=float)
    shift_start = int(round(n_samples * shift_fraction))
    shifted = np.arange(n_samples) >= shift_start
    strength = rng.normal(0.0, 1.0, n_samples) + shifted.astype(float) * 2.25
    pace = rng.normal(0.0, 1.0, n_samples)
    volatility = np.abs(rng.normal(0.0, 1.0, n_samples))
    volatility += shifted.astype(float) * 0.85
    seasonal = np.sin(positions / 35.0)
    X = np.column_stack((strength, pace, volatility, seasonal))

    noise_scale = 1.75 + 1.25 * volatility
    noise_scale *= np.where(shifted, 1.75, 1.0)
    signal = 3.2 * strength + 1.4 * pace + 0.9 * seasonal
    y = signal + rng.standard_t(df=5, size=n_samples) * noise_scale

    first_event = datetime(2025, 1, 1, 20, 0, tzinfo=timezone.utc)
    event_time = tuple(first_event + timedelta(days=int(index)) for index in positions)
    publication_time = tuple(value - timedelta(hours=7) for value in event_time)
    ingestion_time = tuple(value - timedelta(hours=6, minutes=50) for value in event_time)
    feature_available_time = tuple(
        value - timedelta(hours=6, minutes=40) for value in event_time
    )
    prediction_time = tuple(value - timedelta(hours=2) for value in event_time)
    regime = np.where(shifted, "shifted", "stable")
    return TemporalRegressionDataset(
        X=X,
        y=y,
        publication_time=publication_time,
        ingestion_time=ingestion_time,
        feature_available_time=feature_available_time,
        prediction_time=prediction_time,
        event_time=event_time,
        regime=regime,
    )


def chronological_split(
    dataset: TemporalRegressionDataset,
    *,
    train_fraction: float = 0.60,
    conformalization_fraction: float = 0.20,
) -> TemporalSplit:
    if not 0.0 < train_fraction < 1.0:
        raise ValueError("train_fraction must lie in (0, 1)")
    if not 0.0 < conformalization_fraction < 1.0:
        raise ValueError("conformalization_fraction must lie in (0, 1)")
    if train_fraction + conformalization_fraction >= 1.0:
        raise ValueError("train and conformalization fractions must leave a test block")

    rows = len(dataset.y)
    train_stop = int(rows * train_fraction)
    conformalization_stop = train_stop + int(rows * conformalization_fraction)
    if min(train_stop, conformalization_stop - train_stop, rows - conformalization_stop) < 1:
        raise ValueError("each temporal split must contain at least one row")
    return TemporalSplit(
        train=dataset.subset(0, train_stop),
        conformalization=dataset.subset(train_stop, conformalization_stop),
        test=dataset.subset(conformalization_stop, rows),
    )

