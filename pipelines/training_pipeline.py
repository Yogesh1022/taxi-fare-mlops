"""Training pipeline orchestration."""

import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from features.pipeline import build_feature_pipeline, fit_and_save_pipeline, get_feature_names
from utils.config import MODEL_DIR, PROCESSED_DATA_DIR, RANDOM_STATE
from utils.logger import logger


def main():
    """Run the training pipeline."""
    logger.info("Starting training pipeline...")

    try:
        # 1. Load processed data
        logger.info("Loading processed data...")
        train_file = PROCESSED_DATA_DIR / "ingested_train.csv"

        if not train_file.exists():
            logger.warning(f"Training data not found at {train_file}")
            logger.info("Using raw data instead...")
            train_file = Path("data/raw/train.csv")

        df = pd.read_csv(train_file)
        logger.info(f"Loaded {len(df)} rows")

        # 2. Extract target and prepare feature data
        logger.info("Preparing features...")

        # Extract target variable
        if "total_amount" in df.columns:
            target = "total_amount"
            y = df[target].fillna(0)
            X = df.drop(columns=[target])
        else:
            logger.warning("total_amount not found")
            # Select numeric columns and use last as target
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            target = numeric_cols[-1]
            y = df[target].fillna(0)
            X = df[numeric_cols[:-1]].fillna(0)

        logger.info(f"Target: {target}, Input features: {X.shape[1]}")

        # 3. Split data BEFORE feature engineering (best practice)
        logger.info("Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE
        )
        logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")

        # 4. Feature Engineering Pipeline
        logger.info("Building feature engineering pipeline...")
        preprocessor = build_feature_pipeline()

        logger.info("Fitting feature pipeline on training data...")
        preprocessor.fit(X_train)

        logger.info("Transforming training data...")
        X_train_transformed = preprocessor.transform(X_train)

        logger.info("Transforming test data...")
        X_test_transformed = preprocessor.transform(X_test)

        # Get feature names from pipeline
        try:
            feature_names = get_feature_names(preprocessor)
            logger.info(f"Engineered features: {len(feature_names)}")
        except:
            feature_names = [f"feature_{i}" for i in range(X_train_transformed.shape[1])]

        # Handle case where output is numpy array, convert to DataFrame
        if isinstance(X_train_transformed, np.ndarray):
            X_train_transformed = pd.DataFrame(X_train_transformed, columns=feature_names)
            X_test_transformed = pd.DataFrame(X_test_transformed, columns=feature_names)

        logger.info(f"Transformed features shape: {X_train_transformed.shape}")

        # 5. Train model on engineered features
        logger.info("Training Linear Regression model...")
        model = LinearRegression()
        model.fit(X_train_transformed, y_train)

        # 6. Evaluate
        logger.info("Evaluating model...")
        y_pred = model.predict(X_test_transformed)

        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)

        logger.info(f"RMSE: {rmse:.4f}")
        logger.info(f"R² Score: {r2:.4f}")

        # 7. Save model and feature preprocessor
        logger.info("Saving model and preprocessor...")
        MODEL_DIR.mkdir(exist_ok=True)

        # Save the trained model
        model_path = MODEL_DIR / "model.pkl"
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")

        # Save the feature preprocessor
        preprocessor_path = MODEL_DIR / "preprocessor.pkl"
        joblib.dump(preprocessor, preprocessor_path)
        logger.info(f"Preprocessor saved to {preprocessor_path}")

        # 8. Save metrics
        logger.info("Saving metrics...")
        metrics = {
            "rmse": float(rmse),
            "r2_score": float(r2),
            "mse": float(mse),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "input_features": X.shape[1],
            "engineered_features": X_train_transformed.shape[1],
            "model": "LinearRegression",
        }

        metrics_path = MODEL_DIR / "metrics.json"
        with open(metrics_path, "w") as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Metrics saved to {metrics_path}")

        logger.info("Training pipeline complete!")

    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
