"""Tests for Model Registry functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from deployment.model_registry import ModelRegistry, setup_production_models


class TestModelRegistry:
    """Test ModelRegistry class."""

    @pytest.fixture
    def registry(self):
        """Create a ModelRegistry instance for testing."""
        return ModelRegistry(use_mlflow=False)

    def test_initialization(self):
        """Test ModelRegistry initialization."""
        registry = ModelRegistry(use_mlflow=False)
        assert registry.use_mlflow is False
        assert registry.registered_models == {}
        assert registry.model_versions == {}

    def test_register_model_without_mlflow(self, registry):
        """Test model registration without MLflow."""
        result = registry.register_model(
            model_name="test-model", model_uri="runs:/123/model", description="Test model"
        )
        assert result == {}

    @patch("deployment.model_registry.mlflow")
    def test_register_model_with_mlflow(self, mock_mlflow):
        """Test model registration with MLflow."""
        registry = ModelRegistry(use_mlflow=True)

        # Mock MLflow registration
        mock_version = Mock()
        mock_version.version = 1
        mock_mlflow.register_model.return_value = mock_version

        result = registry.register_model(
            model_name="taxi-fare-xgboost",
            model_uri="runs:/123/model",
            description="XGBoost model",
            metadata={"r2": 0.90},
        )

        assert result["model_name"] == "taxi-fare-xgboost"
        assert result["version"] == 1
        assert result["description"] == "XGBoost model"
        assert result["metadata"] == {"r2": 0.90}
        mock_mlflow.register_model.assert_called_once()

    def test_set_model_alias_without_mlflow(self, registry):
        """Test alias setting without MLflow."""
        result = registry.set_model_alias("test-model", "production", 1)
        assert result == {}

    @patch("deployment.model_registry.mlflow.tracking.MlflowClient")
    def test_set_model_alias_with_mlflow(self, mock_client_class):
        """Test alias setting with MLflow."""
        registry = ModelRegistry(use_mlflow=True)
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        result = registry.set_model_alias("taxi-fare-xgboost", "production", 1)

        assert result["model_name"] == "taxi-fare-xgboost"
        assert result["alias"] == "production"
        assert result["version"] == 1
        mock_client.set_registered_model_alias.assert_called_once_with(
            "taxi-fare-xgboost", "production", 1
        )

    @patch("deployment.model_registry.mlflow.tracking.MlflowClient")
    def test_transition_stage_valid(self, mock_client_class):
        """Test stage transition with valid stage."""
        registry = ModelRegistry(use_mlflow=True)
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        result = registry.transition_stage("taxi-fare-xgboost", 1, "Production")

        assert result["model_name"] == "taxi-fare-xgboost"
        assert result["version"] == 1
        assert result["stage"] == "Production"
        mock_client.transition_model_version_stage.assert_called_once_with(
            "taxi-fare-xgboost", 1, "Production"
        )

    def test_transition_stage_invalid(self, registry):
        """Test stage transition with invalid stage."""
        with pytest.raises(ValueError):
            registry.transition_stage("test-model", 1, "InvalidStage")

    @patch("deployment.model_registry.mlflow.tracking.MlflowClient")
    def test_update_model_description(self, mock_client_class):
        """Test updating model description."""
        registry = ModelRegistry(use_mlflow=True)
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        result = registry.update_model_description(
            "taxi-fare-xgboost", "Updated XGBoost model for production"
        )

        assert result["model_name"] == "taxi-fare-xgboost"
        assert result["description"] == "Updated XGBoost model for production"
        mock_client.update_registered_model.assert_called_once()

    @patch("deployment.model_registry.mlflow.tracking.MlflowClient")
    def test_get_model_info(self, mock_client_class):
        """Test retrieving model information."""
        registry = ModelRegistry(use_mlflow=True)
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock model response
        mock_version = Mock()
        mock_version.version = 1
        mock_version.current_stage = "Production"
        mock_version.run_id = "run_123"
        mock_version.source = "models:/taxi-fare-xgboost"

        mock_model = Mock()
        mock_model.name = "taxi-fare-xgboost"
        mock_model.creation_timestamp = 1234567890
        mock_model.last_updated_timestamp = 1234567890
        mock_model.description = "XGBoost model"
        mock_model.latest_versions = [mock_version]

        mock_client.get_registered_model.return_value = mock_model

        result = registry.get_model_info("taxi-fare-xgboost")

        assert result["name"] == "taxi-fare-xgboost"
        assert result["description"] == "XGBoost model"
        assert len(result["latest_versions"]) == 1
        assert result["latest_versions"][0]["version"] == 1

    @patch("deployment.model_registry.mlflow.tracking.MlflowClient")
    def test_list_registered_models(self, mock_client_class):
        """Test listing registered models."""
        registry = ModelRegistry(use_mlflow=True)
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock models - set name attribute properly
        mock_model1 = Mock()
        mock_model1.name = "taxi-fare-xgboost"

        mock_model2 = Mock()
        mock_model2.name = "taxi-fare-lightgbm"

        mock_model3 = Mock()
        mock_model3.name = "taxi-fare-svm"

        mock_client.search_registered_models.return_value = [mock_model1, mock_model2, mock_model3]

        result = registry.list_registered_models()

        assert len(result) == 3
        assert "taxi-fare-xgboost" in result
        assert "taxi-fare-lightgbm" in result
        assert "taxi-fare-svm" in result

    @patch("deployment.model_registry.mlflow.tracking.MlflowClient")
    def test_get_production_model(self, mock_client_class):
        """Test retrieving production model."""
        registry = ModelRegistry(use_mlflow=True)
        mock_client = Mock()
        mock_client_class.return_value = mock_client

        # Mock production version
        mock_version = Mock()
        mock_version.version = 1
        mock_version.current_stage = "Production"
        mock_version.run_id = "run_123"
        mock_version.source = "models:/taxi-fare-xgboost"
        mock_version.creation_timestamp = 1234567890

        # Mock staging version
        mock_staging = Mock()
        mock_staging.version = 2
        mock_staging.current_stage = "Staging"

        mock_model = Mock()
        mock_model.name = "taxi-fare-xgboost"
        mock_model.latest_versions = [mock_version, mock_staging]

        mock_client.get_registered_model.return_value = mock_model

        result = registry.get_production_model("taxi-fare-xgboost")

        assert result["model_name"] == "taxi-fare-xgboost"
        assert result["version"] == 1
        assert result["stage"] == "Production"

    def test_save_registry_summary(self, registry):
        """Test saving registry summary."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "summary.json"

            # Add some models to registry
            registry.registered_models["taxi-fare-xgboost"] = {
                "model_name": "taxi-fare-xgboost",
                "version": 1,
            }
            registry.model_versions["taxi-fare-xgboost@v1"] = {
                "model_name": "taxi-fare-xgboost",
                "version": 1,
            }

            result_path = registry.save_registry_summary(output_path)

            assert result_path.exists()

            # Verify saved content
            with open(result_path, "r") as f:
                summary = json.load(f)

            assert summary["total_models"] == 1
            assert summary["total_versions"] == 1
            assert "taxi-fare-xgboost" in summary["registered_models"]


class TestSetupProductionModels:
    """Test setup_production_models function."""

    def test_setup_with_missing_tuning_results(self):
        """Test setup when tuning results are missing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            missing_path = Path(tmpdir) / "missing.json"
            result = setup_production_models(tuning_results_path=missing_path, use_mlflow=False)
            assert result == {}

    def test_setup_with_tuning_results(self):
        """Test setup with valid tuning results."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)

            # Create mock tuning results
            tuning_results = {
                "XGBoost": {
                    "tuned_r2": 0.9011,
                    "tuned_metrics": {"rmse": 2.5, "mae": 1.8},
                    "improvement_pct": 4.75,
                },
                "LightGBM": {
                    "tuned_r2": 0.8205,
                    "tuned_metrics": {"rmse": 3.2, "mae": 2.3},
                    "improvement_pct": -1.5,
                },
                "SVM": {
                    "tuned_r2": 0.7553,
                    "tuned_metrics": {"rmse": 3.8, "mae": 2.7},
                    "improvement_pct": -8.9,
                },
            }

            results_path = tmpdir / "tuning_comparison.json"
            with open(results_path, "w") as f:
                json.dump(tuning_results, f)

            # Patch MODEL_DIR for testing
            with patch("deployment.model_registry.MODEL_DIR", tmpdir):
                result = setup_production_models(tuning_results_path=results_path, use_mlflow=False)

            # Should not error even without MLflow
            assert isinstance(result, dict)


class TestIntegration:
    """Integration tests for Model Registry."""

    def test_workflow_without_mlflow(self):
        """Test complete workflow without MLflow."""
        registry = ModelRegistry(use_mlflow=False)

        # These should not raise errors
        registry.register_model("model1", "uri1")
        registry.set_model_alias("model1", "production", 1)
        registry.transition_stage("model1", 1, "Production")
        registry.update_model_description("model1", "desc")
        registry.get_model_info("model1")
        registry.list_registered_models()
        registry.get_production_model("model1")

        # Should have empty models
        assert len(registry.registered_models) == 0
