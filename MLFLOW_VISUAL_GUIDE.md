# MLflow UI Navigation - Visual Quick Reference

## 📱 MLflow Dashboard Structure

```
┌─────────────────────────────────────────────────────────────────┐
│                   MLflow Tracking Server                          │
│                   http://localhost:5000                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 📊 Experiments List                                              │
│                                                                   │
│ ✓ taxi-fare-prediction  │ 2026-04-01  │ 5 hours ago │ 52 runs   │
│ ✓ baseline-test         │ 2026-03-31  │ 1 day ago   │ 8 runs    │
│ ✓ feature-engineering   │ 2026-03-30  │ 2 days ago  │ 12 runs   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    [Click: taxi-fare-prediction]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 📈 Experiment: taxi-fare-prediction                             │
│                                                                   │
│ Runs (52 total):                                                 │
│ ┌──────────────────────────────────────────────────────────────┐│
│ │ Hyperparameter-Tuning   FINISHED  50.2s   [Main Run]         ││
│ │  ├─ SVM-Tuning         FINISHED  12.3s   [Parent Run]        ││
│ │  ├─ XGBoost-Tuning     FINISHED  18.5s   [Parent Run] ⭐    ││
│ │  └─ LightGBM-Tuning    FINISHED  19.4s   [Parent Run]        ││
│ └──────────────────────────────────────────────────────────────┘│
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                              │
                    [Click: SVM-Tuning]
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│ 🔍 Detailed View: SVM-Tuning (Parent Run)                       │
│                                                                   │
│ ┌─ Run Information ──────────────────────────────────────────┐  │
│ │ Run ID:        abc123def456                                 │  │
│ │ Name:          SVM-Tuning                                   │  │
│ │ Start Time:    2026-04-01 10:15:30                          │  │
│ │ Duration:      12.3 seconds                                 │  │
│ │ Status:        ✓ FINISHED                                   │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌─ Parameters (Model Level) ─────────────────────────────────┐  │
│ │ n_trials        20                                          │  │
│ │ algorithm       Optuna-TPE                                  │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌─ Metrics (Model Level) ────────────────────────────────────┐  │
│ │ best_val_r2           0.8831                               │  │
│ │ n_completed_trials    18                                   │  │
│ │ n_pruned_trials       2                                    │  │
│ │ SVM_test_r2           0.8831                               │  │
│ │ SVM_test_rmse         8.8282                               │  │
│ │ SVM_test_mae          3.5881                               │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌─ Nested Runs (Child Runs / Trials) ────────────────────────┐  │
│ │ [18 child runs shown]                                       │  │
│ │                                                              │  │
│ │ Trial 1: ✓ FINISHED                                         │  │
│ │   ├─ C: 45.20                                               │  │
│ │   ├─ epsilon: 0.150                                         │  │
│ │   ├─ val_r2: 0.8824                                         │  │
│ │   ├─ val_rmse: 8.8345                                       │  │
│ │   └─ val_mae: 3.5921                                        │  │
│ │                                                              │  │
│ │ Trial 2: ✓ FINISHED                                         │  │
│ │   ├─ C: 38.50                                               │  │
│ │   ├─ epsilon: 0.120                                         │  │
│ │   ├─ val_r2: 0.8831 ← Best trial                           │  │
│ │   ├─ val_rmse: 8.8273                                       │  │
│ │   └─ val_mae: 3.5873                                        │  │
│ │                                                              │  │
│ │ Trial 3: 🚫 PRUNED                                          │  │
│ │   ├─ C: 52.10                                               │  │
│ │   ├─ epsilon: 0.180                                         │  │
│ │   ├─ val_r2: 0.8739 (below threshold)                      │  │
│ │   └─ Status: Early stopped to save time                     │  │
│ │                                                              │  │
│ │ [Continue to Trial 18...]                                   │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
│ ┌─ Artifacts ────────────────────────────────────────────────┐  │
│ │ 📄 tuned_best_params.json                                   │  │
│ │ 📄 tuning_results.json                                      │  │
│ │ 📄 tuning_comparison.json                                   │  │
│ └────────────────────────────────────────────────────────────┘  │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 What to Look For at Each Level

### Level 1: Experiments List
```
WHAT YOU SEE          →  WHAT IT MEANS
─────────────────────────────────────────────
taxi-fare-prediction  →  Your main experiment
52 runs               →  Parent runs + all trial runs
2026-04-01            →  When tuning was performed
5 hours ago           →  Last time you ran tuning
```

### Level 2: Experiment with 3 Parent Runs
```
PARENT RUNS                   WHAT THEY ARE
────────────────────────────────────────────────
Hyperparameter-Tuning         Master/Overall run
├─ SVM-Tuning                 All SVM trials grouped
├─ XGBoost-Tuning ⭐          All XGBoost trials (BEST)
└─ LightGBM-Tuning            All LightGBM trials
```

### Level 3: Inside Parent Run (e.g., SVM-Tuning)
```
SECTION                  WHAT IT SHOWS
──────────────────────────────────────────────
Run Information          When/where run happened
Parameters Section       Model-level settings (n_trials=20)
Metrics Section          Parent-level results (best_val_r2=0.8831)
Nested Runs Section      All 18-20 individual trials
Artifacts Section        Downloadable JSON files
```

### Level 4: Individual Trial (Nested Run)
```
TRIAL DETAILS                 VALUE
────────────────────────────────────────
C (regularization)            45.20
epsilon (margin)              0.150
val_r2 (validation score)     0.8824
val_rmse (validation error)   8.8345
val_mae (validation error)    3.5921
Status                        ✓ FINISHED or 🚫 PRUNED
```

---

## 📊 Comparison View

### XGBoost vs SVM - Performance
```
┌─────────────────────────────────────────┐
│ MODEL COMPARISON                         │
├─────────────────────────────────────────┤
│                                         │
│ XGBoost:    ████████████████████ 0.8996 │ ⭐ BEST
│ SVM:        ████████████████████ 0.8831 │
│ LightGBM:   ██████████████████▒ 0.8413  │
│                                         │
│ Improvement:                            │
│ XGBoost:    +4.75% (0.8588 → 0.8996)   │
│ SVM:        -0.01% (0.8832 → 0.8831)   │
│ LightGBM:   -0.99% (0.8497 → 0.8413)   │
│                                         │
└─────────────────────────────────────────┘
```

---

## 🔢 Key Metrics Explained

### Understanding Trial Metrics

| Metric | Meaning | Good Value | Example |
|--------|---------|-----------|---------|
| **val_r2** | Validation accuracy (0-1) | >0.85 | 0.8824 ✓ |
| **val_rmse** | Prediction error (lower is better) | <10 | 8.8345 ✓ |
| **val_mae** | Average prediction error | <5 | 3.5921 ✓ |
| **Status** | Trial completed or stopped early | FINISHED | PRUNED ✓ |

### Understanding Parent Run Metrics

| Metric | Meaning | Example |
|--------|---------|---------|
| **best_val_r2** | Best score achieved in any trial | 0.8831 |
| **n_completed_trials** | Trials that finished | 18 |
| **n_pruned_trials** | Trials stopped early (good optimization) | 2 |
| **SVM_test_r2** | Final SVM score on test set | 0.8831 |

---

## 🗺️ Navigation Flowchart

```
START HERE
    ↓
http://localhost:5000
    ↓
See Experiments List
    ↓
Click "taxi-fare-prediction"
    ↓
See 3 Parent Runs:
├─ SVM-Tuning
├─ XGBoost-Tuning ⭐
└─ LightGBM-Tuning
    ↓
Click "XGBoost-Tuning" (best)
    ↓
See Parent Metrics:
├─ best_val_r2: 0.8996
├─ n_completed_trials: 18
└─ n_pruned_trials: 2
    ↓
Scroll Down to "Nested Runs"
    ↓
See All 18 XGBoost Trials:
├─ Trial 1: val_r2=0.8996 ✓
├─ Trial 2: val_r2=0.8988 ✓
├─ Trial 3: 🚫 PRUNED
└─ ... 15 more trials
    ↓
Click on Trial 1
    ↓
See Trial Details:
├─ Parameters (max_depth, learning_rate, etc.)
├─ Metrics (val_r2, val_rmse, val_mae)
└─ Status (FINISHED)
    ↓
[Continue exploring other models or]
    ↓
Go to Artifacts
    ↓
Download tuned_best_params.json
    ↓
View your best parameters!
    ↓
END
```

---

## 💾 File Structure in MLflow

```
mlruns/
├── 0/
│   └── experiments.json          # Experiment metadata
│
├── 537958138435953754/           # Experiment ID
│   ├── abc123def456/             # Parent Run ID (Hyperparameter-Tuning)
│   │   ├── artifacts/
│   │   │   ├── tuned_best_params.json
│   │   │   ├── tuning_results.json
│   │   │   └── tuning_comparison.json
│   │   ├── metrics/
│   │   ├── params/
│   │   ├── tags/
│   │   └── meta.yaml
│   │
│   ├── def456ghi789/             # Parent Run ID (SVM-Tuning)
│   │   ├── params/               # Model-level params
│   │   ├── metrics/              # best_val_r2, etc.
│   │   └── child_runs/
│   │       ├── trial_1_id/       # Child Run (Trial 1)
│   │       ├── trial_2_id/       # Child Run (Trial 2)
│   │       └── trial_3_id/       # Child Run (Trial 3)
│   │
│   ├── ghi789jkl012/             # Parent Run ID (XGBoost-Tuning)
│   │   ├── params/
│   │   ├── metrics/
│   │   └── child_runs/
│   │       ├── trial_1_id/
│   │       ├── trial_2_id/
│   │       └── ... 16 more trials
│   │
│   └── jkl012mno345/             # Parent Run ID (LightGBM-Tuning)
│       ├── params/
│       ├── metrics/
│       └── child_runs/
│           ├── trial_1_id/
│           ├── trial_2_id/
│           └── ... more trials
│
└── .gitignore                    # MLflow gitignore
```

---

## 🎬 Quick Start (Copy-Paste Ready)

### Terminal Command #1: Start MLflow
```bash
cd e:\TaxiFare MLOps
mlflow ui
```

**Expected Output:**
```
[2026-04-01 10:30:00 +0000] [12345] [INFO] Listening on http://127.0.0.1:5000
[2026-04-01 10:30:00 +0000] [12345] [INFO] Application startup complete
```

### Browser Action #1: Open MLflow
**Type in browser address bar:**
```
http://localhost:5000
```

**Press:** Enter

### Browser Action #2: Select Experiment
1. Find: `taxi-fare-prediction`
2. Click: On the experiment name
3. Wait: Page loads

### Browser Action #3: Explore Runs
1. Find: `XGBoost-Tuning` (has ⭐ best performance)
2. Click: On the run name
3. Read: Parent metrics and nested trials

---

## 📋 Checklist: Things to Verify

- [ ] MLflow UI opens at http://localhost:5000
- [ ] `taxi-fare-prediction` experiment appears in list
- [ ] Experiment shows 52 total runs
- [ ] Can click on `SVM-Tuning` parent run
- [ ] Can see nested child runs (trials) inside parent
- [ ] Can view trial metrics (val_r2, val_rmse, val_mae)
- [ ] Can see `XGBoost-Tuning` has best R² = 0.8996
- [ ] Can see pruned trials (🚫) in the list
- [ ] Can download artifact JSON files
- [ ] Best parameters show: XGBoost max_depth=8, learning_rate=0.025

---

## ⚠️ Common Issues & Fixes

| Problem | Solution |
|---------|----------|
| "Cannot connect" | Make sure `mlflow ui` terminal is still open |
| "No experiments" | Run `python -m pipelines.tuning_pipeline` first |
| "No nested runs" | Scroll down on parent run details page |
| "Port 5000 in use" | Kill existing process: `netstat -ano \| findstr :5000` |
| "Artifacts missing" | Make sure `use_mlflow=True` was set during tuning |

---

## 🎓 Learning Path

1. **Level 1**: View experiments list (2 min)
2. **Level 2**: Click into taxi-fare-prediction (2 min)
3. **Level 3**: Explore SVM-Tuning parent run (3 min)
4. **Level 4**: View individual trials/nested runs (3 min)
5. **Level 5**: Compare XGBoost vs other models (3 min)
6. **Level 6**: Download and inspect JSON artifacts (2 min)
7. **Level 7**: Understand metrics and improvements (2 min)

**Total Time**: ~15-20 minutes to become comfortable

---

## 📚 References

- Full Guide: `MLFLOW_OPTUNA_INTEGRATION_GUIDE.md`
- Implementation Details: `DAY6_MLFLOW_OPTUNA_IMPLEMENTATION.md`
- Demo Script: `examples/mlflow_optuna_demo.py`

---

**🚀 You're ready to explore MLflow!**

Created: April 1, 2026
Last Updated: April 1, 2026
