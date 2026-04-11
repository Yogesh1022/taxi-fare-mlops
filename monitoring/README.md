# Monitoring and Observability

Complete monitoring and observability stack for Taxi Fare MLOps pipeline using Prometheus, Grafana, Jaeger, and ELK Stack.

## Overview

This monitoring solution provides:

- **Metrics**: Prometheus for time-series metrics collection and alerting
- **Visualization**: Grafana for metrics dashboards and alerting
- **Tracing**: Jaeger for distributed tracing and request flow analysis
- **Logging**: ELK Stack (Elasticsearch, Logstash, Kibana) for centralized logging
- **Structured Logging**: JSON-based logging for easy parsing and analysis

## Architecture

```
┌─────────────────────────────────────┐
│   Taxi Fare MLOps Applications      │
│  (API, Training, Feature Store)     │
└────────────┬────────────────────────┘
             │
    ┌────────┴──────────┬─────────┬──────────┐
    │                   │         │          │
Metrics             Traces     Logs    Health Checks
    │                   │         │          │
┌───▼────┐         ┌────▼──┐  ┌─▼────┐     │
│Prometheus
         │         │Jaeger │  │Logstash   (Readiness)
└───┬────┘         └────┬──┘  └─┬────┘     │
    │                   │        │         │
    └───────────────────┴────────┴─────────┘
                        │
            ┌───────────▼───────────┐
            │ Storage / Databases   │
            │ - Prometheus          │
            │ - Elasticsearch       │
            │ - Jaeger Storage      │
            └───────────┬───────────┘
                        │
            ┌───────────▼───────────┐
            │ Visualization Layer   │
            │ - Grafana Dashboards  │
            │ - Kibana Log Analysis │
            │ - Jaeger UI           │
            └───────────────────────┘
```

## Components

### 1. Prometheus
- **Purpose**: Metrics collection and alerting
- **Features**:
  - Scrapes metrics from /metrics endpoint
  - Rules-based alerting
  - Data retention policies
  - Service discovery

**Key Metrics**:
- API request count and latency
- Model prediction latency and success rate
- Data quality scores
- System resource usage

### 2. Grafana
- **Purpose**: Metrics visualization and alerting
- **Features**:
  - Pre-configured dashboards
  - Alert management
  - Multi-datasource support
  - RBAC and team management

**Pre-built Dashboards**:
- API Performance Dashboard
- Model Performance Dashboard
- Infrastructure Dashboard
- Data Quality Dashboard

### 3. Jaeger
- **Purpose**: Distributed tracing
- **Features**:
  - Request trace flow visualization
  - Service dependency mapping
  - Latency analysis
  - Error tracking

**Trace Scenarios**:
- API request end-to-end trace
- Model serving pipeline trace
- Data validation pipeline trace

### 4. ELK Stack

#### Elasticsearch
- Central log storage
- Full-text search
- Index management
- Cluster management

#### Logstash
- Log processing and enrichment
- Filter rules for log categorization
- Forwarding to Elasticsearch
- Metrics extraction

#### Kibana
- Log visualization
- Interactive log analysis
- Dashboard creation
- Alert configuration

**Log Types**:
- Application logs
- API access logs
- Model training logs
- Data validation logs
- System logs

## Quick Start

### Local Development

```bash
# Start monitoring stack
cd monitoring/docker
docker-compose up -d

# Verify services
docker-compose ps

# Access dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# Jaeger: http://localhost:16686
# Kibana: http://localhost:5601
```

### Kubernetes Production

```bash
# Create namespace
kubectl create namespace taxi-fare-prod

# Deploy stack
kubectl apply -f monitoring/kubernetes/

# Verify
kubectl get pods -n taxi-fare-prod

# Access dashboards
kubectl port-forward -n taxi-fare-prod svc/grafana 3000:3000
kubectl port-forward -n taxi-fare-prod svc/jaeger-query 16686:16686
```

## Integration

### Application Instrumentation

```python
from src.monitoring import setup_monitoring, track_latency, track_request

# Setup
app = Flask(__name__)
tracing, logger = setup_monitoring(app, service_name="taxi-fare-api")

# Track latency
@track_latency("model_inference")
def predict(input_data):
    return model.predict(input_data)

# Track request
@track_request("predict_endpoint")
def predict_api():
    return predict(request.json)

# Emit logs
logger.info("prediction_complete", prediction=result)
```

### Metrics Available

- `api_requests_total`: Total API requests by endpoint, method, status
- `api_request_duration_seconds`: Request latency histogram
- `model_inference_duration_seconds`: Model inference latency
- `model_predictions_total`: Total predictions by status
- `data_quality_score`: Data quality metrics
- `training_duration_seconds`: Training job duration
- `model_accuracy`: Model accuracy scores

### Log Levels

- `INFO`: General information (predictions, requests)
- `WARNING`: Non-critical issues (data quality degradation)
- `ERROR`: Errors (failed predictions, validation errors)
- `DEBUG`: Detailed information for troubleshooting

## Dashboards

### API Performance Dashboard
- Request rate (RPS)
- Latency percentiles (p50, p95, p99)
- Error rate
- Endpoint breakdown

### Model Performance Dashboard
- Inference latency
- Prediction volume
- Success/error rates
- Model accuracy over time

### Infrastructure Dashboard
- Pod resource usage
- Container restarts
- Network I/O
- Storage usage

### Data Quality Dashboard
- Quality scores by dataset
- Data validation results
- Data drift detection
- Record counts and distributions

## Alerts

Pre-configured alerts for:
- High API latency
- Elevated error rates
- Model accuracy degradation
- Data quality issues
- Storage capacity warnings
- Component health checks

## Troubleshooting

### Prometheus

```bash
# Check scrape targets
curl http://localhost:9090/api/v1/targets | jq .

# Check for scrape errors
curl http://localhost:9090/api/v1/query?query=up | jq .
```

### Jaeger

```bash
# Check collector endpoint
curl http://localhost:14268/

# View traces
# Go to http://localhost:16686
# Search by service or trace ID
```

### Elasticsearch

```bash
# Check cluster health
curl http://localhost:9200/_cluster/health | jq .

# List indices
curl http://localhost:9200/_cat/indices

# Check storage
curl http://localhost:9200/_cat/allocation | jq .
```

## Configuration Files

- [prometheus.yaml](prometheus/prometheus.yaml) - Prometheus configuration
- [grafana.yaml](grafana/grafana.yaml) - Grafana deployment
- [jaeger.yaml](jaeger/jaeger.yaml) - Jaeger deployment
- [elk-stack.yaml](elk/elk-stack.yaml) - ELK stack deployment
- [docker-compose.yml](docker/docker-compose.yml) - Local development setup

## Documentation

- [Integration Guide](INTEGRATION_GUIDE.md) - How to integrate components
- [Deployment Guide](DEPLOYMENT_GUIDE.md) - Deployment instructions
- [API Example](api_example.py) - Example instrumented Flask API
- [Monitoring Client](../src/monitoring/__init__.py) - Client library

## Performance Tuning

- **Prometheus Retention**: Adjust based on storage capacity
- **Scrape Interval**: Increase for high-traffic systems
- **Elasticsearch Heap**: Increase for large volumes
- **Logstash Pipeline**: Optimize filter rules
- **Jaeger Sampling**: Adjust sampling rate for high-traffic services

## Best Practices

1. **Instrumentation**
   - Add latency tracking to critical operations
   - Use structured logging for all important events
   - Implement circuit breakers with metrics

2. **Alerting**
   - Alert on business metrics (accuracy, quality)
   - Alert on infrastructure (capacity, health)
   - Avoid alert fatigue with proper thresholds

3. **Dashboard Design**
   - Focus on actionable metrics
   - Use drill-down dashboards for detail
   - Include alerts and thresholds

4. **Storage**
   - Configure retention policies
   - Archive old data
   - Monitor storage usage

5. **Security**
   - Restrict access to sensitive dashboards
   - Use authentication for Grafana/Kibana
   - Enable HTTPS for external access

## Next Steps

1. Deploy monitoring stack in dev environment
2. Instrument core application components
3. Create custom dashboards for business metrics
4. Set up alerting rules and notification channels
5. Configure backup and disaster recovery
6. Implement monitoring for monitoring stack

## Support

For issues or questions:
1. Check [Troubleshooting](#troubleshooting) section
2. Review component logs
3. Consult [Integration Guide](INTEGRATION_GUIDE.md)
4. Check component documentation (Prometheus, Grafana, Jaeger, Elasticsearch)

## References

- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)
- [Jaeger Documentation](https://www.jaegertracing.io/docs/)
- [Elasticsearch Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/)
- [OpenTelemetry Documentation](https://opentelemetry.io/docs/)
