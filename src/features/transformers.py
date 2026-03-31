"""Custom feature transformers for taxi fare prediction."""

import pandas as pd
import numpy as np
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from pandas.api.types import is_numeric_dtype


class DatetimeFeatureExtractor(BaseEstimator, TransformerMixin):
    """Extract temporal features from datetime columns."""
    
    def __init__(self, datetime_cols=None):
        """
        Initialize transformer.
        
        Args:
            datetime_cols: List of datetime column names to process
        """
        self.datetime_cols = datetime_cols or [
            'tpep_pickup_datetime',
            'tpep_dropoff_datetime'
        ]
    
    def fit(self, X, y=None):
        """Fit transformer (no-op for this transformer)."""
        return self
    
    def transform(self, X):
        """Extract temporal features."""
        X = X.copy()
        
        for col in self.datetime_cols:
            if col in X.columns:
                # Convert to datetime if not already
                if not pd.api.types.is_datetime64_any_dtype(X[col]):
                    X[col] = pd.to_datetime(X[col], errors='coerce')
                
                # Extract temporal features
                X[f'{col}_hour'] = X[col].dt.hour
                X[f'{col}_day'] = X[col].dt.day
                X[f'{col}_weekday'] = X[col].dt.weekday  # 0=Monday, 6=Sunday
                X[f'{col}_month'] = X[col].dt.month
                X[f'{col}_quarter'] = X[col].dt.quarter
                X[f'{col}_is_weekend'] = (X[col].dt.weekday >= 5).astype(int)
                
                # Drop original datetime column
                X = X.drop(columns=[col])
        
        return X
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names."""
        feature_names = []
        for col in self.datetime_cols:
            feature_names.extend([
                f'{col}_hour',
                f'{col}_day',
                f'{col}_weekday',
                f'{col}_month',
                f'{col}_quarter',
                f'{col}_is_weekend'
            ])
        return np.array(feature_names)


class TripDurationCalculator(BaseEstimator, TransformerMixin):
    """Calculate trip duration from pickup and dropoff times."""
    
    def fit(self, X, y=None):
        """Fit transformer (no-op)."""
        return self
    
    def transform(self, X):
        """Calculate trip duration in minutes."""
        X = X.copy()
        
        pickup_col = 'tpep_pickup_datetime'
        dropoff_col = 'tpep_dropoff_datetime'
        
        if pickup_col in X.columns and dropoff_col in X.columns:
            # Convert to datetime if not already
            if not pd.api.types.is_datetime64_any_dtype(X[pickup_col]):
                X[pickup_col] = pd.to_datetime(X[pickup_col], errors='coerce')
            if not pd.api.types.is_datetime64_any_dtype(X[dropoff_col]):
                X[dropoff_col] = pd.to_datetime(X[dropoff_col], errors='coerce')
            
            # Calculate duration in minutes
            X['trip_duration_min'] = (X[dropoff_col] - X[pickup_col]).dt.total_seconds() / 60
            X['trip_duration_min'] = X['trip_duration_min'].fillna(0)
            X['trip_duration_min'] = X['trip_duration_min'].clip(lower=0)  # Remove negative values
        
        return X
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names."""
        return np.array(['trip_duration_min'])


class SpeedCalculator(BaseEstimator, TransformerMixin):
    """Calculate trip speed from distance and duration."""
    
    def fit(self, X, y=None):
        """Fit transformer (no-op)."""
        return self
    
    def transform(self, X):
        """Calculate average speed (miles per minute)."""
        X = X.copy()
        
        if 'trip_distance' in X.columns and 'trip_duration_min' in X.columns:
            # Calculate speed: distance / duration (in miles per minute)
            X['avg_speed'] = X['trip_distance'] / (X['trip_duration_min'] + 1)  # +1 to avoid division by zero
            X['avg_speed'] = X['avg_speed'].fillna(0)
            X['avg_speed'] = X['avg_speed'].clip(lower=0, upper=100)  # Reasonable bounds
        
        return X
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names."""
        return np.array(['avg_speed'])


class FareComponentAggregator(BaseEstimator, TransformerMixin):
    """Aggregate fare components into derived features."""
    
    def fit(self, X, y=None):
        """Fit transformer (no-op)."""
        return self
    
    def transform(self, X):
        """Calculate fare component aggregates."""
        X = X.copy()
        
        # Base fare components (excluding tip)
        surcharge_cols = ['extra', 'improvement_surcharge', 'congestion_surcharge', 'Airport_fee']
        existing_cols = [col for col in surcharge_cols if col in X.columns]
        
        if existing_cols:
            X['total_surcharges'] = X[existing_cols].sum(axis=1)
        
        # Toll components
        if 'tolls_amount' in X.columns:
            X['has_tolls'] = (X['tolls_amount'] > 0).astype(int)
        
        # Tip ratio (if we have total_amount in training)
        if 'tip_amount' in X.columns and 'total_amount' in X.columns:
            X['tip_ratio'] = X['tip_amount'] / (X['total_amount'] + 1)  # +1 to avoid division by zero
            X['tip_ratio'] = X['tip_ratio'].fillna(0)
            X['tip_ratio'] = X['tip_ratio'].clip(0, 1)  # Reasonable bounds (0-100%)
        
        return X
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names."""
        return np.array(['total_surcharges', 'has_tolls', 'tip_ratio'])


class LocationDistanceCalculator(BaseEstimator, TransformerMixin):
    """Calculate location-based distance features."""
    
    def fit(self, X, y=None):
        """Fit transformer (no-op)."""
        return self
    
    def transform(self, X):
        """Calculate location proximity."""
        X = X.copy()
        
        if 'PULocationID' in X.columns and 'DOLocationID' in X.columns:
            # Same zone indicator
            X['same_location'] = (X['PULocationID'] == X['DOLocationID']).astype(int)
            
            # Location distance proxy (location ID difference)
            X['location_distance'] = np.abs(X['PULocationID'] - X['DOLocationID'])
        
        return X
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names."""
        return np.array(['same_location', 'location_distance'])


class CategoricalEncoder(BaseEstimator, TransformerMixin):
    """One-hot encode categorical features."""
    
    def __init__(self, categorical_cols=None):
        """
        Initialize transformer.
        
        Args:
            categorical_cols: List of categorical column names
        """
        self.categorical_cols = categorical_cols or [
            'store_and_fwd_flag',
            'payment_type'
        ]
        self.encoder = OneHotEncoder(
            sparse_output=False,
            handle_unknown='ignore',
            drop='first'  # Drop first category to avoid multicollinearity
        )
        self.feature_names_ = None
    
    def fit(self, X, y=None):
        """Fit one-hot encoder."""
        existing_cols = [col for col in self.categorical_cols if col in X.columns]
        if existing_cols:
            self.encoder.fit(X[existing_cols])
            self.feature_names_ = self.encoder.get_feature_names_out(existing_cols)
        return self
    
    def transform(self, X):
        """Encode categorical features."""
        X = X.copy()
        existing_cols = [col for col in self.categorical_cols if col in X.columns]
        
        if existing_cols:
            encoded = self.encoder.transform(X[existing_cols])
            encoded_df = pd.DataFrame(encoded, columns=self.feature_names_, index=X.index)
            X = pd.concat([X.drop(columns=existing_cols), encoded_df], axis=1)
        
        return X
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names."""
        return self.feature_names_ if self.feature_names_ is not None else np.array([])


class NumericalScaler(BaseEstimator, TransformerMixin):
    """Scale numerical features."""
    
    def __init__(self, numerical_cols=None):
        """
        Initialize transformer.
        
        Args:
            numerical_cols: List of numerical column names
        """
        self.numerical_cols = numerical_cols
        self.scaler = StandardScaler()
        self.feature_names_ = None
    
    def fit(self, X, y=None):
        """Fit scaler."""
        if self.numerical_cols is None:
            # Auto-detect numerical columns
            self.numerical_cols = X.select_dtypes(include=[np.number]).columns.tolist()
        
        existing_cols = [col for col in self.numerical_cols if col in X.columns]
        if existing_cols:
            self.scaler.fit(X[existing_cols])
            self.feature_names_ = existing_cols
        
        return self
    
    def transform(self, X):
        """Scale numerical features."""
        X = X.copy()
        
        if self.feature_names_:
            X[self.feature_names_] = self.scaler.transform(X[self.feature_names_])
        
        return X
    
    def get_feature_names_out(self, input_features=None):
        """Return feature names."""
        return np.array(self.feature_names_) if self.feature_names_ else np.array([])
