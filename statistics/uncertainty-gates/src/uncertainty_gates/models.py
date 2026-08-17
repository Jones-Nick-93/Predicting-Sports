from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from mapie.regression import SplitConformalRegressor
from ngboost import NGBRegressor
from ngboost.distns import Normal
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.tree import DecisionTreeRegressor


@dataclass(frozen=True)
class IntervalPrediction:
    model_name: str
    point: np.ndarray
    lower: np.ndarray
    upper: np.ndarray
    confidence_level: float

    def __post_init__(self) -> None:
        point = np.asarray(self.point, dtype=float)
        lower = np.asarray(self.lower, dtype=float)
        upper = np.asarray(self.upper, dtype=float)
        if point.ndim != 1 or lower.shape != point.shape or upper.shape != point.shape:
            raise ValueError("prediction arrays must be aligned one-dimensional vectors")
        if len(point) == 0 or not all(
            np.isfinite(values).all() for values in (point, lower, upper)
        ):
            raise ValueError("prediction arrays must be nonempty and finite")
        if np.any(lower > point) or np.any(point > upper):
            raise ValueError("prediction point must lie inside ordered interval bounds")
        if not 0.0 < self.confidence_level < 1.0:
            raise ValueError("confidence_level must lie in (0, 1)")
        object.__setattr__(self, "point", point)
        object.__setattr__(self, "lower", lower)
        object.__setattr__(self, "upper", upper)

    @property
    def width(self) -> np.ndarray:
        return self.upper - self.lower


@dataclass
class MapieIntervalModel:
    model: SplitConformalRegressor
    confidence_level: float

    @classmethod
    def fit(
        cls,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_conformalization: np.ndarray,
        y_conformalization: np.ndarray,
        *,
        confidence_level: float = 0.90,
        seed: int = 71,
        max_iter: int = 120,
    ) -> MapieIntervalModel:
        estimator = HistGradientBoostingRegressor(
            max_iter=max_iter,
            learning_rate=0.06,
            max_leaf_nodes=15,
            min_samples_leaf=15,
            l2_regularization=0.1,
            random_state=seed,
        )
        model = SplitConformalRegressor(
            estimator=estimator,
            confidence_level=confidence_level,
            conformity_score="absolute",
            prefit=False,
            n_jobs=1,
        )
        model.fit(X_train, y_train)
        model.conformalize(X_conformalization, y_conformalization)
        return cls(model=model, confidence_level=confidence_level)

    def predict(self, X: np.ndarray) -> IntervalPrediction:
        point, intervals = self.model.predict_interval(X)
        interval_array = np.asarray(intervals, dtype=float)
        if interval_array.ndim != 3 or interval_array.shape[1:] != (2, 1):
            raise ValueError("unexpected MAPIE interval shape")
        return IntervalPrediction(
            model_name="mapie_split_conformal",
            point=np.asarray(point, dtype=float),
            lower=interval_array[:, 0, 0],
            upper=interval_array[:, 1, 0],
            confidence_level=self.confidence_level,
        )


@dataclass
class NGBoostIntervalModel:
    model: NGBRegressor
    confidence_level: float

    @classmethod
    def fit(
        cls,
        X_train: np.ndarray,
        y_train: np.ndarray,
        *,
        confidence_level: float = 0.90,
        seed: int = 71,
        n_estimators: int = 120,
    ) -> NGBoostIntervalModel:
        base = DecisionTreeRegressor(
            max_depth=2,
            min_samples_leaf=15,
            random_state=seed,
        )
        model = NGBRegressor(
            Dist=Normal,
            Base=base,
            n_estimators=n_estimators,
            learning_rate=0.035,
            minibatch_frac=1.0,
            col_sample=1.0,
            verbose=False,
            random_state=seed,
        )
        model.fit(X_train, y_train)
        return cls(model=model, confidence_level=confidence_level)

    def predict(self, X: np.ndarray) -> IntervalPrediction:
        distribution = self.model.pred_dist(X)
        point = np.asarray(distribution.params["loc"], dtype=float)
        lower, upper = distribution.dist.interval(self.confidence_level)
        return IntervalPrediction(
            model_name="ngboost_normal",
            point=point,
            lower=np.asarray(lower, dtype=float),
            upper=np.asarray(upper, dtype=float),
            confidence_level=self.confidence_level,
        )


def fit_point_baseline(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_test: np.ndarray,
    *,
    seed: int = 71,
    max_iter: int = 120,
) -> np.ndarray:
    model = HistGradientBoostingRegressor(
        max_iter=max_iter,
        learning_rate=0.06,
        max_leaf_nodes=15,
        min_samples_leaf=15,
        l2_regularization=0.1,
        random_state=seed,
    )
    return np.asarray(model.fit(X_train, y_train).predict(X_test), dtype=float)
