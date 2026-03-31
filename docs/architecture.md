"""Architecture documentation."""

# Taxi Fare Prediction - System Architecture

## Overview

This is a production-grade MLOps system for predicting NYC taxi fares using regression models.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Data Layer                                │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ Raw Data     │  │ Validation   │  │ Processed Features  │   │
│  │ (CSV/DB)     │─→│ (Schema)     │─→│ (DVC Versioned)     │   │
│  └──────────────┘  └──────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    ML Training Layer                             │
│  ┌──────────────┐  ┌──────────────┐  ┌─────────────────────┐   │
│  │ Feature      │  │ Multi-Model  │  │ Hyperparameter      │   │
│  │ Engineering  │─→│ Training     │─→│ Tuning (Optuna)     │   │
│  │ (sklearn)    │  │ (8 models)   │  │ (Top 3)             │   │
│  └──────────────┘  └──────────────┘  └─────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Experiment Tracking Layer                       │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │ MLflow Experiment Tracking & Model Registry              │   │
│  │ - All runs logged with params, metrics, artifacts       │   │
│  │ - Best model registered with version control             │   │
│  │ - Stage transitions: Staging → Production                │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Deployment Layer                              │
│  ┌──────────────┐              ┌──────────────────────────────┐ │
│  │ FastAPI      │ Real-time    │ Streamlit Dashboard          │ │
│  │ Inference    │ predictions  │ - Single predictions         │ │
│  │ Endpoint     │ + validation  │ - Batch processing (CSV)    │ │
│  │ /predict     │              │ - Model explanations         │ │
│  └──────────────┘              └──────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  Monitoring & Observability                      │
│  ┌──────────────┐  ┌───────────────┐  ┌──────────────────────┐ │
│  │ Prometheus   │  │ Grafana       │  │ Data Drift           │ │
│  │ Metrics      │→ │ Dashboards    │→ │ Detection            │ │
│  │ (req/error)  │  │ (visualization)   │ (Evidently)          │ │
│  └──────────────┘  └───────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Overview

### Data Management
- **Data Versioning**: DVC tracks all data versions from raw → processed
- **Data Validation**: Schema checks, null/outlier detection
- **Feature Store**: Processed features versioned and reproducible

### Model Training
- **Multi-Model Training**: LinearRegression, Ridge, Lasso, ElasticNet, SVR, RF, XGBoost, LightGBM
- **Experiment Tracking**: MLflow logs all runs with reproducibility
- **Hyperparameter Optimization**: Optuna for top-3 models with early stopping

### Deployment
- **API**: FastAPI with Pydantic validation for real-time inference
- **Dashboard**: Streamlit for batch processing and visualization
- **Containerization**: Docker + Docker Compose for reproducible deployment

### Monitoring
- **Metrics**: Prometheus for collecting operational metrics
- **Visualization**: Grafana for dashboarding
- **Drift Detection**: Evidently for data/model monitoring

## Tech Stack

| Component | Tool | Purpose |
|-----------|------|---------|
| **Source Control** | Git + GitHub | Version control, PRs, CI/CD |
| **Data Versioning** | DVC | Pipeline & data artifact versioning |
| **Experiment Tracking** | MLflow | Params, metrics, artifacts logging |
| **Hyperparameter Tuning** | Optuna | Efficient HPO with early stopping |
| **Model Training** | scikit-learn | Baseline models + preprocessing |
| **Boosting Models** | XGBoost, LightGBM | High-performance models |
| **API** | FastAPI | Low-latency inference endpoint |
| **Dashboard** | Streamlit | User-facing UI |
| **Containerization** | Docker | Reproducible deployments |
| **Orchestration** | Makefile + GitHub Actions | Simple task automation & CI/CD |
| **Monitoring** | Prometheus + Grafana | Operational observability |
| **Drift Detection** | Evidently | Data quality monitoring |

## Data Flow

1. **Ingestion**: Raw CSV → validation → storage in `data/raw/`
2. **Versioning**: DVC tracks processed pipeline outputs
3. **Features**: Temporal + numerical features engineered via sklearn Pipeline
4. **Training**: 8 models trained in parallel, metrics logged to MLflow
5. **Selection**: Top 3 models tuned via Optuna
6. **Registration**: Best model registered to MLflow Model Registry
7. **Deployment**: Model loaded into API + Dashboard containers
8. **Monitoring**: Inference metrics scraped by Prometheus

## Reproducibility Strategy

- **Environment**: `pyproject.toml` + `pip install -e .` ensures dependency consistency
- **Data**: DVC checksums prevent data mutation
- **Code**: Git versioning + tagged releases
- **Experiments**: MLflow run IDs tied to Git commits
- **Models**: Artifacts stored with version metadata

## Deployment Pipeline (Option A: Makefile + GitHub Actions)

```
Code Pushed
    ↓
GitHub Actions Triggered
    ↓
├─ Lint (ruff, black, isort)
├─ Test (pytest)
├─ Build Docker images
└─ Security scan (bandit, pip-audit)
    ↓
PR Approved & Merged to main
    ↓
Deploy workflow runs
    ↓
Docker containers up
    ↓
Health checks pass
    ↓
Ready for production
```

## Future Enhancements (Option B: Kubeflow)

For advanced orchestration, consider:
- Kubeflow Pipelines for complex DAGs
- Kubernetes for auto-scaling
- Distributed training with Ray/Spark
- Advanced monitoring with Prometheus + custom exporters
