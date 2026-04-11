# Monitoring Integration Guide

## Overview
This guide explains how to integrate Prometheus, Grafana, Jaeger, and ELK stack with the Taxi Fare MLOps pipeline.

## Architecture
```
┌─────────────────────────────────────────────────────────┐
│                 Taxi Fare Applications                   │
│  (API, Training Pipeline, MLflow, Feature Store)         │
└────────────────┬──────────────────────────────────────────┘
                 │
        ┌────────┴─────────┬──────────────┬─────────────┐
        │                  │              │             │
    Metrics           Traces           Logs        Health Checks
        │                  │              │             │
    ┌───▼────┐        ┌────▼─────┐  ┌───▼────┐    (Readiness)
    │Prometheus
    │         │        │  Jaeger  │  │Logstash│
    └───┬────┘        └────┬─────┘  └───┬────┘
        │                  │            │
        └──────┬───────────┴────────────┘
               │
        ┌──────▼──────────────────┐
        │   Centralized Storage   │
        │ (Prometheus | ES)       │
        └──────┬──────────────────┘
               │
        ┌──────▼──────────────────┐
        │  Visualization Layer    │
        │(Grafana | Kibana)       │
        └──────────────────────────┘
```

## Components Integration

### 1. Application Instrumentation

All applications should emit metrics to Prometheus and logs to Logstash:

```python
from monitoring.metrics import setup_metrics, track_latency, track_request
from monitoring.logging import setup_logging

# Setup monitoring
setup_metrics(app)
setup_logging("taxi-fare-api")

@app.route("/predict", methods=["POST"])
@track_latency("prediction_inference")
@track_request("predict")
def predict():
    # Your prediction logic
    pass
```

### 2. MLflow Integration

MLflow server emits metrics automatically to Prometheus:

```yaml
mlflow:
  tracking_uri: http://localhost:5000
  backend_store_uri: postgresql://user:pass@postgres:5432/mlflow
  default_artifact_root: /tmp/mlflow-artifacts
```

### 3. Training Pipeline Instrumentation

```python
from monitoring.training import log_training_metrics

@log_training_metrics
def train_model(config):
    # Training code
    pass
```

## Deployment Steps

### Prerequisites
- Kubernetes cluster
- kubectl configured
- Helm (optional, for package management)

### 1. Create Monitoring Namespace

```bash
kubectl create namespace taxi-fare-prod
```

### 2. Deploy Prometheus

```bash
kubectl apply -f monitoring/prometheus/prometheus.yaml
kubectl apply -f monitoring/prometheus/prometheus-ingress.yaml
```

Verify:
```bash
kubectl get pods -n taxi-fare-prod | grep prometheus
```

Access: http://prometheus.taxi-fare.example.com

### 3. Deploy Grafana

```bash
# Create secret for Grafana admin password
kubectl create secret generic grafana-auth \
  -n taxi-fare-prod \
  --from-literal=admin-password=your-secure-password

kubectl apply -f monitoring/grafana/grafana.yaml
kubectl apply -f monitoring/grafana/grafana-dashboards.yaml
```

Verify:
```bash
kubectl get pods -n taxi-fare-prod | grep grafana
```

Access: http://grafana.taxi-fare.example.com (admin/password)

### 4. Deploy Jaeger

```bash
kubectl apply -f monitoring/jaeger/jaeger.yaml
```

Verify:
```bash
kubectl get pods -n taxi-fare-prod | grep jaeger
```

Access: http://tracing.taxi-fare.example.com

### 5. Deploy ELK Stack

```bash
# Deploy Elasticsearch
kubectl apply -f monitoring/elk/elk-stack.yaml

# Wait for Elasticsearch to be ready
kubectl wait --for=condition=ready pod \
  -l app=elasticsearch -n taxi-fare-prod --timeout=300s

# Verify all components
kubectl get pods -n taxi-fare-prod | grep -E "elasticsearch|logstash|kibana"
```

Access: http://logs.taxi-fare.example.com

## Data Flow

### Metrics Flow
1. Application instruments code with prometheus_client
2. Prometheus scrapes metrics from /metrics endpoint
3. Grafana queries Prometheus for dashboards
4. Alerts triggered based on alert rules

### Traces Flow
1. Application instruments code with OpenTelemetry
2. Traces sent to Jaeger collector (gRPC or HTTP)
3. Jaeger stores in Elasticsearch or memory
4. Jaeger UI queries for visualization

### Logs Flow
1. Application sends logs to Logstash (TCP/UDP)
2. Logstash parses, filters, and enriches logs
3. Logstash sends to Elasticsearch
4. Kibana queries for log visualization and analysis

## Troubleshooting

### Prometheus
```bash
# Check if scraping targets
kubectl port-forward -n taxi-fare-prod svc/prometheus 9090:9090
# Visit http://localhost:9090/targets

# Check for scrape errors
kubectl logs -n taxi-fare-prod deployment/prometheus
```

### Jaeger
```bash
# Check collector status
kubectl port-forward -n taxi-fare-prod svc/jaeger-collector 14268:14268
curl http://localhost:14268/

# View traces
kubectl port-forward -n taxi-fare-prod svc/jaeger-query 16686:16686
```

### Elasticsearch
```bash
# Check cluster health
kubectl port-forward -n taxi-fare-prod svc/elasticsearch 9200:9200
curl http://localhost:9200/_cluster/health

# List indices
curl http://localhost:9200/_cat/indices
```

## Performance Tuning

### Prometheus
- Adjust scrape_interval if load is high
- Increase storage retention if needed
- Use recording rules for heavy queries

### Grafana
- Optimize dashboard query complexity
- Use caching for expensive queries
- Implement dashboard refresh intervals

### Elasticsearch
- Increase heap size for memory-intensive operations
- Configure index lifecycle management (ILM)
- Use log rotation and index cleanup

### Jaeger
- Adjust sampling rate based on traffic
- Configure storage backend (Elasticsearch recommended for large scale)
- Monitor collector queue sizes

## Monitoring The Monitoring Stack

Create alerts for monitoring infrastructure:

```yaml
groups:
  - name: infrastructure
    rules:
    - alert: PrometheusDown
      expr: up{job="prometheus"} == 0
      for: 1m
      
    - alert: ElasticsearchDown
      expr: up{job="elasticsearch"} == 0
      for: 1m
      
    - alert: JaegerCollectorDown
      expr: up{job="jaeger"} == 0
      for: 1m
      
    - alert: GrafanaDown
      expr: up{job="grafana"} == 0
      for: 1m
```

## Next Steps

1. Configure service discovery for automatic scraping
2. Set up alert management with AlertManager
3. Implement custom dashboards for business metrics
4. Configure backup and disaster recovery
5. Set up monitoring for monitoring infrastructure
