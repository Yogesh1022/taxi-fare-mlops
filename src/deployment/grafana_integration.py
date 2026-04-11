"""
Grafana Integration: Real-time Monitoring Dashboard

Prometheus metrics export and Grafana dashboard configuration:
1. Model performance metrics (accuracy, latency, throughput)
2. Data drift tracking
3. Prediction distribution
4. System health metrics
5. Pre-built Grafana dashboard JSON

Author: MLOps Team
Date: 2026-04-08
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class MetricSnapshot:
    """Snapshot of metrics at a point in time."""
    timestamp: str
    model_accuracy: float
    prediction_latency_ms: float
    throughput_per_min: int
    prediction_distribution_mean: float
    prediction_distribution_std: float
    data_drift_score: float
    batch_size: int
    error_rate_pct: float


class PrometheusMetricsExporter:
    """
    Export metrics in Prometheus format.
    
    Metrics:
    - model_accuracy_metric
    - prediction_latency_seconds
    - throughput_per_minute
    - data_drift_score
    - prediction_distribution
    """
    
    def __init__(self, service_name: str = "taxi_fare_model"):
        """Initialize metrics exporter."""
        self.service_name = service_name
        self.metrics = {}
        self.history = []
        logger.info(f"[MONITOR] PrometheusMetricsExporter initialized for {service_name}")
    
    def add_metric(self, metric_name: str, value: float, labels: Dict[str, str] = None):
        """Add metric value."""
        if labels is None:
            labels = {}
        
        key = f"{metric_name}_{json.dumps(labels)}"
        self.metrics[key] = {
            'name': metric_name,
            'value': value,
            'labels': labels,
            'timestamp': datetime.now().isoformat()
        }
    
    def export_prometheus_format(self) -> str:
        """Export metrics in Prometheus text format."""
        lines = []
        
        # HELP and TYPE lines
        for metric_key, metric in self.metrics.items():
            metric_name = metric['name']
            
            # Add HELP line (only once per metric)
            if not any(line.startswith(f"# HELP {metric_name}") for line in lines):
                lines.append(f"# HELP {metric_name} {metric_name}")
                lines.append(f"# TYPE {metric_name} gauge")
            
            # Format: metric_name{label1="value1",label2="value2"} value timestamp
            labels_str = ""
            if metric['labels']:
                label_pairs = [f'{k}="{v}"' for k, v in metric['labels'].items()]
                labels_str = "{" + ",".join(label_pairs) + "}"
            
            timestamp_ms = int(datetime.now().timestamp() * 1000)
            lines.append(f"{metric_name}{labels_str} {metric['value']} {timestamp_ms}")
        
        return "\n".join(lines) + "\n"
    
    def save_prometheus_format(self, output_dir: str = "mlops/monitoring") -> str:
        """Save metrics in Prometheus format."""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        metrics_file = output_path / "prometheus_metrics.txt"
        content = self.export_prometheus_format()
        
        with open(metrics_file, 'w') as f:
            f.write(content)
        
        logger.info(f"[MONITOR] Prometheus metrics saved to {metrics_file}")
        return str(metrics_file)


class ModelPerformanceMonitor:
    """
    Monitor model performance in production.
    
    Tracks:
    - Model accuracy
    - Inference latency
    - Throughput
    - Error rates
    """
    
    def __init__(self, model_name: str = "taxi_fare_model"):
        """Initialize monitor."""
        self.model_name = model_name
        self.snapshots = []
        self.current_metrics = {}
        logger.info(f"[MONITOR] ModelPerformanceMonitor initialized for {model_name}")
    
    def record_prediction_batch(
        self,
        y_true: np.ndarray = None,
        y_pred: np.ndarray = None,
        latencies: List[float] = None,
        batch_size: int = None
    ) -> MetricSnapshot:
        """
        Record a batch of predictions and metrics.
        
        Args:
            y_true: True values (optional)
            y_pred: Predictions
            latencies: Latency per sample in seconds
            batch_size: Batch size
            
        Returns:
            MetricSnapshot
        """
        logger.info(f"[MONITOR] Recording batch: {batch_size} samples")
        
        # Calculate accuracy
        if y_true is not None and y_pred is not None:
            mae = np.mean(np.abs(y_true - y_pred))
            mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-6)))
            accuracy = 100 * (1 - min(mape / 100, 1))  # Approximate accuracy
        else:
            accuracy = 0
        
        # Calculate latency metrics
        if latencies:
            latency_ms = np.mean(latencies) * 1000
            throughput = int(60 / np.mean(latencies))  # samples per minute
        else:
            latency_ms = 0
            throughput = 0
        
        # Prediction distribution
        if y_pred is not None:
            pred_mean = float(np.mean(y_pred))
            pred_std = float(np.std(y_pred))
        else:
            pred_mean = 0
            pred_std = 0
        
        snapshot = MetricSnapshot(
            timestamp=datetime.now().isoformat(),
            model_accuracy=accuracy,
            prediction_latency_ms=latency_ms,
            throughput_per_min=throughput,
            prediction_distribution_mean=pred_mean,
            prediction_distribution_std=pred_std,
            data_drift_score=0.0,  # Calculated separately
            batch_size=batch_size or len(y_pred) if y_pred is not None else 0,
            error_rate_pct=0.0
        )
        
        self.snapshots.append(snapshot)
        self.current_metrics = asdict(snapshot)
        
        logger.info(f"[MONITOR] Accuracy: {accuracy:.1f}% | Latency: {latency_ms:.1f}ms | Throughput: {throughput}/min")
        
        return snapshot
    
    def get_performance_summary(self, lookback_hours: int = 24) -> Dict[str, Any]:
        """Get performance summary over time period."""
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
        
        recent = [
            s for s in self.snapshots
            if datetime.fromisoformat(s.timestamp) > cutoff_time
        ]
        
        if not recent:
            return {
                'lookback_hours': lookback_hours,
                'samples': 0,
                'message': 'No data for period'
            }
        
        accuracies = [s.model_accuracy for s in recent]
        latencies = [s.prediction_latency_ms for s in recent]
        throughputs = [s.throughput_per_min for s in recent]
        
        return {
            'lookback_hours': lookback_hours,
            'samples': len(recent),
            'accuracy': {
                'mean': float(np.mean(accuracies)),
                'min': float(np.min(accuracies)),
                'max': float(np.max(accuracies)),
                'std': float(np.std(accuracies))
            },
            'latency_ms': {
                'mean': float(np.mean(latencies)),
                'min': float(np.min(latencies)),
                'max': float(np.max(latencies)),
                'p99': float(np.percentile(latencies, 99))
            },
            'throughput_per_min': {
                'mean': int(np.mean(throughputs)),
                'min': int(np.min(throughputs)),
                'max': int(np.max(throughputs))
            }
        }


class DataDriftMonitor:
    """
    Monitor data distribution drift.
    
    Compares current data against baseline using:
    - Kolmogorov-Smirnov test
    - Population Stability Index (PSI)
    - Distribution comparison
    """
    
    def __init__(self, baseline_data: pd.DataFrame = None):
        """Initialize drift monitor."""
        self.baseline_data = baseline_data
        self.drift_history = []
        logger.info("[MONITOR] DataDriftMonitor initialized")
    
    def calculate_psi(
        self,
        baseline: np.ndarray,
        current: np.ndarray,
        bins: int = 10
    ) -> float:
        """
        Calculate Population Stability Index (PSI).
        
        PSI > 0.25: Significant drift
        PSI > 0.10: Potential drift
        PSI < 0.10: Acceptable
        
        Args:
            baseline: Baseline distribution
            current: Current distribution
            bins: Number of bins
            
        Returns:
            PSI score
        """
        baseline = baseline[~np.isnan(baseline)]
        current = current[~np.isnan(current)]
        
        # Create bins based on baseline
        bin_edges = np.histogram_bin_edges(baseline, bins=bins)
        
        # Calculate proportions
        baseline_counts, _ = np.histogram(baseline, bins=bin_edges)
        current_counts, _ = np.histogram(current, bins=bin_edges)
        
        baseline_pct = baseline_counts / baseline_counts.sum()
        current_pct = current_counts / current_counts.sum()
        
        # Avoid division by zero
        baseline_pct = np.where(baseline_pct == 0, 0.001, baseline_pct)
        current_pct = np.where(current_pct == 0, 0.001, current_pct)
        
        # Calculate PSI
        psi = np.sum((current_pct - baseline_pct) * np.log(current_pct / baseline_pct))
        
        return float(psi)
    
    def detect_drift(
        self,
        current_data: pd.DataFrame,
        columns: List[str] = None,
        psi_threshold: float = 0.1
    ) -> Dict[str, Any]:
        """
        Detect drift across columns.
        
        Args:
            current_data: Current dataset
            columns: Columns to check (default: all numeric)
            psi_threshold: PSI threshold for drift
            
        Returns:
            Drift detection results
        """
        if self.baseline_data is None:
            logger.warning("[MONITOR] No baseline data for drift detection")
            return {'error': 'No baseline data'}
        
        if columns is None:
            columns = current_data.select_dtypes(include=[np.number]).columns.tolist()
        
        drift_results = {
            'timestamp': datetime.now().isoformat(),
            'columns_checked': len(columns),
            'drifted_columns': [],
            'psi_scores': {},
            'drift_detected': False
        }
        
        for col in columns:
            if col not in self.baseline_data.columns:
                continue
            
            baseline_vals = self.baseline_data[col].dropna().values
            current_vals = current_data[col].dropna().values
            
            psi = self.calculate_psi(baseline_vals, current_vals)
            drift_results['psi_scores'][col] = float(psi)
            
            if psi > psi_threshold:
                drift_results['drifted_columns'].append(col)
                drift_results['drift_detected'] = True
                logger.warning(f"[MONITOR] Drift detected in {col}: PSI={psi:.3f}")
        
        # Calculate overall drift score
        if drift_results['psi_scores']:
            drift_results['overall_psi'] = float(np.mean(list(drift_results['psi_scores'].values())))
        
        self.drift_history.append(drift_results)
        
        return drift_results


class GrafanaDashboardGenerator:
    """Generate Grafana dashboard JSON configuration."""
    
    @staticmethod
    def generate_model_monitoring_dashboard() -> Dict[str, Any]:
        """Generate model monitoring dashboard configuration."""
        dashboard = {
            "dashboard": {
                "title": "Taxi Fare Model Monitoring",
                "tags": ["MLOps", "Model Monitoring"],
                "timezone": "browser",
                "panels": [
                    {
                        "title": "Model Accuracy",
                        "targets": [
                            {"expr": "model_accuracy_metric"}
                        ],
                        "type": "graph",
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "title": "Prediction Latency (ms)",
                        "targets": [
                            {"expr": "prediction_latency_seconds * 1000"}
                        ],
                        "type": "graph",
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "title": "Throughput (samples/min)",
                        "targets": [
                            {"expr": "throughput_per_minute"}
                        ],
                        "type": "graph",
                        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "title": "Data Drift Score",
                        "targets": [
                            {"expr": "data_drift_score"}
                        ],
                        "type": "graph",
                        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8},
                        "alert": {
                            "name": "Drift Alert",
                            "conditions": [
                                {
                                    "evaluator": {"type": "gt"},
                                    "operator": {"type": "and"},
                                    "query": {"params": ["data_drift_score", "5m", "now"]},
                                    "reducer": {"type": "avg"},
                                    "type": "query",
                                    "value": 0.25
                                }
                            ]
                        }
                    },
                    {
                        "title": "Prediction Distribution",
                        "targets": [
                            {"expr": "prediction_distribution_mean"},
                            {"expr": "prediction_distribution_std"}
                        ],
                        "type": "graph",
                        "gridPos": {"x": 0, "y": 16, "w": 12, "h": 8}
                    },
                    {
                        "title": "Error Rate (%)",
                        "targets": [
                            {"expr": "error_rate_pct"}
                        ],
                        "type": "stat",
                        "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8},
                        "alert": {
                            "name": "Error Rate Alert",
                            "conditions": [
                                {
                                    "evaluator": {"type": "gt"},
                                    "value": 5.0
                                }
                            ]
                        }
                    }
                ]
            },
            "overwrite": True
        }
        
        return dashboard
    
    @staticmethod
    def generate_data_quality_dashboard() -> Dict[str, Any]:
        """Generate data quality monitoring dashboard."""
        dashboard = {
            "dashboard": {
                "title": "Data Quality Monitoring",
                "tags": ["MLOps", "Data Quality"],
                "timezone": "browser",
                "panels": [
                    {
                        "title": "Null Values by Column",
                        "type": "bargauge",
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "title": "Data Validation Pass Rate",
                        "type": "stat",
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "title": "Distribution Drift by Feature",
                        "type": "heatmap",
                        "gridPos": {"x": 0, "y": 8, "w": 24, "h": 8}
                    },
                    {
                        "title": "Record Count Over Time",
                        "type": "graph",
                        "gridPos": {"x": 0, "y": 16, "w": 12, "h": 8}
                    },
                    {
                        "title": "Data Quality Score",
                        "type": "gauge",
                        "gridPos": {"x": 12, "y": 16, "w": 12, "h": 8}
                    }
                ]
            },
            "overwrite": True
        }
        
        return dashboard
    
    @staticmethod
    def generate_inference_pipeline_dashboard() -> Dict[str, Any]:
        """Generate inference pipeline monitoring dashboard."""
        dashboard = {
            "dashboard": {
                "title": "Inference Pipeline Status",
                "tags": ["MLOps", "Pipeline"],
                "timezone": "browser",
                "panels": [
                    {
                        "title": "API Response Time (p50, p95, p99)",
                        "type": "graph",
                        "gridPos": {"x": 0, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "title": "Requests per Second",
                        "type": "graph",
                        "gridPos": {"x": 12, "y": 0, "w": 12, "h": 8}
                    },
                    {
                        "title": "HTTP Status Code Distribution",
                        "type": "piechart",
                        "gridPos": {"x": 0, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "title": "Failed Predictions",
                        "type": "stat",
                        "gridPos": {"x": 12, "y": 8, "w": 12, "h": 8}
                    },
                    {
                        "title": "Model Version Active",
                        "type": "stat",
                        "gridPos": {"x": 0, "y": 16, "w": 24, "h": 4}
                    }
                ]
            },
            "overwrite": True
        }
        
        return dashboard


def save_grafana_dashboards(output_dir: str = "mlops/monitoring") -> Dict[str, str]:
    """
    Save all Grafana dashboard configurations.
    
    Args:
        output_dir: Output directory
        
    Returns:
        Dictionary mapping dashboard names to file paths
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    dashboards = {
        'model_monitoring': GrafanaDashboardGenerator.generate_model_monitoring_dashboard(),
        'data_quality': GrafanaDashboardGenerator.generate_data_quality_dashboard(),
        'inference_pipeline': GrafanaDashboardGenerator.generate_inference_pipeline_dashboard()
    }
    
    saved_files = {}
    for name, dashboard_config in dashboards.items():
        filepath = output_path / f"grafana_dashboard_{name}.json"
        with open(filepath, 'w') as f:
            json.dump(dashboard_config, f, indent=2)
        
        saved_files[name] = str(filepath)
        logger.info(f"[MONITOR] Dashboard saved: {filepath}")
    
    return saved_files


def create_monitoring_setup() -> Dict[str, Any]:
    """
    Create complete monitoring setup.
    
    Returns:
        Setup configuration
    """
    logger.info("[MONITOR] Creating monitoring setup...")
    
    setup = {
        'timestamp': datetime.now().isoformat(),
        'components': {
            'prometheus': {
                'port': 9090,
                'scrape_interval': '15s',
                'metrics_file': 'mlops/monitoring/prometheus_metrics.txt'
            },
            'grafana': {
                'port': 3000,
                'dashboards': save_grafana_dashboards(),
                'default_datasource': 'Prometheus'
            },
            'monitoring': {
                'model_performance': 'Enabled',
                'data_drift': 'Enabled',
                'data_quality': 'Enabled',
                'alerts': 'Configured'
            }
        }
    }
    
    logger.info("[MONITOR] Monitoring setup complete")
    
    return setup
