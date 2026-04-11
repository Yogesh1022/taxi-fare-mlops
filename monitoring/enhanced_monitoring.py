"""
Enhanced Monitoring Client Library
Day 13: Advanced Monitoring & Drift Detection

Integrates:
- Prometheus metrics collection
- Jaeger distributed tracing
- ELK Stack log forwarding
- Data quality monitoring
- Business KPI tracking
- Drift detection
"""

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from functools import wraps
import time
import logging
from typing import Any, Callable, Dict, Optional
import json

# Configure logging with ELK support
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class EnhancedMonitoringClient:
    """Enhanced monitoring client with drift detection and business KPI support."""
    
    def __init__(self, 
                 service_name: str = "taxi-fare-prediction",
                 prometheus_port: int = 8000,
                 jaeger_host: str = "localhost",
                 jaeger_port: int = 6831,
                 enable_jaeger: bool = True,
                 enable_prometheus: bool = True):
        """
        Initialize enhanced monitoring client.
        
        Args:
            service_name: Service name for tracing and metrics
            prometheus_port: Prometheus metrics port
            jaeger_host: Jaeger agent host
            jaeger_port: Jaeger agent port
            enable_jaeger: Enable distributed tracing
            enable_prometheus: Enable Prometheus metrics
        """
        self.service_name = service_name
        self.registry = CollectorRegistry()
        
        # Initialize Jaeger tracing
        if enable_jaeger:
            jaeger_exporter = JaegerExporter(
                agent_host_name=jaeger_host,
                agent_port=jaeger_port,
            )
            trace.set_tracer_provider(TracerProvider())
            trace.get_tracer_provider().add_span_processor(
                BatchSpanProcessor(jaeger_exporter)
            )
            self.tracer = trace.get_tracer(__name__)
        else:
            self.tracer = None
        
        # Initialize Prometheus metrics  
        if enable_prometheus:
            self._init_prometheus_metrics()
        
        logger.info(f"Enhanced monitoring initialized for {service_name}")
    
    def _init_prometheus_metrics(self):
        """Initialize Prometheus metrics."""
        # Model performance metrics
        self.model_predictions_total = Counter(
            'model_predictions_total',
            'Total predictions made',
            ['model_name', 'status'],
            registry=self.registry
        )
        
        self.model_inference_duration = Histogram(
            'model_inference_duration_seconds',
            'Model inference duration in seconds',
            ['model_name'],
            registry=self.registry,
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0)
        )
        
        self.model_accuracy = Gauge(
            'model_accuracy',
            'Current model accuracy',
            ['model_name'],
            registry=self.registry
        )
        
        # Data quality metrics
        self.data_quality_score = Gauge(
            'data_quality_score',
            'Overall data quality score (0-1)',
            ['dataset'],
            registry=self.registry
        )
        
        self.data_quality_missing_values = Gauge(
            'data_quality_missing_values_ratio',
            'Ratio of missing values',
            ['dataset', 'feature'],
            registry=self.registry
        )
        
        self.data_quality_outliers = Gauge(
            'data_quality_outlier_ratio',
            'Ratio of outliers',
            ['dataset', 'feature'],
            registry=self.registry
        )
        
        self.data_drift_detected = Counter(
            'data_drift_detected_total',
            'Total drift detection events',
            ['feature', 'dataset'],
            registry=self.registry
        )
        
        self.data_validation_failures = Counter(
            'data_validation_failures_total',
            'Total validation failures',
            ['validation_type', 'dataset'],
            registry=self.registry
        )
        
        # API metrics
        self.api_requests_total = Counter(
            'api_requests_total',
            'Total API requests',
            ['endpoint', 'status'],
            registry=self.registry
        )
        
        self.api_request_duration = Histogram(
            'api_request_duration_seconds',
            'API request duration',
            ['endpoint'],
            registry=self.registry,
            buckets=(0.01, 0.05, 0.1, 0.5, 1.0, 2.5, 5.0)
        )
        
        # Business KPI metrics
        self.taxi_accuracy = Gauge(
            'taxi_model_accuracy',
            'Taxi fare prediction accuracy',
            ['borough'],
            registry=self.registry
        )
        
        self.taxi_revenue_impact = Gauge(
            'taxi_revenue_impact',
            'Estimated revenue impact in dollars',
            ['borough'],
            registry=self.registry
        )
    
    def track_prediction(self, 
                        model_name: str,
                        inference_time_ms: float,
                        status: str = 'success',
                        accuracy: Optional[float] = None,
                        metadata: Optional[Dict[str, Any]] = None):
        """
        Track a model prediction.
        
        Args:
            model_name: Name of the model
            inference_time_ms: Inference time in milliseconds
            status: Prediction status (success, error, etc.)
            accuracy: Prediction accuracy if available
            metadata: Additional metadata to log
        """
        if self.tracer:
            with self.tracer.start_as_current_span(f"predict_{model_name}") as span:
                span.set_attribute("model_name", model_name)
                span.set_attribute("inference_time_ms", inference_time_ms)
                span.set_attribute("status", status)
                
                self.model_predictions_total.labels(
                    model_name=model_name,
                    status=status
                ).inc()
                
                self.model_inference_duration.labels(
                    model_name=model_name
                ).observe(inference_time_ms / 1000.0)
                
                if accuracy is not None:
                    self.model_accuracy.labels(model_name=model_name).set(accuracy)
        
        # Log prediction
        log_entry = {
            'event': 'prediction',
            'model_name': model_name,
            'inference_time_ms': inference_time_ms,
            'status': status,
            'accuracy': accuracy,
        }
        if metadata:
            log_entry.update(metadata)
        
        logger.info(json.dumps(log_entry))
    
    def track_data_quality(self,
                          dataset_name: str,
                          quality_score: float,
                          missing_values: Optional[Dict[str, float]] = None,
                          outliers: Optional[Dict[str, float]] = None,
                          issues: Optional[list] = None):
        """
        Track data quality metrics.
        
        Args:
            dataset_name: Name of the dataset
            quality_score: Overall quality score (0-1)
            missing_values: Dict of feature -> missing ratio
            outliers: Dict of feature -> outlier ratio
            issues: List of quality issues detected
        """
        self.data_quality_score.labels(dataset=dataset_name).set(quality_score)
        
        if missing_values:
            for feature, ratio in missing_values.items():
                self.data_quality_missing_values.labels(
                    dataset=dataset_name,
                    feature=feature
                ).set(ratio)
        
        if outliers:
            for feature, ratio in outliers.items():
                self.data_quality_outliers.labels(
                    dataset=dataset_name,
                    feature=feature
                ).set(ratio)
        
        # Log data quality event
        log_entry = {
            'event': 'data_quality_check',
            'dataset': dataset_name,
            'quality_score': quality_score,
            'issues_count': len(issues) if issues else 0,
            'issues': issues or []
        }
        
        if quality_score < 0.8:
            logger.warning(json.dumps(log_entry))
        else:
            logger.info(json.dumps(log_entry))
    
    def track_drift_detection(self,
                            feature: str,
                            dataset_name: str,
                            drift_score: float,
                            threshold: float = 0.5,
                            metadata: Optional[Dict[str, Any]] = None):
        """
        Track drift detection event.
        
        Args:
            feature: Feature name
            dataset_name: Dataset name
            drift_score: Drift score
            threshold: Drift threshold
            metadata: Additional metadata
        """
        if drift_score > threshold:
            self.data_drift_detected.labels(
                feature=feature,
                dataset=dataset_name
            ).inc()
            
            log_entry = {
                'event': 'drift_detected',
                'feature': feature,
                'dataset': dataset_name,
                'drift_score': drift_score,
                'threshold': threshold,
                'severity': 'high' if drift_score > threshold * 1.5 else 'medium'
            }
            if metadata:
                log_entry.update(metadata)
            
            logger.warning(json.dumps(log_entry))
    
    def track_api_request(self, 
                         endpoint: str,
                         duration_ms: float,
                         status_code: int):
        """
        Track API request metrics.
        
        Args:
            endpoint: API endpoint
            duration_ms: Request duration in milliseconds
            status_code: HTTP status code
        """
        status = 'success' if 200 <= status_code < 300 else 'error'
        
        self.api_requests_total.labels(
            endpoint=endpoint,
            status=status
        ).inc()
        
        self.api_request_duration.labels(
            endpoint=endpoint
        ).observe(duration_ms / 1000.0)
        
        log_entry = {
            'event': 'api_request',
            'endpoint': endpoint,
            'duration_ms': duration_ms,
            'status_code': status_code
        }
        
        if status_code >= 400:
            logger.error(json.dumps(log_entry))
        else:
            logger.info(json.dumps(log_entry))
    
    def track_business_kpi(self,
                          metric_name: str,
                          value: float,
                          borough: str = 'overall',
                          metadata: Optional[Dict[str, Any]] = None):
        """
        Track business KPI metrics.
        
        Args:
            metric_name: KPI metric name
            value: Metric value
            borough: Geographic borough
            metadata: Additional metadata
        """
        if metric_name == 'accuracy':
            self.taxi_accuracy.labels(borough=borough).set(value)
        elif metric_name == 'revenue_impact':
            self.taxi_revenue_impact.labels(borough=borough).set(value)
        
        log_entry = {
            'event': 'business_kpi',
            'metric_name': metric_name,
            'value': value,
            'borough': borough
        }
        if metadata:
            log_entry.update(metadata)
        
        logger.info(json.dumps(log_entry))
    
    def track_latency(self, operation_name: str = None):
        """
        Decorator to track operation latency.
        
        Usage:
            @monitor.track_latency("data_processing")
            def process_data(): pass
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                op_name = operation_name or func.__name__
                start_time = time.time()
                
                try:
                    result = func(*args, **kwargs)
                    return result
                finally:
                    duration_ms = (time.time() - start_time) * 1000
                    logger.info(json.dumps({
                        'event': 'operation_latency',
                        'operation': op_name,
                        'duration_ms': duration_ms
                    }))
            
            return wrapper
        
        return decorator
    
    def get_registry(self):
        """Get Prometheus CollectorRegistry for serving metrics."""
        return self.registry


# Global monitoring client instance
_monitoring_client: Optional[EnhancedMonitoringClient] = None


def init_monitoring(service_name: str = "taxi-fare-prediction", **kwargs) -> EnhancedMonitoringClient:
    """Initialize global monitoring client."""
    global _monitoring_client
    _monitoring_client = EnhancedMonitoringClient(service_name=service_name, **kwargs)
    return _monitoring_client


def get_monitoring_client() -> Optional[EnhancedMonitoringClient]:
    """Get global monitoring client instance."""
    return _monitoring_client
