# Day 13 - Advanced Monitoring & Drift Detection Dashboard

This directory contains all artifacts for Day 13 implementation.

## Components

- `evidently/` - Drift detection configuration
- `dashboards/` - Grafana dashboard definitions
- `metrics/` - Prometheus metrics configuration
- `alerts/` - Alert rules
- `documentation/` - Setup guides

## Quick Start

```bash
# 1. Deploy monitoring stack
docker-compose -f docker/docker-compose.yml up -d

# 2. Install Evidently
pip install evidently

# 3. Run drift detection
python drift_detection/run_drift_detection.py

# 4. Access dashboards
# Grafana: http://localhost:3000
```
