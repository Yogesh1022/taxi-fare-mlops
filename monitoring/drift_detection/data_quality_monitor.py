"""
Data Quality Monitoring Module
Day 13: Advanced Monitoring & Drift Detection

Provides real-time data quality metrics collection for Prometheus.
Integrates with monitoring pipeline to track:
- Missing values ratio
- Outlier ratios
- Data type mismatches
- Duplicate records
- Schema violations
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class DataQualityMonitor:
    """Monitors data quality metrics for prediction pipeline."""

    def __init__(self, reference_data: pd.DataFrame, thresholds: Dict[str, float] = None):
        """
        Initialize data quality monitor.
        
        Args:
            reference_data: Reference dataset for establishing baseline metrics
            thresholds: Dict of metric_name -> threshold values
        """
        self.reference_data = reference_data
        self.thresholds = thresholds or {
            'missing_values_ratio': 0.1,
            'outlier_ratio': 0.05,
            'duplicate_ratio': 0.01,
            'type_mismatch_count': 0,
        }
        self.reference_stats = self._compute_stats(reference_data)
        
    def _compute_stats(self, df: pd.DataFrame) -> Dict:
        """Compute reference statistics for data quality baseline."""
        stats = {}
        
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64']:
                stats[col] = {
                    'type': 'numeric',
                    'mean': df[col].mean(),
                    'std': df[col].std(),
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'q1': df[col].quantile(0.25),
                    'q3': df[col].quantile(0.75),
                }
            else:
                stats[col] = {
                    'type': 'categorical',
                    'unique_values': df[col].nunique(),
                    'value_counts': df[col].value_counts().to_dict(),
                }
        
        return stats
    
    def check_missing_values(self, df: pd.DataFrame) -> Tuple[float, Dict[str, float]]:
        """
        Check for missing values in data.
        
        Returns:
            Tuple of (overall_ratio, per_column_ratios)
        """
        overall_ratio = df.isnull().sum().sum() / (len(df) * len(df.columns))
        per_column = (df.isnull().sum() / len(df)).to_dict()
        
        return overall_ratio, per_column
    
    def check_duplicates(self, df: pd.DataFrame) -> float:
        """Check for duplicate records."""
        duplicate_count = df.duplicated().sum()
        duplicate_ratio = duplicate_count / len(df) if len(df) > 0 else 0
        
        return duplicate_ratio
    
    def check_outliers(self, df: pd.DataFrame) -> Tuple[float, Dict[str, int]]:
        """
        Detect outliers using IQR method.
        
        Returns:
            Tuple of (overall_ratio, per_column_outlier_counts)
        """
        outlier_counts = {}
        total_outliers = 0
        total_values = 0
        
        for col in df.columns:
            if df[col].dtype in ['float64', 'int64']:
                col_stats = self.reference_stats.get(col, {})
                
                if 'q1' in col_stats and 'q3' in col_stats:
                    q1 = col_stats['q1']
                    q3 = col_stats['q3']
                    iqr = q3 - q1
                    lower_bound = q1 - 1.5 * iqr
                    upper_bound = q3 + 1.5 * iqr
                    
                    outlier_mask = (df[col] < lower_bound) | (df[col] > upper_bound)
                    outlier_count = outlier_mask.sum()
                    outlier_counts[col] = int(outlier_count)
                    total_outliers += outlier_count
                    total_values += len(df)
        
        overall_ratio = total_outliers / total_values if total_values > 0 else 0
        
        return overall_ratio, outlier_counts
    
    def check_type_mismatches(self, df: pd.DataFrame) -> int:
        """Check for unexpected data type changes."""
        mismatches = 0
        
        for col in df.columns:
            if col in self.reference_stats:
                ref_type = self.reference_stats[col]['type']
                
                if ref_type == 'numeric' and df[col].dtype not in ['float64', 'int64']:
                    mismatches += 1
                    logger.warning(f"Type mismatch in column {col}: expected numeric, got {df[col].dtype}")
                elif ref_type == 'categorical' and df[col].dtype == 'object':
                    pass  # OK
                else:
                    mismatches += 1
        
        return mismatches
    
    def compute_quality_score(self, df: pd.DataFrame) -> float:
        """
        Compute overall data quality score (0-1).
        
        Score components:
        - Missing values penalty: -0.25 max
        - Duplicates penalty: -0.15 max
        - Outliers penalty: -0.25 max
        - Type mismatches penalty: -0.35 max
        """
        score = 1.0
        
        # Missing values
        missing_ratio, _ = self.check_missing_values(df)
        missing_penalty = min(0.25, missing_ratio / self.thresholds['missing_values_ratio'] * 0.25)
        score -= missing_penalty
        
        # Duplicates
        dup_ratio = self.check_duplicates(df)
        dup_penalty = min(0.15, dup_ratio / self.thresholds['duplicate_ratio'] * 0.15)
        score -= dup_penalty
        
        # Outliers
        outlier_ratio, _ = self.check_outliers(df)
        outlier_penalty = min(0.25, outlier_ratio / self.thresholds['outlier_ratio'] * 0.25)
        score -= outlier_penalty
        
        # Type mismatches
        type_mismatches = self.check_type_mismatches(df)
        type_penalty = min(0.35, type_mismatches / self.thresholds['type_mismatch_count'] * 0.35 if self.thresholds['type_mismatch_count'] > 0 else 0)
        score -= type_penalty
        
        return max(0.0, score)
    
    def check_schema(self, df: pd.DataFrame) -> Tuple[bool, List[str]]:
        """
        Validate schema matches reference data.
        
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check columns exist
        missing_cols = set(self.reference_data.columns) - set(df.columns)
        if missing_cols:
            issues.append(f"Missing columns: {', '.join(missing_cols)}")
        
        # Check for extra columns
        extra_cols = set(df.columns) - set(self.reference_data.columns)
        if extra_cols:
            issues.append(f"Extra columns: {', '.join(extra_cols)}")
        
        return len(issues) == 0, issues
    
    def generate_quality_report(self, df: pd.DataFrame) -> Dict:
        """Generate comprehensive data quality report."""
        missing_ratio, missing_per_col = self.check_missing_values(df)
        dup_ratio = self.check_duplicates(df)
        outlier_ratio, outliers_per_col = self.check_outliers(df)
        type_mismatches = self.check_type_mismatches(df)
        quality_score = self.compute_quality_score(df)
        is_valid, schema_issues = self.check_schema(df)
        
        report = {
            'timestamp': datetime.utcnow().isoformat(),
            'data_shape': df.shape,
            'quality_score': quality_score,
            'missing_values_ratio': missing_ratio,
            'missing_per_column': missing_per_col,
            'duplicate_ratio': dup_ratio,
            'outlier_ratio': outlier_ratio,
            'outliers_per_column': outliers_per_col,
            'type_mismatches': type_mismatches,
            'schema_valid': is_valid,
            'schema_issues': schema_issues,
            'thresholds': {
                'missing_values_exceeded': missing_ratio > self.thresholds['missing_values_ratio'],
                'duplicates_exceeded': dup_ratio > self.thresholds['duplicate_ratio'],
                'outliers_exceeded': outlier_ratio > self.thresholds['outlier_ratio'],
            },
        }
        
        return report
    
    def get_prometheus_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Generate metrics in Prometheus format.
        
        Returns:
            Dict of metric_name -> value for scraping
        """
        missing_ratio, missing_per_col = self.check_missing_values(df)
        dup_ratio = self.check_duplicates(df)
        outlier_ratio, outliers_per_col = self.check_outliers(df)
        quality_score = self.compute_quality_score(df)
        
        metrics = {
            'data_quality_score': quality_score,
            'data_quality_missing_values_ratio': missing_ratio,
            'data_quality_duplicate_ratio': dup_ratio,
            'data_quality_outlier_ratio': outlier_ratio,
            'data_records_processed_total': len(df),
            'data_quality_issues_total': int((missing_ratio > 0.1) + (dup_ratio > 0.01) + (outlier_ratio > 0.05)),
        }
        
        return metrics
