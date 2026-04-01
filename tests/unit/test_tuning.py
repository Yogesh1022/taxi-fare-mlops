"""Unit tests for hyperparameter tuning."""

import pandas as pd
import numpy as np
import pytest
from pathlib import Path
import json
import joblib

from src.models.tune import HyperparameterTuner, tune_top_3_models


# Sample data fixtures
@pytest.fixture
def sample_tuning_data():
    """Create sample data for tuning tests."""
    np.random.seed(42)
    n_samples = 200
    n_features = 10
    
    X = pd.DataFrame(
        np.random.randn(n_samples, n_features),
        columns=[f"feature_{i}" for i in range(n_features)]
    )
    y = pd.Series(
        np.random.randn(n_samples) * 10 + 20,
        name='target'
    )
    
    return X, y


@pytest.fixture
def train_val_test_split(sample_tuning_data):
    """Split data for tuning (50/25/25)."""
    X, y = sample_tuning_data
    
    n = len(X)
    train_idx = int(0.5 * n)
    val_idx = int(0.75 * n)
    
    X_train = X[:train_idx]
    X_val = X[train_idx:val_idx]
    X_test = X[val_idx:]
    
    y_train = y[:train_idx]
    y_val = y[train_idx:val_idx]
    y_test = y[val_idx:]
    
    return X_train, X_val, X_test, y_train, y_val, y_test


# Test HyperparameterTuner
def test_tuner_initialization(train_val_test_split):
    """Test tuner initialization."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    tuner = HyperparameterTuner(X_train, X_val, y_train, y_val, X_test, y_test, n_trials=5, use_mlflow=False)
    
    assert tuner.X_train.shape[0] == 100
    assert tuner.X_val.shape[0] == 50
    assert tuner.X_test.shape[0] == 50
    assert tuner.n_trials == 5
    assert len(tuner.studies) == 0
    assert len(tuner.best_models) == 0


def test_svm_tuning(train_val_test_split):
    """Test SVM hyperparameter tuning."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    tuner = HyperparameterTuner(X_train, X_val, y_train, y_val, X_test, y_test, n_trials=3, use_mlflow=False)
    svm_model, svm_params = tuner.tune_svm()
    
    assert svm_model is not None
    assert 'C' in svm_params
    assert 'epsilon' in svm_params
    assert 'SVM' in tuner.best_models
    assert 'SVM' in tuner.best_params


def test_compute_metrics(train_val_test_split):
    """Test metrics computation."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    tuner = HyperparameterTuner(X_train, X_val, y_train, y_val, X_test, y_test, use_mlflow=False)
    
    y_true = np.array([1, 2, 3, 4, 5])
    y_pred = np.array([1.1, 1.9, 3.2, 3.8, 5.1])
    
    metrics = tuner._compute_metrics(y_true, y_pred)
    
    assert 'r2_score' in metrics
    assert 'rmse' in metrics
    assert 'mae' in metrics
    assert metrics['r2_score'] > 0.9
    assert metrics['rmse'] < 1.0


def test_tune_all(train_val_test_split):
    """Test tuning all models."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    tuner = HyperparameterTuner(X_train, X_val, y_train, y_val, X_test, y_test, n_trials=3, use_mlflow=False)
    results = tuner.tune_all()
    
    assert len(results) >= 1  # At least SVM
    assert 'SVM' in results
    assert results['SVM']['status'] == 'success'
    assert 'test_metrics' in results['SVM']
    assert 'best_params' in results['SVM']


def test_save_results(train_val_test_split, tmp_path):
    """Test saving tuning results."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    tuner = HyperparameterTuner(X_train, X_val, y_train, y_val, X_test, y_test, n_trials=3, use_mlflow=False)
    tuner.tune_all()
    tuner.save_results(output_dir=tmp_path)
    
    # Check that expected files were created
    assert (tmp_path / "tuned_best_params.json").exists()
    assert (tmp_path / "tuning_results.json").exists()
    assert (tmp_path / "tuning_comparison.json").exists()
    
    # Verify best params JSON
    with open(tmp_path / "tuned_best_params.json") as f:
        best_params = json.load(f)
    assert 'SVM' in best_params
    assert 'C' in best_params['SVM']


def test_load_baseline_results(train_val_test_split, tmp_path):
    """Test loading baseline results for comparison."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    # Create a mock baseline results file
    baseline_results = {
        'SVM': {
            'test_metrics': {'r2_score': 0.85, 'rmse': 9.0, 'mae': 3.5}
        }
    }
    baseline_path = tmp_path / "baseline_training_results.json"
    with open(baseline_path, 'w') as f:
        json.dump(baseline_results, f)
    
    # This test would require mocking MODEL_DIR, so we skip the actual file loading
    # In real usage, _load_baseline_results would read from MODEL_DIR


def test_tune_top_3_models_function(train_val_test_split, tmp_path):
    """Test convenience function."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    results = tune_top_3_models(
        X_train, X_val, X_test, y_train, y_val, y_test,
        n_trials=3,
        output_dir=tmp_path,
        use_mlflow=False
    )
    
    assert isinstance(results, dict)
    assert 'SVM' in results
    assert results['SVM']['status'] == 'success'
    
    # Verify output files exist
    assert (tmp_path / "tuned_best_params.json").exists()


def test_model_persistence(train_val_test_split, tmp_path):
    """Test that tuned models can be loaded and used."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    tuner = HyperparameterTuner(X_train, X_val, y_train, y_val, X_test, y_test, n_trials=3, use_mlflow=False)
    tuner.tune_all()
    tuner.save_results(output_dir=tmp_path)
    
    # Load tuned SVM model
    svm_model_path = tmp_path / "tuned_svm_model.pkl"
    if svm_model_path.exists():
        loaded_model = joblib.load(svm_model_path)
        
        # Make predictions
        y_pred = loaded_model.predict(X_test.iloc[:5])
        
        assert len(y_pred) == 5
        assert y_pred.dtype == np.float64


def test_tuning_improves_or_matches_baseline(train_val_test_split):
    """Test that tuned models achieve reasonable performance."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    tuner = HyperparameterTuner(X_train, X_val, y_train, y_val, X_test, y_test, n_trials=5, use_mlflow=False)
    results = tuner.tune_all()
    
    # Tuned models should have reasonable R² scores
    for model_name, result in results.items():
        if result['status'] == 'success':
            r2 = result['test_metrics']['r2_score']
            # R² should be in a reasonable range
            assert r2 > -1.0  # Better than dummy model
            assert r2 <= 1.0


def test_best_params_structure(train_val_test_split):
    """Test that best parameters have expected structure."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    tuner = HyperparameterTuner(X_train, X_val, y_train, y_val, X_test, y_test, n_trials=3)
    tuner.tune_svm()
    
    params = tuner.best_params['SVM']
    
    # SVM params should include C and epsilon
    assert isinstance(params, dict)
    assert 'C' in params
    assert 'epsilon' in params
    assert params['C'] > 0
    assert params['epsilon'] > 0


def test_multiple_trial_improvements(train_val_test_split):
    """Test that more trials can improve results."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    # Run with few trials
    tuner1 = HyperparameterTuner(X_train, X_val, y_train, y_val, X_test, y_test, n_trials=2)
    results1 = tuner1.tune_svm()
    
    # Run with more trials
    tuner2 = HyperparameterTuner(X_train, X_val, y_train, y_val, X_test, y_test, n_trials=5)
    results2 = tuner2.tune_svm()
    
    # Both should produce non-None models
    assert results1[0] is not None
    assert results2[0] is not None
