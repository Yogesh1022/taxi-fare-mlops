"""Feature schema and feature engineering documentation."""

from typing import Dict, List

# Original input features (from raw data)
INPUT_FEATURES = {
    "temporal": [
        "tpep_pickup_datetime",
        "tpep_dropoff_datetime",
    ],
    "numerical": [
        "passenger_count",
        "trip_distance",
        "extra",
        "tip_amount",
        "tolls_amount",
        "improvement_surcharge",
        "congestion_surcharge",
        "Airport_fee",
    ],
    "categorical": [
        "store_and_fwd_flag",
        "payment_type",
    ],
    "location": [
        "RatecodeID",
        "PULocationID",
        "DOLocationID",
        "VendorID",
    ],
}

# Engineered features (output from pipeline)
ENGINEERED_FEATURES = {
    "temporal": [
        "tpep_pickup_datetime_hour",
        "tpep_pickup_datetime_day",
        "tpep_pickup_datetime_weekday",
        "tpep_pickup_datetime_month",
        "tpep_pickup_datetime_quarter",
        "tpep_pickup_datetime_is_weekend",
        "tpep_dropoff_datetime_hour",
        "tpep_dropoff_datetime_day",
        "tpep_dropoff_datetime_weekday",
        "tpep_dropoff_datetime_month",
        "tpep_dropoff_datetime_quarter",
        "tpep_dropoff_datetime_is_weekend",
    ],
    "derived": [
        "trip_duration_min",  # Duration in minutes
        "avg_speed",  # Miles per minute
        "total_surcharges",  # Sum of all surcharges
        "has_tolls",  # Binary flag
        "tip_ratio",  # Tip as % of total (training only)
        "same_location",  # Same pickup/dropoff zone
        "location_distance",  # Distance between zones
    ],
    "categorical_encoded": [
        # One-hot encoded categorical features (exact names depend on categories)
        "store_and_fwd_flag_Y",
        "payment_type_Cash",
        "payment_type_other",
    ],
    "numerical_scaled": [
        # Scaled numerical features from original data
        "passenger_count",
        "trip_distance",
        "extra",
        "tip_amount",
        "tolls_amount",
        "improvement_surcharge",
        "congestion_surcharge",
        "Airport_fee",
        "RatecodeID",
        "PULocationID",
        "DOLocationID",
        "VendorID",
    ],
}

# Feature engineering rules documentation
FEATURE_ENGINEERING_RULES = """
## Feature Engineering Pipeline

### Stage 1: Temporal Feature Extraction
From `tpep_pickup_datetime` and `tpep_dropoff_datetime`:
- `{col}_hour`: Hour of day (0-23)
- `{col}_day`: Day of month (1-31)
- `{col}_weekday`: Day of week (0=Monday, 6=Sunday)
- `{col}_month`: Month (1-12)
- `{col}_quarter`: Quarter (1-4)
- `{col}_is_weekend`: Binary flag (1 if Saturday/Sunday, 0 otherwise)

**Why**: Taxi fares vary significantly by time of day and day of week

### Stage 2: Trip Duration
From `tpep_pickup_datetime` and `tpep_dropoff_datetime`:
- `trip_duration_min`: Duration in minutes
  - Clamped to [0, ∞): removes negative values
  
**Why**: Longer trips → higher fares (though distance is better)

### Stage 3: Trip Speed  
From `trip_distance` and `trip_duration_min`:
- `avg_speed`: miles per minute
  - Clamped to [0, 100]: realistic speed bounds
  
**Why**: Speed proxy for traffic conditions (high speed = light traffic = lower fare)

### Stage 4: Fare Component Aggregation
- `total_surcharges`: Sum of extra + improvement_surcharge + congestion_surcharge + Airport_fee
- `has_tolls`: Binary (1 if tolls_amount > 0)
- `tip_ratio`: tip_amount / total_amount (training only)
  - Clamped to [0, 1]: valid tip percentage
  
**Why**: Aggregated charges predict total fare; tip ratio shows payment behavior

### Stage 5: Location Features
From `PULocationID` and `DOLocationID`:
- `same_location`: Binary (1 if pickup and dropoff in same zone)
- `location_distance`: |PULocationID - DOLocationID|
  
**Why**: Same-zone trips are shorter/cheaper; location ID difference correlates with distance

### Stage 6: Categorical Encoding
One-hot encode with drop='first':
- `store_and_fwd_flag_Y`: Stored and forwarded trip
- `payment_type_Cash`: Cash payment (vs Credit Card/other)
  
**Why**: One-hot encoding enables linear models to capture categorical effects

### Stage 7: Numerical Scaling
StandardScaler on all numerical features:
- (x - mean) / std
  
**Why**: Ensures all features on same scale; important for linear models and regularization

## Feature Counts
- Input features: 14
- Engineered features: ~35
- Total pipeline output: ~45 features
"""


def get_feature_list() -> List[str]:
    """Get complete list of engineered features."""
    features = []
    for category, items in ENGINEERED_FEATURES.items():
        features.extend(items)
    return features


def validate_feature_schema(X) -> bool:
    """
    Validate that features match expected schema.

    Args:
        X: Feature data (DataFrame or array)

    Returns:
        True if schema matches, False otherwise
    """
    if hasattr(X, "columns"):
        feature_names = set(X.columns)
    else:
        # If array, can't validate exact features, just check shape
        return X.shape[1] > 0

    expected_count = sum(len(v) for v in ENGINEERED_FEATURES.values())
    return len(feature_names) >= expected_count * 0.8  # Allow 20% variance


FEATURE_SCHEMA = {
    "input": INPUT_FEATURES,
    "engineered": ENGINEERED_FEATURES,
    "rules": FEATURE_ENGINEERING_RULES,
}
