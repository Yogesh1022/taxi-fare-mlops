# Day 13 Quick Reference - Advanced Monitoring & Drift Detection

## What's New (Day 13 Implementation)

### 📊 Grafana Dashboards (3 NEW)
```
Model Performance Dashboard
├── Inference latency distribution
├── Accuracy score gauge
├── Predictions by status
├── P95/P99 percentiles
└── Error rate trends
URL: http://localhost:3000/d/model-performance

Prediction Volume & Latency Dashboard
├── Volume per minute
├── API latency distribution
├── Request percentiles
└── Volume by endpoint/status
URL: http://localhost:3000/d/prediction-volume-latency

Data Drift Monitoring Dashboard
├── Quality scores
├── Feature drift detection
├── Validation failures
├── Processing rates
└── Quality issues breakdown
URL: http://localhost:3000/d/data-drift-monitoring
```

### 🚨 Alert Rules (14 NEW - Extended)
**File:** `monitoring/docker/prometheus/alerts_extended.yaml`

```
Model Performance:
  - HighPredictionLatency (P95 > 1.0s)
  - ModelAccuracyDegradation (Error > 15%)
  - HighErrorRate (>1%)

Data Quality:
  - DataDriftDetected (score > 0.5)
  - DataValidationFailure (>100 in 5m)
  - MissingValuesExceeded (>10%)
  - OutliersDetected (>5%)

API:
  - HighAPILatency (P99 > 2.0s)
  - APIErrorRateHigh (>5%)

Infrastructure:
  - PrometheusDown
  - ServiceDown
```

### 🔬 Data Quality Monitor (NEW)
**File:** `monitoring/drift_detection/data_quality_monitor.py`

```python
from monitoring.drift_detection.data_quality_monitor import DataQualityMonitor

# Initialize
monitor = DataQualityMonitor(reference_data, thresholds={...})

# Check metrics
missing_ratio, per_col = monitor.check_missing_values(df)
dup_ratio = monitor.check_duplicates(df)
outlier_ratio, per_col = monitor.check_outliers(df)

# Get score and report
quality_score = monitor.compute_quality_score(df)
report = monitor.generate_quality_report(df)
metrics = monitor.get_prometheus_metrics(df)
```

### 💰 Business KPIs (NEW)
**File:** `monitoring/drift_detection/business_kpis.py`

```python
from monitoring.drift_detection.business_kpis import TaxiFarePredictionKPIs

kpis = TaxiFarePredictionKPIs(lookback_hours=24)

# Calculate by borough
borough_kpis = kpis.calculate_by_borough(predictions_df)
# -> Manhattan: 92.5% accuracy, $12.50 MAE, $150 revenue impact

# Demand forecast accuracy
forecast = kpis.calculate_demand_forecast_accuracy(actual, predicted)
# -> MAPE: 3.2%, Direction accuracy: 92%

# Business value
value = kpis.calculate_model_value_metrics()
# -> Annual ROI: 156%, Revenue lift: $27,375

# Report & metrics
report = kpis.generate_kpi_report()
metrics = kpis.get_prometheus_metrics(borough_kpis)
```

### 🔗 Enhanced Monitoring Client (NEW)
**File:** `monitoring/enhanced_monitoring.py`

```python
from monitoring.enhanced_monitoring import init_monitoring

monitor = init_monitoring("taxi-fare-prediction")

# Track predictions
monitor.track_prediction(
    model_name="xgboost_v2",
    inference_time_ms=42.5,
    status="success",
    accuracy=0.925
)

# Track data quality
monitor.track_data_quality(
    dataset_name="production",
    quality_score=0.95,
    missing_values={"fare": 0.01}
)

# Track drift
monitor.track_drift_detection(
    feature="distance",
    dataset_name="production",
    drift_score=0.62,
    threshold=0.5
)

# Use decorator
@monitor.track_latency("feature_engineering")
def process_features(data):
    return data + 1
```

---

## Quick Start (5 Minutes)

### 1. Verify Stack Running
```bash
cd "e:\TaxiFare MLOps\monitoring\docker"
docker-compose ps  # Should show 7 containers running
```

### 2. Open Dashboards
- **Grafana:** http://localhost:3000 (admin/admin)
- **Prometheus:** http://localhost:9090
- **Kibana:** http://localhost:5601
- **Jaeger:** http://localhost:16686

### 3. Run Integration Tests
```bash
cd "e:\TaxiFare MLOps"
python DAY13_INTEGRATION_TESTS.py
```

### 4. Start Monitoring Your Model
```python
from monitoring.enhanced_monitoring import init_monitoring

monitor = init_monitoring("my-service")
monitor.track_prediction("model_v1", 45.0, accuracy=0.92)
```

---

## API Examples

### Example 1: Monitor Batch Predictions
```python
from monitoring.drift_detection.run_drift_detection import DriftDetectionPipeline
from monitoring.enhanced_monitoring import init_monitoring

monitor = init_monitoring("batch_processor")

# Load batch data
reference = pd.read_csv("reference.csv")
current = pd.read_csv("batch.csv")

# Run drift detection
pipeline = DriftDetectionPipeline(reference, current)
pipeline.run()  # Generates report

# Track metrics
monitor.track_data_quality(
    dataset_name="batch_001",
    quality_score=0.94
)
```

### Example 2: Monitor API Predictions
```python
from monitoring.enhanced_monitoring import get_monitoring_client

monitor = get_monitoring_client()

@app.post("/predict")
def predict(request):
    start = time.time()
    
    result = model.predict(request.data)
    
    duration_ms = (time.time() - start) * 1000
    monitor.track_api_request(
        endpoint="/predict",
        duration_ms=duration_ms,
        status_code=200
    )
    
    return result
```

### Example 3: Business Reporting
```python
from monitoring.drift_detection.business_kpis import TaxiFarePredictionKPIs

kpis = TaxiFarePredictionKPIs()

# Load predictions with actuals
predictions_df = pd.read_csv("daily_predictions.csv")

# Calculate KPIs
borough_kpis = kpis.calculate_by_borough(predictions_df)

# Generate report
report = kpis.generate_kpi_report()

# Extract metrics for reporting
for borough, kpi in borough_kpis.items():
    print(f"{borough}:")
    print(f"  Accuracy: {kpi.accuracy:.1%}")
    print(f"  Revenue Impact: ${kpi.revenue_impact:.0f}")
```

---

## File Location Reference

| Component | File |
|-----------|------|
| **Dashboards** | `monitoring/docker/grafana/dashboards/` |
| - Model Performance | `model-performance.json` |
| - Volume & Latency | `prediction-volume-latency.json` |
| - Drift Monitoring | `data-drift-monitoring.json` |
| **Alert Rules** | `monitoring/docker/prometheus/alerts_extended.yaml` |
| **Data Quality** | `monitoring/drift_detection/data_quality_monitor.py` |
| **Business KPIs** | `monitoring/drift_detection/business_kpis.py` |
| **Monitoring Client** | `monitoring/enhanced_monitoring.py` |
| **Tests** | `DAY13_INTEGRATION_TESTS.py` |
| **Docs** | `DAY13_SETUP_COMPLETE.md` |
| **Report** | `DAY13_COMPLETION_REPORT.md` |

---

## Verification Checklist

- [ ] Docker stack running: `docker-compose ps` shows 7 containers
- [ ] Prometheus responding: `curl http://localhost:9090/targets`
- [ ] Grafana accessible: http://localhost:3000
- [ ] Dashboards created: 3 dashboards visible in Grafana
- [ ] Integration tests pass: `DAY13_INTEGRATION_TESTS.py` returns exit code 0
- [ ] Monitoring client initialized: Can create EnhancedMonitoringClient
- [ ] KPIs calculated: TaxiFarePredictionKPIs generates reports

---

## Common Issues & Solutions

### Issue: Grafana dashboards show no data
**Solution:** Dashboards are visualization templates. Data appears after:
1. Binding monitoring client to your app
2. Making predictions for 30+ seconds
3. Refreshing dashboard

### Issue: Alert rules not working
**Solution:** Rules require AlertManager for notifications:
```bash
# Install AlertManager
brew install alertmanager  # or docker pull prom/alertmanager

# Configure alertmanager.yml with email/Slack
# Update prometheus.yaml with alerting config
```

### Issue: "Port already in use"
**Solution:** Change ports in docker-compose.yml or kill existing:
```bash
docker-compose down  # Stop containers
# or
lsof -i :9090  # Find process on port 9090
kill -9 <PID>
```

---

## Next Steps

1. **Integrate with Your API**
   ```python
   from monitoring.enhanced_monitoring import init_monitoring
   monitor = init_monitoring("your-service")
   # Add tracking calls to endpoints
   ```

2. **Setup Alert Notifications**
   - Install AlertManager
   - Configure email/Slack
   - Test alert routing

3. **Extend Business KPIs**
   - Add custom borough metrics
   - Integrate with data warehouse
   - Setup dashboards for stakeholders

4. **Production Deployment**
   - Deploy to Kubernetes
   - Configure persistent storage
   - Setup backup procedures

---

## Metrics Exposed

### Model Metrics
`model_predictions_total{model_name, status}`  
`model_inference_duration_seconds{model_name}`  
`model_accuracy{model_name}`

### Data Quality Metrics
`data_quality_score{dataset}`  
`data_quality_missing_values_ratio{dataset}`  
`data_drift_detected_total{feature}`

### Business KPI Metrics
`taxi_model_accuracy{borough}`  
`taxi_revenue_impact{borough}`  
`taxi_mae_borough_*`

---

## Support

**Quick Start Guide:** [DAY13_SETUP_COMPLETE.md](DAY13_SETUP_COMPLETE.md)  
**Full Report:** [DAY13_COMPLETION_REPORT.md](DAY13_COMPLETION_REPORT.md)  
**Integration Tests:** [DAY13_INTEGRATION_TESTS.py](DAY13_INTEGRATION_TESTS.py)

---

**Status:** ✅ Day 13 Complete  
**Last Updated:** 2024  
**Version:** 1.0
