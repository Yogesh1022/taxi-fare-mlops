# MLflow Complete Step-by-Step Guide

**Date**: April 1, 2026  
**Purpose**: View all experiments, nested runs, and hyperparameter tuning results  
**Duration**: ~5 minutes to complete

---

## Table of Contents
1. [Start MLflow Server](#start-mlflow-server)
2. [Access MLflow UI](#access-mlflow-ui)
3. [View Experiments](#view-experiments)
4. [Navigate Taxi Fare Prediction Experiment](#navigate-taxi-fare-prediction-experiment)
5. [Explore Nested Runs](#explore-nested-runs)
6. [Compare Models](#compare-models)
7. [Download Results](#download-results)
8. [Troubleshooting](#troubleshooting)

---

## STEP 1: Start MLflow Server

### Step 1.1: Open PowerShell or Command Prompt
- Press `Win + R`
- Type: `powershell` or `cmd`
- Press `Enter`

### Step 1.2: Navigate to Project Directory
```bash
cd e:\TaxiFare MLOps
```

**What you should see:**
```
PS E:\TaxiFare MLOps>
```

### Step 1.3: Start MLflow Server
```bash
mlflow ui
```

**What you should see (you'll get a message like this):**
```
[2026-04-01 10:30:00 +0000] [12345] [INFO] Listening on http://127.0.0.1:5000
[2026-04-01 10:30:00 +0000] [12345] [INFO] Application startup complete
```

### Step 1.4: Keep Terminal Open
⚠️ **IMPORTANT**: Do NOT close this terminal! MLflow server needs to keep running.

**Terminal should look like:**
```
PS E:\TaxiFare MLOps> mlflow ui
[2026-04-01 10:30:00 +0000] [12345] [INFO] Listening on http://127.0.0.1:5000
[2026-04-01 10:30:00 +0000] [12345] [INFO] Application startup complete
```

---

## STEP 2: Access MLflow UI

### Step 2.1: Open Web Browser
- Open **Google Chrome**, **Firefox**, or **Edge**
- Click on the address bar
- Type: `http://localhost:5000`
- Press `Enter`

### Step 2.2: MLflow Home Page Loads
**You should see:**
```
┌─────────────────────────────────────────┐
│  MLflow Tracking Server                 │
│                                         │
│  Experiments (List of all experiments)  │
│  Recent Runs                            │
│  Models                                 │
└─────────────────────────────────────────┘
```

### Step 2.3: Verify Browser Address
**Address bar should show:**
```
http://localhost:5000/
```

✅ **Success**: You should see the MLflow main dashboard with a list of experiments.

---

## STEP 3: View All Experiments

### Step 3.1: Look at Experiments List
You should see a table with columns:
- **Name** (Experiment name)
- **Created** (Date created)
- **Last Modified** (Last update time)
- **Runs** (Number of runs in experiment)

### Step 3.2: Find "taxi-fare-prediction"
Look for the experiment named:
```
taxi-fare-prediction
```

**This is the main experiment we created for your tuning.**

### Step 3.3: Click on "taxi-fare-prediction"
- Click on the experiment name or row
- Watch the page load

**Expected result**: You'll see the experiment details page with all runs.

---

## STEP 4: Navigate Taxi Fare Prediction Experiment

### Step 4.1: Experiment Details Page Loads
**You should see a table with these columns:**

| Column | What It Shows |
|--------|---------------|
| **Date** | When the run was created |
| **Run Name** | Name like "SVM-Tuning", "XGBoost-Tuning", "LightGBM-Tuning" |
| **User** | Who created it (usually "mlflow") |
| **Status** | FINISHED, RUNNING, or FAILED |
| **Duration** | How long the run took |
| **Tags** | Labels like "model: SVM", "stage: tuning" |

### Step 4.2: Look for Parent Runs
You should see **3 main parent runs** (they will appear in the list):

1. **Hyperparameter-Tuning** (master run)
2. **SVM-Tuning** (parent run for SVM trials)
3. **XGBoost-Tuning** (parent run for XGBoost trials) ⭐ Best model
4. **LightGBM-Tuning** (parent run for LightGBM trials)

**Example what you'll see:**
```
┌────────────────────────────────────────────────────┐
│ Run Name                  │ Status    │ Duration    │
├────────────────────────────────────────────────────┤
│ Hyperparameter-Tuning     │ FINISHED  │ 50.2 s      │
│ - SVM-Tuning              │ FINISHED  │ 12.3 s      │
│ - XGBoost-Tuning          │ FINISHED  │ 18.5 s      │ ⭐
│ - LightGBM-Tuning         │ FINISHED  │ 19.4 s      │
└────────────────────────────────────────────────────┘
```

### Step 4.3: Check Total Runs
You should see a number showing **total runs**. Example:
```
Total Runs: 52 runs
```

This includes all parent runs + nested child runs (trials).

---

## STEP 5: Explore Nested Runs

### Step 5.1: Click on "SVM-Tuning" Parent Run
- Find the row with **"SVM-Tuning"**
- Click on the run name or anywhere in the row
- Wait for the page to load

### Step 5.2: View SVM-Tuning Details Page
**You should see sections:**

#### Section A: Run Details (Top)
```
Run Name:           SVM-Tuning
Start Time:         2026-04-01 10:15:30
Duration:           12.3 seconds
Status:             FINISHED
Run ID:             abc123def456
```

#### Section B: Parameters (Middle)
You'll see a table with model-level parameters:
```
Parameter           Value
─────────────────────────
n_trials            20
algorithm           Optuna-TPE
```

#### Section C: Metrics (Middle-Lower)
You'll see model-level metrics:
```
Metric              Value
─────────────────────────
best_val_r2         0.8831
n_completed_trials  18
n_pruned_trials     2
```

#### Section D: Nested Runs (Lower)
**This is the important part!** You should see a section showing:
```
Nested Runs (Child Runs)

Trial  Params (C, epsilon)              Metrics (val_r2)      Status
────────────────────────────────────────────────────────────────────
1      C: 45.20, epsilon: 0.150         val_r2: 0.8824        FINISHED
2      C: 38.50, epsilon: 0.120         val_r2: 0.8831        FINISHED
3      C: 52.10, epsilon: 0.180         val_r2: 0.8739        PRUNED
...
```

### Step 5.3: Click on a Child Run (Trial)
- Click on **Trial 1** or **Trial 2** in the nested runs list
- This will show the detailed trial metrics

**You should see:**
```
Trial Details

Parameters:
  C: 45.2
  epsilon: 0.150

Metrics:
  val_r2:   0.8824
  val_rmse: 8.8345
  val_mae:  3.5921
```

---

## STEP 6: Compare All Models

### Step 6.1: Go Back to Experiment (Click Browser Back Button)
- Press **Back button** in browser or use keyboard shortcut `Alt + ←`
- You should return to the experiments runs list

### Step 6.2: Click on "XGBoost-Tuning" (Best Model)
- Find **XGBoost-Tuning** in the list
- Click on the run name
- Wait for page to load

### Step 6.3: View XGBoost Results
**You should see:**

```
XGBoost-Tuning Details

Parameters:
  n_trials: 20
  algorithm: Optuna-TPE

Metrics:
  best_val_r2: 0.8996        ⭐ Best R²
  n_completed_trials: 18
  n_pruned_trials: 2

Test Metrics:
  XGBoost_test_r2:  0.8996
  XGBoost_test_rmse: 8.1829
  XGBoost_test_mae:  3.3176

Best Parameters:
  max_depth: 8
  learning_rate: 0.025
  n_estimators: 125
  subsample: 0.85
  colsample_bytree: 0.90
```

### Step 6.4: View Nested Trials
Scroll down to see all **18-20 XGBoost trials** with their metrics:
```
Nested Runs: 18 child runs

Trial  n_estimators  learning_rate  Metrics (val_r2)    Status
──────────────────────────────────────────────────────────────
1      100           0.025          0.8996              FINISHED ⭐
2      125           0.030          0.8988              FINISHED
3      120           0.020          0.8975              PRUNED
...
```

### Step 6.5: Compare LightGBM Results
- Go back to experiment list
- Click on **LightGBM-Tuning**
- Observe the metrics:

```
LightGBM-Tuning Details

Best Metrics:
  best_val_r2: 0.8298
  n_completed_trials: 18
  n_pruned_trials: 2

Best Parameters:
  num_leaves: 113
  max_depth: 15
  learning_rate: 0.171
```

---

## STEP 7: Download and View Results

### Step 7.1: View Artifacts
On any run details page, look for **"Artifacts"** section.

### Step 7.2: View Artifact Files
You should see files listed:
```
Artifacts:

📁 mlruns/
  └─ 📄 tuned_best_params.json
  └─ 📄 tuning_results.json
  └─ 📄 tuning_comparison.json
```

### Step 7.3: Click on "tuned_best_params.json"
- Click on the filename
- You should see JSON content:

```json
{
  "SVM": {
    "C": 45.201,
    "epsilon": 0.0118
  },
  "XGBoost": {
    "max_depth": 8,
    "learning_rate": 0.025,
    "n_estimators": 125,
    "subsample": 0.85,
    "colsample_bytree": 0.90
  },
  "LightGBM": {
    "num_leaves": 113,
    "max_depth": 15,
    "learning_rate": 0.1715
  }
}
```

### Step 7.4: View Comparison Results
Click on **tuning_comparison.json** to see:

```json
{
  "XGBoost": {
    "baseline_r2": 0.8588,
    "tuned_r2": 0.8996,
    "improvement": 0.0408,
    "improvement_pct": 4.75  ⭐ 4.75% improvement
  },
  "SVM": {
    "baseline_r2": 0.8832,
    "tuned_r2": 0.8831,
    "improvement": -0.0001,
    "improvement_pct": -0.01
  },
  "LightGBM": {
    "baseline_r2": 0.8497,
    "tuned_r2": 0.8413,
    "improvement": -0.0084,
    "improvement_pct": -0.99
  }
}
```

---

## STEP 8: Understanding the Complete Flow

### Visual Flow Diagram
```
START
  ↓
[Open http://localhost:5000]
  ↓
[Select "taxi-fare-prediction" experiment]
  ↓
[View 3 parent runs: SVM, XGBoost, LightGBM]
  ↓
[Click on each parent run]
  ↓
[View nested child runs (trials)]
  ↓
[Check metrics, parameters for each trial]
  ↓
[Compare best models]
  ↓
[Download results JSON files]
  ↓
END
```

### What Each Section Shows

| Section | Shows | Important |
|---------|-------|-----------|
| **Parent Run** | Model-level metrics | Best_val_r2, n_completed_trials |
| **Child Runs** | Individual trial performance | Trial-specific params & metrics |
| **Metrics** | R², RMSE, MAE | Quality of tuning |
| **Parameters** | Hyperparameters tested | Best parameter values |
| **Artifacts** | JSON result files | Downloadable results |

---

## STEP 9: Key Things to Look For

### ✅ Check These Things:

1. **Total Runs Count**
   - Should show ~52 runs (3 parent runs + 49 child runs)
   - Location: Top of experiment page

2. **Best Model Identification**
   - Find **XGBoost-Tuning** with R² = 0.8996
   - This is the best tuned model

3. **Trial Success Rate**
   - Most trials should show **FINISHED**
   - Some trials should show **PRUNED** (optimization stopped them early)
   - Example: 18 FINISHED, 2 PRUNED = 90% efficiency

4. **Improvement Over Baseline**
   - XGBoost improved from 0.8588 → 0.8996 (+4.75%)
   - SVM stayed same (0.8832 → 0.8831)
   - LightGBM decreased (0.8497 → 0.8413)

5. **Parameter Ranges**
   - Look at variety of parameters tested
   - Optuna found the best combination

6. **Execution Time**
   - Total tuning: ~50 seconds (very fast!)
   - Per-model: 12-19 seconds each

---

## STEP 10: Troubleshooting

### Problem 1: "Connection Refused" or "Cannot Connect to Server"
**Solution:**
- Check terminal where you ran `mlflow ui`
- Should see: `Listening on http://127.0.0.1:5000`
- If not, run command: `mlflow ui`
- Make sure terminal is still open

### Problem 2: Page Shows "No Experiments"
**Solution:**
- Run your tuning pipeline first:
  ```bash
  python -m pipelines.tuning_pipeline
  ```
- This will create the MLflow runs
- Then refresh MLflow page

### Problem 3: Cannot See Nested Runs
**Solution:**
- Scroll down on the run details page
- Look for section that says "Nested Runs" or "Child Runs"
- Make sure you run with `use_mlflow=True`

### Problem 4: Artifacts Not Showing
**Solution:**
- Run save_results() to create artifacts:
  ```python
  from models.tune import tune_top_3_models
  results = tune_top_3_models(..., use_mlflow=True)
  ```

### Problem 5: Port Already in Use (Address Already in Use)
**Solution:**
- Kill existing MLflow process:
  ```bash
  # On Windows
  netstat -ano | findstr :5000
  taskkill /PID <PID> /F
  
  # Then start again
  mlflow ui
  ```

---

## STEP 11: Using MLflow for Your Project

### One-Time Setup
```bash
# 1. Make sure you're in project directory
cd e:\TaxiFare MLOps

# 2. Start MLflow server
mlflow ui

# 3. Open http://localhost:5000 in browser
```

### Running Tuning with MLflow
```python
from models.tune import tune_top_3_models

# This automatically logs to MLflow
results = tune_top_3_models(
    X_train, X_val, X_test,
    y_train, y_val, y_test,
    n_trials=20,
    use_mlflow=True  # Enable MLflow (default)
)
```

### Disabling MLflow (for fast testing)
```python
# Don't log to MLflow
results = tune_top_3_models(
    X_train, X_val, X_test,
    y_train, y_val, y_test,
    n_trials=3,
    use_mlflow=False  # Disable MLflow
)
```

---

## STEP 12: Next Steps

After exploring MLflow, you can:

1. **Compare Different Experiments**
   - Run tuning multiple times
   - Compare results across runs

2. **Download Results**
   - Export JSON files for analysis
   - Use results in reports

3. **Register Best Model**
   - Mark best model for production
   - Version the models

4. **Monitor Performance**
   - Track metrics over time
   - Detect model drift

5. **Share with Team**
   - MLflow tracks who, when, what was done
   - Easy to share findings via MLflow links

---

## Quick Reference Card

### Essential URLs
| Action | URL |
|--------|-----|
| MLflow Home | http://localhost:5000 |
| Experiments | http://localhost:5000/#/experiments |
| Specific Experiment | http://localhost:5000/#/experiments/[ID] |

### Essential Commands
```bash
# Start MLflow
mlflow ui

# Stop MLflow (press Ctrl+C in terminal)
Ctrl+C

# Run tuning with MLflow
python -m pipelines.tuning_pipeline
```

### Key Metrics to Watch
| Metric | Good Value | Excellent |
|--------|-----------|-----------|
| best_val_r² | >0.85 | >0.89 |
| n_pruned_trials | <30% | <20% |
| improvement_pct | >2% | >4% |

---

## Summary

✅ **You now know how to:**
1. Start MLflow server
2. View all experiments and runs
3. Navigate parent and nested runs
4. Compare models and metrics
5. Download and view results
6. Troubleshoot common issues
7. Use MLflow for your project

🎯 **Next Time:**
1. Open terminal → `mlflow ui`
2. Open browser → `http://localhost:5000`
3. Select your experiment and explore!

---

**Happy Tracking! 📊**

*For more details, see MLFLOW_OPTUNA_INTEGRATION_GUIDE.md*

---

**Created**: April 1, 2026  
**Last Updated**: April 1, 2026  
**Status**: Ready to use
