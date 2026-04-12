# GitHub Actions Monitoring & Verification Guide

Complete step-by-step process to check if all GitHub Actions workflows are running properly.

---

## Quick Check (5 minutes)

### Step 1: Go to GitHub Actions Dashboard

1. Open browser and go to: https://github.com/Yogesh1022/taxi-fare-mlops
2. Click the **"Actions"** tab (top navigation bar)

**Expected View:**
- List of recent workflow runs
- Each showing status (✅, ❌, ⏳, ⏭️)
- Latest commit should appear at the top

---

## Detailed Monitoring (15 minutes)

### Step 2: View All Workflows

You should see 5 main workflows:

| Workflow | Trigger | Purpose |
|----------|---------|---------|
| **CI** | Push to main | Run tests + code quality checks |
| **Model Validation** | Push to main | Validate ML models |
| **Deployment Ready** | Manual trigger | Pre-deployment checks |
| **Docker Build** | Push to main | Build Docker image |
| **Release** | Manual trigger | Release management |

### Step 3: Check Workflow Status

**Green Checkmark (✅)** = All jobs passed  
**Red X (❌)** = One or more jobs failed  
**Yellow Dot (⏳)** = Currently running  
**Skip (⏭️)** = Workflow was skipped

Click on **any workflow** to view detailed information.

---

## Comprehensive Verification Process

### Phase 1: Recent Runs (Latest Commits)

#### Step 1: View Latest Workflow Run

1. Go to **Actions** tab
2. Look at the latest run at the top
3. Check the **status icon**:
   - ✅ = Success (all jobs completed)
   - ❌ = Failure (at least one job failed)
   - ⏳ = In Progress
   - ? = Pending

#### Step 2: Click on the Latest Run

Click on the workflow name or commit message to see:
- Workflow name
- Branch (should be `main`)
- Commit hash
- Author name
- Timestamp
- List of **jobs** that ran

---

### Phase 2: Individual Job Details

#### Step 3: View Each Job

For each workflow, you should see these jobs:

**CI Workflow Jobs:**
1. ✓ Test (runs pytest with all unit tests)
2. ✓ Code-Quality (runs black, isort, flake8)
3. ✓ Coverage (checks if coverage ≥ 30%)

**Model Validation Workflow Jobs:**
1. ✓ Model-Validation (validates trained models)
2. ✓ Properties-Test (checks model properties)
3. ✓ Batch-Prediction (tests batch prediction)

**Deployment Ready Workflow Jobs:**
1. ✓ Pre-Deployment-Validation
2. ✓ Artifact-Check
3. ✓ Deployment-Summary

#### Step 4: Click on Individual Job

Click on any job name to see:
- ✅ or ❌ status
- Duration (how long it took)
- Each **step** within the job

Example steps in "Test" job:
```
✓ Checkout code
✓ Setup Python 3.11
✓ Install dependencies
✓ Run pytest
✓ Upload coverage reports
```

---

### Phase 3: Detailed Log Inspection

#### Step 5: View Job Logs

Click on any **step name** to expand and see detailed logs:

**Example: "Run pytest" step logs**
```
collected 107 items
tests/unit/test_batch_predictions.py ..................... [ 19%]
tests/unit/test_data.py . [ 20%]
...
========================== 107 passed in 10.23s ==========================
✓ All tests passed!
```

#### Step 6: Check for Errors

Look for red text or ERROR messages:

```
ERROR: test_inference_api.py::test_create_prediction - AssertionError
❌ Test failed - see stack trace below
```

If you see errors, expand the step to read the full error message.

---

## Troubleshooting Failures

### Issue 1: Workflow Failed to Complete

**Symptom:** Red ❌ on workflow run

**Steps to diagnose:**

1. Click on the failed workflow run
2. Look at which **job** failed (red ❌ next to job name)
3. Click on that job
4. Scroll through logs to find error message
5. Note the error at the bottom of the job

**Common errors:**

```
ERROR: ModuleNotFoundError: No module named 'mlflow'
→ Solution: Check requirements.txt has all dependencies

ERROR: 1 failed assertion
→ Solution: Review test file - code logic issue

ERROR: Docker build failed
→ Solution: Check Dockerfile syntax

ERROR: Coverage 25% < 30% threshold
→ Solution: Write more tests or reduce coverage threshold
```

### Issue 2: Workflow Not Triggering

**Symptom:** Push code but no workflow runs

**Steps to diagnose:**

1. Go to **Actions** tab
2. Check if workflow file exists: **Settings** → **Actions** → **General**
3. For manual workflows (deployment-ready, release):
   - Click **▶ Run workflow** button manually
4. Check workflow trigger conditions - may not match:
   - Check `branches` filter in workflow file
   - Check `paths` filter in workflow file
   - Check `if` conditions on jobs

### Issue 3: Workflow Runs But Takes Too Long

**Symptom:** Workflow runs for 30+ minutes

**Steps to diagnose:**

1. Click on the workflow run
2. Look at job durations
3. Find the slowest job
4. Click that job and check which step is slow
5. Usually is test execution or Docker build

**Solutions:**
- Split tests into parallel jobs
- Cache dependencies
- Optimize Docker build

---

## Verification Checklist

Use this to verify all workflows are healthy:

### ✅ Workflow Runs Automatically

- [ ] Pushed code to `main` branch
- [ ] Waited 1-2 minutes
- [ ] Workflow appears in **Actions** tab
- [ ] Status shows ✅ (green checkmark)

### ✅ Each Workflow Has All Jobs

**CI Workflow:**
- [ ] Test job ✅
- [ ] Code-Quality job ✅
- [ ] Coverage job ✅

**Model Validation Workflow:**
- [ ] Model-Validation job ✅
- [ ] Properties-Test job ✅
- [ ] Batch-Prediction job ✅

**Deployment Ready Workflow:**
- [ ] Pre-Deployment-Validation job ✅
- [ ] Artifact-Check job ✅
- [ ] Deployment-Summary job ✅

**Docker Workflow:**
- [ ] Build job ✅
- [ ] Image uploaded ✅

**Release Workflow:**
- [ ] Release job ✅

### ✅ Each Job Completes Successfully

- [ ] No red ❌ marks on any job
- [ ] All steps show ✓ checkmarks
- [ ] No ERROR messages in logs
- [ ] Total duration < 20 minutes per workflow

### ✅ Test Results

- [ ] 107 tests passing
- [ ] Coverage ≥ 30%
- [ ] No failed assertions
- [ ] No ModuleNotFoundError

### ✅ Code Quality

- [ ] Black formatting ✓
- [ ] isort import sorting ✓
- [ ] flake8 linting ✓
- [ ] No critical errors

---

## Reading Workflow Logs

### Understanding Log Format

```
::group::Run tests
  ▼ Expanding group: Run tests
  
  pytest tests/unit/ -v --cov=src
  
  ============================= test session starts ==============================
  platform linux -- Python 3.11.5, pytest-7.4.3, pluggy-1.5.0
  rootdir: /home/runner/work/taxi-fare-mlops
  configfile: pyproject.toml
  collected 107 items
  
  tests/unit/test_batch_predictions.py PASSED [ 1%]
  tests/unit/test_data.py PASSED [ 1%]
  ...
  
  ============================== 107 passed in 10.23s ===============================
  
::endgroup::
```

**Legend:**
- `::group::` = Start of collapsible section
- `PASSED` = Test passed ✓
- `FAILED` = Test failed ❌
- `SKIPPED` = Test skipped ⏭️
- `100%` = Progress indicator

### Interpreting Test Output

```
collected 107 items                      ← Total tests found
test_batch_predictions.py ........... [ 19%]  ← First 23 tests passed
test_data.py . [ 19%]                   ← 1 more test passed
...
======================== 107 passed in 10.16s ========================

✓ All 107 tests passed successfully
```

### Interpreting Code Quality Output

```
Black:
All done! ✨ 🍰 ✨
53 files left unchanged.

→ Means: 0 files need reformatting ✓

isort:
Skipped 10 files

→ Means: 0 import sorting errors ✓

flake8:
0

→ Means: 0 linting errors ✓
```

---

## Real-Time Monitoring

### Option 1: GitHub Web Interface (Recommended)

1. Go to: https://github.com/Yogesh1022/taxi-fare-mlops/actions
2. Page auto-refreshes every few seconds
3. Watch **status** column for changes
4. Click into running job to see live logs

### Option 2: GitHub CLI (Command Line)

```powershell
# Install GitHub CLI: https://cli.github.com

# View latest workflow runs
gh run list

# View specific run details
gh run view <RUN_ID>

# View job logs
gh run view <RUN_ID> --log

# Watch a run in real-time
gh run view <RUN_ID> --log --exit-status
```

### Option 3: GitHub Desktop App

1. Open GitHub Desktop
2. Go to **Repository** → **View on GitHub**
3. Click **Actions** tab
4. See all workflow runs with status

---

## Success Indicators

### ✅ Workflows Running Correctly

All of these should be true:

1. **Latest Commit** shows ✅ status
2. **All 5 workflows** have completed
3. **No red ❌** marks on any job
4. **107 tests passing**
5. **Coverage ≥ 30%**
6. **Code quality checks passed**
7. **Docker image built successfully**
8. **Logs show no errors**
9. **Total time < 20 minutes**
10. **All jobs show "Completed successfully"**

### ⚠️ Warning Signs

❌ Red ❌ mark on workflow  
❌ "This workflow is disabled"  
❌ Tests showing FAILED  
❌ Coverage < 30%  
❌ ERROR messages in logs  
❌ ModuleNotFoundError  
❌ Code quality failure  
❌ Docker build failure  
❌ Workflow timeout (> 30 minutes)

---

## Step-by-Step: Verify After Latest Push

### 1. Push Code to GitHub

```powershell
cd "e:\TaxiFare MLOps"
git add -A
git commit -m "Your message"
git push origin main
```

### 2. Wait for Workflows to Trigger

⏳ **Wait 1-2 minutes** for workflows to appear

### 3. Check GitHub Actions

1. Go to: https://github.com/Yogesh1022/taxi-fare-mlops/actions
2. Look for your commit message at the top
3. If workflows haven't appeared, wait 30 more seconds and refresh

### 4. Monitor Workflow Progress

| Time | Status |
|------|--------|
| 0-2 min | ⏳ Queued or Starting |
| 2-5 min | ⏳ Running first jobs |
| 5-10 min | ⏳ Running tests |
| 10-15 min | ⏳ Running validations |
| 15-20 min | ✅ Should be completed |

### 5. Verify Success

When complete, check:
- [ ] All workflow runs have ✅ status
- [ ] No red ❌ marks
- [ ] All jobs completed
- [ ] Click into logs to verify 107 tests passed

### 6. If Failed

If you see ❌ status:
1. Click on failed workflow
2. Click on failed job (red ❌)
3. Scroll to find ERROR message
4. Fix the issue locally
5. Commit and push again
6. Repeat steps 1-5

---

## Accessing Workflow Artifacts

### View Coverage Report

1. Go to failed/passed workflow run
2. Click on **CI** workflow
3. Look for **Artifacts** section at bottom
4. Download `coverage-report.zip`
5. Extract and open `htmlcov/index.html` in browser

### View Test Results

1. In workflow logs, look for pytest output
2. Shows pass/fail for each test
3. Failed tests show error messages

### View Build Logs

1. In **Docker** workflow
2. Click **Build** job
3. View Docker build output
4. Look for successful image push message

---

## Automating Checks

### Create Local Verification Script

```powershell
# save as: check_workflows.ps1

param(
    [string]$Owner = "Yogesh1022",
    [string]$Repo = "taxi-fare-mlops"
)

Write-Host "Checking GitHub Actions status..."
gh run list --repo "$Owner/$Repo" --limit 10
```

Run it:
```powershell
./check_workflows.ps1
```

---

## Common Questions

### Q: How long should workflows take?
**A:** Usually 10-15 minutes total. If > 25 min, something may be slow.

### Q: What if a workflow doesn't appear?
**A:** Wait 2 minutes and refresh. Check if branch push was successful. Ensure branch is `main`.

### Q: Can I trigger workflows manually?
**A:** Yes! Deployment-Ready and Release workflows have manual trigger buttons.

### Q: Where can I see failing test details?
**A:** Click on the failed job → scroll to failing test step → expand to see error.

### Q: How do I retry a failed workflow?
**A:** Click "Re-run jobs" or "Re-run all jobs" button on workflow run page.

### Q: Why is coverage < 30%?
**A:** Need more tests. Check coverage report to see which files need tests.

---

## Summary

**To check if GitHub Actions are working properly:**

1. ✅ Push code to `main`
2. ✅ Wait 1-2 minutes
3. ✅ Go to **Actions** tab
4. ✅ Check latest commit has ✅ status
5. ✅ All 5 workflows completed
6. ✅ No red ❌ marks
7. ✅ Click into jobs to verify logs show success
8. ✅ Tests, coverage, code quality all passing

**If any step fails:** Click on failed job and read error message to diagnose issue.

Your workflows are **working properly** when:
- ✅ Latest push shows all workflows ✅
- ✅ 107 tests passing
- ✅ Coverage ≥ 30%
- ✅ Code quality checks passed
- ✅ No error messages in logs
