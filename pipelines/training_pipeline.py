"""Training pipeline orchestration."""

import json
from pathlib import Path
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
import joblib

from src.utils.logger import logger
from src.utils.config import PROCESSED_DATA_DIR, MODEL_DIR, RANDOM_STATE


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
        
        # 2. Basic feature selection and preparation
        logger.info("Preparing features...")
        
        # Select numeric columns for training
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        
        # Check if we have target variable
        if 'total_amount' in numeric_cols:
            target = 'total_amount'
            numeric_cols.remove(target)
        else:
            logger.warning("total_amount not found, using last numeric column as target")
            target = numeric_cols[-1]
            numeric_cols = numeric_cols[:-1]
        
        # Prepare features
        X = df[numeric_cols].fillna(0)
        y = df[target].fillna(0)
        
        logger.info(f"Features: {len(X.columns)}, Target: {target}")
        
        # 3. Split data
        logger.info("Splitting data...")
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=RANDOM_STATE
        )
        logger.info(f"Train: {len(X_train)}, Test: {len(X_test)}")
        
        # 4. Train model
        logger.info("Training Linear Regression model...")
        model = LinearRegression()
        model.fit(X_train, y_train)
        
        # 5. Evaluate
        logger.info("Evaluating model...")
        y_pred = model.predict(X_test)
        
        mse = mean_squared_error(y_test, y_pred)
        rmse = np.sqrt(mse)
        r2 = r2_score(y_test, y_pred)
        
        logger.info(f"RMSE: {rmse:.4f}")
        logger.info(f"R² Score: {r2:.4f}")
        
        # 6. Save model
        logger.info("Saving model...")
        MODEL_DIR.mkdir(exist_ok=True)
        model_path = MODEL_DIR / "model.pkl"
        joblib.dump(model, model_path)
        logger.info(f"Model saved to {model_path}")
        
        # 7. Save metrics
        logger.info("Saving metrics...")
        metrics = {
            "rmse": float(rmse),
            "r2_score": float(r2),
            "mse": float(mse),
            "train_samples": len(X_train),
            "test_samples": len(X_test),
            "features": len(X.columns)
        }
        
        metrics_path = MODEL_DIR / "metrics.json"
        with open(metrics_path, 'w') as f:
            json.dump(metrics, f, indent=2)
        logger.info(f"Metrics saved to {metrics_path}")
        
        logger.info("Training pipeline complete! ✅")
        
    except Exception as e:
        logger.error(f"Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()
