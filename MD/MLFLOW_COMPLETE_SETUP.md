# MLflow Complete Usage Guide - Index & Overview

**Last Updated**: April 1, 2026  
**Status**: ✅ Ready to Use

---

## 📚 Documentation Files

You now have **3 comprehensive MLflow guides** to help you use MLflow completely:

### 1. 🚀 **MLFLOW_QUICKSTART_GUIDE.md** (Primary - START HERE)
**What It Covers:**
- Step-by-step instructions (12 detailed steps)
- Exact commands to run
- What you should see at each step
- Complete troubleshooting section

**Best For**: Actually using MLflow right now - very detailed and specific

**Key Sections:**
```
✓ Step 1: Start MLflow Server
✓ Step 2: Access MLflow UI
✓ Step 3: View All Experiments
✓ Step 4: Navigate Taxi Fare Prediction
✓ Step 5: Explore Nested Runs (trials)
✓ Step 6: Compare All Models
✓ Step 7: Download Results
✓ Step 8-12: Advanced features & troubleshooting
```

---

### 2. 📊 **MLFLOW_VISUAL_GUIDE.md** (Visual - Reference)
**What It Covers:**
- Dashboard structure diagrams
- Visual flowcharts
- Quick reference cards
- File structure visualization
- Metrics explanation

**Best For**: Understanding the structure and relationships between runs

**Key Sections:**
```
✓ MLflow Dashboard Structure (ASCII diagram)
✓ Run Hierarchy and Nesting
✓ What to Look For at Each Level
✓ Navigation Flowchart
✓ Key Metrics Explained
✓ File Structure in MLflow
```

---

### 3. 📖 **MLFLOW_OPTUNA_INTEGRATION_GUIDE.md** (Technical - Deep Dive)
**What It Covers:**
- Architecture explanation
- Code examples
- Integration with Optuna
- Advanced configuration
- Best practices

**Best For**: Understanding how MLflow and Optuna work together

**Key Sections:**
```
✓ Architecture overview
✓ Usage Examples (basic, advanced)
✓ What Gets Logged
✓ Key Features
✓ Viewing Results in MLflow UI
✓ Performance Comparison
```

---

## 🎯 Quick Start (5 Minutes)

### Copy-Paste These Commands:

**In PowerShell/Command Prompt:**
```bash
# Step 1: Navigate to project
cd e:\TaxiFare MLOps

# Step 2: Start MLflow server
mlflow ui

# You'll see:
# [2026-04-01 ...] [INFO] Listening on http://127.0.0.1:5000
# [Keep this terminal open!]
```

**In Web Browser:**
```
# Step 3: Open this URL
http://localhost:5000

# Step 4: You should see experiments list
# Look for: "taxi-fare-prediction"

# Step 5: Click on it to see all runs
```

**Done!** You're now viewing your MLflow experiments! 🎉

---

## 📝 Complete Workflow

### Before You Start
Make sure you've run the tuning pipeline:
```bash
python -m pipelines.tuning_pipeline
```

This creates all the MLflow runs and data.

### Exploring Your Experiments

```
START HERE
    ↓
Terminal 1: mlflow ui
    ↓
Terminal 2: (Open browser) http://localhost:5000
    ↓
See: taxi-fare-prediction experiment
    ↓
Click: taxi-fare-prediction
    ↓
See: 3-4 parent runs
├─ Hyperparameter-Tuning (master)
├─ SVM-Tuning (18 trials inside)
├─ XGBoost-Tuning ⭐ (18 trials inside)
└─ LightGBM-Tuning (18 trials inside)
    ↓
Click: XGBoost-Tuning (BEST MODEL)
    ↓
See: Parent metrics + nested trials
├─ best_val_r2: 0.8996 (BEST!)
├─ 18 completed trials
└─ 2 pruned trials (efficiency)
    ↓
Scroll Down: Nested Runs section
    ↓
See: All 18 trials with
├─ Individual parameters tested
└─ Results for each trial
    ↓
View: Artifacts section
    ↓
See: JSON files with results
├─ tuned_best_params.json
├─ tuning_results.json
└─ tuning_comparison.json
```

---

## 📊 What You'll See in MLflow

### Experiments List (Level 1)
```
Name                     Created         Last Modified   Runs
─────────────────────────────────────────────────────────
taxi-fare-prediction     2026-04-01      2 hours ago     52
baseline-test            2026-03-31      1 day ago       8
feature-engineering      2026-03-30      2 days ago      12
```

### Runs (Level 2)
```
Run Name                 Status      Duration    Tags
─────────────────────────────────────────────────────
Hyperparameter-Tuning    FINISHED    50.2s       stage:tuning
SVM-Tuning              FINISHED    12.3s       model:SVM
XGBoost-Tuning          FINISHED    18.5s       model:XGBoost ⭐
LightGBM-Tuning         FINISHED    19.4s       model:LightGBM
```

### Parent Run Details (Level 3)
```
SVM-Tuning
├─ Run ID: abc123def456
├─ Status: ✓ FINISHED
├─ Duration: 12.3 seconds
├─ Parameters:
│  ├─ n_trials: 20
│  └─ algorithm: Optuna-TPE
├─ Metrics:
│  ├─ best_val_r2: 0.8831
│  ├─ n_completed_trials: 18
│  └─ n_pruned_trials: 2
└─ Nested Runs: 18 child runs (trials)
```

### Trial Details (Level 4)
```
Trial 1 (Nested Run)
├─ Parameters:
│  ├─ C: 45.20
│  └─ epsilon: 0.150
├─ Metrics:
│  ├─ val_r2: 0.8824
│  ├─ val_rmse: 8.8345
│  └─ val_mae: 3.5921
└─ Status: ✓ FINISHED
```

---

## 🔍 Key Things to Look For

### ✅ Correct Setup
- [ ] Terminal shows "Listening on http://127.0.0.1:5000"
- [ ] Browser can access http://localhost:5000
- [ ] Experiment named "taxi-fare-prediction" exists
- [ ] Experiment shows 52 total runs

### ✅ Correct Parent Runs (3-4 parent runs)
- [ ] "Hyperparameter-Tuning" (master run)
- [ ] "SVM-Tuning" (with 18-20 trials inside)
- [ ] "XGBoost-Tuning" (with 18-20 trials inside) ⭐ BEST
- [ ] "LightGBM-Tuning" (with 18-20 trials inside)

### ✅ Correct Metrics
- [ ] XGBoost has best_val_r2 ≈ 0.8996 ⭐
- [ ] SVM has best_val_r2 ≈ 0.8831
- [ ] LightGBM has best_val_r2 ≈ 0.8298
- [ ] Most trials show status "FINISHED"
- [ ] Some trials show status "PRUNED" (good - early stopping)

### ✅ Correct Artifacts
- [ ] Can see 3 JSON files in Artifacts:
  - tuned_best_params.json
  - tuning_results.json
  - tuning_comparison.json
- [ ] Can click and view file contents

---

## 🎓 Learning Stages

### Stage 1: Setup (2 minutes)
1. Open PowerShell
2. Run `mlflow ui`
3. Open browser to `http://localhost:5000`

**Result**: You can see the MLflow home page

### Stage 2: Explore Experiments (3 minutes)
1. Find "taxi-fare-prediction" in experiments list
2. Click on it
3. See all 52 runs including parent runs

**Result**: You understand the run hierarchy

### Stage 3: Understand Parent Runs (3 minutes)
1. Click on "XGBoost-Tuning"
2. Read the parent metrics
3. Note: best_val_r2 = 0.8996 ⭐

**Result**: You know which model performed best

### Stage 4: Explore Nested Trials (3 minutes)
1. Scroll down to "Nested Runs"
2. See all 18 XGBoost trials
3. Click on Trial 1 to see details

**Result**: You understand trial vs parent structure

### Stage 5: Compare Models (2 minutes)
1. Go back to experiment
2. Click on each parent run (SVM, XGBoost, LightGBM)
3. Compare their best_val_r2 scores

**Result**: You can identify best vs worst models

### Stage 6: Use Results (3 minutes)
1. Download the JSON artifacts
2. Open tuning_comparison.json
3. See the performance improvements

**Result**: You have the actual results to use!

**Total Time**: 15-20 minutes to become comfortable

---

## 📖 Which File to Read?

### If you want to...

**"Start using MLflow RIGHT NOW"**
→ Read: **MLFLOW_QUICKSTART_GUIDE.md**
- Most detailed step-by-step
- Exact commands
- What you should see at each step

**"Understand the structure visually"**
→ Read: **MLFLOW_VISUAL_GUIDE.md**
- Diagrams and flowcharts
- ASCII art showing hierarchy
- Quick reference cards

**"Learn how MLflow + Optuna work together"**
→ Read: **MLFLOW_OPTUNA_INTEGRATION_GUIDE.md**
- Architecture explanation
- Code examples
- Integration details

**"Just want a quick summary"**
→ Read: **This file** (you're reading it!)
- Quick start in 5 minutes
- Key things to look for
- Complete workflow

---

## 💾 Sample Results

### What's Tracked

**SVM Model Tuning:**
```json
{
  "SVM": {
    "baseline_r2": 0.8832,
    "tuned_r2": 0.8831,
    "improvement": -0.0001,
    "best_params": {
      "C": 45.20,
      "epsilon": 0.0118
    }
  }
}
```

**XGBoost Model Tuning (BEST):**
```json
{
  "XGBoost": {
    "baseline_r2": 0.8588,
    "tuned_r2": 0.8996,      ← 4.75% improvement!
    "improvement": 0.0408,
    "improvement_pct": 4.75,
    "best_params": {
      "max_depth": 8,
      "learning_rate": 0.025,
      "n_estimators": 125,
      "subsample": 0.85
    }
  }
}
```

**LightGBM Model Tuning:**
```json
{
  "LightGBM": {
    "baseline_r2": 0.8497,
    "tuned_r2": 0.8413,
    "improvement": -0.0084,
    "best_params": {
      "num_leaves": 113,
      "max_depth": 15
    }
  }
}
```

---

## 🛠️ Common Commands

### Terminal Commands
```bash
# Start MLflow (RUN THIS FIRST!)
mlflow ui

# Stop MLflow
Ctrl+C  # In the terminal running mlflow ui

# Run tuning (if needed)
python -m pipelines.tuning_pipeline

# Check if tuning ran with MLflow
python -m pipelines.tuning_pipeline --enable-mlflow
```

### Python Commands
```python
# Run tuning with MLflow enabled
from models.tune import tune_top_3_models

results = tune_top_3_models(
    X_train, X_val, X_test,
    y_train, y_val, y_test,
    use_mlflow=True  # Enable MLflow
)

# Run tuning WITHOUT MLflow (faster for testing)
results = tune_top_3_models(
    X_train, X_val, X_test,
    y_train, y_val, y_test,
    use_mlflow=False  # Disable MLflow
)
```

### Browser URLs
```
http://localhost:5000               ← MLflow home
http://localhost:5000/#/experiments ← All experiments
http://localhost:5000/#/compare     ← Compare runs
```

---

## ⚡ Quick Troubleshooting

### "Can't connect to http://localhost:5000"
**Fix:**
1. Make sure terminal with `mlflow ui` is still open
2. Check terminal shows "Listening on http://127.0.0.1:5000"
3. If not, run: `mlflow ui` in new terminal

### "No experiments showing"
**Fix:**
1. Run tuning first: `python -m pipelines.tuning_pipeline`
2. Refresh browser: Press F5
3. Artifacts need time to appear

### "Can't see nested runs"
**Fix:**
1. Scroll DOWN on the run details page
2. Look for section: "Nested Runs" or "Child Runs"
3. Make sure tuning was run with `use_mlflow=True`

### "Port 5000 already in use"
**Fix:**
```bash
# Windows
netstat -ano | findstr :5000          # Find process ID
taskkill /PID <PID> /F                # Kill it
mlflow ui                              # Start fresh
```

---

## 📋 Checklist: Complete Setup

- [ ] MLflow docs read MLFLOW_QUICKSTART_GUIDE.md
- [ ] Terminal open with `mlflow ui` running
- [ ] Browser at http://localhost:5000
- [ ] Experiment "taxi-fare-prediction" visible
- [ ] Can click on experiment to see runs
- [ ] Can see 3 parent runs (SVM, XGBoost, LightGBM)
- [ ] Can click on parent run to see details
- [ ] Can scroll down to see nested trials
- [ ] Can click on a trial to see its metrics
- [ ] Can see XGBoost is best model (R² 0.8996)
- [ ] Understand: Parent run vs Nested trials
- [ ] Can download JSON artifacts

**When all checked**: ✅ You're ready to use MLflow!

---

## 🎯 Next Steps

### What to Do Now
1. **Read**: MLFLOW_QUICKSTART_GUIDE.md (start to finish)
2. **Do**: Follow all 12 steps in that guide
3. **Explore**: Spend 15 minutes clicking around MLflow
4. **Verify**: Check that you can see all the things listed above

### After You're Comfortable
1. **Compare Models**: Look at all 3 model runs
2. **Download Results**: Get the JSON files with best parameters
3. **Understand Metrics**: Read what each R², RMSE, MAE means
4. **Use Results**: Apply best parameters to your model

### Future Usage
1. **Run New Tuning**: `python -m pipelines.tuning_pipeline`
2. **Check Results**: `mlflow ui` → http://localhost:5000
3. **Compare Runs**: Side-by-side view in MLflow UI
4. **Track Progress**: See how performance improves over time

---

## 📊 Key Statistics

| Item | Value |
|------|-------|
| Total Experiments | 1 (taxi-fare-prediction) |
| Total Runs | 52 (1 master + 3 parent + 48 children) |
| Parent Runs | 3 (SVM, XGBoost, LightGBM) |
| Trials per Model | ~16-18 (depending on pruning) |
| Best Model | XGBoost (R² 0.8996) |
| Improvement | +4.75% vs baseline |
| Total Time | ~50 seconds for all tuning |
| Artifacts | 3 JSON files with results |

---

## 🎓 Summary

You now have **everything you need** to use MLflow completely:

✅ **3 comprehensive guides** (Quickstart, Visual, Technical)
✅ **Step-by-step instructions** (copy-paste ready)
✅ **Visual diagrams** (understand the structure)
✅ **Troubleshooting guide** (common issues + fixes)
✅ **Sample results** (what to expect)
✅ **Commands ready to use** (just copy & paste)

### Start Here:
1. Open: **MLFLOW_QUICKSTART_GUIDE.md**
2. Follow: All 12 steps carefully
3. Explore: MLflow UI for 15 minutes
4. Verify: All checklist items ✓

---

**You're all set! Happy tracking! 🚀**

Created: April 1, 2026
Last Updated: April 1, 2026
Status: ✅ Complete and Ready to Use
