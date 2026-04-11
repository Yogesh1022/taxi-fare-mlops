# GitHub Issues Templates - Day-Wise MLOps Execution

Use this file to create one GitHub issue per day in your project board.

## Suggested Project Board Columns
- Backlog
- Ready
- In Progress
- In Review
- Blocked
- Done

## Suggested Labels
- `mlops`
- `day-1` ... `day-14`
- `data`
- `features`
- `modeling`
- `tuning`
- `mlflow`
- `api`
- `dashboard`
- `ci`
- `cd`
- `monitoring`
- `governance`
- `security`
- `documentation`

## Suggested Milestones
- `M1 Foundation (Day 1-3)`
- `M2 Modeling (Day 4-6)`
- `M3 Productization (Day 7-11)`
- `M4 Operations (Day 12-14)`

---

## Issue 1 - Day 1: Project Bootstrap and Reproducible Environment

Title:
- `[Day 1] Bootstrap repository and reproducible environment`

Labels:
- `mlops`, `day-1`, `documentation`

Milestone:
- `M1 Foundation (Day 1-3)`

Description:
Set up base project structure, deterministic dependencies, and local/container reproducibility.

Checklist:
- [ ] Create folders: data, notebooks, src, tests, docker, .github/workflows, docs
- [ ] Move notebook into notebooks folder
- [ ] Add requirements.txt and/or pyproject.toml
- [ ] Add .gitignore, README.md, Makefile
- [ ] Add base Dockerfile and verify container build
- [ ] Add Make targets: setup, lint, test, train, serve
- [ ] Document setup steps in README

Definition of Done:
- [ ] Fresh machine setup works in under 15 minutes
- [ ] Training entry command runs without environment errors
- [ ] Docker image builds successfully

Artifacts:
- README setup section
- Initial project tree committed

---

## Issue 2 - Day 2: Data Versioning and Validation Contracts

Title:
- `[Day 2] Implement DVC data versioning and data contracts`

Labels:
- `mlops`, `day-2`, `data`

Milestone:
- `M1 Foundation (Day 1-3)`

Depends on:
- Day 1 issue

Description:
Create versioned data pipeline stages with schema checks and quality validation.

Checklist:
- [ ] Initialize DVC in repository
- [ ] Configure DVC remote (local or cloud)
- [ ] Add raw train/test files to data/raw
- [ ] Add schema validation (columns, dtypes, null thresholds)
- [ ] Add simple outlier checks for key numeric columns
- [ ] Add dvc.yaml stages: ingest, validate
- [ ] Generate and save validation report artifact

Definition of Done:
- [ ] Schema mismatch fails pipeline run
- [ ] Data versions can be reproduced via DVC checkout
- [ ] Validation report is generated and stored

Artifacts:
- dvc.yaml
- data validation report

---

## Issue 3 - Day 3: Reusable Feature Engineering Pipeline

Title:
- `[Day 3] Extract feature engineering into reusable sklearn pipeline`

Labels:
- `mlops`, `day-3`, `features`

Milestone:
- `M1 Foundation (Day 1-3)`

Depends on:
- Day 2 issue

Description:
Refactor notebook feature logic into reusable code for both training and inference.

Checklist:
- [ ] Implement datetime feature extraction (hour, day, weekday, month)
- [ ] Implement component_sum and related feature transforms
- [ ] Build ColumnTransformer + Pipeline structure
- [ ] Persist preprocessor artifact (joblib)
- [ ] Add unit tests for transformer outputs
- [ ] Add feature schema contract for training/inference parity

Definition of Done:
- [ ] Same pipeline object used in train and predict code paths
- [ ] Tests pass for expected columns and transformations
- [ ] No training-serving feature mismatch

Artifacts:
- src/features modules
- preprocessor artifact

---

## Issue 4 - Day 4: Multi-Model Baseline Training Framework

Title:
- `[Day 4] Build baseline training framework for 8 regression models`

Labels:
- `mlops`, `day-4`, `modeling`

Milestone:
- `M2 Modeling (Day 4-6)`

Depends on:
- Day 3 issue

Description:
Train and compare 8 baseline models under one standardized evaluation flow.

Checklist:
- [ ] Implement unified train script for all 8 models
- [ ] Standardize data split strategy (CV or train/val/test)
- [ ] Compute R2, RMSE, MAE for each model
- [ ] Save leaderboard table artifact
- [ ] Persist best baseline model and metadata
- [ ] Log run summary to file/artifact store

Definition of Done:
- [ ] One command trains all baseline models
- [ ] Metrics are reproducible
- [ ] Best model selected deterministically

Artifacts:
- model leaderboard
- best baseline model artifact

---

## Issue 5 - Day 5: Hyperparameter Tuning for Top 3 Models

Title:
- `[Day 5] Tune top 3 models with Optuna`

Labels:
- `mlops`, `day-5`, `tuning`

Milestone:
- `M2 Modeling (Day 4-6)`

Depends on:
- Day 4 issue

Description:
Run optimized hyperparameter search for top-3 baseline models.

Checklist:
- [ ] Select top 3 models from baseline leaderboard
- [ ] Define Optuna search spaces for each
- [ ] Set time budget / trial caps
- [ ] Enable early stopping where supported
- [ ] Save best parameters per model
- [ ] Compare tuned vs baseline metrics

Definition of Done:
- [ ] Tuning execution is resumable
- [ ] Best trial info saved in structured file
- [ ] Performance comparison documented

Artifacts:
- best_params.json
- tuned model artifacts

---

## Issue 6 - Day 6: MLflow Tracking and Model Registry

Title:
- `[Day 6] Integrate MLflow tracking and model registry workflow`

Labels:
- `mlops`, `day-6`, `mlflow`

Milestone:
- `M2 Modeling (Day 4-6)`

Depends on:
- Day 5 issue

Description:
Track all experiments and register winning model with stage lifecycle controls.

Checklist:
- [ ] Configure MLflow tracking URI and experiment names
- [ ] Log params, metrics, artifacts, model signature
- [ ] Add tags: commit SHA, data version, pipeline version
- [ ] Register winning model in MLflow Registry
- [ ] Define stage transitions: Staging -> Production
- [ ] Document model naming/versioning policy

Definition of Done:
- [ ] Every registered model has full lineage metadata
- [ ] Registered model is deployable by version reference

Artifacts:
- MLflow experiment runs
- Registered model version

---

## Issue 7 - Day 7: Testing Strategy and Quality Gates

Title:
- `[Day 7] Add tests, linting, and local quality gates`

Labels:
- `mlops`, `day-7`, `documentation`

Milestone:
- `M3 Productization (Day 7-11)`

Depends on:
- Day 6 issue

Description:
Establish test coverage and coding standards for reliability.

Checklist:
- [ ] Add unit tests for data validators and feature transformers
- [ ] Add integration test for training flow
- [ ] Add contract test for prediction request/response schema
- [ ] Configure pytest, ruff, black, isort
- [ ] Configure pre-commit hooks
- [ ] Add minimum coverage threshold for critical modules

Definition of Done:
- [ ] Test and lint commands pass locally
- [ ] Pre-commit blocks non-compliant commits
- [ ] Coverage report generated

Artifacts:
- tests suite
- linter/config files

---

## Issue 8 - Day 8: FastAPI Inference Service with Guardrails

Title:
- `[Day 8] Build production inference API with validation guardrails`

Labels:
- `mlops`, `day-8`, `api`

Milestone:
- `M3 Productization (Day 7-11)`

Depends on:
- Day 7 issue

Description:
Serve model predictions via FastAPI with strict input/output contracts.

Checklist:
- [ ] Implement endpoints: /health, /predict, /metadata
- [ ] Define Pydantic input/output schemas
- [ ] Validate numeric ranges and non-negative constraints
- [ ] Load model and preprocessor artifacts on startup
- [ ] Return model version and inference timestamp
- [ ] Add API smoke test script

Definition of Done:
- [ ] Invalid payloads return clear validation errors
- [ ] Valid payload produces deterministic response schema
- [ ] Health endpoint reports model-loaded status

Artifacts:
- API application code
- API contract document

---

## Issue 9 - Day 9: Streamlit User Dashboard and Batch Prediction

Title:
- `[Day 9] Build Streamlit user dashboard for online and batch prediction`

Labels:
- `mlops`, `day-9`, `dashboard`

Milestone:
- `M3 Productization (Day 7-11)`

Depends on:
- Day 8 issue

Description:
Deliver user-facing app for individual and CSV batch predictions.

Checklist:
- [ ] Create single-record prediction form
- [ ] Add CSV upload and batch prediction workflow
- [ ] Display summary statistics and plots
- [ ] Add export to CSV/Parquet
- [ ] Display active model version and run metadata
- [ ] Add user usage notes and error guidance

Definition of Done:
- [ ] Non-technical user can run predictions end-to-end
- [ ] Batch outputs are downloadable and correctly formatted

Artifacts:
- Streamlit app
- sample input/output files

---

## Issue 10 - Day 10: CI Workflow on Pull Requests

Title:
- `[Day 10] Implement CI workflow for lint, test, and build checks`

Labels:
- `mlops`, `day-10`, `ci`

Milestone:
- `M3 Productization (Day 7-11)`

Depends on:
- Day 7 issue

Description:
Automate quality verification for every pull request.

Checklist:
- [ ] Create .github/workflows/ci.yml
- [ ] Add setup and dependency cache
- [ ] Run lint and tests
- [ ] Run security checks (pip-audit and bandit)
- [ ] Build container in CI for verification
- [ ] Publish test/coverage artifacts

Definition of Done:
- [ ] PRs are blocked on CI failure
- [ ] CI runtime is acceptable and stable
- [ ] Security scan results visible in workflow logs

Artifacts:
- ci.yml workflow
- CI status badges

---

## Issue 11 - Day 11: CD and Multi-Service Container Deployment

Title:
- `[Day 11] Implement deployment pipeline and Docker Compose stack`

Labels:
- `mlops`, `day-11`, `cd`

Milestone:
- `M3 Productization (Day 7-11)`

Depends on:
- Day 8 issue
- Day 9 issue
- Day 10 issue

Description:
Package and deploy API + dashboard services using automated workflow.

Checklist:
- [ ] Create Dockerfile for API service
- [ ] Create Dockerfile for dashboard service
- [ ] Create docker-compose.yml for local orchestration
- [ ] Add deploy workflow for staging
- [ ] Add health checks and startup ordering
- [ ] Add smoke tests after deployment

Definition of Done:
- [ ] Stack boots with one compose command
- [ ] API and dashboard are both reachable
- [ ] Staging deployment workflow succeeds end-to-end

Artifacts:
- Dockerfiles
- docker-compose.yml
- deploy.yml workflow

---

## Issue 12 - Day 12: Monitoring, Observability, and Drift Detection

Title:
- `[Day 12] Add monitoring dashboards and drift detection pipeline`

Labels:
- `mlops`, `day-12`, `monitoring`

Milestone:
- `M4 Operations (Day 12-14)`

Depends on:
- Day 11 issue

Description:
Operationalize system observability and model/data drift detection.

Checklist:
- [ ] Expose API metrics for Prometheus
- [ ] Configure Prometheus scraping
- [ ] Build Grafana operational dashboard panels
- [ ] Add drift analysis job using Evidently or WhyLogs
- [ ] Define drift thresholds and alert rules
- [ ] Store daily/weekly drift reports

Definition of Done:
- [ ] Dashboard shows request rate, error rate, latency
- [ ] Drift report generated on schedule
- [ ] Alerts fire when thresholds are crossed

Artifacts:
- Prometheus config
- Grafana dashboard JSON
- drift reports

---

## Issue 13 - Day 13: Governance, Security, and Auditability

Title:
- `[Day 13] Implement governance controls and security checks`

Labels:
- `mlops`, `day-13`, `governance`, `security`

Milestone:
- `M4 Operations (Day 12-14)`

Depends on:
- Day 12 issue

Description:
Add compliance-style controls, model documentation, and full audit trail.

Checklist:
- [ ] Add model card template and complete for active model
- [ ] Add data card documenting source and assumptions
- [ ] Enforce lineage metadata (model version, data version, commit SHA)
- [ ] Add dependency vulnerability checks in CI
- [ ] Add static security scan in CI
- [ ] Document rollback and incident response steps

Definition of Done:
- [ ] Production model is fully traceable
- [ ] Security checks run on every PR
- [ ] Governance docs are reviewed and approved

Artifacts:
- model card
- data card
- runbook updates

---

## Issue 14 - Day 14: UAT, Performance Validation, and Release Readiness

Title:
- `[Day 14] Complete UAT, load validation, and production readiness sign-off`

Labels:
- `mlops`, `day-14`, `documentation`

Milestone:
- `M4 Operations (Day 12-14)`

Depends on:
- Day 13 issue

Description:
Perform final end-to-end validation, performance checks, and go-live preparation.

Checklist:
- [ ] Run full pipeline from raw data to deployed service
- [ ] Execute UAT scenarios for API and dashboard
- [ ] Run load/performance test and capture SLO metrics
- [ ] Verify monitoring and alert paths
- [ ] Verify rollback procedure with a dry run
- [ ] Create release notes and final sign-off checklist

Definition of Done:
- [ ] Production readiness checklist completed
- [ ] Team can deploy, monitor, and rollback confidently
- [ ] Release tag created with documented outcomes

Artifacts:
- UAT report
- performance test report
- release notes

---

## Optional Parent Epic (Recommended)

Title:
- `Epic: Productionize NYC Taxi Fare notebook into full MLOps system`

Checklist:
- [ ] Day 1 complete
- [ ] Day 2 complete
- [ ] Day 3 complete
- [ ] Day 4 complete
- [ ] Day 5 complete
- [ ] Day 6 complete
- [ ] Day 7 complete
- [ ] Day 8 complete
- [ ] Day 9 complete
- [ ] Day 10 complete
- [ ] Day 11 complete
- [ ] Day 12 complete
- [ ] Day 13 complete
- [ ] Day 14 complete

---

## Suggested Assignee Pattern

- Data Engineer: Day 2-3
- ML Engineer: Day 4-6
- MLOps Engineer: Day 10-12
- Backend Engineer: Day 8, Day 11
- Product/Analytics: Day 9, Day 14
- Security/Governance Reviewer: Day 13

---

## Suggested GitHub Issue Template Header (Copy into each issue)

Use this section at the top of each issue body:

```md
## Goal
<one paragraph outcome>

## Scope
- In scope:
- Out of scope:

## Dependencies
- 

## Checklist
- [ ] 

## Definition of Done
- [ ] 

## Artifacts
- 

## Notes
- 
```
