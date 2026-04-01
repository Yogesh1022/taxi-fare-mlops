"""Hyperparameter tuning orchestration."""

import json
import pandas as pd
import numpy as np
from pathlib import Path

from src.utils.logger import logger
from src.utils.config import PROCESSED_DATA_DIR, MODEL_DIR, RANDOM_STATE
from src.features.pipeline import load_pipeline
from src.models.tune import tune_top_3_models


def main():
    """Run hyperparameter tuning pipeline."""
    logger.info("Starting hyperparameter tuning pipeline...")
    
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
        if 'total_amount' in df.columns:
            target = 'total_amount'
            y = df[target].fillna(0)
            X = df.drop(columns=[target])
        else:
            logger.warning("total_amount not found")
            numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
            target = numeric_cols[-1]
            y = df[target].fillna(0)
            X = df[numeric_cols[:-1]].fillna(0)
        
        logger.info(f"Target: {target}, Input features: {X.shape[1]}")
        
        # 3. Split data into train/val/test (60/20/20)
        logger.info("Splitting data into train/val/test (60/20/20)...")
        
        n = len(X)
        train_idx = int(0.6 * n)
        val_idx = int(0.8 * n)
        
        X_train = X[:train_idx]
        X_val = X[train_idx:val_idx]
        X_test = X[val_idx:]
        
        y_train = y[:train_idx].values  # Convert to numpy array
        y_val = y[train_idx:val_idx].values  # Convert to numpy array
        y_test = y[val_idx:].values  # Convert to numpy array
        
        logger.info(f"Train: {len(X_train)}, Val: {len(X_val)}, Test: {len(X_test)}")
        
        # 4. Load and apply feature pipeline
        logger.info("Loading feature pipeline...")
        preprocessor = load_pipeline()
        
        logger.info("Transforming data with feature pipeline...")
        X_train_transformed = preprocessor.transform(X_train)
        X_val_transformed = preprocessor.transform(X_val)
        X_test_transformed = preprocessor.transform(X_test)
        
        # Convert to DataFrame if needed
        if not isinstance(X_train_transformed, pd.DataFrame):
            n_features = X_train_transformed.shape[1]
            X_train_transformed = pd.DataFrame(X_train_transformed, columns=[f"feature_{i}" for i in range(n_features)])
            X_val_transformed = pd.DataFrame(X_val_transformed, columns=[f"feature_{i}" for i in range(n_features)])
            X_test_transformed = pd.DataFrame(X_test_transformed, columns=[f"feature_{i}" for i in range(n_features)])
        
        logger.info(f"Transformed feature shape: {X_train_transformed.shape}")
        
        # 5. Run hyperparameter tuning (20 trials per model - optimized)
        logger.info("Starting hyperparameter tuning...")
        results = tune_top_3_models(
            X_train_transformed, X_val_transformed, X_test_transformed,
            y_train, y_val, y_test,
            n_trials=20,
            output_dir=MODEL_DIR
        )
        
        # 6. Create comparison report
        logger.info("\n" + "="*80)
        logger.info("HYPERPARAMETER TUNING RESULTS")
        logger.info("="*80)
        
        comparison_path = MODEL_DIR / "tuning_comparison.json"
        if comparison_path.exists():
            with open(comparison_path, 'r') as f:
                comparison = json.load(f)
            
            for model_name, comp in comparison.items():
                if comp['baseline_r2'] is not None:
                    baseline = comp['baseline_r2']
                    tuned = comp['tuned_r2']
                    improvement = comp['improvement']
                    improvement_pct = comp['improvement_pct']
                    
                    logger.info(f"\n{model_name}:")
                    logger.info(f"  Baseline R²: {baseline:.4f}")
                    logger.info(f"  Tuned R²:    {tuned:.4f}")
                    logger.info(f"  Improvement: {improvement:+.4f} ({improvement_pct:+.2f}%)")
                    logger.info(f"  Tuned RMSE:  {comp['tuned_metrics']['rmse']:.4f}")
                    logger.info(f"  Tuned MAE:   {comp['tuned_metrics']['mae']:.4f}")
        
        logger.info("="*80 + "\n")
        
        # 7. Save summary
        summary = {
            "tuning_complete": True,
            "models_tuned": list(results.keys()),
            "n_trials": 30,
            "results": results,
        }
        
        summary_path = MODEL_DIR / "tuning_summary.json"
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        logger.info(f"Tuning summary saved to {summary_path}")
        
        logger.info("Hyperparameter tuning pipeline complete!")
        
    except Exception as e:
        logger.error(f"Error in hyperparameter tuning pipeline: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
