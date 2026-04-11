# Monitoring Client Library

"""
Monitoring utilities for application instrumentation with Prometheus metrics,
OpenTelemetry traces, and structured logging.
"""

import time
import functools
import logging
import json
from typing import Any, Callable, Optional, Dict
from datetime import datetime
from pathlib import Path

from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry
from prometheus_client.core import REGISTRY as prometheus_registry
import structlog
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor


# ============================================================================
# Metrics
# ============================================================================

class MetricsRegistry:
    """Centralized metrics registry for the application."""
    
    def __init__(self, namespace: str = "taxi_fare"):
        self.namespace = namespace
        self.registry = CollectorRegistry()
        self._metrics = {}
    
    def _get_metric_name(self, name: str) -> str:
        return f"{self.namespace}_{name}"
    
    def counter(
        self,
        name: str,
        documentation: str,
        labelnames: Optional[list] = None
    ) -> Counter:
        """Create or get a counter metric."""
        metric_name = self._get_metric_name(name)
        if metric_name not in self._metrics:
            self._metrics[metric_name] = Counter(
                metric_name,
                documentation,
                labelnames=labelnames or [],
                registry=self.registry
            )
        return self._metrics[metric_name]
    
    def histogram(
        self,
        name: str,
        documentation: str,
        labelnames: Optional[list] = None,
        buckets: Optional[tuple] = None
    ) -> Histogram:
        """Create or get a histogram metric."""
        metric_name = self._get_metric_name(name)
        if metric_name not in self._metrics:
            kwargs = {
                'documentation': documentation,
                'labelnames': labelnames or [],
                'registry': self.registry
            }
            if buckets:
                kwargs['buckets'] = buckets
            self._metrics[metric_name] = Histogram(metric_name, **kwargs)
        return self._metrics[metric_name]
    
    def gauge(
        self,
        name: str,
        documentation: str,
        labelnames: Optional[list] = None
    ) -> Gauge:
        """Create or get a gauge metric."""
        metric_name = self._get_metric_name(name)
        if metric_name not in self._metrics:
            self._metrics[metric_name] = Gauge(
                metric_name,
                documentation,
                labelnames=labelnames or [],
                registry=self.registry
            )
        return self._metrics[metric_name]


# Global metrics registry
_metrics_registry = MetricsRegistry()

# API metrics
api_requests_total = _metrics_registry.counter(
    "api_requests_total",
    "Total API requests",
    labelnames=["endpoint", "method", "status"]
)

api_request_duration_seconds = _metrics_registry.histogram(
    "api_request_duration_seconds",
    "API request duration in seconds",
    labelnames=["endpoint", "method"],
    buckets=(0.01, 0.025, 0.05, 0.075, 0.1, 0.25, 0.5, 0.75, 1.0, 2.5, 5.0)
)

# Model metrics
model_inference_duration_seconds = _metrics_registry.histogram(
    "model_inference_duration_seconds",
    "Model inference duration in seconds",
    labelnames=["model_name"],
    buckets=(0.01, 0.05, 0.1, 0.5, 1.0)
)

model_predictions_total = _metrics_registry.counter(
    "model_predictions_total",
    "Total model predictions",
    labelnames=["model_name", "status"]
)

# Training metrics
training_duration_seconds = _metrics_registry.gauge(
    "training_duration_seconds",
    "Training duration in seconds",
    labelnames=["model_name", "run_id"]
)

model_accuracy = _metrics_registry.gauge(
    "model_accuracy",
    "Model accuracy score",
    labelnames=["model_name", "run_id"]
)

# Data quality metrics
data_quality_score = _metrics_registry.gauge(
    "data_quality_score",
    "Data quality score",
    labelnames=["dataset"]
)


# ============================================================================
# Tracing
# ============================================================================

class TracingSetup:
    """Setup and manage OpenTelemetry tracing."""
    
    def __init__(
        self,
        service_name: str,
        jaeger_host: str = "localhost",
        jaeger_port: int = 6831
    ):
        self.service_name = service_name
        
        # Create Jaeger exporter
        jaeger_exporter = JaegerExporter(
            agent_host_name=jaeger_host,
            agent_port=jaeger_port,
        )
        
        # Create and set tracer provider
        trace_provider = TracerProvider()
        trace_provider.add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )
        trace.set_tracer_provider(trace_provider)
        
        self.tracer = trace.get_tracer(__name__)
    
    def instrument_flask(self, app):
        """Instrument Flask application."""
        FlaskInstrumentor().instrument_app(app)
    
    def instrument_requests(self):
        """Instrument requests library."""
        RequestsInstrumentor().instrument()
    
    def instrument_sqlalchemy(self, engine):
        """Instrument SQLAlchemy."""
        SQLAlchemyInstrumentor().instrument(engine=engine)


# ============================================================================
# Logging
# ============================================================================

class StructuredLogger:
    """Structured logging setup with JSON output."""
    
    def __init__(
        self,
        name: str,
        level: str = "INFO",
        log_dir: str = "logs"
    ):
        self.name = name
        self.level = level
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure structlog
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            cache_logger_on_first_use=True,
        )
        
        self.logger = structlog.get_logger(name)
    
    def info(self, msg: str, **kwargs):
        """Log info level."""
        self.logger.info(msg, **kwargs)
    
    def error(self, msg: str, **kwargs):
        """Log error level."""
        self.logger.error(msg, **kwargs)
    
    def warning(self, msg: str, **kwargs):
        """Log warning level."""
        self.logger.warning(msg, **kwargs)
    
    def debug(self, msg: str, **kwargs):
        """Log debug level."""
        self.logger.debug(msg, **kwargs)


# ============================================================================
# Decorators
# ============================================================================

def track_latency(operation_name: str):
    """Decorator to track operation latency."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                return result
            finally:
                duration = time.time() - start_time
                model_inference_duration_seconds.labels(
                    model_name=operation_name
                ).observe(duration)
        return wrapper
    return decorator


def track_request(endpoint: str):
    """Decorator to track API requests."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            status = "unknown"
            try:
                result = func(*args, **kwargs)
                status = "success"
                return result
            except Exception as e:
                status = "error"
                raise
            finally:
                duration = time.time() - start_time
                api_request_duration_seconds.labels(
                    endpoint=endpoint,
                    method="post"
                ).observe(duration)
                api_requests_total.labels(
                    endpoint=endpoint,
                    method="post",
                    status=status
                ).inc()
        return wrapper
    return decorator


def log_training_metrics(func: Callable) -> Callable:
    """Decorator to log training metrics."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        logger = StructuredLogger("training")
        start_time = time.time()
        
        try:
            result = func(*args, **kwargs)
            duration = time.time() - start_time
            
            logger.info(
                "training_complete",
                duration=duration,
                model_name=kwargs.get("model_name", "unknown")
            )
            
            return result
        except Exception as e:
            logger.error(
                "training_failed",
                error=str(e),
                model_name=kwargs.get("model_name", "unknown")
            )
            raise
    
    return wrapper


# ============================================================================
# Initialization Functions
# ============================================================================

def setup_monitoring(
    app,
    service_name: str = "taxi-fare-api",
    jaeger_host: str = "localhost",
    jaeger_port: int = 6831
):
    """Setup all monitoring components."""
    
    # Setup tracing
    tracing = TracingSetup(
        service_name=service_name,
        jaeger_host=jaeger_host,
        jaeger_port=jaeger_port
    )
    tracing.instrument_flask(app)
    tracing.instrument_requests()
    
    # Setup logging
    logger = StructuredLogger(service_name)
    logger.info("monitoring_initialized", service=service_name)
    
    return tracing, logger


def get_metrics_registry():
    """Get the global metrics registry."""
    return _metrics_registry
