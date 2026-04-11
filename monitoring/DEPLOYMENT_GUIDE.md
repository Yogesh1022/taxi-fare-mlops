# Monitoring Deployment Guide

## Quick Start

### Local Development

```bash
# 1. Install dependencies
pip install -r requirements-monitoring.txt

# 2. Start monitoring stack with Docker Compose
cd monitoring/docker
docker-compose up -d

# 3. Access dashboards
# Prometheus: http://localhost:9090
# Grafana: http://localhost:3000 (admin/admin)
# Jaeger: http://localhost:16686
# Kibana: http://localhost:5601
# Elasticsearch: http://localhost:9200

# 4. Start application with monitoring
python monitoring/api_example.py
```

### Kubernetes Deployment

```bash
# 1. Create namespace
kubectl create namespace taxi-fare-prod

# 2. Deploy monitoring stack
kubectl apply -f monitoring/prometheus/prometheus.yaml
kubectl apply -f monitoring/grafana/grafana.yaml
kubectl apply -f monitoring/jaeger/jaeger.yaml
kubectl apply -f monitoring/elk/elk-stack.yaml

# 3. Deploy ingress rules
kubectl apply -f monitoring/ingress/

# 4. Verify deployment
kubectl get pods -n taxi-fare-prod
kubectl get svc -n taxi-fare-prod

# 5. Port forward for testing
kubectl port-forward -n taxi-fare-prod svc/grafana 3000:3000
kubectl port-forward -n taxi-fare-prod svc/jaeger-query 16686:16686
```

## Configuration

### Environment Variables

```bash
# Prometheus
PROMETHEUS_RETENTION=30d
PROMETHEUS_SCRAPE_INTERVAL=15s

# Jaeger
JAEGER_AGENT_HOST=jaeger
JAEGER_AGENT_PORT=6831
JAEGER_SAMPLER_TYPE=probabilistic
JAEGER_SAMPLER_PARAM=1.0

# Elasticsearch
ES_JAVA_OPTS=-Xms512m -Xmx512m
ELASTICSEARCH_HOSTS=http://elasticsearch:9200

# Kibana
KIBANA_ELASTICSEARCH_HOSTS=http://elasticsearch:9200
```

### Application Instrumentation

```python
from src.monitoring import setup_monitoring

# In your Flask app
app = Flask(__name__)

tracing, logger = setup_monitoring(
    app,
    service_name="taxi-fare-api",
    jaeger_host="jaeger",
    jaeger_port=6831
)

# Log metrics endpoint
@app.route("/metrics")
def metrics():
    from src.monitoring import get_metrics_registry
    registry = get_metrics_registry()
    return generate_latest(registry.registry)
```

## Monitoring the Monitoring Stack

### Health Checks

```bash
# Prometheus
curl http://localhost:9090/-/healthy

# Grafana
curl http://localhost:3000/api/health

# Jaeger collector
curl http://localhost:14268/

# Elasticsearch
curl http://localhost:9200/_cluster/health
```

### Common Issues

#### Prometheus Targets Down
```bash
# Check Prometheus targets
curl http://localhost:9090/api/v1/targets | jq .

# Verify application metrics endpoint
curl http://localhost:5000/metrics
```

#### Jaeger Not Receiving Traces
```bash
# Check Jaeger collector logs
kubectl logs -n taxi-fare-prod deployment/jaeger

# Verify collector endpoint
curl http://localhost:14268/

# Check if agent port is open
nc -zv localhost 6831
```

#### Elasticsearch Connection Issues
```bash
# Check Elasticsearch cluster
curl http://localhost:9200/_cluster/health

# Check indices
curl http://localhost:9200/_cat/indices

# Check storage
curl http://localhost:9200/_cat/allocation
```

## Performance Tuning

### Prometheus
```yaml
# Optimize scrape interval
global:
  scrape_interval: 30s  # Increase if high load

# Use recording rules
recording_rules:
  - record: instance:up:sum
    expr: sum by (job) (up)
```

### Elasticsearch
```yaml
# Increase heap for better performance
env:
  - name: ES_JAVA_OPTS
    value: "-Xms1g -Xmx1g"

# Configure index lifecycle
PUT _ilm/policy/logs-policy
{
  "policy": "logs-policy",
  "phases": {
    "hot": {
      "actions": {
        "rollover": { "max_docs": 1000000 }
      }
    },
    "warm": {
      "min_age": "7d"
    },
    "delete": {
      "min_age": "30d",
      "actions": { "delete": {} }
    }
  }
}
```

### Grafana
```yaml
# Optimize dashboard queries
- Disable expensive queries if not needed
- Use caching
- Adjust refresh intervals
```

## Backup and Recovery

### Prometheus
```bash
# Backup data
docker run --volumes-from prometheus-c3 \
  -v $(pwd):/backup \
  alpine tar czf /backup/prometheus-backup.tar.gz /prometheus

# Restore data
docker run --volumes-from prometheus-c3 \
  -v $(pwd):/backup \
  alpine tar xzf /backup/prometheus-backup.tar.gz -C /
```

### Elasticsearch
```bash
# Create snapshot repository
curl -X PUT http://localhost:9200/_snapshot/backup \
  -H 'Content-Type: application/json' \
  -d '{"type":"fs","settings":{"location":"/mnt/backup"}}'

# Create snapshot
curl -X PUT http://localhost:9200/_snapshot/backup/snapshot-1

# List snapshots
curl http://localhost:9200/_snapshot/backup/_all
```

## Scaling for Production

### High Availability

#### Prometheus
- Use PrometheusHA with multiple replicas
- Configure Thanos for long-term storage
- Use persistent volumes

#### Elasticsearch
- Deploy as cluster (3+ nodes)
- Configure replication factor to 2
- Enable cross-cluster replication

#### Grafana
- Deploy multiple replicas
- Use external database
- Configure RBAC

### Monitoring Stack Sizing

| Component | CPU | Memory | Storage |
|-----------|-----|--------|---------|
| Prometheus | 500m | 512Mi | 30-50Gi |
| Grafana | 250m | 512Mi | 5Gi |
| Elasticsearch | 500m | 1Gi | 100Gi+ |
| Logstash | 250m | 256Mi | - |
| Jaeger | 500m | 512Mi | 50Gi |

## Monitoring Alerts

### Key Alerts to Configure

```yaml
- alert: HighPredictionLatency
  expr: api_request_duration_seconds{endpoint="predict"} > 1
  duration: 5m

- alert: ModelErrorRate
  expr: increase(model_predictions_total{status="error"}[5m]) > 10
  duration: 5m

- alert: DataQualityDegraded
  expr: data_quality_score < 0.8
  duration: 5m

- alert: StorageFull
  expr: elasticsearch_storage_available_bytes < 10737418240
  duration: 5m
```

## Cleanup and Maintenance

```bash
# Clean old indices
curl -X DELETE http://localhost:9200/logs-2024.01.*

# Optimize index
curl -X POST http://localhost:9200/logs-2024.02/_forcemerge

# Clear Prometheus cache
curl -X POST http://localhost:9090/api/v1/admin/tsdb/clean_tombstones
```

## Testing

Run the monitoring tests:

```bash
# Unit tests
pytest tests/monitoring/ -v

# Integration tests
pytest tests/monitoring/integration/ -v

# Load testing
locust -f tests/monitoring/load.py --headless -u 100 -r 10 -t 60s
```
