# Complete MLOps Implementation Plan for Taxi Fare Prediction

## 1) Objective and Scope

This document converts your research notebook (`assignment1-mlp.ipynb`) into a production-grade MLOps system for regression prediction of `total_amount` on NYC taxi data.

Current state (research):
- Notebook-centric experimentation
- Local-only runs
- Manual model comparison and submission generation
- No automated reproducibility, deployment, or monitoring

Target state (production):
- Modular codebase with reproducible environments
- Versioned data and models
- Automated training, testing, and deployment pipelines
- Online inference API + user dashboard
- Monitoring, drift detection, and governance controls

---

## 2) Recommended Repository Structure

```text
mlops-taxi-fare-prediction/
├── data/
│   ├── raw/
│   ├── interim/
│   ├── processed/
│   └── external/
├── notebooks/
│   └── assignment1-mlp.ipynb
├── src/
│   ├── data/
│   │   ├── ingest.py
│   │   ├── validate.py
│   │   └── split.py
│   ├── features/
│   │   ├── transformers.py
│   │   ├── pipeline.py
│   │   └── schema.py
│   ├── models/
│   │   ├── train.py
│   │   ├── tune.py
│   │   ├── evaluate.py
│   │   └── predict.py
│   ├── deployment/
│   │   ├── api.py
│   │   ├── schemas.py
│   │   └── dashboard.py
│   └── utils/
│       ├── config.py
│       ├── logger.py
│       └── io.py
├── pipelines/
│   ├── training_pipeline.py
│   └── inference_pipeline.py
├── mlops/
│   ├── mlflow/
│   ├── monitoring/
│   └── governance/
├── tests/
│   ├── unit/
│   ├── integration/
│   └── contract/
├── docker/
│   ├── Dockerfile.api
│   ├── Dockerfile.dashboard
│   └── docker-compose.yml
├── .github/workflows/
│   ├── ci.yml
│   ├── train-register.yml
│   └── deploy.yml
├── dvc.yaml
├── dvc.lock
├── params.yaml
├── pyproject.toml
├── requirements.txt
├── Makefile
├── README.md
└── docs/
    ├── architecture.md
    ├── runbook.md
    └── api_contract.md
```

---

## 3) Tool Stack (What to Use and Why)

## 3.1 Core MLOps Tools

- Git + GitHub
  - Source control, PR workflow, branch protection, release tags
- DVC
  - Data and pipeline versioning (`raw -> processed -> features -> model`)
- MLflow
  - Experiment tracking, artifact logging, model registry, model stage transitions
- Optuna
  - Efficient hyperparameter optimization (for top 3 models)
- FastAPI
  - Low-latency inference endpoint with schema validation
- Streamlit
  - User-facing dashboard for interactive predictions and explanations
- Docker + Docker Compose
  - Reproducible local/CI runtime and service orchestration
- GitHub Actions
  - CI/CD automation (test, train, package, deploy)
- Prometheus + Grafana
  - Operational metrics collection and monitoring dashboards
- Evidently (or WhyLogs)
  - Data drift and model quality monitoring over time

## 3.2 ML/Feature Tooling

- pandas, numpy
  - Data handling and feature calculations
- scikit-learn
  - Baseline models, preprocessing, model pipelines, evaluation
- xgboost, lightgbm
  - High-performance boosting models
- joblib
  - Persisting preprocessor/model artifacts

## 3.3 Quality/Security/Standards Tools

- pytest
  - Unit + integration test framework
- ruff + black + isort
  - Linting, formatting, import consistency
- mypy (optional but recommended)
  - Type checking for reliability
- pre-commit
  - Local quality gates before commits
- bandit + pip-audit
  - Security scan and dependency vulnerability checks

## 3.4 Orchestration (Choose one)

- Option A (quick start): Python scripts + Makefile + GitHub Actions
- Option B (advanced): Kubeflow or Metaflow for production-grade orchestration

Recommendation for your assignment: Start with Option A, then move to Option B once baseline production is stable.

---

## 4) Day-Wise Detailed Schedule (14-Day End-to-End Plan)

## Day 1 - Project Bootstrap and Environment Reproducibility

Tasks:
- Initialize repository structure
- Move notebook into `notebooks/`
- Create `pyproject.toml` and/or `requirements.txt`
- Add `.python-version` (optional) and `.gitignore`
- Add Docker base image and deterministic dependency installation
- Add `Makefile` commands: `setup`, `lint`, `test`, `train`, `serve`

Tools:
- Git/GitHub, uv or Poetry, Docker, Make

Deliverables:
- Reproducible local setup (`make setup` works)
- Container build succeeds

Acceptance criteria:
- New machine can run project in <15 minutes
- `python -m src.models.train` executes without environment errors

---

## Day 2 - Data Versioning and Data Contracts

Tasks:
- Initialize DVC and remote storage (local/S3/GDrive)
- Place datasets into `data/raw`
- Define schema checks for columns and data types
- Implement null/outlier checks for critical fields
- Add data quality report generation

Tools:
- DVC, pandas, Great Expectations (optional), custom validators

Deliverables:
- `dvc.yaml` first stage: `ingest` + `validate`
- Data validation report artifact

Acceptance criteria:
- Any schema mismatch fails pipeline
- Data versions are reproducible by DVC checkout

---

## Day 3 - Feature Engineering as Reusable Pipeline

Tasks:
- Convert notebook feature logic into reusable code:
  - Datetime features (hour, day, weekday, month)
  - Existing numerical components and `component_sum`
- Build sklearn `ColumnTransformer` + `Pipeline`
- Save fitted preprocessor artifact

Tools:
- scikit-learn Pipeline/ColumnTransformer, joblib

Deliverables:
- `src/features/transformers.py`, `src/features/pipeline.py`
- Feature unit tests

Acceptance criteria:
- Same transformation used in both training and inference
- No train/inference feature mismatch

---

## Day 4 - Baseline Multi-Model Training Framework

Tasks:
- Implement training script for 8 models
- Standardize split/evaluation (`train/val/test` or CV)
- Log all metrics per model (`R2`, `RMSE`, `MAE`)
- Save best baseline model

Tools:
- scikit-learn, xgboost, lightgbm, MLflow (tracking only)

Deliverables:
- `src/models/train.py`
- Model leaderboard table artifact

Acceptance criteria:
- One command runs all 8 models and ranks them
- Metrics are persisted and reproducible

---

## Day 5 - Hyperparameter Optimization for Top 3 Models

Tasks:
- Select top 3 candidate models from Day 4
- Implement Optuna optimization studies
- Add early stopping/time budget per model
- Compare tuned vs untuned performance

Tools:
- Optuna, MLflow nested runs

Deliverables:
- `src/models/tune.py`
- Best params JSON + tuned model artifacts

Acceptance criteria:
- Tuning run is resumable
- Best model performance improves baseline (or clearly documented if not)

---

## Day 6 - Experiment Tracking and Model Registry

Tasks:
- Configure MLflow tracking URI and experiment names
- Log params, metrics, artifacts, feature schema
- Register winning model to MLflow Registry
- Define stage flow: `Staging -> Production`

Tools:
- MLflow Tracking + Registry

Deliverables:
- Standardized run naming convention
- Registered model with version and tags

Acceptance criteria:
- You can trace any deployed model to data version + code commit

---

## Day 7 - Test Strategy and Quality Gates

Tasks:
- Unit tests for transformers, data validation, model scoring
- Integration test for training pipeline
- Contract test for prediction request/response schema
- Add linting and formatting checks

Tools:
- pytest, ruff, black, isort, mypy (optional), pre-commit

Deliverables:
- `tests/` suite and quality configuration

Acceptance criteria:
- CI fails on lint/test failures
- Minimum 70% test coverage for critical modules

---

## Day 8 - Inference API (FastAPI) and Input Guardrails

Tasks:
- Build `/health`, `/predict`, `/metadata` endpoints
- Add Pydantic request validation
- Include business rules/guardrails:
  - Non-negative distance/fare components
  - Allowed ranges for surcharges and fees
- Return model version and inference timestamp

Tools:
- FastAPI, Uvicorn, Pydantic

Deliverables:
- `src/deployment/api.py`, `src/deployment/schemas.py`

Acceptance criteria:
- API rejects malformed inputs with clear errors
- p95 inference latency target defined and measured

---

## Day 9 - User Dashboard and Batch Prediction UX

Tasks:
- Build Streamlit UI:
  - Single prediction form
  - CSV upload for batch predictions
  - Prediction summary charts
- Show model metadata and confidence proxies
- Export results as CSV/Parquet

Tools:
- Streamlit, pandas, plotly

Deliverables:
- `src/deployment/dashboard.py`

Acceptance criteria:
- Non-technical user can generate predictions without notebook use

---

## Day 10 - CI Pipeline Automation

Tasks:
- Create GitHub Actions workflow (`ci.yml`):
  - Setup environment
  - Lint + test
  - Build artifacts
- Add cache for dependencies
- Publish test reports and coverage

Tools:
- GitHub Actions

Deliverables:
- Passing CI on PRs

Acceptance criteria:
- Every PR automatically validated before merge

---

## Day 11 - CD Pipeline, Containerization, and Deployment

Tasks:
- Create API and dashboard Dockerfiles
- Compose multi-service deployment
- Add deploy workflow (`deploy.yml`) for staging
- Optional: Helm chart/K8s manifests for future scaling

Tools:
- Docker, Docker Compose, GitHub Actions, optional Kubernetes

Deliverables:
- One-command deployment with compose

Acceptance criteria:
- Services restart-safe and health-checked
- Re-deploy from clean environment succeeds

---

## Day 12 - Monitoring, Drift, and Alerting

Tasks:
- Expose API metrics for Prometheus scraping
- Create Grafana dashboards:
  - Request rate, error rate, latency
  - Prediction distribution trends
- Add drift job (Evidently/WhyLogs) for key features:
  - `trip_distance`, `tip_amount`, `fare_amount`, etc.
- Alert rules for drift and API anomalies

Tools:
- Prometheus, Grafana, Evidently or WhyLogs

Deliverables:
- Operational dashboard + drift report pipeline

Acceptance criteria:
- Drift detection runs on schedule
- Alerts triggered for threshold breaches

---

## Day 13 - Governance, Security, and Auditability

Tasks:
- Add model card and data card templates
- Document assumptions, limitations, and fairness notes
- Add dependency scans and secret scanning
- Enforce audit trail: model version, data version, commit SHA

Tools:
- MLflow tags, pip-audit, bandit, GitHub Advanced Security (if available)

Deliverables:
- Governance docs + security checks in CI

Acceptance criteria:
- Full traceability for production model lineage

---

## Day 14 - UAT, Performance Validation, and Go-Live Runbook

Tasks:
- End-to-end dry run from raw data to deployed prediction
- Load test API and validate SLOs
- Finalize runbook and rollback procedures
- Sign-off checklist for production readiness

Tools:
- Locust/k6, Docker Compose/Kubernetes, documentation templates

Deliverables:
- Release candidate tag + operational runbook

Acceptance criteria:
- Team can deploy, monitor, and rollback without notebook dependency

---

## 5) CI/CD Design (Jobs and Responsibilities)

## CI Pipeline (`ci.yml`)

Stages:
- Lint + format check
- Unit/integration tests
- Security scans
- Build test container

Triggers:
- Pull request to `main`
- Push to feature branches

## Training/Registry Pipeline (`train-register.yml`)

Stages:
- Pull latest DVC data
- Train baseline + tune top 3
- Log to MLflow
- Register selected model

Triggers:
- Manual dispatch
- Scheduled retraining
- Data update event

## Deployment Pipeline (`deploy.yml`)

Stages:
- Pull registered model
- Build and tag images
- Deploy to staging
- Smoke tests
- Manual approval to production

Triggers:
- New MLflow model promoted to Production

---

## 6) Monitoring and SLO Framework

Operational SLOs (initial):
- API availability: >= 99.5%
- p95 latency: <= 300 ms
- Prediction request error rate: <= 1%
- Weekly drift score below agreed threshold

Model Quality SLOs:
- Online proxy quality tracking enabled
- Scheduled offline backtesting against newly labeled data
- Alert when quality degrades by configured delta

Key Dashboards:
- User dashboard:
  - Interactive prediction panel
  - Batch upload results
  - Export and summary visuals
- Operations dashboard:
  - Throughput, errors, latency
  - Data drift indicators
  - Model version currently serving

---

## 7) Governance and Compliance Checklist

- Data schema and range validation at ingress
- Input payload validation via Pydantic
- Versioned lineage:
  - Code commit SHA
  - DVC dataset version
  - MLflow run and model version
- Reproducible builds via Docker + lockfile dependencies
- Approval gate for promotion to production
- Incident response and rollback documentation

---

## 8) Risk Register and Mitigation

- Risk: Training-serving skew
  - Mitigation: Shared preprocessing pipeline artifact and contract tests
- Risk: Data drift degrades predictions
  - Mitigation: Scheduled drift monitoring + auto alerting
- Risk: Silent model regression after retraining
  - Mitigation: Champion/challenger comparison before promotion
- Risk: Environment inconsistencies
  - Mitigation: Containerized builds and pinned dependencies

---

## 9) Detailed Tooling Matrix by Lifecycle Stage

| Lifecycle Stage | Primary Tools | Optional Tools | Output |
|---|---|---|---|
| Ingestion | pandas, DVC | Airbyte/Fivetran | Versioned raw dataset |
| Validation | custom checks, Great Expectations | Soda | Data quality report |
| Feature Engineering | sklearn Pipeline | Feature store (Feast) | Reusable preprocessor |
| Training | sklearn, XGBoost, LightGBM | CatBoost | Trained models |
| Tuning | Optuna | Ray Tune | Best hyperparameters |
| Tracking | MLflow | Weights & Biases | Experiment history |
| Registry | MLflow Registry | SageMaker Registry | Versioned approved model |
| Serving | FastAPI | KServe/Seldon | Prediction endpoint |
| UI | Streamlit | Gradio | User-facing app |
| CI/CD | GitHub Actions | GitLab CI/Jenkins | Automated quality + deploy |
| Monitoring | Prometheus + Grafana | Datadog/New Relic | Ops observability |
| Drift/Quality | Evidently/WhyLogs | Arize/Fiddler | Drift reports and alerts |
| Governance | model card templates | OpenLineage | Auditability + controls |

---

## 10) Definition of Done (Project Completion)

Project is complete when all are true:
- Notebook logic is fully modularized under `src/`
- DVC tracks data and pipeline stages
- MLflow tracks experiments and stores registered model
- FastAPI serves production prediction endpoint
- Streamlit dashboard supports user interaction and batch prediction
- CI/CD automates test, train/register, and deploy workflows
- Monitoring dashboard and drift detection are live
- Governance, security, and rollback runbooks are documented

---

## 11) Immediate Execution Plan (If You Want a 5-Day Fast Track)

## Day A
- Repo setup, environment, Docker, formatting/linting

## Day B
- Data versioning, validation, feature pipeline extraction

## Day C
- Multi-model training + top-3 tuning + MLflow logging

## Day D
- FastAPI + Streamlit + Docker Compose deployment

## Day E
- GitHub Actions CI/CD + Prometheus/Grafana + drift checks

This 5-day plan gets you to a functional production baseline quickly; then continue with governance hardening and advanced orchestration.

---

## 12) Suggested First Commands

```bash
# Environment and dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Initialize DVC and MLflow
 dvc init
 mlflow ui

# Run training
python -m src.models.train
python -m src.models.tune

# Serve API
uvicorn src.deployment.api:app --reload --host 0.0.0.0 --port 8000

# Run dashboard
streamlit run src/deployment/dashboard.py
```

---

## 13) Final Notes

This plan is intentionally detailed so you can execute implementation in a structured, auditable, and production-ready way while preserving the strong experimental work already completed in your notebook.

If needed, convert this plan into:
- Sprint board tasks (Jira/Trello)
- GitHub milestones and issues
- Team RACI matrix (owner per task)
