# Local development environment setup for monitoring

## Start Monitoring Stack

```bash
# Navigate to monitoring directory
cd monitoring

# Start all services
docker-compose -f docker/docker-compose.yml up -d

# Check status
docker-compose -f docker/docker-compose.yml ps

# View logs
docker-compose -f docker/docker-compose.yml logs -f
```

## Access Dashboards

### Prometheus
- URL: http://localhost:9090
- Check targets: http://localhost:9090/targets
- Query metrics: http://localhost:9090/graph

### Grafana
- URL: http://localhost:3000
- Username: admin
- Password: admin
- Import dashboards after setup

### Jaeger
- URL: http://localhost:16686
- Search for traces by service

### Kibana
- URL: http://localhost:5601
- Create index patterns for logs-*
- Create visualizations

### Elasticsearch
- URL: http://localhost:9200
- Check health: http://localhost:9200/_cluster/health
- List indices: http://localhost:9200/_cat/indices

## Test Monitoring

### Send Test Logs

```bash
# Send JSON log via TCP
echo '{"message":"Test log from Python","level":"INFO","logger":"test"}' | nc localhost 5000

# Send via curl
curl -X POST http://localhost:5000 \
  -H "Content-Type: application/json" \
  -d '{"message":"Test","level":"INFO"}'
```

### Generate Test Metrics

```bash
# Start example API
python -m monitoring.api_example

# Visit http://localhost:5000/metrics to see metrics
# Make prediction requests to http://localhost:5000/predict
```

### View in Kibana

1. Create index pattern: logs-*
2. Go to Discover
3. Search for your test logs
4. Create visualizations

## Development Workflow

1. Make changes to code
2. Restart API: `docker-compose -f docker/docker-compose.yml restart`
3. View metrics in Prometheus/Grafana
4. View logs in Kibana
5. View traces in Jaeger

## Cleanup

```bash
# Stop services
docker-compose -f docker/docker-compose.yml down

# Remove volumes (careful - deletes data)
docker-compose -f docker/docker-compose.yml down -v

# Remove all monitoring containers and images
docker system prune -a
```

## Troubleshooting

### Services won't start
```bash
# Check Docker daemon
docker ps

# Check logs
docker-compose -f docker/docker-compose.yml logs service_name

# Increase Docker resources
# (Docker Desktop: Preferences > Resources)
```

### Elasticsearch not responding
```bash
# Check health
curl http://localhost:9200/_cluster/health

# Check logs
docker logs elasticsearch
```

### Grafana can't connect to Prometheus
```bash
# Check network
docker network ls

# Check Prometheus logs
docker logs prometheus
```

### Jaeger not receiving traces
```bash
# Check collector
curl http://localhost:14268/

# Check if application can reach jaeger:6831
nc -zv jaeger 6831
```
