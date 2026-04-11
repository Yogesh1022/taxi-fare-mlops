"""
Advanced Anomaly Detection and Data Drift Monitoring

Implements multiple drift detection strategies:
1. Isolation Forest - Anomaly detection
2. Statistical Tests - KS test, Wasserstein distance
3. Distribution Comparison - Kolmogorov-Smirnov test
4. Model-based Drift - Using model predictions
5. Reference Window Comparison - Compare against baseline

Author: MLOps Team
Date: 2026-04-08
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime

import numpy as np
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from scipy.stats import ks_2samp, wasserstein_distance, entropy
from scipy.spatial.distance import jensenshannon
import joblib

logger = logging.getLogger(__name__)


class AnomalyDetector:
    """
    Advanced anomaly detection using Isolation Forest.
    
    Detects data points that deviate significantly from normal patterns.
    """
    
    def __init__(self, contamination: float = 0.05, random_state: int = 42):
        """
        Initialize anomaly detector.
        
        Args:
            contamination: Expected proportion of outliers
            random_state: Random seed
        """
        self.contamination = contamination
        self.random_state = random_state
        self.model = None
        self.scaler = StandardScaler()
        logger.info(f"[ANOMALY] AnomalyDetector initialized (contamination={contamination})")
    
    def fit(self, X: np.ndarray):
        """
        Fit anomaly detector on training data.
        
        Args:
            X: Training features
        """
        logger.info("[ANOMALY] Fitting Isolation Forest...")
        
        X_scaled = self.scaler.fit_transform(X)
        self.model = IsolationForest(
            contamination=self.contamination,
            random_state=self.random_state,
            n_jobs=-1
        )
        self.model.fit(X_scaled)
        
        logger.info("[ANOMALY] Isolation Forest fitted")
    
    def predict_anomalies(self, X: np.ndarray) -> Tuple[np.ndarray, np.ndarray]:
        """
        Predict anomalies (-1 for anomaly, 1 for normal).
        
        Args:
            X: Features to check
            
        Returns:
            Tuple of (predictions, anomaly_scores)
        """
        if self.model is None:
            raise ValueError("Model not fitted yet")
        
        X_scaled = self.scaler.transform(X)
        predictions = self.model.predict(X_scaled)
        scores = self.model.score_samples(X_scaled)
        
        return predictions, scores
    
    def get_anomalies(self, X: np.ndarray) -> Dict[str, Any]:
        """Get detailed anomaly information."""
        predictions, scores = self.predict_anomalies(X)
        
        n_anomalies = (predictions == -1).sum()
        anomaly_pct = 100 * n_anomalies / len(predictions)
        
        logger.info(f"[ANOMALY] Detected {n_anomalies} anomalies ({anomaly_pct:.1f}%)")
        
        return {
            'n_anomalies': int(n_anomalies),
            'anomaly_percentage': float(anomaly_pct),
            'anomaly_indices': np.where(predictions == -1)[0].tolist(),
            'anomaly_scores': scores,
            'predictions': predictions
        }


class DriftDetector:
    """
    Advanced data drift detection using multiple statistical methods.
    
    Detects distribution shifts and data quality degradation.
    """
    
    def __init__(self, significance_level: float = 0.05):
        """
        Initialize drift detector.
        
        Args:
            significance_level: Statistical significance threshold
        """
        self.significance_level = significance_level
        self.reference_data = None
        self.reference_stats = {}
        logger.info(f"[DRIFT] DriftDetector initialized (alpha={significance_level})")
    
    def set_reference(self, X_reference: np.ndarray, feature_names: List[str] = None):
        """
        Set reference data for drift comparison.
        
        Args:
            X_reference: Reference data (baseline)
            feature_names: List of feature names
        """
        logger.info("[DRIFT] Setting reference data for drift detection...")
        
        self.reference_data = X_reference
        
        if feature_names is None:
            feature_names = [f"feature_{i}" for i in range(X_reference.shape[1])]
        self.feature_names = feature_names
        
        # Compute reference statistics
        self.reference_stats = {
            'mean': X_reference.mean(axis=0),
            'std': X_reference.std(axis=0),
            'min': X_reference.min(axis=0),
            'max': X_reference.max(axis=0),
            'median': np.median(X_reference, axis=0),
            'q25': np.percentile(X_reference, 25, axis=0),
            'q75': np.percentile(X_reference, 75, axis=0),
        }
        
        logger.info("[DRIFT] Reference statistics computed")
    
    def kolmogorov_smirnov_test(self, X_current: np.ndarray) -> Dict[str, Any]:
        """
        Kolmogorov-Smirnov test for distribution shift.
        
        Compares distributions of reference and current data.
        
        Args:
            X_current: Current data to test
            
        Returns:
            Dictionary with KS test results
        """
        logger.info("[DRIFT] Running Kolmogorov-Smirnov test...")
        
        if self.reference_data is None:
            raise ValueError("Reference data not set")
        
        results = {
            'method': 'kolmogorov_smirnov',
            'features_with_drift': [],
            'feature_stats': {}
        }
        
        for i, feature_name in enumerate(self.feature_names):
            statistic, p_value = ks_2samp(self.reference_data[:, i], X_current[:, i])
            
            feature_result = {
                'statistic': float(statistic),
                'p_value': float(p_value),
                'drifted': p_value < self.significance_level
            }
            results['feature_stats'][feature_name] = feature_result
            
            if p_value < self.significance_level:
                results['features_with_drift'].append(feature_name)
                logger.info(f"[DRIFT]   {feature_name}: DRIFT DETECTED (p={p_value:.4f})")
            else:
                logger.info(f"[DRIFT]   {feature_name}: No drift (p={p_value:.4f})")
        
        results['overall_drift'] = len(results['features_with_drift']) > 0
        
        return results
    
    def wasserstein_distance_test(self, X_current: np.ndarray) -> Dict[str, Any]:
        """
        Wasserstein distance for distribution comparison.
        
        Measures 'earth mover distance' between distributions.
        
        Args:
            X_current: Current data to test
            
        Returns:
            Dictionary with Wasserstein test results
        """
        logger.info("[DRIFT] Computing Wasserstein distances...")
        
        if self.reference_data is None:
            raise ValueError("Reference data not set")
        
        results = {
            'method': 'wasserstein_distance',
            'features_with_drift': [],
            'feature_distances': {}
        }
        
        # Compute threshold as 90th percentile of distances on reference splits
        reference_distances = []
        n_splits = 5
        split_size = len(self.reference_data) // n_splits
        
        for i in range(n_splits - 1):
            split1 = self.reference_data[i*split_size:(i+1)*split_size]
            split2 = self.reference_data[(i+1)*split_size:(i+2)*split_size]
            
            for j in range(split1.shape[1]):
                dist = wasserstein_distance(split1[:, j], split2[:, j])
                reference_distances.append(dist)
        
        threshold = np.percentile(reference_distances, 90)
        logger.info(f"[DRIFT] Wasserstein threshold (90th percentile): {threshold:.4f}")
        
        distances = []
        for i, feature_name in enumerate(self.feature_names):
            distance = wasserstein_distance(self.reference_data[:, i], X_current[:, i])
            distances.append(distance)
            
            drifted = distance > threshold
            
            feature_result = {
                'distance': float(distance),
                'threshold': float(threshold),
                'drifted': drifted
            }
            results['feature_distances'][feature_name] = feature_result
            
            if drifted:
                results['features_with_drift'].append(feature_name)
                logger.info(f"[DRIFT]   {feature_name}: DRIFT DETECTED (distance={distance:.4f})")
            else:
                logger.info(f"[DRIFT]   {feature_name}: No drift (distance={distance:.4f})")
        
        results['overall_drift'] = len(results['features_with_drift']) > 0
        results['mean_distance'] = float(np.mean(distances))
        
        return results
    
    def jensen_shannon_divergence(self, X_current: np.ndarray, n_bins: int = 10) -> Dict[str, Any]:
        """
        Jensen-Shannon divergence for distribution comparison.
        
        Symmetric version of KL divergence.
        
        Args:
            X_current: Current data to test
            n_bins: Number of histogram bins
            
        Returns:
            Dictionary with JS divergence results
        """
        logger.info("[DRIFT] Computing Jensen-Shannon divergences...")
        
        if self.reference_data is None:
            raise ValueError("Reference data not set")
        
        results = {
            'method': 'jensen_shannon_divergence',
            'features_with_drift': [],
            'feature_divergences': {}
        }
        
        divergences = []
        for i, feature_name in enumerate(self.feature_names):
            # Create histograms
            hist_ref, bin_edges = np.histogram(self.reference_data[:, i], bins=n_bins)
            hist_curr, _ = np.histogram(X_current[:, i], bins=bin_edges)
            
            # Normalize to probabilities
            hist_ref = hist_ref / hist_ref.sum()
            hist_curr = hist_curr / hist_curr.sum()
            
            # Add small epsilon to avoid log(0)
            hist_ref = hist_ref + 1e-10
            hist_curr = hist_curr + 1e-10
            
            divergence = jensenshannon(hist_ref, hist_curr)
            divergences.append(divergence)
            
            drifted = divergence > 0.1  # Typical threshold
            
            feature_result = {
                'divergence': float(divergence),
                'drifted': drifted
            }
            results['feature_divergences'][feature_name] = feature_result
            
            if drifted:
                results['features_with_drift'].append(feature_name)
                logger.info(f"[DRIFT]   {feature_name}: DRIFT DETECTED (JS={divergence:.4f})")
            else:
                logger.info(f"[DRIFT]   {feature_name}: No drift (JS={divergence:.4f})")
        
        results['overall_drift'] = len(results['features_with_drift']) > 0
        results['mean_divergence'] = float(np.mean(divergences))
        
        return results
    
    def statistical_comparison(self, X_current: np.ndarray) -> Dict[str, Any]:
        """
        Statistical comparison of mean and variance.
        
        Checks if current data statistics differ significantly from reference.
        
        Args:
            X_current: Current data to test
            
        Returns:
            Dictionary with statistical comparison results
        """
        logger.info("[DRIFT] Running statistical comparison test...")
        
        if self.reference_data is None:
            raise ValueError("Reference data not set")
        
        current_stats = {
            'mean': X_current.mean(axis=0),
            'std': X_current.std(axis=0),
        }
        
        results = {
            'method': 'statistical_comparison',
            'features_with_drift': [],
            'feature_stats': {}
        }
        
        for i, feature_name in enumerate(self.feature_names):
            mean_diff = (current_stats['mean'][i] - self.reference_stats['mean'][i]) / (self.reference_stats['std'][i] + 1e-10)
            std_ratio = current_stats['std'][i] / (self.reference_stats['std'][i] + 1e-10)
            
            # Threshold for drift: mean difference > 2 std or std ratio > 1.5 or < 0.67
            drifted = (np.abs(mean_diff) > 2) or (std_ratio > 1.5) or (std_ratio < 0.67)
            
            feature_result = {
                'mean_difference_std': float(mean_diff),
                'std_ratio': float(std_ratio),
                'drifted': drifted
            }
            results['feature_stats'][feature_name] = feature_result
            
            if drifted:
                results['features_with_drift'].append(feature_name)
                logger.info(f"[DRIFT]   {feature_name}: DRIFT DETECTED (mean_diff={mean_diff:.2f}σ, std_ratio={std_ratio:.2f})")
            else:
                logger.info(f"[DRIFT]   {feature_name}: No drift")
        
        results['overall_drift'] = len(results['features_with_drift']) > 0
        
        return results
    
    def run_all_tests(self, X_current: np.ndarray) -> Dict[str, Any]:
        """
        Run all drift detection tests.
        
        Args:
            X_current: Current data to test
            
        Returns:
            Dictionary with results from all tests
        """
        if self.reference_data is None:
            raise ValueError("Reference data not set. Call set_reference() first.")
        
        logger.info("[DRIFT] Running comprehensive drift detection suite...")
        logger.info(f"[DRIFT] Reference data shape: {self.reference_data.shape}")
        logger.info(f"[DRIFT] Current data shape: {X_current.shape}")
        
        results = {
            'timestamp': datetime.now().isoformat(),
            'reference_shape': self.reference_data.shape,
            'current_shape': X_current.shape,
            'tests': {}
        }
        
        # Run all tests
        results['tests']['ks_test'] = self.kolmogorov_smirnov_test(X_current)
        results['tests']['wasserstein'] = self.wasserstein_distance_test(X_current)
        results['tests']['jensen_shannon'] = self.jensen_shannon_divergence(X_current)
        results['tests']['statistical'] = self.statistical_comparison(X_current)
        
        # Overall drift verdict
        any_drift = any(test['overall_drift'] for test in results['tests'].values())
        results['overall_drift_detected'] = any_drift
        results['drift_consensus'] = sum(test['overall_drift'] for test in results['tests'].values())
        
        drift_severity = "SEVERE" if results['drift_consensus'] >= 3 else "MODERATE" if results['drift_consensus'] == 2 else "MILD" if results['drift_consensus'] == 1 else "NONE"
        results['drift_severity'] = drift_severity
        
        logger.info(f"\n[DRIFT] DRIFT DETECTION SUMMARY")
        logger.info(f"[DRIFT] Overall Drift: {any_drift}")
        logger.info(f"[DRIFT] Tests with Drift: {results['drift_consensus']}/4")
        logger.info(f"[DRIFT] Severity: {drift_severity}")
        
        return results
    
    def save_results(self, results: Dict, output_dir: str = "models"):
        """Save drift detection results."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        results_file = output_path / "drift_detection_results.json"
        
        # Convert numpy types to Python types for JSON serialization
        def convert_to_serializable(obj):
            if isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_to_serializable(i) for i in obj]
            return obj
        
        serializable_results = convert_to_serializable(results)
        
        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
        
        logger.info(f"[DRIFT] Results saved to {results_file}")


def run_comprehensive_drift_detection(
    X_reference: np.ndarray,
    X_current: np.ndarray,
    feature_names: List[str] = None,
    output_dir: str = "models"
) -> Dict[str, Any]:
    """
    Run comprehensive drift detection.
    
    Args:
        X_reference: Reference (baseline) data
        X_current: Current data to check for drift
        feature_names: List of feature names
        output_dir: Directory to save results
        
    Returns:
        Dictionary with comprehensive drift detection results
    """
    logger.info("[DRIFT] Starting comprehensive drift detection...")
    
    detector = DriftDetector()
    detector.set_reference(X_reference, feature_names)
    
    results = detector.run_all_tests(X_current)
    detector.save_results(results, output_dir)
    
    # Also run anomaly detection
    logger.info("\n[ANOMALY] Running anomaly detection...")
    anomaly_detector = AnomalyDetector()
    anomaly_detector.fit(X_reference)
    anomalies = anomaly_detector.get_anomalies(X_current)
    
    results['anomaly_detection'] = anomalies
    
    return results
