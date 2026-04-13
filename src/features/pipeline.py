"""Feature engineering pipeline for taxi fare prediction."""

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

from features.transformers import (
    CategoricalEncoder,
    DatetimeFeatureExtractor,
    FareComponentAggregator,
    LocationDistanceCalculator,
    NumericalScaler,
    SpeedCalculator,
    TripDurationCalculator,
)
from utils.logger import logger


def build_feature_pipeline() -> Pipeline:
    """
    Build complete feature engineering pipeline.

    Pipeline stages:
    1. Extract temporal features from datetime columns
    2. Calculate trip duration
    3. Calculate trip speed
    4. Aggregate fare components
    5. Calculate location features
    6. Encode categorical variables
    7. Scale numerical features

    Returns:
        Fitted sklearn Pipeline
    """
    pipeline = Pipeline(
        [
            # Stage 1: Temporal feature extraction
            ("datetime_features", DatetimeFeatureExtractor()),
            # Stage 2: Calculate trip duration (depends on datetime columns)
            ("trip_duration", TripDurationCalculator()),
            # Stage 3: Calculate speed (depends on trip_distance and duration)
            ("speed", SpeedCalculator()),
            # Stage 4: Aggregate fare components
            ("fare_aggregator", FareComponentAggregator()),
            # Stage 5: Location features
            ("location_features", LocationDistanceCalculator()),
            # Stage 6: Encode categorical features
            ("categorical_encoder", CategoricalEncoder()),
            # Stage 7: Scale numerical features (must be last)
            ("scaler", NumericalScaler()),
        ]
    )

    logger.info(f"Feature pipeline created with {len(pipeline.steps)} stages")
    return pipeline


def fit_and_save_pipeline(X_train: pd.DataFrame, save_path: Path = None) -> Pipeline:
    """
    Fit feature pipeline on training data and save it.

    Args:
        X_train: Training data
        save_path: Path to save fitted pipeline (default: models/preprocessor.pkl)

    Returns:
        Fitted pipeline
    """
    if save_path is None:
        save_path = Path("models/preprocessor.pkl")

    logger.info(f"Building and fitting feature pipeline on {len(X_train)} training samples...")

    # Build pipeline
    pipeline = build_feature_pipeline()

    # Fit on training data
    pipeline.fit(X_train)
    logger.info("Pipeline fitting complete")

    # Save fitted pipeline
    save_path.parent.mkdir(exist_ok=True, parents=True)
    joblib.dump(pipeline, save_path)
    logger.info(f"Fitted pipeline saved to {save_path}")

    return pipeline


def load_pipeline(path: Path = None) -> Pipeline:
    """
    Load fitted feature pipeline.

    Args:
        path: Path to saved pipeline (default: models/preprocessor.pkl)

    Returns:
        Loaded pipeline
    """
    if path is None:
        path = Path("models/preprocessor.pkl")

    if not path.exists():
        raise FileNotFoundError(f"Pipeline not found at {path}")

    pipeline = joblib.load(path)
    logger.info(f"Pipeline loaded from {path}")
    return pipeline


def transform_features(X: pd.DataFrame, pipeline: Pipeline = None) -> pd.DataFrame:
    """
    Transform features using fitted pipeline.

    Args:
        X: Input features
        pipeline: Fitted pipeline (loads from disk if None)

    Returns:
        Transformed features
    """
    if pipeline is None:
        pipeline = load_pipeline()

    logger.info(f"Transforming {len(X)} samples through feature pipeline...")
    X_transformed = pipeline.transform(X)
    logger.info(f"Transformation complete: {X_transformed.shape[1]} features generated")

    return X_transformed


def get_feature_names(pipeline: Pipeline = None) -> np.ndarray:
    """
    Get feature names from pipeline.

    Args:
        pipeline: Fitted pipeline

    Returns:
        Array of feature names
    """
    if pipeline is None:
        pipeline = load_pipeline()

    # Get all feature names from all pipeline stages
    feature_names = []

    # Collect original columns that pass through unchanged
    original_cols = [
        "id",
        "VendorID",
        "passenger_count",
        "trip_distance",
        "RatecodeID",
        "PULocationID",
        "DOLocationID",
    ]

    # Add feature names from each step
    for name, step in pipeline.named_steps.items():
        if hasattr(step, "get_feature_names_out"):
            step_features = step.get_feature_names_out()
            feature_names.extend(step_features)

    return np.array(feature_names)
