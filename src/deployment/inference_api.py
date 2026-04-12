"""FastAPI inference server for production model serving."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

import mlflow
import numpy as np
import pandas as pd
import uvicorn
from fastapi import BackgroundTasks, FastAPI, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from src.deployment.batch_predictions import BatchPredictor, PredictionMonitor
from src.utils.config import MLFLOW_EXPERIMENT_NAME, MLFLOW_TRACKING_URI, MODEL_DIR
from src.utils.logger import logger


# Pydantic models for request/response
class PredictionRequest(BaseModel):
    """Single prediction request."""

    features: List[float] = Field(..., description="Feature values")
    feature_names: Optional[List[str]] = Field(None, description="Feature names")


class BatchPredictionRequest(BaseModel):
    """Batch prediction request."""

    features: List[List[float]] = Field(..., description="Feature matrix (n_samples × n_features)")
    feature_names: Optional[List[str]] = Field(None, description="Feature names")
    return_statistics: Optional[bool] = Field(True, description="Return prediction statistics")


class PredictionResponse(BaseModel):
    """Single prediction response."""

    prediction: float
    timestamp: str
    model_name: str
    version: int = 1


class BatchPredictionResponse(BaseModel):
    """Batch prediction response."""

    predictions: List[float]
    count: int
    statistics: Optional[Dict[str, float]] = None
    timestamp: str
    model_name: str
    version: int = 1


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    model_loaded: bool
    model_name: str
    timestamp: str


class ErrorResponse(BaseModel):
    """Error response."""

    error: str
    timestamp: str
    details: Optional[str] = None


# Initialize FastAPI app
app = FastAPI(
    title="Taxi Fare Prediction API",
    description="Production inference API for taxi fare prediction model",
    version="1.0.0",
)

# Global predictor and monitor
predictor: Optional[BatchPredictor] = None
monitor: Optional[PredictionMonitor] = None
request_count = 0
prediction_count = 0


@app.on_event("startup")
async def startup_event():
    """Initialize model on startup."""
    global predictor, monitor

    logger.info("[API] Starting inference server...")

    try:
        # Initialize predictor
        predictor = BatchPredictor(model_name="taxi-fare-xgboost", use_mlflow=True)

        # Load model
        if not predictor.load_production_model():
            logger.warning(
                "[API] Model loading returned False (may be expected with MLflow in dev mode)"
            )

        # Initialize monitor with baseline metrics
        baseline_metrics = {
            "mean_prediction": 13.2,  # From Day 5 tuned model
            "std_prediction": 8.5,
        }
        monitor = PredictionMonitor(baseline_metrics=baseline_metrics)

        logger.info("[API] ✅ Server startup complete")

    except Exception as e:
        logger.error(f"[API] Error during startup: {e}")
        raise


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("[API] Shutting down inference server...")
    logger.info(f"[API] Total requests: {request_count}")
    logger.info(f"[API] Total predictions: {prediction_count}")


@app.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns:
        HealthResponse with model status
    """
    global request_count
    request_count += 1

    return HealthResponse(
        status="healthy",
        model_loaded=predictor is not None and predictor.model is not None,
        model_name="taxi-fare-xgboost",
        timestamp=datetime.now().isoformat(),
    )


@app.get("/info")
async def get_info() -> Dict[str, Any]:
    """
    Get API information.

    Returns:
        API info dict
    """
    return {
        "name": "Taxi Fare Prediction API",
        "version": "1.0.0",
        "model_name": "taxi-fare-xgboost",
        "endpoints": [
            "/health - Health check",
            "/predict - Single prediction",
            "/predict/batch - Batch predictions",
            "/metrics - Monitoring metrics",
        ],
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/predict", response_model=PredictionResponse)
async def predict_single(request: PredictionRequest) -> PredictionResponse:
    """
    Make a single prediction.

    Args:
        request: Prediction request with features

    Returns:
        PredictionResponse with prediction

    Raises:
        HTTPException: If model not loaded or prediction fails
    """
    global request_count, prediction_count
    request_count += 1

    try:
        if predictor is None or predictor.model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")

        # Convert to DataFrame
        feature_names = request.feature_names or [
            f"feature_{i}" for i in range(len(request.features))
        ]
        X = pd.DataFrame([request.features], columns=feature_names)

        # Make prediction
        prediction = predictor.model.predict(X)[0]
        prediction_count += 1

        logger.info(f"[API] Prediction: {prediction:.2f}")

        return PredictionResponse(
            prediction=float(prediction),
            timestamp=datetime.now().isoformat(),
            model_name="taxi-fare-xgboost",
            version=1,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/predict/batch", response_model=BatchPredictionResponse)
async def predict_batch(request: BatchPredictionRequest) -> BatchPredictionResponse:
    """
    Make batch predictions.

    Args:
        request: Batch prediction request with features

    Returns:
        BatchPredictionResponse with predictions

    Raises:
        HTTPException: If model not loaded or prediction fails
    """
    global request_count, prediction_count
    request_count += 1

    try:
        if predictor is None or predictor.model is None:
            raise HTTPException(status_code=503, detail="Model not loaded")

        # Handle empty features
        if not request.features:
            raise HTTPException(status_code=400, detail="No features provided")

        # Convert to DataFrame
        feature_names = request.feature_names or [
            f"feature_{i}" for i in range(len(request.features[0]))
        ]
        X = pd.DataFrame(request.features, columns=feature_names)

        # Make predictions
        predictions, metrics = predictor.predict_batch(X, return_metrics=True)
        prediction_count += len(predictions)

        # Get statistics
        stats = None
        if request.return_statistics:
            stats = predictor.get_prediction_statistics()

        logger.info(f"[API] Batch prediction: {len(predictions)} samples")

        return BatchPredictionResponse(
            predictions=predictions.tolist(),
            count=len(predictions),
            statistics=stats,
            timestamp=datetime.now().isoformat(),
            model_name="taxi-fare-xgboost",
            version=1,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Batch prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/metrics")
async def get_metrics() -> Dict[str, Any]:
    """
    Get monitoring metrics.

    Returns:
        Metrics dict
    """
    stats = predictor.get_prediction_statistics() if predictor else {}
    alerts = monitor.get_alerts() if monitor else []

    return {
        "request_count": request_count,
        "prediction_count": prediction_count,
        "prediction_statistics": stats,
        "alerts": alerts,
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/monitoring/drift")
async def check_data_drift() -> Dict[str, Any]:
    """
    Check for data drift.

    Returns:
        Drift analysis
    """
    if monitor is None or predictor is None:
        raise HTTPException(status_code=503, detail="Monitor not initialized")

    try:
        stats = predictor.get_prediction_statistics()
        if not stats:
            raise HTTPException(status_code=400, detail="No predictions yet")

        drift = monitor.check_data_drift(stats)
        return drift

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[API] Drift check error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/monitoring/report")
async def save_monitoring_report() -> Dict[str, str]:
    """
    Save monitoring report.

    Returns:
        Report save status
    """
    if monitor is None:
        raise HTTPException(status_code=503, detail="Monitor not initialized")

    try:
        report_path = monitor.save_monitoring_report()
        logger.info(f"[API] Report saved to {report_path}")

        return {
            "status": "success",
            "path": str(report_path),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"[API] Report save error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status() -> Dict[str, Any]:
    """
    Get server status.

    Returns:
        Status information
    """
    return {
        "server": "running",
        "model_loaded": predictor is not None and predictor.model is not None,
        "model_name": "taxi-fare-xgboost",
        "requests_processed": request_count,
        "predictions_made": prediction_count,
        "alerts": monitor.get_alerts() if monitor else [],
        "timestamp": datetime.now().isoformat(),
    }


@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler."""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code,
            "timestamp": datetime.now().isoformat(),
        },
    )


def run_server(host: str = "127.0.0.1", port: int = 8000, reload: bool = True):
    """
    Run the FastAPI server.

    Args:
        host: Server host
        port: Server port
        reload: Enable auto-reload on code changes
    """
    logger.info(f"[API] Starting server on {host}:{port}")

    uvicorn.run(
        "src.deployment.inference_api:app", host=host, port=port, reload=reload, log_level="info"
    )


if __name__ == "__main__":
    run_server()
