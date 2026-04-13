# Monitoring API Example

"""
Example Flask API with complete monitoring instrumentation.
Shows how to integrate Prometheus, Jaeger, and structured logging.
"""

from flask import Flask, request, jsonify
from prometheus_client import generate_latest
import time

from monitoring import (
    setup_monitoring,
    track_latency,
    track_request,
    api_requests_total,
    api_request_duration_seconds,
    model_predictions_total,
    StructuredLogger
)


# Initialize Flask app
app = Flask(__name__)

# Setup monitoring
tracing, logger = setup_monitoring(
    app,
    service_name="taxi-fare-api",
    jaeger_host="jaeger",
    jaeger_port=6831
)

# Initialize logger
api_logger = StructuredLogger("taxi-fare-api")


# ============================================================================
# Health Check Endpoints
# ============================================================================

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint."""
    return jsonify({"status": "healthy"}), 200


@app.route("/ready", methods=["GET"])
def ready():
    """Readiness check endpoint."""
    # Check dependencies
    checks = {
        "database": check_database(),
        "mlflow": check_mlflow(),
        "elasticsearch": check_elasticsearch()
    }
    
    if all(checks.values()):
        return jsonify({"status": "ready", "checks": checks}), 200
    else:
        api_logger.warning(
            "readiness_check_failed",
            checks=checks
        )
        return jsonify({"status": "not_ready", "checks": checks}), 503


# ============================================================================
# API Endpoints with Monitoring
# ============================================================================

@app.route("/predict", methods=["POST"])
@track_request("predict")
def predict():
    """
    Prediction endpoint with full monitoring.
    
    Metrics tracked:
    - Request count (endpoint, method, status)
    - Request latency (endpoint, method)
    - Prediction count (status)
    - Request tracing
    """
    
    try:
        data = request.get_json()
        
        # Validate input
        if not data:
            api_logger.warning("predict_invalid_input", data=None)
            model_predictions_total.labels(
                model_name="taxi-fare",
                status="invalid_input"
            ).inc()
            return jsonify({"error": "No input data"}), 400
        
        api_logger.info(
            "predict_request",
            input_keys=list(data.keys()),
            endpoint="predict"
        )
        
        # Run prediction
        prediction = run_prediction(data)
        
        api_logger.info(
            "predict_success",
            prediction=prediction,
            endpoint="predict"
        )
        
        model_predictions_total.labels(
            model_name="taxi-fare",
            status="success"
        ).inc()
        
        return jsonify({"prediction": prediction}), 200
    
    except Exception as e:
        api_logger.error(
            "predict_error",
            error=str(e),
            endpoint="predict"
        )
        model_predictions_total.labels(
            model_name="taxi-fare",
            status="error"
        ).inc()
        return jsonify({"error": str(e)}), 500


@app.route("/batch-predict", methods=["POST"])
@track_request("batch_predict")
def batch_predict():
    """Batch prediction endpoint."""
    
    try:
        data = request.get_json()
        predictions = []
        
        for item in data.get("items", []):
            pred = run_prediction(item)
            predictions.append(pred)
        
        api_logger.info(
            "batch_predict_success",
            count=len(predictions)
        )
        
        model_predictions_total.labels(
            model_name="taxi-fare",
            status="success"
        ).inc(len(predictions))
        
        return jsonify({"predictions": predictions}), 200
    
    except Exception as e:
        api_logger.error(
            "batch_predict_error",
            error=str(e)
        )
        model_predictions_total.labels(
            model_name="taxi-fare",
            status="error"
        ).inc()
        return jsonify({"error": str(e)}), 500


@app.route("/metrics", methods=["GET"])
def metrics():
    """Prometheus metrics endpoint."""
    from monitoring import get_metrics_registry
    registry = get_metrics_registry()
    return generate_latest(registry.registry), 200


# ============================================================================
# Helper Functions
# ============================================================================

@track_latency("model_inference")
def run_prediction(input_data: dict) -> dict:
    """
    Run model prediction with latency tracking.
    
    Args:
        input_data: Input features for prediction
        
    Returns:
        Prediction result
    """
    
    # Simulate model inference
    time.sleep(0.1)  # Simulate latency
    
    return {
        "prediction": 42.5,
        "confidence": 0.95,
        "model_version": "1.0.0"
    }


def check_database() -> bool:
    """Check database connectivity."""
    try:
        # Implement actual check
        return True
    except Exception:
        return False


def check_mlflow() -> bool:
    """Check MLflow connectivity."""
    try:
        # Implement actual check
        return True
    except Exception:
        return False


def check_elasticsearch() -> bool:
    """Check Elasticsearch connectivity."""
    try:
        # Implement actual check
        return True
    except Exception:
        return False


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    api_logger.warning("not_found", path=request.path)
    api_requests_total.labels(
        endpoint="unknown",
        method=request.method,
        status="404"
    ).inc()
    return jsonify({"error": "Not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    api_logger.error("internal_error", error=str(error))
    api_requests_total.labels(
        endpoint="unknown",
        method=request.method,
        status="500"
    ).inc()
    return jsonify({"error": "Internal server error"}), 500


# ============================================================================
# Main
# ============================================================================

if __name__ == "__main__":
    api_logger.info("starting_api_server", port=5000)
    app.run(host="0.0.0.0", port=5000, debug=False)
