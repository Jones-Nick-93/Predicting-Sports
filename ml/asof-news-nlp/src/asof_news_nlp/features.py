from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .data import NewsCorpus


@dataclass(frozen=True)
class DocumentBatch:
    event_ids: np.ndarray
    texts: tuple[str, ...]
    labels: np.ndarray
    included_items: np.ndarray
    excluded_future_items: np.ndarray


def build_documents(corpus: NewsCorpus, *, as_of_safe: bool) -> DocumentBatch:
    texts, included, excluded = [], [], []
    for event_id, prediction_time in zip(corpus.event_ids, corpus.prediction_times):
        candidates = [item for item in corpus.items if item.event_id == event_id]
        usable = [item for item in candidates if (item.feature_available_time <= prediction_time or not as_of_safe)]
        usable.sort(key=lambda item: (item.feature_available_time, item.revision))
        texts.append(" ".join(item.text for item in usable) or "no available report")
        included.append(len(usable))
        excluded.append(len(candidates) - len(usable))
    return DocumentBatch(corpus.event_ids.copy(), tuple(texts), corpus.labels.copy(), np.asarray(included), np.asarray(excluded))
