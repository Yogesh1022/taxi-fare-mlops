# GitHub CLI Auto-Create Script (All 14 Day-Wise Issues)

This file provides a one-shot PowerShell script to create all 14 issues from your plan using GitHub CLI.

## Prerequisites

- GitHub CLI installed: `gh --version`
- Authenticated session: `gh auth login`
- Run from your repository root

Optional check:

```powershell
# Confirm current repository target
$repo = gh repo view --json nameWithOwner -q .nameWithOwner
"Using repo: $repo"
```

---

## One-Shot Script (PowerShell)

Copy, paste, and run the full script below in PowerShell.

```powershell
$ErrorActionPreference = "Stop"

function Ensure-Label {
    param(
        [string]$Name,
        [string]$Color = "0E8A16",
        [string]$Description = ""
    )

    $exists = gh label list --limit 500 --json name -q ".[].name" | Where-Object { $_ -eq $Name }
    if (-not $exists) {
        if ([string]::IsNullOrWhiteSpace($Description)) {
            gh label create $Name --color $Color | Out-Null
        } else {
            gh label create $Name --color $Color --description $Description | Out-Null
        }
        Write-Host "Created label: $Name"
    } else {
        Write-Host "Label exists: $Name"
    }
}

function Ensure-Milestone {
    param([string]$Title)

    $exists = gh api repos/{owner}/{repo}/milestones --paginate --jq ".[] | select(.title == \"$Title\") | .title"
    if (-not $exists) {
        gh api repos/{owner}/{repo}/milestones -X POST -f title="$Title" | Out-Null
        Write-Host "Created milestone: $Title"
    } else {
        Write-Host "Milestone exists: $Title"
    }
}

function New-Issue {
    param(
        [string]$Title,
        [string]$Body,
        [string[]]$Labels,
        [string]$Milestone
    )

    $args = @("issue", "create", "--title", $Title, "--body", $Body, "--milestone", $Milestone)
    foreach ($label in $Labels) {
        $args += @("--label", $label)
    }

    $url = gh @args
    Write-Host "Created: $url"

    # URL format ends with /issues/<number>
    $issueNumber = [int]($url.Trim().Split("/")[-1])
    return $issueNumber
}

# 1) Ensure labels
$labels = @(
    "mlops","data","features","modeling","tuning","mlflow","api","dashboard","ci","cd","monitoring","governance","security","documentation"
)
$dayLabels = 1..14 | ForEach-Object { "day-$_" }

foreach ($l in $labels) { Ensure-Label -Name $l }
foreach ($l in $dayLabels) { Ensure-Label -Name $l -Color "1D76DB" }

# 2) Ensure milestones
$m1 = "M1 Foundation (Day 1-3)"
$m2 = "M2 Modeling (Day 4-6)"
$m3 = "M3 Productization (Day 7-11)"
$m4 = "M4 Operations (Day 12-14)"

Ensure-Milestone -Title $m1
Ensure-Milestone -Title $m2
Ensure-Milestone -Title $m3
Ensure-Milestone -Title $m4

# 3) Create issues in dependency order
$issues = @{}

$body1 = @"
## Goal
Set up base project structure, deterministic dependencies, and local/container reproducibility.

## Checklist
- [ ] Create folders: data, notebooks, src, tests, docker, .github/workflows, docs
- [ ] Move notebook into notebooks folder
- [ ] Add requirements.txt and/or pyproject.toml
- [ ] Add .gitignore, README.md, Makefile
- [ ] Add base Dockerfile and verify container build
- [ ] Add Make targets: setup, lint, test, train, serve
- [ ] Document setup steps in README

## Definition of Done
- [ ] Fresh machine setup works in under 15 minutes
- [ ] Training entry command runs without environment errors
- [ ] Docker image builds successfully
"@
$issues[1] = New-Issue -Title "[Day 1] Bootstrap repository and reproducible environment" -Body $body1 -Labels @("mlops","day-1","documentation") -Milestone $m1

$body2 = @"
## Goal
Create versioned data pipeline stages with schema checks and quality validation.

## Depends on
- #$($issues[1])

## Checklist
- [ ] Initialize DVC in repository
- [ ] Configure DVC remote (local or cloud)
- [ ] Add raw train/test files to data/raw
- [ ] Add schema validation (columns, dtypes, null thresholds)
- [ ] Add simple outlier checks for key numeric columns
- [ ] Add dvc.yaml stages: ingest, validate
- [ ] Generate and save validation report artifact

## Definition of Done
- [ ] Schema mismatch fails pipeline run
- [ ] Data versions can be reproduced via DVC checkout
- [ ] Validation report is generated and stored
"@
$issues[2] = New-Issue -Title "[Day 2] Implement DVC data versioning and data contracts" -Body $body2 -Labels @("mlops","day-2","data") -Milestone $m1

$body3 = @"
## Goal
Refactor notebook feature logic into reusable code for both training and inference.

## Depends on
- #$($issues[2])

## Checklist
- [ ] Implement datetime feature extraction (hour, day, weekday, month)
- [ ] Implement component_sum and related feature transforms
- [ ] Build ColumnTransformer + Pipeline structure
- [ ] Persist preprocessor artifact (joblib)
- [ ] Add unit tests for transformer outputs
- [ ] Add feature schema contract for training/inference parity

## Definition of Done
- [ ] Same pipeline object used in train and predict code paths
- [ ] Tests pass for expected columns and transformations
- [ ] No training-serving feature mismatch
"@
$issues[3] = New-Issue -Title "[Day 3] Extract feature engineering into reusable sklearn pipeline" -Body $body3 -Labels @("mlops","day-3","features") -Milestone $m1

$body4 = @"
## Goal
Train and compare 8 baseline models under one standardized evaluation flow.

## Depends on
- #$($issues[3])

## Checklist
- [ ] Implement unified train script for all 8 models
- [ ] Standardize data split strategy (CV or train/val/test)
- [ ] Compute R2, RMSE, MAE for each model
- [ ] Save leaderboard table artifact
- [ ] Persist best baseline model and metadata
- [ ] Log run summary to file/artifact store

## Definition of Done
- [ ] One command trains all baseline models
- [ ] Metrics are reproducible
- [ ] Best model selected deterministically
"@
$issues[4] = New-Issue -Title "[Day 4] Build baseline training framework for 8 regression models" -Body $body4 -Labels @("mlops","day-4","modeling") -Milestone $m2

$body5 = @"
## Goal
Run optimized hyperparameter search for top-3 baseline models.

## Depends on
- #$($issues[4])

## Checklist
- [ ] Select top 3 models from baseline leaderboard
- [ ] Define Optuna search spaces for each
- [ ] Set time budget / trial caps
- [ ] Enable early stopping where supported
- [ ] Save best parameters per model
- [ ] Compare tuned vs baseline metrics

## Definition of Done
- [ ] Tuning execution is resumable
- [ ] Best trial info saved in structured file
- [ ] Performance comparison documented
"@
$issues[5] = New-Issue -Title "[Day 5] Tune top 3 models with Optuna" -Body $body5 -Labels @("mlops","day-5","tuning") -Milestone $m2

$body6 = @"
## Goal
Track all experiments and register winning model with stage lifecycle controls.

## Depends on
- #$($issues[5])

## Checklist
- [ ] Configure MLflow tracking URI and experiment names
- [ ] Log params, metrics, artifacts, model signature
- [ ] Add tags: commit SHA, data version, pipeline version
- [ ] Register winning model in MLflow Registry
- [ ] Define stage transitions: Staging -> Production
- [ ] Document model naming/versioning policy

## Definition of Done
- [ ] Every registered model has full lineage metadata
- [ ] Registered model is deployable by version reference
"@
$issues[6] = New-Issue -Title "[Day 6] Integrate MLflow tracking and model registry workflow" -Body $body6 -Labels @("mlops","day-6","mlflow") -Milestone $m2

$body7 = @"
## Goal
Establish test coverage and coding standards for reliability.

## Depends on
- #$($issues[6])

## Checklist
- [ ] Add unit tests for data validators and feature transformers
- [ ] Add integration test for training flow
- [ ] Add contract test for prediction request/response schema
- [ ] Configure pytest, ruff, black, isort
- [ ] Configure pre-commit hooks
- [ ] Add minimum coverage threshold for critical modules

## Definition of Done
- [ ] Test and lint commands pass locally
- [ ] Pre-commit blocks non-compliant commits
- [ ] Coverage report generated
"@
$issues[7] = New-Issue -Title "[Day 7] Add tests, linting, and local quality gates" -Body $body7 -Labels @("mlops","day-7","documentation") -Milestone $m3

$body8 = @"
## Goal
Serve model predictions via FastAPI with strict input/output contracts.

## Depends on
- #$($issues[7])

## Checklist
- [ ] Implement endpoints: /health, /predict, /metadata
- [ ] Define Pydantic input/output schemas
- [ ] Validate numeric ranges and non-negative constraints
- [ ] Load model and preprocessor artifacts on startup
- [ ] Return model version and inference timestamp
- [ ] Add API smoke test script

## Definition of Done
- [ ] Invalid payloads return clear validation errors
- [ ] Valid payload produces deterministic response schema
- [ ] Health endpoint reports model-loaded status
"@
$issues[8] = New-Issue -Title "[Day 8] Build production inference API with validation guardrails" -Body $body8 -Labels @("mlops","day-8","api") -Milestone $m3

$body9 = @"
## Goal
Deliver user-facing app for individual and CSV batch predictions.

## Depends on
- #$($issues[8])

## Checklist
- [ ] Create single-record prediction form
- [ ] Add CSV upload and batch prediction workflow
- [ ] Display summary statistics and plots
- [ ] Add export to CSV/Parquet
- [ ] Display active model version and run metadata
- [ ] Add user usage notes and error guidance

## Definition of Done
- [ ] Non-technical user can run predictions end-to-end
- [ ] Batch outputs are downloadable and correctly formatted
"@
$issues[9] = New-Issue -Title "[Day 9] Build Streamlit user dashboard for online and batch prediction" -Body $body9 -Labels @("mlops","day-9","dashboard") -Milestone $m3

$body10 = @"
## Goal
Automate quality verification for every pull request.

## Depends on
- #$($issues[7])

## Checklist
- [ ] Create .github/workflows/ci.yml
- [ ] Add setup and dependency cache
- [ ] Run lint and tests
- [ ] Run security checks (pip-audit and bandit)
- [ ] Build container in CI for verification
- [ ] Publish test/coverage artifacts

## Definition of Done
- [ ] PRs are blocked on CI failure
- [ ] CI runtime is acceptable and stable
- [ ] Security scan results visible in workflow logs
"@
$issues[10] = New-Issue -Title "[Day 10] Implement CI workflow for lint, test, and build checks" -Body $body10 -Labels @("mlops","day-10","ci") -Milestone $m3

$body11 = @"
## Goal
Package and deploy API + dashboard services using automated workflow.

## Depends on
- #$($issues[8])
- #$($issues[9])
- #$($issues[10])

## Checklist
- [ ] Create Dockerfile for API service
- [ ] Create Dockerfile for dashboard service
- [ ] Create docker-compose.yml for local orchestration
- [ ] Add deploy workflow for staging
- [ ] Add health checks and startup ordering
- [ ] Add smoke tests after deployment

## Definition of Done
- [ ] Stack boots with one compose command
- [ ] API and dashboard are both reachable
- [ ] Staging deployment workflow succeeds end-to-end
"@
$issues[11] = New-Issue -Title "[Day 11] Implement deployment pipeline and Docker Compose stack" -Body $body11 -Labels @("mlops","day-11","cd") -Milestone $m3

$body12 = @"
## Goal
Operationalize system observability and model/data drift detection.

## Depends on
- #$($issues[11])

## Checklist
- [ ] Expose API metrics for Prometheus
- [ ] Configure Prometheus scraping
- [ ] Build Grafana operational dashboard panels
- [ ] Add drift analysis job using Evidently or WhyLogs
- [ ] Define drift thresholds and alert rules
- [ ] Store daily/weekly drift reports

## Definition of Done
- [ ] Dashboard shows request rate, error rate, latency
- [ ] Drift report generated on schedule
- [ ] Alerts fire when thresholds are crossed
"@
$issues[12] = New-Issue -Title "[Day 12] Add monitoring dashboards and drift detection pipeline" -Body $body12 -Labels @("mlops","day-12","monitoring") -Milestone $m4

$body13 = @"
## Goal
Add governance controls, model documentation, and full audit trail.

## Depends on
- #$($issues[12])

## Checklist
- [ ] Add model card template and complete for active model
- [ ] Add data card documenting source and assumptions
- [ ] Enforce lineage metadata (model version, data version, commit SHA)
- [ ] Add dependency vulnerability checks in CI
- [ ] Add static security scan in CI
- [ ] Document rollback and incident response steps

## Definition of Done
- [ ] Production model is fully traceable
- [ ] Security checks run on every PR
- [ ] Governance docs are reviewed and approved
"@
$issues[13] = New-Issue -Title "[Day 13] Implement governance controls and security checks" -Body $body13 -Labels @("mlops","day-13","governance","security") -Milestone $m4

$body14 = @"
## Goal
Perform final end-to-end validation, performance checks, and go-live preparation.

## Depends on
- #$($issues[13])

## Checklist
- [ ] Run full pipeline from raw data to deployed service
- [ ] Execute UAT scenarios for API and dashboard
- [ ] Run load/performance test and capture SLO metrics
- [ ] Verify monitoring and alert paths
- [ ] Verify rollback procedure with a dry run
- [ ] Create release notes and final sign-off checklist

## Definition of Done
- [ ] Production readiness checklist completed
- [ ] Team can deploy, monitor, and rollback confidently
- [ ] Release tag created with documented outcomes
"@
$issues[14] = New-Issue -Title "[Day 14] Complete UAT, load validation, and production readiness sign-off" -Body $body14 -Labels @("mlops","day-14","documentation") -Milestone $m4

Write-Host ""
Write-Host "All 14 issues created successfully."
Write-Host "Issue numbers:"
$issues.GetEnumerator() | Sort-Object Name | ForEach-Object { Write-Host "Day $($_.Name): #$($_.Value)" }
```

---

## Optional: Create a Parent Epic and Link the 14 Issues

Run after the script above:

```powershell
$epicBody = @"
## Goal
Track end-to-end productionization of NYC Taxi Fare notebook into a complete MLOps system.

## Checklist
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
"@

gh issue create \
  --title "Epic: Productionize NYC Taxi Fare notebook into full MLOps system" \
  --body $epicBody \
  --label mlops \
  --label documentation
```

---

## Optional: Add Created Issues to a GitHub Project (v2)

If you use GitHub Projects, list your projects first:

```powershell
gh project list --owner "<OWNER>"
```

Then add each issue URL manually, or script against `gh project item-add` if you have a fixed project ID.

---

## Troubleshooting

- `milestone not found`:
  - Re-run script; it creates milestones automatically.
- `label not found`:
  - Re-run script; it creates labels automatically.
- `HTTP 401/403`:
  - Re-authenticate with `gh auth login` and confirm repo permissions.
- Wrong repo target:
  - Run inside correct repo folder, or use `--repo owner/name` on each command.
