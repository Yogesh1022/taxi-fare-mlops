# GitHub Actions Workflow Verification Guide

Complete step-by-step process to check if GitHub Actions workflows are running correctly.

---

## Table of Contents
1. [Local Pre-Commit Checks](#local-pre-commit-checks)
2. [Workflow File Validation](#workflow-file-validation)
3. [Running Tests Locally](#running-tests-locally)
4. [Code Quality Checks](#code-quality-checks)
5. [Viewing GitHub Actions Dashboard](#viewing-github-actions-dashboard)
6. [Interpreting Workflow Logs](#interpreting-workflow-logs)
7. [Common Issues & Solutions](#common-issues--solutions)
8. [Complete Verification Checklist](#complete-verification-checklist)

---

## Local Pre-Commit Checks

Before pushing to GitHub, verify everything works locally.

### Step 1: Install Development Dependencies

```bash
pip install -r requirements.txt
pip install pytest pytest-cov pytest-asyncio black isort flake8
```

### Step 2: Verify Python Version (Python 3.10+ required)

```bash
python --version
# Expected output: Python 3.10.x or higher
```

### Step 3: Check Virtual Environment (Optional but Recommended)

```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

---

## Workflow File Validation

### Step 1: List All Workflow Files

```bash
# Windows PowerShell
ls .github/workflows/

# macOS/Linux
ls -la .github/workflows/
```

Expected files:
- `ci.yml` - Continuous Integration pipeline
- `deployment-ready.yml` - Deployment validation
- `model-validation.yml` - Model testing
- `docker.yml` - Docker build
- `release.yml` - Release management

### Step 2: Validate YAML Syntax

Each workflow should have proper YAML structure:

```bash
# Check for YAML syntax errors
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))" && echo "✓ ci.yml is valid"
python -c "import yaml; yaml.safe_load(open('.github/workflows/deployment-ready.yml'))" && echo "✓ deployment-ready.yml is valid"
python -c "import yaml; yaml.safe_load(open('.github/workflows/model-validation.yml'))" && echo "✓ model-validation.yml is valid"
python -c "import yaml; yaml.safe_load(open('.github/workflows/docker.yml'))" && echo "✓ docker.yml is valid"
python -c "import yaml; yaml.safe_load(open('.github/workflows/release.yml'))" && echo "✓ release.yml is valid"
```

---

## Running Tests Locally

### Step 1: Run Unit Tests

```bash
pytest tests/unit/ -v --tb=short
```

Expected output:
```
============================= test session starts ==============================
...
============================== 107 passed in X.XXs ===============================
```

### Step 2: Run Integration Tests

```bash
pytest tests/integration/ -v --tb=short
```

### Step 3: Run Contract Tests

```bash
pytest tests/contract/ -v --tb=short
```

### Step 4: Run All Tests with Coverage Report

```bash
pytest tests/ --cov=src --cov-report=html --cov-report=term-missing
```

Expected output should show:
- Green checkmarks (✓) for all passed tests
- Coverage percentage ≥ 30%
- No import errors
- No test failures

---

## Code Quality Checks

### Step 1: Check Code Formatting with Black

```bash
black --check src/ tests/ pipelines/
```

Expected output:
```
All done! ✨ 🍰 ✨
53 files left unchanged.
```

If files need formatting:
```bash
black src/ tests/ pipelines/
```

### Step 2: Check Import Sorting with isort

```bash
isort --check-only src/ tests/ pipelines/
```

Expected output:
```
Skipped 10 files
```

If imports need fixing:
```bash
isort src/ tests/ pipelines/
```

### Step 3: Lint Code with Flake8

```bash
flake8 src/ tests/ --count --select=E9,F63,F82 --show-source
```

Expected output:
```
0     # No error count
```

### Step 4: Run All Quality Checks Together

```bash
# Comprehensive quality check
black --check src/ tests/ pipelines/ && \
isort --check-only src/ tests/ pipelines/ && \
flake8 src/ tests/ --count --select=E9,F63,F82 && \
echo "✓ All code quality checks passed!"
```

---

## Viewing GitHub Actions Dashboard

### Step 1: Navigate to GitHub Repository

1. Open your browser
2. Go to: `https://github.com/Yogesh1022/taxi-fare-mlops`
3. Click on **"Actions"** tab (top navigation)

### Step 2: View All Workflow Runs

You should see a list of recent workflow runs showing:
- Workflow name
- Status (✓ Success, ✗ Failure, ⏳ In Progress)
- Trigger (push, pull_request, scheduled)
- Commit message
- Timestamp

### Step 3: Filter by Workflow Type

Click on specific workflows to filter:
- **CI Workflow** - Unit tests, code quality checks
- **Model Validation** - Model tests
- **Deployment Readiness** - Pre-deployment checks
- **Docker Build** - Docker image building
- **Release** - Release management

### Step 4: Check Workflow Status

Look for indicators:
- ✅ **Green Checkmark** = All jobs passed
- ❌ **Red X** = One or more jobs failed
- ⏳ **Yellow Circle** = Currently running
- ⏭️ **Skip** = Workflow was skipped

---

## Interpreting Workflow Logs

### Step 1: Click on a Workflow Run

Click on any workflow run to see detailed information.

### Step 2: View Job Status

Each workflow contains multiple jobs. Check status of:

**For CI Workflow:**
- Unit Tests ✓
- Code Quality ✓
- Integration Tests ✓
- Security Checks ✓

**For Model Validation:**
- Validate Models ✓
- Batch Prediction Test ✓
- API Endpoint Validation ✓
- Model Performance ✓

**For Deployment Readiness:**
- Pre-Deployment Validation ✓
- Docker Build Check ✓
- Artifact Check ✓
- Code Coverage ✓
- Deployment Summary ✓

### Step 3: Click on a Failed Job

If a job failed, click it to see:
- Job name
- Elapsed time
- Error message
- Failed step

### Step 4: Review Error Details

Look for common errors:

```
ERROR: unrecognized arguments: --cov=src
# Solution: pip install pytest-cov

ModuleNotFoundError: No module named 'mlflow'
# Solution: pip install mlflow

Imports are incorrectly sorted
# Solution: isort src/ tests/

Code would be reformatted
# Solution: black src/ tests/
```

### Step 5: Check Raw Logs

Click "View workflow file" to see:
- Each step's output
- Environment variables set
- Command executed
- Any warnings or errors

---

## Common Issues & Solutions

### Issue 1: Tests Failing with Import Errors

**Symptom:**
```
ModuleNotFoundError: No module named 'mlflow'
```

**Solution:**
```bash
pip install -r requirements.txt
pip install mlflow optuna dvc evidently
```

### Issue 2: Code Quality Check Failing (isort)

**Symptom:**
```
ERROR: src/deployment/inference_api.py Imports are incorrectly sorted
```

**Solution:**
```bash
isort src/ tests/ pipelines/
git add -A
git commit -m "Fix: Resolve import sorting issues"
git push
```

### Issue 3: Code Quality Check Failing (black)

**Symptom:**
```
would reformat src/deployment/model_registry.py
```

**Solution:**
```bash
black src/ tests/ pipelines/
git add -A
git commit -m "Fix: Resolve code formatting issues"
git push
```

### Issue 4: Coverage Below Threshold

**Symptom:**
```
Coverage: 25.0% (threshold: 30%)
```

**Solution:**
```bash
# Write more tests or check coverage details
pytest tests/ --cov=src --cov-report=html
# Open htmlcov/index.html to see coverage by file
```

### Issue 5: Workflow Not Triggered on Push

**Cause:**
- Workflow file has syntax error
- Trigger conditions not met
- Changes don't match path filters

**Solution:**
```bash
# Validate workflow YAML
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"

# Manually trigger workflow
# On GitHub > Actions > Select Workflow > "Run workflow" > "Run workflow"
```

### Issue 6: Test Collection Failing

**Symptom:**
```
ERROR collecting tests/unit/test_batch_predictions.py
```

**Solution:**
```bash
# Verify test runs locally
python -m pytest tests/unit/ --collect-only

# Install missing dependencies
pip install -r requirements.txt
```

---

## Complete Verification Checklist

Use this checklist to verify everything before pushing to GitHub:

### ✓ Pre-Commit Checks (Local Machine)

- [ ] Python version is 3.10+
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] All dev dependencies: `pip install pytest pytest-cov black isort flake8`

### ✓ Test Verification

- [ ] Unit tests pass: `pytest tests/unit/ -v` → 107 passed
- [ ] Integration tests pass: `pytest tests/integration/ -v`
- [ ] Contract tests pass: `pytest tests/contract/ -v`
- [ ] No import errors when running tests
- [ ] Coverage is ≥ 30%: `pytest --cov=src --cov-report=term-missing`

### ✓ Code Quality

- [ ] Black formatting passes: `black --check src/ tests/` → 0 files to reformat
- [ ] isort imports correct: `isort --check-only src/ tests/` → 0 errors
- [ ] Flake8 linting passes: `flake8 src/ tests/` → 0 errors
- [ ] No undefined names or syntax errors

### ✓ Git Preparation

- [ ] All changes staged: `git add -A`
- [ ] Meaningful commit message written
- [ ] Latest code pulled: `git pull origin main`
- [ ] No merge conflicts

### ✓ GitHub Actions Monitoring (After Push)

- [ ] Commit pushed to GitHub: `git push origin main`
- [ ] GitHub Actions dashboard loads
- [ ] Workflow runs appear within 1-2 minutes
- [ ] All workflow jobs show ✅ status
- [ ] CI Workflow passed
- [ ] Model Validation passed
- [ ] Deployment Readiness passed
- [ ] Docker Build passed (if applicable)

### ✓ Viewing Logs

- [ ] Click on each workflow run
- [ ] Review each job's status
- [ ] No red error messages in logs
- [ ] All steps completed successfully
- [ ] Build artifact uploaded (if applicable)

### ✓ Final Validation

- [ ] Compare local test results with GitHub Actions results
- [ ] Verify code quality metrics match
- [ ] Check that all required jobs completed
- [ ] Confirm no unexpected failures

---

## Quick Command Reference

```bash
# 1. Run all local checks
pytest tests/ -v --tb=short && \
black --check src/ tests/ pipelines/ && \
isort --check-only src/ tests/ pipelines/ && \
flake8 src/ tests/ && \
echo "✓ All checks passed!"

# 2. Auto-fix formatting and imports
black src/ tests/ pipelines/
isort src/ tests/ pipelines/

# 3. Get detailed coverage report
pytest tests/ --cov=src --cov-report=html
# Then open: htmlcov/index.html

# 4. Commit and push
git add -A
git commit -m "Fix: [describe changes]"
git push origin main

# 5. Monitor GitHub Actions
# Visit: https://github.com/Yogesh1022/taxi-fare-mlops/actions
```

---

## Success Indicators

### Workflow Running Successfully

✅ All of these should be true:

1. **GitHub Actions Dashboard:**
   - Latest commit shows ✅ status
   - All workflow jobs completed
   - No red X marks or warnings

2. **Test Results:**
   - 107 tests passed (or more)
   - Coverage ≥ 30%
   - No failed assertions

3. **Code Quality:**
   - Black: 0 files would be reformatted
   - isort: Skipped X files (no errors)
   - flake8: 0 errors found

4. **Logs:**
   - No error messages
   - All steps show "✓" or green checkmarks
   - Build artifacts uploaded successfully

### Workflow Issues

❌ Warning signs:

1. **Red X on GitHub Actions** = Job failed
2. **ModuleNotFoundError** = Missing dependency
3. **Test assertion failed** = Logic error
4. **Coverage below 30%** = Need more tests
5. **"would reformat" message** = Code not formatted
6. **"Imports are incorrectly sorted"** = Import issues

---

## Support & Debugging

### If Workflow Fails:

1. **Check GitHub Actions logs** - Look for error message
2. **Run same command locally** - Reproduce the issue
3. **Verify dependencies** - `pip install -r requirements.txt`
4. **Check recent changes** - Review last commit
5. **Try manual trigger** - GitHub > Actions > Run workflow

### If Still Stuck:

Look at these files for configuration:
- `.github/workflows/ci.yml` - Main CI pipeline
- `.github/workflows/deployment-ready.yml` - Deployment checks
- `.github/workflows/model-validation.yml` - Model tests
- `pyproject.toml` - Python project configuration
- `requirements.txt` - Production dependencies
- `pytest.ini` or `pyproject.toml` - Test configuration

---

## Testing Your Fix

After making changes:

```bash
# 1. Fix locally and verify
black src/ tests/ pipelines/
isort src/ tests/ pipelines/
pytest tests/ -v

# 2. Commit with descriptive message
git add -A
git commit -m "Fix: Resolve [specific issue]

- Fixed import sorting in X files
- Reformatted Y files with black
- All 107 tests passing
- Coverage: 30%+"

# 3. Push to GitHub
git push origin main

# 4. Monitor GitHub Actions
# Visit https://github.com/Yogesh1022/taxi-fare-mlops/actions
# Wait 1-2 minutes for workflow to run
# Verify all jobs have ✅ status
```

---

## Conclusion

A successful workflow run indicates:

✅ **Code Quality** - Properly formatted and sorted
✅ **Functionality** - All tests passing
✅ **Dependencies** - All required packages available
✅ **CI/CD** - Pipeline automated and working
✅ **Deployment Ready** - Code ready for production

Monitor the **Actions dashboard** regularly to ensure your workflows stay healthy!
