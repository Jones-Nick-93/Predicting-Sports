from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

import numpy as np


@dataclass(frozen=True)
class NewsItem:
    document_id: str
    event_id: str
    revision: int
    text: str
    publication_time: datetime
    ingestion_time: datetime
    feature_available_time: datetime


@dataclass(frozen=True)
class NewsCorpus:
    event_ids: np.ndarray
    labels: np.ndarray
    prediction_times: tuple[datetime, ...]
    event_times: tuple[datetime, ...]
    settlement_times: tuple[datetime, ...]
    items: tuple[NewsItem, ...]

    def __post_init__(self) -> None:
        rows = len(self.event_ids)
        if self.labels.shape != (rows,) or set(np.unique(self.labels)) != {0, 1}:
            raise ValueError("labels must be aligned binary values")
        if len(set(self.event_ids)) != rows:
            raise ValueError("event identifiers must be unique")
        if any(len(values) != rows for values in (self.prediction_times, self.event_times, self.settlement_times)):
            raise ValueError("event timestamps must align")
        if any(not predicted < event < settled for predicted, event, settled in zip(self.prediction_times, self.event_times, self.settlement_times)):
            raise ValueError("event timestamp ordering is invalid")
        known = set(self.event_ids)
        if any(item.event_id not in known for item in self.items):
            raise ValueError("news item references an unknown event")
        if any(not item.publication_time <= item.ingestion_time <= item.feature_available_time for item in self.items):
            raise ValueError("news availability ordering is invalid")

    def select(self, selected_ids: np.ndarray) -> NewsCorpus:
        selected = set(np.asarray(selected_ids))
        mask = np.asarray([event_id in selected for event_id in self.event_ids])
        indices = np.flatnonzero(mask)
        return NewsCorpus(
            self.event_ids[mask].copy(), self.labels[mask].copy(),
            tuple(self.prediction_times[i] for i in indices), tuple(self.event_times[i] for i in indices),
            tuple(self.settlement_times[i] for i in indices),
            tuple(item for item in self.items if item.event_id in selected),
        )


@dataclass(frozen=True)
class CorpusSplit:
    train: NewsCorpus
    calibration: NewsCorpus
    test: NewsCorpus

    def __post_init__(self) -> None:
        if not (max(self.train.settlement_times) < min(self.calibration.prediction_times) and max(self.calibration.settlement_times) < min(self.test.prediction_times)):
            raise ValueError("prior labels must settle before later predictions")


def generate_corpus(*, n_events: int = 600, seed: int = 97) -> NewsCorpus:
    if n_events < 200:
        raise ValueError("n_events must be at least 200")
    rng = np.random.default_rng(seed)
    first_event = datetime(2025, 1, 1, 20, tzinfo=timezone.utc)
    ids, labels, predictions, events, settlements, items = [], [], [], [], [], []
    for index in range(n_events):
        label = int(rng.random() < 0.48)
        event = first_event + timedelta(days=index * 2)
        prediction = event - timedelta(hours=8)
        event_id = f"SYN-{index:05d}"
        early_signal = label if rng.random() < 0.68 else 1 - label
        early = "limited in training status uncertain" if early_signal else "full training trending available"
        definitive = "official update ruled out inactive" if label else "official update cleared active"
        recap = "postgame absence confirmed missed event" if label else "postgame participation confirmed played event"
        ids.append(event_id); labels.append(label); predictions.append(prediction); events.append(event); settlements.append(event + timedelta(hours=4))
        specs = (
            (0, early, prediction - timedelta(hours=5), prediction - timedelta(hours=4, minutes=45)),
            (1, definitive, prediction + timedelta(hours=2), prediction + timedelta(hours=2, minutes=10)),
            (2, recap, event + timedelta(hours=5), event + timedelta(hours=5, minutes=5)),
        )
        for revision, text, published, available in specs:
            noise = rng.choice((" team report", " beat note", " roster news"))
            items.append(NewsItem(f"DOC-{index:05d}", event_id, revision, text + noise, published, published + timedelta(minutes=5), available))
    return NewsCorpus(np.asarray(ids), np.asarray(labels), tuple(predictions), tuple(events), tuple(settlements), tuple(items))


def temporal_split(corpus: NewsCorpus, *, train_fraction: float = 0.70, calibration_fraction: float = 0.15) -> CorpusSplit:
    if not 0 < train_fraction < 1 or not 0 < calibration_fraction < 1 or train_fraction + calibration_fraction >= 1:
        raise ValueError("fractions must form nonempty chronological blocks")
    train_stop = int(len(corpus.event_ids) * train_fraction)
    calibration_stop = train_stop + int(len(corpus.event_ids) * calibration_fraction)
    return CorpusSplit(corpus.select(corpus.event_ids[:train_stop]), corpus.select(corpus.event_ids[train_stop:calibration_stop]), corpus.select(corpus.event_ids[calibration_stop:]))
