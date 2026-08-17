from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

from .features import DocumentBatch


@dataclass
class CalibratedTextClassifier:
    vectorizer: TfidfVectorizer
    classifier: LogisticRegression
    calibrator: LogisticRegression

    @classmethod
    def fit(cls, train: DocumentBatch, calibration: DocumentBatch, *, seed: int = 97) -> CalibratedTextClassifier:
        vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True)
        X_train = vectorizer.fit_transform(train.texts)
        classifier = LogisticRegression(C=1.0, max_iter=1000, random_state=seed)
        classifier.fit(X_train, train.labels)
        raw = classifier.predict_proba(vectorizer.transform(calibration.texts))[:, 1]
        logits = np.log(np.clip(raw, 1e-6, 1 - 1e-6) / np.clip(1 - raw, 1e-6, 1))[:, None]
        calibrator = LogisticRegression(C=1.0, max_iter=1000, random_state=seed)
        calibrator.fit(logits, calibration.labels)
        return cls(vectorizer, classifier, calibrator)

    def predict_proba(self, batch: DocumentBatch) -> np.ndarray:
        raw = self.classifier.predict_proba(self.vectorizer.transform(batch.texts))[:, 1]
        logits = np.log(np.clip(raw, 1e-6, 1 - 1e-6) / np.clip(1 - raw, 1e-6, 1))[:, None]
        return np.asarray(self.calibrator.predict_proba(logits)[:, 1])
