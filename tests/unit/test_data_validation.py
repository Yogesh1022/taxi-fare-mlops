"""Unit tests for data validation."""

import pandas as pd
import pytest

from data.schema import DataSchema
from data.validate import DataValidator


@pytest.fixture
def sample_data():
    """Create sample valid data."""
    return pd.DataFrame(
        {
            "tpep_pickup_datetime": ["2023-06-28 17:31:46", "2023-06-29 19:15:55"],
            "tpep_dropoff_datetime": ["2023-06-28 18:22:12", "2023-06-29 19:07:31"],
            "passenger_count": [1.0, 2.0],
            "trip_distance": [1.5, 3.8],
            "RatecodeID": [1.0, 1.0],
            "store_and_fwd_flag": ["N", "N"],
            "PULocationID": [212.0, 6.0],
            "DOLocationID": [237.0, 163.0],
            "payment_type": ["Credit Card", "Credit Card"],
            "VendorID": [0.0, 1.0],
            "extra": [5.0, 5.0],
            "tip_amount": [6.0, 9.0],
            "tolls_amount": [0.0, 0.0],
            "improvement_surcharge": [1.0, 1.0],
            "congestion_surcharge": [2.5, 2.5],
            "Airport_fee": [0.0, 0.0],
            "total_amount": [24.8, 31.55],
        }
    )


def test_validator_creation():
    """Test that validator can be created."""
    validator = DataValidator()
    assert validator is not None
    assert validator.schema is not None


def test_valid_data(sample_data):
    """Test validation of valid data."""
    validator = DataValidator()
    is_valid, report = validator.validate(sample_data)

    assert is_valid is True
    assert len(report["errors"]) == 0


def test_missing_required_column():
    """Test validation fails when required column is missing."""
    df = pd.DataFrame(
        {
            "tpep_pickup_datetime": ["2023-06-28 17:31:46"],
            "passenger_count": [1.0],
        }
    )

    validator = DataValidator()
    is_valid, report = validator.validate(df)

    assert is_valid is False
    assert len(report["errors"]) > 0
    assert any("Missing required columns" in error for error in report["errors"])


def test_null_values_in_non_nullable_column(sample_data):
    """Test validation detects nulls in non-nullable columns."""
    df = sample_data.copy()
    df.loc[0, "passenger_count"] = None

    validator = DataValidator()
    is_valid, report = validator.validate(df)

    assert is_valid is False
    assert any("should not have nulls" in error for error in report["errors"])


def test_out_of_range_values(sample_data):
    """Test validation detects out-of-range numeric values."""
    df = sample_data.copy()
    df.loc[0, "passenger_count"] = 10.0  # Out of range

    validator = DataValidator()
    is_valid, report = validator.validate(df)

    assert is_valid is False
    assert any("above maximum" in error for error in report["errors"])


def test_invalid_categorical_value(sample_data):
    """Test validation detects invalid categorical values."""
    df = sample_data.copy()
    df.loc[0, "store_and_fwd_flag"] = "X"  # Invalid

    validator = DataValidator()
    is_valid, report = validator.validate(df)

    assert is_valid is False
    assert any("found invalid values" in error for error in report["errors"])


def test_schema_methods():
    """Test schema utility methods."""
    schema = DataSchema()

    # Test column retrieval
    required = schema.get_required_columns()
    assert "trip_distance" in required
    assert "total_amount" in required

    # Test numeric columns
    numeric = schema.get_numeric_columns()
    assert "trip_distance" in numeric
    assert "passenger_count" in numeric

    # Test categorical columns
    categorical = schema.get_categorical_columns()
    assert "payment_type" in categorical
    assert "store_and_fwd_flag" in categorical

    # Test datetime columns
    datetimes = schema.get_datetime_columns()
    assert "tpep_pickup_datetime" in datetimes
    assert "tpep_dropoff_datetime" in datetimes


@pytest.mark.unit
def test_placeholder():
    """Placeholder test."""
    assert True
