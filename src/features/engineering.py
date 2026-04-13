"""Feature engineering facade for a cleaner package API."""

from pathlib import Path

import pandas as pd
from sklearn.pipeline import Pipeline

from features.pipeline import build_feature_pipeline, fit_and_save_pipeline, transform_features


__all__ = [
    "build_feature_pipeline",
    "fit_and_save_pipeline",
    "transform_features",
    "fit_engineering_pipeline",
]


def fit_engineering_pipeline(X_train: pd.DataFrame, save_path: Path | None = None) -> Pipeline:
    """Fit and persist the engineering pipeline."""
    return fit_and_save_pipeline(X_train, save_path=save_path)
