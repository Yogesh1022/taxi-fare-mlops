"""Unit tests for feature engineering."""

import pandas as pd
import numpy as np
import pytest
from datetime import datetime, timedelta

from src.features.transformers import (
    DatetimeFeatureExtractor,
    TripDurationCalculator,
    SpeedCalculator,
    FareComponentAggregator,
    LocationDistanceCalculator,
    CategoricalEncoder,
    NumericalScaler
)
from src.features.pipeline import (
    build_feature_pipeline,
    fit_and_save_pipeline,
    load_pipeline,
    transform_features,
)


# Sample data fixtures
@pytest.fixture
def sample_taxi_data():
    """Create sample taxi data for testing."""
    base_time = datetime(2024, 1, 15, 10, 0, 0)
    
    return pd.DataFrame({
        'tpep_pickup_datetime': [base_time + timedelta(hours=i) for i in range(10)],
        'tpep_dropoff_datetime': [base_time + timedelta(hours=i, minutes=30) for i in range(10)],
        'passenger_count': [1, 2, 1, 3, 1, 2, 1, 4, 1, 2],
        'trip_distance': [2.5, 5.0, 1.5, 8.0, 3.0, 6.0, 1.2, 10.0, 2.8, 4.5],
        'extra': [0, 0.5, 0, 1, 0, 0.5, 0, 1, 0, 0.5],
        'tip_amount': [0.5, 1.0, 0.25, 2.0, 0.5, 1.5, 0.25, 2.5, 0.5, 1.0],
        'tolls_amount': [0, 0, 5.76, 0, 0, 0, 0, 6.50, 0, 0],
        'improvement_surcharge': [0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3, 0.3],
        'congestion_surcharge': [2.5, 2.5, 0, 2.5, 2.5, 2.5, 0, 2.5, 2.5, 2.5],
        'Airport_fee': [0, 0, 0, 0, 0, 0, 0, 2.5, 0, 0],
        'store_and_fwd_flag': ['N', 'N', 'Y', 'N', 'N', 'Y', 'N', 'N', 'N', 'N'],
        'payment_type': ['Credit Card', 'Credit Card', 'Cash', 'Credit Card', 'Credit Card',
                        'Cash', 'Credit Card', 'Credit Card', 'Credit Card', 'Cash'],
        'RatecodeID': [1, 1, 2, 1, 1, 2, 1, 3, 1, 1],
        'PULocationID': [10, 20, 30, 10, 40, 50, 10, 60, 20, 30],
        'DOLocationID': [20, 30, 30, 40, 50, 50, 15, 70, 40, 40],
        'VendorID': [1, 2, 1, 2, 1, 2, 1, 2, 1, 2],
        'total_amount': [10.5, 15.0, 8.75, 20.0, 12.5, 18.0, 7.5, 25.0, 11.0, 16.0],
    })


# Test DatetimeFeatureExtractor
def test_datetime_feature_extractor(sample_taxi_data):
    """Test datetime feature extraction."""
    extractor = DatetimeFeatureExtractor()
    transformed = extractor.fit_transform(sample_taxi_data.copy())
    
    # Check that datetime columns are removed
    assert 'tpep_pickup_datetime' not in transformed.columns
    assert 'tpep_dropoff_datetime' not in transformed.columns
    
    # Check that temporal features are created
    assert 'tpep_pickup_datetime_hour' in transformed.columns
    assert 'tpep_pickup_datetime_weekday' in transformed.columns
    assert 'tpep_pickup_datetime_is_weekend' in transformed.columns
    
    # Check value ranges
    assert transformed['tpep_pickup_datetime_hour'].min() >= 0
    assert transformed['tpep_pickup_datetime_hour'].max() < 24
    assert transformed['tpep_pickup_datetime_weekday'].min() >= 0
    assert transformed['tpep_pickup_datetime_weekday'].max() <= 6


def test_trip_duration_calculator(sample_taxi_data):
    """Test trip duration calculation."""
    # First extract datetime features to ensure columns exist
    sample_taxi_data_copy = sample_taxi_data.copy()
    sample_taxi_data_copy['tpep_pickup_datetime'] = pd.to_datetime(sample_taxi_data_copy['tpep_pickup_datetime'])
    sample_taxi_data_copy['tpep_dropoff_datetime'] = pd.to_datetime(sample_taxi_data_copy['tpep_dropoff_datetime'])
    
    calculator = TripDurationCalculator()
    transformed = calculator.fit_transform(sample_taxi_data_copy)
    
    assert 'trip_duration_min' in transformed.columns
    assert transformed['trip_duration_min'].min() >= 0
    assert (transformed['trip_duration_min'] == 30).all()  # All 30-minute trips


def test_speed_calculator(sample_taxi_data):
    """Test speed calculation."""
    # Create minimal data with required columns
    data = pd.DataFrame({
        'trip_distance': [2.0, 5.0, 1.0],
        'trip_duration_min': [30, 60, 10],
    })
    
    calculator = SpeedCalculator()
    transformed = calculator.fit_transform(data)
    
    assert 'avg_speed' in transformed.columns
    assert transformed['avg_speed'].min() >= 0
    assert transformed['avg_speed'].max() <= 100


def test_fare_component_aggregator(sample_taxi_data):
    """Test fare component aggregation."""
    aggregator = FareComponentAggregator()
    transformed = aggregator.fit_transform(sample_taxi_data.copy())
    
    assert 'total_surcharges' in transformed.columns
    assert 'has_tolls' in transformed.columns
    assert 'tip_ratio' in transformed.columns
    
    # Check has_tolls is binary
    assert set(transformed['has_tolls'].unique()).issubset({0, 1})
    
    # Check tip_ratio is in valid range
    assert transformed['tip_ratio'].min() >= 0
    assert transformed['tip_ratio'].max() <= 1


def test_location_distance_calculator(sample_taxi_data):
    """Test location distance feature calculation."""
    calculator = LocationDistanceCalculator()
    transformed = calculator.fit_transform(sample_taxi_data.copy())
    
    assert 'same_location' in transformed.columns
    assert 'location_distance' in transformed.columns
    
    # Check same_location is binary
    assert set(transformed['same_location'].unique()).issubset({0, 1})
    
    # Check location_distance is non-negative
    assert (transformed['location_distance'] >= 0).all()


def test_categorical_encoder(sample_taxi_data):
    """Test categorical encoding."""
    encoder = CategoricalEncoder()
    transformed = encoder.fit_transform(sample_taxi_data.copy())
    
    # Original categorical columns should be removed
    assert 'store_and_fwd_flag' not in transformed.columns
    assert 'payment_type' not in transformed.columns


def test_numerical_scaler(sample_taxi_data):
    """Test numerical feature scaling."""
    scaler = NumericalScaler()
    transformed = scaler.fit_transform(sample_taxi_data.copy())
    
    # For scaled numerical features, mean should be ~0 and std ~1
    # (allowing for some numerical precision issues)
    numerical_cols = sample_taxi_data.select_dtypes(include=[np.number]).columns
    
    for col in numerical_cols:
        if col in transformed.columns:
            mean = transformed[col].mean()
            assert abs(mean) < 0.1  # Should be close to 0


def test_feature_pipeline_creation():
    """Test that feature pipeline can be created."""
    pipeline = build_feature_pipeline()
    
    assert pipeline is not None
    assert len(pipeline.steps) > 0
    assert pipeline.steps[-1][0] == 'scaler'  # Last stage should be scaler


def test_feature_pipeline_fit_transform(sample_taxi_data):
    """Test full pipeline fit and transform."""
    pipeline = build_feature_pipeline()
    
    # Fit and transform
    transformed = pipeline.fit_transform(sample_taxi_data.copy())
    
    # Check output shape
    assert transformed.shape[0] == sample_taxi_data.shape[0]  # Same number of rows
    assert transformed.shape[1] > sample_taxi_data.shape[1]  # More columns (engineered features)
    
    # Check no NaN values (except where expected)
    nan_count = np.isnan(transformed).sum().sum()
    assert nan_count < transformed.size * 0.05  # Less than 5% NaN


def test_feature_pipeline_reproducibility(sample_taxi_data):
    """Test that pipeline produces reproducible results."""
    pipeline = build_feature_pipeline()
    
    # Transform twice
    result1 = pipeline.fit_transform(sample_taxi_data.copy())
    result2 = pipeline.fit_transform(sample_taxi_data.copy())
    
    # Results should be identical
    np.testing.assert_array_almost_equal(result1, result2)


def test_feature_pipeline_persistence(sample_taxi_data, tmp_path):
    """Test that pipeline can be saved and loaded."""
    # Fit pipeline
    pipeline = build_feature_pipeline()
    pipeline.fit(sample_taxi_data.copy())
    
    # Transform with original
    result1 = pipeline.transform(sample_taxi_data.copy())
    
    # Save and load
    save_path = tmp_path / "pipeline.pkl"
    import joblib
    joblib.dump(pipeline, save_path)
    
    loaded_pipeline = joblib.load(save_path)
    
    # Transform with loaded
    result2 = loaded_pipeline.transform(sample_taxi_data.copy())
    
    # Results should be identical
    np.testing.assert_array_almost_equal(result1, result2)
