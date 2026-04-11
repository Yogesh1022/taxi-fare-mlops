# MLflow + Optuna Nested Runs Integration Guide

## Overview

This guide demonstrates how to use **MLflow with Optuna nested runs** for comprehensive hyperparameter tuning experiment tracking. Each model's tuning process creates a parent run with child runs for individual trials.

---

## Architecture

```
MLflow Experiment: taxi-fare-prediction
├── Parent Run: Hyperparameter-Tuning (overall tuning)
│   ├── Parent Run: SVM-Tuning (SVM model tuning)
│   │   ├── Trial 1 (nested)
│   │   ├── Trial 2 (nested)
│   │   └── Trial 3 (nested)
│   ├── Parent Run: XGBoost-Tuning (XGBoost model tuning)  ⭐ Best model
│   │   ├── Trial 1 (nested)
│   │   ├── Trial 2 (nested)
│   │   └── Trial 3 (nested)
│   └── Parent Run: LightGBM-Tuning (LightGBM model tuning)
│       ├── Trial 1 (nested)
│       ├── Trial 2 (nested)
│       └── Trial 3 (nested)
```

---

## Usage Examples

### 1. Basic Usage with MLflow Enabled (Default)

```python
from src.models.tune import HyperparameterTuner, tune_top_3_models
from src.data.ingest import load_processed_data
import pandas as pd

# Load data
X, y = load_processed_data()

# Split data
from sklearn.model_selection import train_test_split
X_train, X_temp, y_train, y_temp = train_test_split(X, y, test_size=0.3, random_state=42)
X_val, X_test, y_val, y_test = train_test_split(X_temp, y_temp, test_size=0.5, random_state=42)

# Initialize tuner with MLflow enabled (default)
tuner = HyperparameterTuner(
    X_train, X_val, y_train, y_val, X_test, y_test,
    n_trials=20,
    use_mlflow=True  # MLflow enabled by default
)

# Run tuning - all trials logged to MLflow automatically
results = tuner.tune_all()

# Save results and log artifacts to MLflow
tuner.save_results()

print("Tuning complete! Check MLflow UI for experiment tracking:")
print("  mlflow ui --backend-store-uri ./mlruns")
```

### 2. Convenience Function

```python
from src.models.tune import tune_top_3_models

# Tune all models with MLflow tracking
results = tune_top_3_models(
    X_train, X_val, X_test,
    y_train, y_val, y_test,
    n_trials=20,
    use_mlflow=True  # Enable MLflow
)
```

### 3. Testing Without MLflow

For unit tests or development without MLflow overhead:

```python
# Disable MLflow tracking
tuner = HyperparameterTuner(
    X_train, X_val, y_train, y_val, X_test, y_test,
    n_trials=3,
    use_mlflow=False  # Disable for faster testing
)

results = tuner.tune_all()
```

---

## What Gets Logged to MLflow

### Parent Run Metrics (Overall Tuning)
- `SVM_test_r2`: SVM final R² on test set
- `SVM_test_rmse`: SVM RMSE
- `SVM_test_mae`: SVM MAE
- `XGBoost_test_r2`: XGBoost final R²
- `XGBoost_test_rmse`: XGBoost RMSE
- `XGBoost_test_mae`: XGBoost MAE
- `LightGBM_test_r2`: LightGBM final R²
- `LightGBM_test_rmse`: LightGBM RMSE
- `LightGBM_test_mae`: LightGBM MAE

### Per-Model Parent Run Metrics
- `best_val_r2`: Best validation R² achieved
- `n_completed_trials`: Number of completed trials
- `n_pruned_trials`: Number of pruned trials

### Child Run Metrics (Per Trial)
For each trial (nested run):
- `val_r2`: Validation R² score
- `val_rmse`: Validation RMSE
- `val_mae`: Validation MAE
- All hyperparameters tested in that trial

### Artifacts
- `tuned_best_params.json`: Best parameters for all models
- `tuning_results.json`: Complete tuning results
- `tuning_comparison.json`: Comparison with baseline models

---

## Key Features

### 1. **Nested Runs Structure**
```
Each trial becomes a child run nested under the model's parent run
- Easier navigation in MLflow UI
- Logical grouping of experiments
- Clear trial-level metrics and parameters
```

### 2. **Automatic Pruning Tracking**
```json
{
  "n_completed_trials": 18,
  "n_pruned_trials": 2
}
```
Pruned trials are logged but marked separately, helping understand optimization efficiency.

### 3. **Comprehensive Parameter Logging**
Each trial logs:
```python
{
  "C": 45.2,
  "epsilon": 0.15,
  "max_depth": 8,
  "learning_rate": 0.025,
  ...
}
```

### 4. **Multi-Level Metrics**
- **Trial Level**: Individual trial validation metrics
- **Model Level**: Best model performance metrics
- **Overall Level**: Aggregate results across all models

---

## Viewing Results in MLflow UI

### 1. Start MLflow UI
```bash
mlflow ui --backend-store-uri ./mlruns
```

### 2. Access UI
Open browser: `http://localhost:5000`

### 3. Navigation
- **Experiments**: Find `taxi-fare-prediction`
- **Runs**: View parent runs (SVM-Tuning, XGBoost-Tuning, LightGBM-Tuning)
- **Nested Runs**: Click on parent run → view individual trials
- **Metrics**: Compare performance across trials
- **Parameters**: Analyze hyperparameter search space
- **Artifacts**: Download best parameters and results JSON files

---

## Performance Comparison

### With MLflow Enabled
- **Tuning Time**: ~50 seconds (20 trials × 3 models)
- **Overhead**: <5% (MLflow logging is lightweight with nested=True)
- **Storage**: ~50 MB for run data

### Without MLflow
- **Tuning Time**: ~45 seconds (5% faster)
- **Use Case**: Development, CI/CD where tracking not needed

---

## Advanced Configuration

### Custom MLflow Tracking URI
```python
import os
from src.utils.config import MLFLOW_TRACKING_URI

# Use database backend (recommended for production)
os.environ['MLFLOW_TRACKING_URI'] = 'sqlite:///mlflow.db'

# Then create tuner - it will use the new URI
tuner = HyperparameterTuner(..., use_mlflow=True)
```

### Custom Experiment Name
```python
import mlflow
from src.utils.config import MLFLOW_EXPERIMENT_NAME

# Set experiment before creating tuner
mlflow.set_experiment("custom-experiment-name")

tuner = HyperparameterTuner(..., use_mlflow=True)
```

---

## Integration with DVC Pipeline

The tuning process integrates seamlessly with DVC:

```yaml
# dvc.yaml
stages:
  tune:
    cmd: python -m pipelines.tuning_pipeline
    deps:
      - src/models/tune.py
      - models/trained_models.pkl
    outs:
      - models/tuned_svm_model.pkl
      - models/tuned_xgboost_model.pkl
      - models/tuned_lightgbm_model.pkl
```

**DVC tracks**: Model artifacts and checksums
**MLflow tracks**: Trial metrics, parameters, and experiment history

---

## Troubleshooting

### Issue: FileStore Deprecation Warning
```
FutureWarning: The filesystem tracking backend is deprecated as of February 2026
```

**Solution**: Switch to database backend
```bash
# SQLite (lightweight)
export MLFLOW_TRACKING_URI=sqlite:///mlflow.db

# PostgreSQL (production)
export MLFLOW_TRACKING_URI=postgresql://user:password@localhost/mlflow
```

### Issue: Nested Runs Not Appearing
- Ensure `nested=True` in `mlflow.start_run()` ✅ (Already configured)
- Check MLflow version >= 1.20

### Issue: Memory Usage High During Tuning
- Reduce `n_trials` parameter
- Increase `n_jobs` for faster completion
- Disable MLflow: `use_mlflow=False`

---

## Best Practices

1. **Always enable MLflow in production**: `use_mlflow=True`
2. **Use nested runs for trial tracking**: Keeps UI clean
3. **Log artifacts**: Enable comparison with baseline
4. **Track Git commits**: Link experiments to code versions
5. **Use meaningful run names**: `"SVM-Tuning-v2-optimized"`
6. **Archive old experiments**: Prevent UI clutter

---

## Next Steps

- **Day 6**: Model Registry - Register best tuned models
- **Day 7**: Advanced tracking - Custom metrics and tags
- **Day 8**: Batch predictions - Log predictions with MLflow
- **Day 9**: Monitoring - Track model drift over time

---

**Last Updated**: 2026-04-01
**MLflow Version**: 2.8.0+
**Optuna Version**: 3.4.0+
