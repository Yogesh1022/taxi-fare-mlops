# GitHub CLI Minimal Script (Titles + Labels Only)

Use this minimal variant when you want very fast issue creation with only titles and labels.

## Prerequisites

- GitHub CLI installed: `gh --version`
- Logged in: `gh auth login`
- Run from your repository root

---

## Minimal One-Shot Script (PowerShell)

```powershell
$ErrorActionPreference = "Stop"

function Ensure-Label {
    param(
        [string]$Name,
        [string]$Color = "0E8A16"
    )

    $exists = gh label list --limit 500 --json name -q ".[].name" | Where-Object { $_ -eq $Name }
    if (-not $exists) {
        gh label create $Name --color $Color | Out-Null
        Write-Host "Created label: $Name"
    }
}

# Create shared labels + day labels
$labels = @(
    "mlops","data","features","modeling","tuning","mlflow","api","dashboard","ci","cd","monitoring","governance","security","documentation"
)
$dayLabels = 1..14 | ForEach-Object { "day-$_" }

foreach ($l in $labels) { Ensure-Label -Name $l }
foreach ($l in $dayLabels) { Ensure-Label -Name $l -Color "1D76DB" }

# Issue definitions: Title + labels only
$issues = @(
    @{ Title = "[Day 1] Bootstrap repository and reproducible environment"; Labels = @("mlops","day-1","documentation") },
    @{ Title = "[Day 2] Implement DVC data versioning and data contracts"; Labels = @("mlops","day-2","data") },
    @{ Title = "[Day 3] Extract feature engineering into reusable sklearn pipeline"; Labels = @("mlops","day-3","features") },
    @{ Title = "[Day 4] Build baseline training framework for 8 regression models"; Labels = @("mlops","day-4","modeling") },
    @{ Title = "[Day 5] Tune top 3 models with Optuna"; Labels = @("mlops","day-5","tuning") },
    @{ Title = "[Day 6] Integrate MLflow tracking and model registry workflow"; Labels = @("mlops","day-6","mlflow") },
    @{ Title = "[Day 7] Add tests, linting, and local quality gates"; Labels = @("mlops","day-7","documentation") },
    @{ Title = "[Day 8] Build production inference API with validation guardrails"; Labels = @("mlops","day-8","api") },
    @{ Title = "[Day 9] Build Streamlit user dashboard for online and batch prediction"; Labels = @("mlops","day-9","dashboard") },
    @{ Title = "[Day 10] Implement CI workflow for lint, test, and build checks"; Labels = @("mlops","day-10","ci") },
    @{ Title = "[Day 11] Implement deployment pipeline and Docker Compose stack"; Labels = @("mlops","day-11","cd") },
    @{ Title = "[Day 12] Add monitoring dashboards and drift detection pipeline"; Labels = @("mlops","day-12","monitoring") },
    @{ Title = "[Day 13] Implement governance controls and security checks"; Labels = @("mlops","day-13","governance","security") },
    @{ Title = "[Day 14] Complete UAT, load validation, and production readiness sign-off"; Labels = @("mlops","day-14","documentation") }
)

# Create issues quickly with a minimal placeholder body
$created = @()
foreach ($item in $issues) {
    $args = @("issue", "create", "--title", $item.Title, "--body", "Minimal issue. See planning docs for full checklist.")
    foreach ($label in $item.Labels) {
        $args += @("--label", $label)
    }
    $url = gh @args
    $created += $url
    Write-Host "Created: $url"
}

Write-Host ""
Write-Host "Created $($created.Count) issues."
```

---

## Optional Even-Faster Variant (No Label Auto-Creation)

Use this only if labels already exist in the repo.

```powershell
$issues = @(
    @{ Title = "[Day 1] Bootstrap repository and reproducible environment"; Labels = "mlops,day-1,documentation" },
    @{ Title = "[Day 2] Implement DVC data versioning and data contracts"; Labels = "mlops,day-2,data" },
    @{ Title = "[Day 3] Extract feature engineering into reusable sklearn pipeline"; Labels = "mlops,day-3,features" },
    @{ Title = "[Day 4] Build baseline training framework for 8 regression models"; Labels = "mlops,day-4,modeling" },
    @{ Title = "[Day 5] Tune top 3 models with Optuna"; Labels = "mlops,day-5,tuning" },
    @{ Title = "[Day 6] Integrate MLflow tracking and model registry workflow"; Labels = "mlops,day-6,mlflow" },
    @{ Title = "[Day 7] Add tests, linting, and local quality gates"; Labels = "mlops,day-7,documentation" },
    @{ Title = "[Day 8] Build production inference API with validation guardrails"; Labels = "mlops,day-8,api" },
    @{ Title = "[Day 9] Build Streamlit user dashboard for online and batch prediction"; Labels = "mlops,day-9,dashboard" },
    @{ Title = "[Day 10] Implement CI workflow for lint, test, and build checks"; Labels = "mlops,day-10,ci" },
    @{ Title = "[Day 11] Implement deployment pipeline and Docker Compose stack"; Labels = "mlops,day-11,cd" },
    @{ Title = "[Day 12] Add monitoring dashboards and drift detection pipeline"; Labels = "mlops,day-12,monitoring" },
    @{ Title = "[Day 13] Implement governance controls and security checks"; Labels = "mlops,day-13,governance,security" },
    @{ Title = "[Day 14] Complete UAT, load validation, and production readiness sign-off"; Labels = "mlops,day-14,documentation" }
)

foreach ($item in $issues) {
    gh issue create --title $item.Title --body "Minimal issue." --label $item.Labels
}
```

---

## Notes

- This minimal script intentionally skips milestones and detailed bodies.
- Use the full script in `GITHUB_ISSUES_CLI_AUTOCREATE.md` when you need complete issue descriptions and dependency links.
