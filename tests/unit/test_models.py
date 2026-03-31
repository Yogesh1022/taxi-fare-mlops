"""Unit tests for model utilities."""

import pandas as pd
import numpy as np
import pytest
from pathlib import Path
import joblib
import json

from src.models.train import (
    BaselineModelTrainer,
    train_baseline_models,
)


# Sample data fixtures
@pytest.fixture
def sample_train_data():
    """Create sample training data."""
    np.random.seed(42)
    n_samples = 100
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
def train_val_test_split(sample_train_data):
    """Split data into train/val/test."""
    X, y = sample_train_data
    
    n = len(X)
    train_idx = int(0.6 * n)
    val_idx = int(0.8 * n)
    
    X_train = X[:train_idx]
    X_val = X[train_idx:val_idx]
    X_test = X[val_idx:]
    
    y_train = y[:train_idx]
    y_val = y[train_idx:val_idx]
    y_test = y[val_idx:]
    
    return X_train, X_val, X_test, y_train, y_val, y_test


# Test BaselineModelTrainer
def test_trainer_initialization(train_val_test_split):
    """Test trainer initialization."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    trainer = BaselineModelTrainer(X_train, X_val, X_test, y_train, y_val, y_test)
    
    assert trainer.X_train.shape[0] == 60
    assert trainer.X_val.shape[0] == 20
    assert trainer.X_test.shape[0] == 20
    assert trainer.best_model is None
    assert trainer.best_model_name is None


def test_get_baseline_models():
    """Test that baseline models are created."""
    X_train, X_val, X_test, y_train, y_val, y_test = (
        pd.DataFrame(np.random.randn(60, 5)),
        pd.DataFrame(np.random.randn(20, 5)),
        pd.DataFrame(np.random.randn(20, 5)),
        pd.Series(np.random.randn(60)),
        pd.Series(np.random.randn(20)),
        pd.Series(np.random.randn(20)),
    )
    
    trainer = BaselineModelTrainer(X_train, X_val, X_test, y_train, y_val, y_test)
    models = trainer._get_baseline_models()
    
    # Should have at least 6 basic models (LinearRegression, Ridge, Lasso, ElasticNet, SVM, KNN)
    # XGBoost and LightGBM may or may not be available
    assert len(models) >= 6
    assert 'LinearRegression' in models
    assert 'Ridge' in models
    assert 'Lasso' in models
    assert 'SVM' in models
    assert 'KNN' in models


def test_compute_metrics():
    """Test metric computation."""
    X_train, X_val, X_test, y_train, y_val, y_test = (
        pd.DataFrame(np.random.randn(60, 5)),
        pd.DataFrame(np.random.randn(20, 5)),
        pd.DataFrame(np.random.randn(20, 5)),
        pd.Series(np.random.randn(60)),
        pd.Series(np.random.randn(20)),
        pd.Series(np.random.randn(20)),
    )
    
    trainer = BaselineModelTrainer(X_train, X_val, X_test, y_train, y_val, y_test)
    
    y_true = np.array([1, 2, 3, 4, 5])
    y_pred = np.array([1.1, 1.9, 3.2, 3.8, 5.1])
    
    metrics = trainer._compute_metrics(y_true, y_pred)
    
    assert 'r2_score' in metrics
    assert 'rmse' in metrics
    assert 'mae' in metrics
    assert 'mape' in metrics
    
    assert metrics['r2_score'] > 0.9  # Good predictions
    assert metrics['rmse'] < 1.0
    assert metrics['mae'] < 1.0


def test_train_single_model(train_val_test_split):
    """Test training a single model."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    trainer = BaselineModelTrainer(X_train, X_val, X_test, y_train, y_val, y_test)
    
    from sklearn.linear_model import LinearRegression
    model = LinearRegression()
    
    results = trainer.train_model('LinearRegression', model)
    
    assert results['status'] == 'success'
    assert results['model'] is not None
    assert 'train_metrics' in results
    assert 'val_metrics' in results
    assert 'test_metrics' in results
    assert 'r2_score' in results['test_metrics']
    assert 'rmse' in results['test_metrics']


def test_train_all_models(train_val_test_split):
    """Test training all baseline models."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    trainer = BaselineModelTrainer(X_train, X_val, X_test, y_train, y_val, y_test)
    results = trainer.train_all_models()
    
    assert len(results) >= 6  # At least 6 models
    assert trainer.best_model is not None
    assert trainer.best_model_name is not None
    
    # All successful results should have metrics
    for name, result in results.items():
        if result['status'] == 'success':
            assert 'test_metrics' in result
            assert result['test_metrics']['r2_score'] is not None


def test_get_leaderboard(train_val_test_split):
    """Test leaderboard generation."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    trainer = BaselineModelTrainer(X_train, X_val, X_test, y_train, y_val, y_test)
    trainer.train_all_models()
    leaderboard = trainer.get_leaderboard()
    
    assert isinstance(leaderboard, pd.DataFrame)
    assert len(leaderboard) > 0
    assert 'Model' in leaderboard.columns
    assert 'Test_R2' in leaderboard.columns or 'Status' in leaderboard.columns
    
    # Leaderboard should be sorted by Test_R2 if it exists
    if 'Test_R2' in leaderboard.columns:
        r2_values = leaderboard['Test_R2'].dropna()
        assert (r2_values == r2_values.sort_values(ascending=False)).all()


def test_save_results(train_val_test_split, tmp_path):
    """Test saving results."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    trainer = BaselineModelTrainer(X_train, X_val, X_test, y_train, y_val, y_test)
    trainer.train_all_models()
    trainer.save_results(output_dir=tmp_path)
    
    # Check that all expected files were created
    assert (tmp_path / "leaderboard.csv").exists()
    assert (tmp_path / "leaderboard.json").exists()
    assert (tmp_path / "best_baseline_model.pkl").exists()
    assert (tmp_path / "best_baseline_model_metadata.json").exists()
    assert (tmp_path / "baseline_training_results.json").exists()
    
    # Verify leaderboard CSV
    leaderboard_df = pd.read_csv(tmp_path / "leaderboard.csv")
    assert len(leaderboard_df) > 0
    
    # Verify best model metadata
    with open(tmp_path / "best_baseline_model_metadata.json") as f:
        metadata = json.load(f)
    assert 'name' in metadata
    assert 'metrics' in metadata
    assert metadata['name'] == trainer.best_model_name


def test_train_baseline_models_function(train_val_test_split, tmp_path):
    """Test the train_baseline_models convenience function."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    leaderboard, best_model = train_baseline_models(
        X_train, X_val, X_test, y_train, y_val, y_test,
        output_dir=tmp_path
    )
    
    assert isinstance(leaderboard, pd.DataFrame)
    assert len(leaderboard) > 0
    assert isinstance(best_model, str)
    assert best_model in leaderboard['Model'].values


def test_model_persistence(train_val_test_split, tmp_path):
    """Test that trained models can be loaded and used."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    trainer = BaselineModelTrainer(X_train, X_val, X_test, y_train, y_val, y_test)
    trainer.train_all_models()
    trainer.save_results(output_dir=tmp_path)
    
    # Load best model
    best_model_path = tmp_path / "best_baseline_model.pkl"
    loaded_model = joblib.load(best_model_path)
    
    # Make predictions
    y_pred = loaded_model.predict(X_test)
    
    assert len(y_pred) == len(y_test)
    assert y_pred.dtype == np.float64


def test_cross_model_comparison(train_val_test_split):
    """Test that models can be compared fairly."""
    X_train, X_val, X_test, y_train, y_val, y_test = train_val_test_split
    
    trainer = BaselineModelTrainer(X_train, X_val, X_test, y_train, y_val, y_test)
    trainer.train_all_models()
    leaderboard = trainer.get_leaderboard()
    
    # Leaderboard should have meaningful differences between models
    test_r2_values = leaderboard['Test_R2'].dropna()
    assert test_r2_values.max() > test_r2_values.min()
    
    # All R² values should be between -1 and 1
    assert (test_r2_values >= -1).all()
    assert (test_r2_values <= 1).all()

