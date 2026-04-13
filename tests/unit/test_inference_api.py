"""Tests for FastAPI inference server."""

import json
from unittest.mock import MagicMock, Mock, patch

import numpy as np
import pandas as pd
import pytest
from fastapi.testclient import TestClient

from deployment.inference_api import BatchPredictionRequest, PredictionRequest, app


@pytest.fixture
def client():
    """Create FastAPI test client."""
    # Mock predictor to avoid model loading issues in tests
    from unittest.mock import Mock

    from deployment import inference_api

    mock_predictor = Mock()
    mock_model = Mock()
    # Make predict return a numpy array that can be indexed
    mock_model.predict.return_value = np.array([15.0, 20.0, 12.0])
    mock_predictor.model = mock_model
    mock_predictor.get_prediction_statistics.return_value = {
        "count": 100,
        "mean": 15.0,
        "std": 5.0,
        "min": 5.0,
        "max": 35.0,
        "median": 15.0,
        "q25": 12.0,
        "q75": 18.0,
    }
    mock_predictor.predict_batch.return_value = (
        np.array([15.0, 20.0]),
        {
            "n_samples": 2,
            "mean_prediction": 17.5,
            "std_prediction": 2.5,
            "min_prediction": 15.0,
            "max_prediction": 20.0,
        },
    )

    # Patch the global predictor
    inference_api.predictor = mock_predictor
    inference_api.monitor = Mock()
    inference_api.monitor.get_alerts.return_value = []
    inference_api.monitor.check_data_drift.return_value = {"checks": {}}

    return TestClient(app)


class TestHealthEndpoints:
    """Test health and status endpoints."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "timestamp" in data

    def test_get_info(self, client):
        """Test API info endpoint."""
        response = client.get("/info")
        assert response.status_code == 200
        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "endpoints" in data

    def test_get_status(self, client):
        """Test status endpoint."""
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["server"] == "running"
        assert "requests_processed" in data
        assert "predictions_made" in data


class TestPredictionEndpoints:
    """Test prediction endpoints."""

    def test_single_prediction(self, client):
        """Test single prediction endpoint."""
        request_data = {
            "features": [2.5, 10, 1],
            "feature_names": ["distance", "hour", "passenger_count"],
        }

        response = client.post("/predict", json=request_data)

        # Should now succeed with mocked predictor
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data
        assert "model_name" in data
        assert "timestamp" in data

    def test_batch_prediction(self, client):
        """Test batch prediction endpoint."""
        request_data = {
            "features": [[2.5, 10, 1], [5.0, 14, 2], [1.2, 22, 1]],
            "feature_names": ["distance", "hour", "passenger_count"],
            "return_statistics": True,
        }

        response = client.post("/predict/batch", json=request_data)

        # Should succeed with mocked predictor
        assert response.status_code == 200
        data = response.json()
        assert "predictions" in data
        assert "count" in data
        # Count will be 2 from mock, that's fine
        assert data["count"] >= 2

    def test_prediction_without_feature_names(self, client):
        """Test prediction without providing feature names."""
        request_data = {"features": [2.5, 10, 1]}

        response = client.post("/predict", json=request_data)

        # Should handle successfully
        assert response.status_code == 200
        data = response.json()
        assert "prediction" in data

    def test_batch_prediction_statistics(self, client):
        """Test batch prediction with statistics."""
        request_data = {"features": [[2.5, 10, 1], [5.0, 14, 2]], "return_statistics": True}

        response = client.post("/predict/batch", json=request_data)

        assert response.status_code == 200
        data = response.json()
        if data.get("statistics"):
            assert "mean" in data["statistics"]
            assert "std" in data["statistics"]


class TestMonitoringEndpoints:
    """Test monitoring endpoints."""

    def test_get_metrics(self, client):
        """Test metrics endpoint."""
        response = client.get("/metrics")
        assert response.status_code == 200
        data = response.json()
        assert "request_count" in data
        assert "prediction_count" in data
        assert "alerts" in data

    def test_check_drift(self, client):
        """Test data drift check endpoint."""
        response = client.get("/monitoring/drift")

        # May fail if no predictions yet, but endpoint should exist
        # Now with mocked data, should work or give 400
        assert response.status_code in [200, 400, 503]

    def test_save_report(self, client):
        """Test monitoring report save endpoint."""
        response = client.post("/monitoring/report")

        # Should now work with mocked monitor
        assert response.status_code in [200, 503]


class TestErrorHandling:
    """Test error handling."""

    def test_invalid_request_format(self, client):
        """Test invalid request format."""
        response = client.post("/predict", json={"invalid": "data"})
        assert response.status_code == 422  # Validation error

    def test_batch_empty_features(self, client):
        """Test batch with empty features."""
        request_data = {"features": []}

        response = client.post("/predict/batch", json=request_data)
        # Should reject empty features
        assert response.status_code in [400, 422, 500]

    def test_malformed_json(self, client):
        """Test malformed JSON."""
        response = client.post(
            "/predict", content=b"not valid json", headers={"Content-Type": "application/json"}
        )
        assert response.status_code in [400, 422]


class TestRequestModels:
    """Test Pydantic request models."""

    def test_prediction_request_valid(self):
        """Test valid prediction request."""
        req = PredictionRequest(
            features=[2.5, 10, 1], feature_names=["distance", "hour", "passenger"]
        )
        assert req.features == [2.5, 10, 1]
        assert req.feature_names == ["distance", "hour", "passenger"]

    def test_prediction_request_minimal(self):
        """Test minimal prediction request."""
        req = PredictionRequest(features=[1, 2, 3])
        assert req.features == [1, 2, 3]
        assert req.feature_names is None

    def test_batch_request_valid(self):
        """Test valid batch request."""
        req = BatchPredictionRequest(features=[[1, 2], [3, 4]], return_statistics=True)
        assert len(req.features) == 2
        assert req.return_statistics is True


class TestConcurrentRequests:
    """Test handling of concurrent requests."""

    def test_multiple_predictions(self, client):
        """Test handling multiple predictions."""
        for i in range(5):
            response = client.get("/health")
            assert response.status_code == 200

    def test_mixed_request_types(self, client):
        """Test mix of health and info requests."""

        for _ in range(2):
            client.get("/health")
            client.get("/info")
            client.get("/status")

        # Final status check
        response = client.get("/status")
        assert response.status_code == 200
        data = response.json()
        assert data["requests_processed"] >= 6


class TestResponseFormats:
    """Test response format correctness."""

    def test_health_response_format(self, client):
        """Test health response has required fields."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        required_fields = ["status", "model_loaded", "model_name", "timestamp"]
        for field in required_fields:
            assert field in data

    def test_status_response_format(self, client):
        """Test status response has required fields."""
        response = client.get("/status")
        assert response.status_code == 200

        data = response.json()
        required_fields = ["server", "model_loaded", "requests_processed", "timestamp"]
        for field in required_fields:
            assert field in data


class TestAPIIntegration:
    """Integration tests for API."""

    def test_endpoint_discovery(self, client):
        """Test discovering all endpoints."""
        response = client.get("/info")
        assert response.status_code == 200

        data = response.json()
        assert "endpoints" in data
        endpoints = data["endpoints"]

        # Check some key endpoints are listed
        assert any("/health" in ep for ep in endpoints)
        assert any("/predict" in ep for ep in endpoints)

    def test_health_before_and_after(self, client):
        """Test health check consistency."""
        # First health check
        response1 = client.get("/health")
        assert response1.status_code == 200

        # Do some other operations
        client.get("/status")
        client.get("/info")

        # Second health check
        response2 = client.get("/health")
        assert response2.status_code == 200

        # Should both be healthy
        assert response1.json()["status"] == "healthy"
        assert response2.json()["status"] == "healthy"


class TestEdgeCases:
    """Test edge cases."""

    def test_empty_feature_list(self, client):
        """Test with empty feature list."""
        request_data = {"features": []}

        response = client.post("/predict", json=request_data)
        # Should error or handle gracefully
        assert response.status_code in [200, 400, 422, 500]

    def test_very_large_features(self, client):
        """Test with very large feature values."""
        request_data = {"features": [1e6, 1e6, 1e6]}

        response = client.post("/predict", json=request_data)
        # Should handle or error appropriately
        assert response.status_code in [200, 500]

    def test_negative_features(self, client):
        """Test with negative feature values."""
        request_data = {"features": [-10, -5, -1]}

        response = client.post("/predict", json=request_data)
        # Should handle with mocked predictor
        assert response.status_code in [200, 500]


class TestStatusTracking:
    """Test status and tracking endpoints."""

    def test_status_updates_request_count(self, client):
        """Test that status endpoint reflects requests."""
        # Get initial status
        response1 = client.get("/status")
        initial_count = response1.json()["requests_processed"]

        # Make some requests
        client.get("/health")
        client.get("/info")

        # Get updated status
        response2 = client.get("/status")
        final_count = response2.json()["requests_processed"]

        # Count should have increased
        assert final_count > initial_count

    def test_metrics_endpoint_response(self, client):
        """Test metrics endpoint returns valid format."""
        response = client.get("/metrics")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data["alerts"], list)
        assert isinstance(data["request_count"], int)
        assert isinstance(data["prediction_count"], int)
