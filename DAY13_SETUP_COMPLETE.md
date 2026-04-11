# Day 13: Advanced Monitoring & Drift Detection - Complete Setup Guide

## Overview

Day 13 implements a production-grade monitoring and observability stack with drift detection, data quality monitoring, and business KPI tracking for the taxi fare prediction system.

### Key Features Implemented

✅ **Prometheus Metrics Collection**
- Model inference latency tracking
- Prediction accuracy metrics  
- Request volume and error rates
- Data quality scores
- Drift detection events

✅ **Grafana Dashboards** (3 dashboards)
- Model Performance Dashboard: accuracy, latency, error rates
- Prediction Volume & Latency Dashboard: requests/min, p95/p99 latencies
- Data Drift Monitoring Dashboard: drift scores, quality metrics, validation failures

✅ **Evidently-Based Drift Detection**
- Data drift detection with configurable thresholds
- Model performance monitoring
- Data quality assessment
- Test suite execution with detailed reports

✅ **Data Quality Monitoring**
- Missing values tracking
- Outlier detection (IQR method)
- Duplicate record identification
- Schema validation
- Quality score computation

✅ **Business KPI Metrics**
- Revenue impact estimation
- Geographic (borough) performance tracking
- Demand forecasting accuracy
- Model value metrics (ROI, cost savings)
- Customer satisfaction proxy metrics

✅ **Advanced Alert Rules**
- High prediction latency alerts (>1s)
- Model accuracy degradation alerts
- Data drift detection alerts
- Validation failure alerts
- API error rate alerts

✅ **Distributed Tracing**
- Jaeger integration for request tracing
- Span tracking for ML predictions
- Latency visualization

✅ **Centralized Logging**
- ELK Stack (Elasticsearch, Logstash, Kibana)
- JSON-structured logging
- Log aggregation and analysis

---

## Infrastructure Status

### Docker Stack Components

```
✅ Prometheus (port 9090)
   - Metrics scraping from /metrics endpoint
   - 15-second scrape interval
   - 30-day retention
   
✅ Grafana (port 3000)  
   - Credentials: admin / admin
   - 3 pre-built dashboards
   - Prometheus datasource configured
   
✅ Jaeger (port 6831, 16686)
   - Distributed tracing backend
   - Service dependency visualization
   
✅ Elasticsearch (port 9200)
   - Log storage (30GB PersistentVolumeClaim)
   - 8.0.0 with security disabled for dev
   
✅ Logstash (port 5000)
   - JSON log parsing and enrichment
   - Filter plugins for log processing
   
✅ Kibana (port 5601)
   - Log visualization and search
```

### Verify All Services Running

```bash
# Check all containers
docker-compose ps

# Expected output: 7 containers, all running
prometheus     Up 2 minutes
grafana        Up 2 minutes  
jaeger         Up 2 minutes
elasticsearch  Up 2 minutes
logstash       Up 2 minutes
kibana         Up 2 minutes
redis          Up 2 minutes (optional cache)
```

---

## Quick Start Guide

### 1. Access Monitoring Dashboards

**Grafana** (http://localhost:3000)
- Username: `admin`
- Password: `admin`
- Change password on first login (recommended)

Available Dashboards:
- [Model Performance Dashboard](http://localhost:3000/d/model-performance)
- [Prediction Volume & Latency Dashboard](http://localhost:3000/d/prediction-volume-latency)
- [Data Drift Monitoring Dashboard](http://localhost:3000/d/data-drift-monitoring)

**Prometheus** (http://localhost:9090)
- Metrics explorer and query interface
- Alert status and rules
- Target health monitoring

**Kibana** (http://localhost:5601)
- Log analysis and visualization
- Index management
- Alerting configuration

**Jaeger** (http://localhost:16686)
- Distributed trace visualization
- Service topology
- Latency analysis

---

## Module Reference

### 1. Drift Detection Pipeline

Location: `monitoring/drift_detection/run_drift_detection.py`

```python
from drift_detection.run_drift_detection import DriftDetectionPipeline
import pandas as pd

# Load data
reference_df = pd.read_csv('data/reference_data.csv')
current_df = pd.read_csv('data/current_data.csv')

# Initialize pipeline
pipeline = DriftDetectionPipeline(
    reference_data=reference_df,
    current_data=current_df
)

# Generate reports
drift_report = pipeline.generate_data_drift_report()
quality_report = pipeline.generate_quality_report()

# Run test suites
drift_tests = pipeline.run_drift_tests()
quality_tests = pipeline.run_quality_tests()

# Get summary
summary = pipeline.generate_summary()
print(summary)
```

### 2. Data Quality Monitor

Location: `monitoring/drift_detection/data_quality_monitor.py`

```python
from drift_detection.data_quality_monitor import DataQualityMonitor
import pandas as pd

# Initialize monitor with reference data
reference_data = pd.read_csv('data/reference.csv')
monitor = DataQualityMonitor(reference_data)

# Check individual datasets
new_data = pd.read_csv('data/new_batch.csv')

# Check for issues
missing_ratio, missing_per_col = monitor.check_missing_values(new_data)
dup_ratio = monitor.check_duplicates(new_data)
outlier_ratio, outliers_per_col = monitor.check_outliers(new_data)

# Generate report and Prometheus metrics
report = monitor.generate_quality_report(new_data)
metrics = monitor.get_prometheus_metrics(new_data)

print(f"Quality Score: {report['quality_score']:.2%}")
print(f"Missing Values: {report['missing_values_ratio']:.2%}")
print(f"Duplicates: {report['duplicate_ratio']:.2%}")
print(f"Outliers: {report['outlier_ratio']:.2%}")
```

### 3. Business KPI Metrics

Location: `monitoring/drift_detection/business_kpis.py`

```python
from drift_detection.business_kpis import TaxiFarePredictionKPIs
import pandas as pd
import numpy as np

# Initialize KPI tracker
kpis = TaxiFarePredictionKPIs(lookback_hours=24)

# Prepare prediction data with columns:
# - actual_fare, predicted_fare, borough, timestamp, inference_time_ms
predictions_df = pd.read_csv('predictions.csv')

# Calculate KPIs by borough
borough_kpis = kpis.calculate_by_borough(
    predictions_df,
    predictions_col='predicted_fare',
    actual_col='actual_fare',
    borough_col='borough'
)

# Print results
for borough, kpi in borough_kpis.items():
    print(f"{borough}:")
    print(f"  Accuracy: {kpi.accuracy:.2%}")
    print(f"  MAE: ${kpi.mae:.2f}")
    print(f"  Revenue Impact: ${kpi.revenue_impact:.2f}")

# Calculate demand forecasting accuracy
demand_kpi = kpis.calculate_demand_forecast_accuracy(
    actual_demand=np.array([100, 110, 105, 120]),
    predicted_demand=np.array([98, 112, 103, 115])
)

# Calculate business value
value_metrics = kpis.calculate_model_value_metrics()
print(f"Annual ROI: {value_metrics['roi_pct']:.1f}%")
print(f"Annual Revenue Lift: ${value_metrics['annual_revenue_lift']:.0f}")
```

### 4. Enhanced Monitoring Client

Location: `monitoring/enhanced_monitoring.py`

```python
from monitoring.enhanced_monitoring import init_monitoring

# Initialize monitoring
monitor = init_monitoring(
    service_name="taxi-fare-prediction",
    enable_jaeger=True,
    enable_prometheus=True,
    jaeger_host="localhost"
)

# Track predictions
monitor.track_prediction(
    model_name="xgboost_v2",
    inference_time_ms=45.2,
    status="success",
    accuracy=0.92,
    metadata={"borough": "Manhattan"}
)

# Track data quality
monitor.track_data_quality(
    dataset_name="production_batch_001",
    quality_score=0.95,
    missing_values={"fare": 0.01, "distance": 0.002},
    issues=[]
)

# Track drift
monitor.track_drift_detection(
    feature="distance",
    dataset_name="production",
    drift_score=0.62,
    threshold=0.5
)

# Track business KPIs
monitor.track_business_kpi(
    metric_name="accuracy",
    value=0.925,
    borough="Brooklyn"
)

# Use as decorator
@monitor.track_latency("feature_engineering")
def process_features(data):
    return data * 2
```

---

## Alert Rules Configuration

### Location
- Prometheus alerts: `monitoring/docker/prometheus/alerts.yaml`
- Extended alerts: `monitoring/docker/prometheus/alerts_extended.yaml`

### Alert Groups

**Model Performance Alerts**
- `HighPredictionLatency`: P95 latency > 1.0 seconds
- `ModelAccuracyDegradation`: Error rate > 15% for 10 minutes
- `HighErrorRate`: Prediction errors > 1% for 5 minutes

**Data Quality Alerts**
- `DataDriftDetected`: Drift score > 0.5
- `DataValidationFailure`: >100 failures in 5 minutes
- `MissingValuesExceeded`: >10% missing values
- `OutliersDetected`: >5% outlier ratio

**API Alerts**
- `HighAPILatency`: P99 latency > 2.0 seconds
- `APIErrorRateHigh`: 5+ error rate for 5 minutes

**Infrastructure Alerts**
- `PrometheusDown`: Prometheus unavailable
- `ServiceDown`: Any service unavailable for 2 minutes

---

## Metrics Exposed

### Model Metrics
```
model_predictions_total{model_name, status}
model_inference_duration_seconds{model_name}
model_accuracy{model_name}
```

### Data Quality Metrics
```
data_quality_score{dataset}
data_quality_missing_values_ratio{dataset, feature}
data_quality_outlier_ratio{dataset, feature}
data_drift_detected_total{feature, dataset}
data_validation_failures_total{validation_type, dataset}
```

### API Metrics
```
api_requests_total{endpoint, status}
api_request_duration_seconds{endpoint}
```

### Business KPI Metrics
```
taxi_model_accuracy{borough}
taxi_revenue_impact{borough}
taxi_mae_borough_{borough}
taxi_inference_time_ms_borough_{borough}
```

---

## Running Complete Day 13 Pipeline

### Option 1: Python Script

```bash
cd "e:\TaxiFare MLOps"

# Install dependencies
pip install evidently prometheus-client opentelemetry-api opentelemetry-sdk

# Run drift detection
python -m monitoring.drift_detection.run_drift_detection

# Run data quality check
python -c "
from monitoring.drift_detection.data_quality_monitor import DataQualityMonitor
import pandas as pd

ref_data = pd.read_csv('data/raw/train.csv')
test_data = pd.read_csv('data/raw/test.csv')

monitor = DataQualityMonitor(ref_data)
report = monitor.generate_quality_report(test_data)

import json
print(json.dumps(report, indent=2, default=str))
"
```

### Option 2: Jupyter Notebook

See: `DAY13_IMPLEMENTATION_NOTEBOOK.ipynb`

```bash
jupyter notebook
# Open DAY13_IMPLEMENTATION_NOTEBOOK.ipynb
```

---

## Troubleshooting

### Prometheus Not Scraping Metrics

**Check:**
```bash
# Verify Prometheus target health
curl http://localhost:9090/api/v1/targets

# Check prometheus.yaml for scrape_configs
cat monitoring/docker/prometheus/prometheus.yaml
```

**Fix:**
- Ensure your metrics endpoint is accessible
- Add service to `scrape_configs` in prometheus.yaml
- Restart Prometheus: `docker-compose restart prometheus`

### Grafana Dashboards Not Showing Data

**Check:**
1. Verify Prometheus datasource is configured
2. Check metric names in dashboard match exposed metrics
3. Ensure data has been collected (wait 30s after first metrics exposure)

**Fix:**
```bash
# Re-import dashboards
docker-compose stop grafana
docker volume rm docker_grafana_storage
docker-compose up -d grafana
```

### Drift Detection Not Running

**Check:**
```bash
# Verify evidently is installed
python -c "import evidently; print(evidently.__version__)"

# Check report generation
python monitoring/drift_detection/run_drift_detection.py
```

**Fix:**
```bash
pip install --upgrade evidently
```

---

## Next Steps

1. **Integrate with Production API**
   - Import `EnhancedMonitoringClient` in your Flask/FastAPI service
   - Add tracking calls to prediction endpoints
   - Export metrics for scraping

2. **Configure Alert Notifications**
   - Setup AlertManager for Prometheus
   - Configure email/Slack/PagerDuty integrations
   - Test alert routing

3. **Extend Dashboards**
   - Add custom business metrics
   - Create department-specific views
   - Setup dashboard sharing and permissions

4. **Production Deployment**
   - Deploy to Kubernetes (manifests in `monitoring/k8s/`)
   - Configure persistent storage
   - Setup high-availability Prometheus
   - Configure external log shipping

---

## Files Created

```
monitoring/
├── enhanced_monitoring.py              # Enhanced monitoring client
├── docker/
│   ├── prometheus/
│   │   ├── alerts.yaml                 # Basic alert rules
│   │   ├── alerts_extended.yaml        # Extended alert rules (NEW)
│   │   └── rules.yaml                  # Recording rules
│   └── grafana/
│       └── dashboards/
│           ├── model-performance.json  # Model Performance Dashboard (NEW)
│           ├── prediction-volume-latency.json  # Volume/Latency Dashboard (NEW)
│           └── data-drift-monitoring.json     # Drift Monitoring Dashboard (NEW)
└── drift_detection/
    ├── config.py                       # Drift detection config (existing)
    ├── run_drift_detection.py          # Drift pipeline (existing)
    ├── data_quality_monitor.py         # Data quality monitoring (NEW)
    └── business_kpis.py                # Business KPI tracking (NEW)
```

---

## Support & Documentation

For detailed component documentation:
- Drift Detection: See `monitoring/drift_detection/run_drift_detection.py` docstrings
- Data Quality: See `monitoring/drift_detection/data_quality_monitor.py`
- Business KPIs: See `monitoring/drift_detection/business_kpis.py`
- Monitoring Library: See `monitoring/enhanced_monitoring.py`

For infrastructure documentation:
- Prometheus Alerts: See `monitoring/docker/prometheus/alerts_extended.yaml`
- Grafana Provisioning: See `monitoring/docker/grafana/provisioning/`
- Docker Compose: See `monitoring/docker/docker-compose.yml`

---

**Last Updated:** Day 13 - Advanced Monitoring & Drift Detection
**Status:** ✅ Complete Implementation
