"""Batch prediction module for production model inference and monitoring."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import mlflow
import numpy as np
import pandas as pd

from utils.config import MLFLOW_EXPERIMENT_NAME, MLFLOW_TRACKING_URI, MODEL_DIR
from utils.logger import logger


class BatchPredictor:
    """Load production model and make batch predictions with monitoring."""

    def __init__(self, model_name: str = "taxi-fare-xgboost", use_mlflow: bool = True):
        """
        Initialize batch predictor with production model.

        Args:
            model_name: Name of registered model in MLflow
            use_mlflow: Whether to use MLflow for model loading
        """
        self.model_name = model_name
        self.use_mlflow = use_mlflow
        self.model = None
        self.predictions = []
        self.metrics = {}

        if self.use_mlflow:
            mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
            mlflow.set_experiment(MLFLOW_EXPERIMENT_NAME)
            logger.info(f"[BATCH] Initialized with MLflow: {MLFLOW_TRACKING_URI}")

    def load_production_model(self) -> bool:
        """
        Load production model from MLflow Model Registry.

        Returns:
            True if loaded successfully, False otherwise
        """
        logger.info(f"[BATCH] Loading production model: {self.model_name}")

        try:
            if self.use_mlflow:
                # Try to load by alias first (production)
                try:
                    model_uri = f"models:/{self.model_name}@production"
                    self.model = mlflow.sklearn.load_model(model_uri)
                    logger.info(f"[BATCH] ✅ Loaded {self.model_name}@production")
                    return True
                except Exception as e:
                    logger.warning(f"[BATCH] Could not load by alias: {str(e)[:50]}")
                    # Fallback: load by version
                    model_uri = f"models:/{self.model_name}/1"
                    self.model = mlflow.sklearn.load_model(model_uri)
                    logger.info(f"[BATCH] ✅ Loaded {self.model_name} v1")
                    return True
            else:
                logger.warning("[BATCH] MLflow disabled, cannot load model")
                return False

        except Exception as e:
            logger.error(f"[BATCH] Error loading model: {str(e)}")
            return False

    def predict_batch(
        self, X: pd.DataFrame, return_metrics: bool = True
    ) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Make predictions on batch of data.

        Args:
            X: Features DataFrame (n_samples, n_features)
            return_metrics: Whether to compute performance metrics

        Returns:
            Tuple of (predictions array, metrics dict)
        """
        if self.model is None:
            logger.error("[BATCH] Model not loaded, call load_production_model() first")
            raise RuntimeError("Model not loaded")

        logger.info(f"[BATCH] Making predictions on {len(X)} samples...")

        try:
            # Make predictions
            predictions = self.model.predict(X)
            self.predictions = predictions

            # Compute metrics
            metrics = {
                "n_samples": len(predictions),
                "mean_prediction": float(np.mean(predictions)),
                "std_prediction": float(np.std(predictions)),
                "min_prediction": float(np.min(predictions)),
                "max_prediction": float(np.max(predictions)),
            }

            self.metrics = metrics
            logger.info(f"[BATCH] ✅ Predictions complete")
            logger.info(
                f"[BATCH] Mean: {metrics['mean_prediction']:.2f}, "
                f"Std: {metrics['std_prediction']:.2f}"
            )

            return predictions, metrics

        except Exception as e:
            logger.error(f"[BATCH] Error during prediction: {e}")
            raise

    def evaluate_predictions(self, y_true: np.ndarray) -> Dict[str, float]:
        """
        Evaluate predictions against ground truth.

        Args:
            y_true: True target values

        Returns:
            Metrics dict with R², RMSE, MAE, MAPE
        """
        if len(self.predictions) == 0:
            logger.error("[BATCH] No predictions to evaluate")
            raise RuntimeError("No predictions available")

        logger.info("[BATCH] Evaluating predictions...")

        from sklearn.metrics import (
            mean_absolute_error,
            mean_absolute_percentage_error,
            mean_squared_error,
            r2_score,
        )

        try:
            y_pred = self.predictions

            # Compute metrics
            r2 = r2_score(y_true, y_pred)
            rmse = np.sqrt(mean_squared_error(y_true, y_pred))
            mae = mean_absolute_error(y_true, y_pred)
            mape = mean_absolute_percentage_error(y_true, y_pred)

            eval_metrics = {
                "r2_score": float(r2),
                "rmse": float(rmse),
                "mae": float(mae),
                "mape": float(mape),
                "n_samples": len(y_true),
            }

            logger.info(f"[BATCH] ✅ Evaluation complete")
            logger.info(f"[BATCH] R²: {r2:.4f}, RMSE: {rmse:.2f}, MAE: {mae:.2f}")

            return eval_metrics

        except Exception as e:
            logger.error(f"[BATCH] Error evaluating predictions: {e}")
            raise

    def save_predictions(
        self,
        predictions: np.ndarray,
        output_path: Optional[Path] = None,
        y_true: Optional[np.ndarray] = None,
    ) -> Path:
        """
        Save predictions to file.

        Args:
            predictions: Predictions array
            output_path: Path to save predictions (default: models/batch_predictions.json)
            y_true: Optional true values for comparison

        Returns:
            Path to saved predictions file
        """
        if output_path is None:
            output_path = MODEL_DIR / "batch_predictions.json"

        logger.info(f"[BATCH] Saving predictions to {output_path}")

        prediction_data = {
            "timestamp": datetime.now().isoformat(),
            "model_name": self.model_name,
            "n_predictions": len(predictions),
            "predictions": (
                predictions.tolist() if isinstance(predictions, np.ndarray) else predictions
            ),
            "metrics": self.metrics,
        }

        # Add evaluation metrics if ground truth provided
        if y_true is not None:
            try:
                eval_metrics = self.evaluate_predictions(y_true)
                prediction_data["evaluation_metrics"] = eval_metrics
            except Exception as e:
                logger.warning(f"[BATCH] Could not evaluate: {e}")

        # Save to JSON
        with open(output_path, "w") as f:
            json.dump(prediction_data, f, indent=2)

        logger.info(f"[BATCH] ✅ Predictions saved: {output_path}")
        return output_path

    def log_to_mlflow(
        self, metrics: Dict[str, float], predictions: Optional[np.ndarray] = None
    ) -> str:
        """
        Log batch prediction metrics to MLflow.

        Args:
            metrics: Metrics dict to log
            predictions: Optional predictions array to log as artifact

        Returns:
            Run ID
        """
        if not self.use_mlflow:
            logger.warning("[BATCH] MLflow disabled, skipping logging")
            return ""

        logger.info("[BATCH] Logging batch predictions to MLflow...")

        try:
            with mlflow.start_run(run_name="Batch-Predictions"):
                run_id = mlflow.active_run().info.run_id

                # Log parameters
                mlflow.log_param("model_name", self.model_name)
                mlflow.log_param("n_predictions", metrics.get("n_samples", 0))

                # Log metrics
                for key, value in metrics.items():
                    if isinstance(value, (int, float)):
                        mlflow.log_metric(key, value)

                # Log predictions as artifact
                if predictions is not None:
                    pred_artifact_path = Path("batch_predictions.npy")
                    np.save(pred_artifact_path, predictions)
                    mlflow.log_artifact(str(pred_artifact_path))
                    pred_artifact_path.unlink()  # Clean up

                logger.info(f"[BATCH] ✅ Logged to MLflow run: {run_id}")
                return run_id

        except Exception as e:
            logger.error(f"[BATCH] Error logging to MLflow: {e}")
            return ""

    def get_prediction_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about predictions.

        Returns:
            Statistics dict
        """
        if len(self.predictions) == 0:
            return {}

        predictions = self.predictions

        return {
            "count": len(predictions),
            "mean": float(np.mean(predictions)),
            "median": float(np.median(predictions)),
            "std": float(np.std(predictions)),
            "min": float(np.min(predictions)),
            "max": float(np.max(predictions)),
            "q25": float(np.percentile(predictions, 25)),
            "q75": float(np.percentile(predictions, 75)),
        }


class PredictionMonitor:
    """Monitor model predictions for data drift and performance degradation."""

    def __init__(self, baseline_metrics: Dict[str, float] = None):
        """
        Initialize prediction monitor.

        Args:
            baseline_metrics: Baseline metrics for comparison (from training)
        """
        self.baseline_metrics = baseline_metrics or {}
        self.prediction_history = []
        self.alerts = []

        logger.info("[MONITOR] Prediction monitor initialized")

    def check_data_drift(
        self, current_stats: Dict[str, float], threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Check for data drift using statistical comparison.

        Args:
            current_stats: Current prediction statistics
            threshold: Percentage change threshold for alerting (default 10%)

        Returns:
            Drift analysis dict
        """
        logger.info("[MONITOR] Checking for data drift...")

        if not self.baseline_metrics:
            logger.warning("[MONITOR] No baseline metrics for comparison")
            return {}

        drift_analysis = {"timestamp": datetime.now().isoformat(), "checks": {}}

        for metric_name, baseline_value in self.baseline_metrics.items():
            if metric_name in current_stats:
                current_value = current_stats[metric_name]

                # Calculate percentage change
                if baseline_value != 0:
                    pct_change = abs(current_value - baseline_value) / abs(baseline_value)

                    check = {
                        "baseline": baseline_value,
                        "current": current_value,
                        "pct_change": pct_change,
                        "drifted": pct_change > threshold,
                    }

                    drift_analysis["checks"][metric_name] = check

                    if check["drifted"]:
                        alert = f"Data drift detected in {metric_name}: {pct_change:.1%} change"
                        self.alerts.append(alert)
                        logger.warning(f"[MONITOR] ⚠️  {alert}")

        return drift_analysis

    def check_performance_degradation(
        self, current_metrics: Dict[str, float], threshold: float = 0.95
    ) -> Dict[str, Any]:
        """
        Check for model performance degradation.

        Args:
            current_metrics: Current evaluation metrics (r2, rmse, etc.)
            threshold: R² drop threshold (default 95% of baseline)

        Returns:
            Degradation analysis dict
        """
        logger.info("[MONITOR] Checking for performance degradation...")

        if not self.baseline_metrics or "r2_score" not in self.baseline_metrics:
            logger.warning("[MONITOR] No baseline R² for comparison")
            return {}

        current_r2 = current_metrics.get("r2_score")
        baseline_r2 = self.baseline_metrics.get("r2_score")

        degradation_analysis = {
            "timestamp": datetime.now().isoformat(),
            "baseline_r2": baseline_r2,
            "current_r2": current_r2,
        }

        if current_r2 is not None and baseline_r2 is not None:
            r2_ratio = current_r2 / baseline_r2 if baseline_r2 != 0 else 0

            degradation_analysis["r2_ratio"] = r2_ratio
            degradation_analysis["degraded"] = r2_ratio < threshold

            if r2_ratio < threshold:
                alert = f"Performance degradation: R² dropped to {r2_ratio:.1%} of baseline"
                self.alerts.append(alert)
                logger.warning(f"[MONITOR] ⚠️  {alert}")

        return degradation_analysis

    def get_alerts(self) -> List[str]:
        """Get all monitoring alerts."""
        return self.alerts

    def save_monitoring_report(self, output_path: Optional[Path] = None) -> Path:
        """
        Save monitoring report to file.

        Args:
            output_path: Path to save report

        Returns:
            Path to saved report
        """
        if output_path is None:
            output_path = MODEL_DIR / "monitoring_report.json"

        logger.info(f"[MONITOR] Saving monitoring report to {output_path}")

        report = {
            "timestamp": datetime.now().isoformat(),
            "alerts": self.alerts,
            "prediction_history_count": len(self.prediction_history),
            "baseline_metrics": self.baseline_metrics,
        }

        with open(output_path, "w") as f:
            json.dump(report, f, indent=2)

        logger.info(f"[MONITOR] ✅ Report saved: {output_path}")
        return output_path


def run_batch_predictions(
    data_path: Path, model_name: str = "taxi-fare-xgboost", use_mlflow: bool = True
) -> Tuple[np.ndarray, Dict[str, Any]]:
    """
    Run batch predictions on provided data.

    Args:
        data_path: Path to CSV file with features
        model_name: Name of registered model
        use_mlflow: Whether to use MLflow

    Returns:
        Tuple of (predictions, metrics)
    """
    logger.info(f"[DAY8] Running batch predictions on {data_path}")

    # Load data
    X = pd.read_csv(data_path)
    logger.info(f"[DAY8] Loaded {len(X)} samples from {data_path}")

    # Initialize predictor
    predictor = BatchPredictor(model_name=model_name, use_mlflow=use_mlflow)

    # Load model
    if not predictor.load_production_model():
        logger.error("[DAY8] Failed to load production model")
        return np.array([]), {}

    # Make predictions
    try:
        predictions, metrics = predictor.predict_batch(X)

        # Save predictions
        predictor.save_predictions(predictions)

        # Log to MLflow
        if use_mlflow:
            predictor.log_to_mlflow(metrics, predictions)

        logger.info("[DAY8] ✅ Batch predictions complete")
        return predictions, metrics

    except Exception as e:
        logger.error(f"[DAY8] Error during batch predictions: {e}")
        raise
