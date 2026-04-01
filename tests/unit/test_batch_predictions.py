"""Tests for batch prediction functionality."""

import pytest
import json
import numpy as np
import pandas as pd
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.deployment.batch_predictions import (
    BatchPredictor, PredictionMonitor, run_batch_predictions
)


class TestBatchPredictor:
    """Test BatchPredictor class."""
    
    @pytest.fixture
    def predictor(self):
        """Create a BatchPredictor instance for testing."""
        return BatchPredictor(use_mlflow=False)
    
    @pytest.fixture
    def sample_data(self):
        """Create sample data for testing."""
        X = pd.DataFrame({
            'distance': [2.5, 5.0, 1.2, 3.8],
            'hour': [10, 14, 22, 8],
            'passenger_count': [1, 2, 1, 3]
        })
        y = np.array([12.5, 25.0, 8.0, 18.5])
        return X, y
    
    def test_initialization(self):
        """Test BatchPredictor initialization."""
        predictor = BatchPredictor(model_name="test-model", use_mlflow=False)
        assert predictor.model_name == "test-model"
        assert predictor.use_mlflow is False
        assert predictor.model is None
        assert len(predictor.predictions) == 0
    
    def test_load_without_mlflow(self, predictor):
        """Test loading model without MLflow."""
        result = predictor.load_production_model()
        assert result is False
    
    @patch('src.deployment.batch_predictions.mlflow')
    def test_load_with_mlflow(self, mock_mlflow):
        """Test loading model with MLflow."""
        predictor = BatchPredictor(use_mlflow=True)
        
        # Mock model
        mock_model = Mock()
        mock_mlflow.sklearn.load_model.return_value = mock_model
        
        result = predictor.load_production_model()
        assert result is True
        assert predictor.model is not None
    
    def test_predict_batch_without_model(self, predictor, sample_data):
        """Test batch prediction without loaded model."""
        X, _ = sample_data
        
        with pytest.raises(RuntimeError):
            predictor.predict_batch(X)
    
    def test_predict_batch_with_mock_model(self, predictor, sample_data):
        """Test batch prediction with mock model."""
        X, _ = sample_data
        
        # Mock model
        predictor.model = Mock()
        predictor.model.predict.return_value = np.array([12.5, 25.0, 8.0, 18.5])
        
        predictions, metrics = predictor.predict_batch(X)
        
        assert len(predictions) == 4
        assert metrics['n_samples'] == 4
        assert 'mean_prediction' in metrics
        assert 'std_prediction' in metrics
    
    def test_evaluate_predictions(self, predictor, sample_data):
        """Test prediction evaluation."""
        X, y = sample_data
        
        # Mock model
        predictor.model = Mock()
        predictor.model.predict.return_value = y
        
        # Make predictions
        predictions, _ = predictor.predict_batch(X)
        
        # Evaluate
        eval_metrics = predictor.evaluate_predictions(y)
        
        assert 'r2_score' in eval_metrics
        assert 'rmse' in eval_metrics
        assert 'mae' in eval_metrics
        assert 'mape' in eval_metrics
        assert eval_metrics['r2_score'] == 1.0  # Perfect predictions
    
    def test_evaluate_without_predictions(self, predictor):
        """Test evaluation without predictions."""
        y = np.array([1, 2, 3])
        
        with pytest.raises(RuntimeError):
            predictor.evaluate_predictions(y)
    
    def test_save_predictions(self, predictor, sample_data):
        """Test saving predictions."""
        X, y = sample_data
        predictor.model = Mock()
        predictor.model.predict.return_value = y
        
        predictor.predict_batch(X)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "predictions.json"
            result_path = predictor.save_predictions(y, output_path)
            
            assert result_path.exists()
            
            with open(result_path, 'r') as f:
                data = json.load(f)
            
            assert data['n_predictions'] == 4
            assert 'model_name' in data
            assert 'timestamp' in data
    
    def test_get_prediction_statistics(self, predictor, sample_data):
        """Test getting prediction statistics."""
        X, y = sample_data
        predictor.predictions = y
        
        stats = predictor.get_prediction_statistics()
        
        assert stats['count'] == 4
        assert 'mean' in stats
        assert 'median' in stats
        assert 'std' in stats
        assert 'min' in stats
        assert 'max' in stats


class TestPredictionMonitor:
    """Test PredictionMonitor class."""
    
    @pytest.fixture
    def monitor(self):
        """Create a PredictionMonitor instance."""
        baseline = {'mean_prediction': 15.0, 'std_prediction': 5.0}
        return PredictionMonitor(baseline_metrics=baseline)
    
    def test_initialization(self, monitor):
        """Test monitor initialization."""
        assert monitor.baseline_metrics == {'mean_prediction': 15.0, 'std_prediction': 5.0}
        assert len(monitor.prediction_history) == 0
        assert len(monitor.alerts) == 0
    
    def test_check_data_drift_no_alerts(self, monitor):
        """Test drift detection without exceeding threshold."""
        current_stats = {'mean_prediction': 15.2, 'std_prediction': 5.1}
        
        drift = monitor.check_data_drift(current_stats, threshold=0.1)
        
        assert 'checks' in drift
        assert len(monitor.alerts) == 0
    
    def test_check_data_drift_with_alerts(self, monitor):
        """Test drift detection with threshold exceeded."""
        current_stats = {'mean_prediction': 18.0, 'std_prediction': 5.0}
        
        drift = monitor.check_data_drift(current_stats, threshold=0.1)
        
        assert 'checks' in drift
        assert len(monitor.alerts) > 0
        assert 'Data drift detected' in monitor.alerts[0]
    
    def test_check_performance_degradation_no_alerts(self, monitor):
        """Test performance check without degradation."""
        current_metrics = {'r2_score': 0.95}
        monitor.baseline_metrics['r2_score'] = 0.90
        
        degradation = monitor.check_performance_degradation(current_metrics, threshold=0.95)
        
        assert 'r2_ratio' in degradation
        assert len(monitor.alerts) == 0
    
    def test_check_performance_degradation_with_alerts(self, monitor):
        """Test performance degradation alert."""
        current_metrics = {'r2_score': 0.80}
        monitor.baseline_metrics['r2_score'] = 0.90
        
        degradation = monitor.check_performance_degradation(current_metrics, threshold=0.95)
        
        assert degradation['degraded'] is True
        assert len(monitor.alerts) > 0
        assert 'Performance degradation' in monitor.alerts[0]
    
    def test_get_alerts(self, monitor):
        """Test retrieving alerts."""
        monitor.alerts = ["Alert 1", "Alert 2"]
        
        alerts = monitor.get_alerts()
        assert len(alerts) == 2
        assert "Alert 1" in alerts
    
    def test_save_monitoring_report(self, monitor):
        """Test saving monitoring report."""
        monitor.alerts = ["Test alert"]
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "report.json"
            result_path = monitor.save_monitoring_report(output_path)
            
            assert result_path.exists()
            
            with open(result_path, 'r') as f:
                report = json.load(f)
            
            assert 'alerts' in report
            assert report['alerts'] == ["Test alert"]


class TestBatchPredictionIntegration:
    """Integration tests for batch predictions."""
    
    def test_end_to_end_workflow(self):
        """Test complete batch prediction workflow."""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir = Path(tmpdir)
            
            # Create sample data
            data = pd.DataFrame({
                'distance': [2.5, 5.0, 1.2],
                'hour': [10, 14, 22],
                'passenger_count': [1, 2, 1]
            })
            data_path = tmpdir / "test_data.csv"
            data.to_csv(data_path, index=False)
            
            # Create predictor with mock model
            predictor = BatchPredictor(use_mlflow=False)
            predictor.model = Mock()
            predictor.model.predict.return_value = np.array([12.5, 25.0, 8.0])
            
            # Make predictions
            predictions, metrics = predictor.predict_batch(data)
            
            # Evaluate
            y_true = np.array([12.5, 25.0, 8.0])
            eval_metrics = predictor.evaluate_predictions(y_true)
            
            assert len(predictions) == 3
            assert eval_metrics['r2_score'] == 1.0
            
            # Save
            pred_path = tmpdir / "predictions.json"
            predictor.save_predictions(predictions, pred_path)
            
            assert pred_path.exists()


class TestBatchPredictionEdgeCases:
    """Test edge cases for batch predictions."""
    
    def test_empty_predictions(self):
        """Test with empty prediction array."""
        predictor = BatchPredictor(use_mlflow=False)
        predictor.predictions = np.array([])
        
        stats = predictor.get_prediction_statistics()
        assert stats == {}
    
    def test_single_sample_prediction(self):
        """Test with single sample."""
        predictor = BatchPredictor(use_mlflow=False)
        predictor.model = Mock()
        predictor.model.predict.return_value = np.array([15.0])
        
        X = pd.DataFrame({'a': [1]})
        predictions, metrics = predictor.predict_batch(X)
        
        assert len(predictions) == 1
        assert metrics['n_samples'] == 1
    
    def test_large_batch_prediction(self):
        """Test with large batch."""
        predictor = BatchPredictor(use_mlflow=False)
        predictor.model = Mock()
        
        n = 10000
        pred_values = np.random.normal(15, 5, n)
        predictor.model.predict.return_value = pred_values
        
        X = pd.DataFrame({'a': range(n)})
        predictions, metrics = predictor.predict_batch(X)
        
        assert len(predictions) == n
        assert metrics['n_samples'] == n


class TestIntegrationWithMLflow:
    """Test MLflow integration."""
    
    @patch('src.deployment.batch_predictions.mlflow')
    def test_log_to_mlflow(self, mock_mlflow):
        """Test logging to MLflow."""
        predictor = BatchPredictor(use_mlflow=True)
        
        mock_run = Mock()
        mock_run.info.run_id = "test_run_123"
        mock_mlflow.start_run.return_value.__enter__.return_value = mock_run
        mock_mlflow.active_run.return_value = mock_run
        
        metrics = {'n_samples': 100, 'mean_prediction': 15.0}
        predictions = np.array([15.0] * 100)
        
        run_id = predictor.log_to_mlflow(metrics, predictions)
        
        assert run_id == "test_run_123"
        mock_mlflow.start_run.assert_called_once()
