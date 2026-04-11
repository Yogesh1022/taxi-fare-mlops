"""
Evidently Drift Detection Configuration
Detects model drift and data quality issues
"""

from evidently.metric_preset import DataDriftPreset, DataQualityPreset, RegressionPerformancePreset
from evidently.report import Report
from evidently.test_suite import TestSuite
from evidently.tests import (
    TestNumberOfMissingValues,
    TestNumberOfDuplicateRows,
    TestShareOfDriftedFeatures,
    TestShareOfOutListValues,
    TestMeanInNSigmas,
    TestRegressionMAE,
    TestRegressionRMSE,
)

# Configuration for drift detection
DRIFT_CONFIG = {
    # Data drift detection threshold
    "drift_threshold": 0.5,  # 50% threshold for feature drift
    
    # Features to monitor
    "numerical_features": [
        "trip_distance",
        "fare_amount",
        "total_amount",
        "trip_duration",
        "passenger_count",
        "hour_of_day",
        "day_of_week"
    ],
    
    "categorical_features": [
        "pickup_borough",
        "dropoff_borough",
        "payment_type",
        "vendor_id"
    ],
    
    # Model performance thresholds
    "performance_thresholds": {
        "mae": 3.5,
        "rmse": 4.5,
        "r2": 0.70
    },
    
    # Data quality checks
    "quality_checks": {
        "missing_threshold": 0.05,  # 5% missing values
        "duplicate_threshold": 0.01,  # 1% duplicate rows
        "outlier_threshold": 0.05,  # 5% outliers
    },
    
    # Check frequency
    "check_frequency": "daily",
    "reference_period_days": 30,
}

# Metric presets for reports
METRIC_PRESETS = {
    "data_drift": DataDriftPreset(),
    "data_quality": DataQualityPreset(),
    "regression_performance": RegressionPerformancePreset(),
}

# Test suites configuration
TEST_SUITES = {
    "data_quality": [
        TestNumberOfMissingValues(),
        TestNumberOfDuplicateRows(),
        TestShareOfOutListValues(),
    ],
    "drift_detection": [
        TestShareOfDriftedFeatures(threshold=DRIFT_CONFIG["drift_threshold"]),
        TestMeanInNSigmas(),
    ],
    "model_performance": [
        TestRegressionMAE(lte=DRIFT_CONFIG["performance_thresholds"]["mae"]),
        TestRegressionRMSE(lte=DRIFT_CONFIG["performance_thresholds"]["rmse"]),
    ],
}
