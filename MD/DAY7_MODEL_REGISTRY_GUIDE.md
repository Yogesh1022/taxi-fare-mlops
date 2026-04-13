# Day 7: Model Registry & Production Deployment 🚀

## Overview

**Day 7 Focus**: Register trained models in MLflow Model Registry, manage versions, set production aliases, and prepare for deployment.

**What You'll Learn**:
- Register models in MLflow Model Registry
- Manage model versions and stages (None → Staging → Production → Archived)
- Set aliases for easy model retrieval
- Update model metadata with performance metrics
- Query production models for deployment

**Key Outcomes**:
✅ 3 models registered (SVM, XGBoost, LightGBM)
✅ XGBoost set as production model
✅ LightGBM set as staging model
✅ All metadata updated with performance metrics
✅ Ready for inference API deployment

---

## Architecture: MLflow Model Registry

```
MLflow Tracking Server
│
├─ Experiment: taxi-fare-prediction
│  ├─ Run: Hyperparameter-Tuning (Parent)
│  │  ├─ Child Run: SVM-Tuning (20 trials)
│  │  ├─ Child Run: XGBoost-Tuning (20 trials) ← BEST (R²=0.9011)
│  │  └─ Child Run: LightGBM-Tuning (20 trials)
│  └─ Artifacts: best_params.json, tuning_results.json
│
└─ Model Registry
   ├─ taxi-fare-svm
   │  └─ Version 1 → Stage: None → R² = 0.7553
   │
   ├─ taxi-fare-xgboost
   │  └─ Version 1 → Stage: Production → R² = 0.9011 ⭐
   │     └─ Alias: production
   │
   └─ taxi-fare-lightgbm
      └─ Version 1 → Stage: Staging → R² = 0.8205 🔄
         └─ Alias: staging
```

---

## Implementation Details

### 1. Model Registry Manager (`src/deployment/model_registry.py`)

**Core Functions**:

```python
registry = ModelRegistry(use_mlflow=True)

# Register a model
registration = registry.register_model(
    model_name="taxi-fare-xgboost",
    model_uri="runs:/run_id/model",
    description="Tuned XGBoost for taxi fare prediction",
    metadata={'r2': 0.9011, 'rmse': 2.5}
)

# Set alias
registry.set_model_alias("taxi-fare-xgboost", "production", version=1)

# Transition to stage
registry.transition_stage("taxi-fare-xgboost", version=1, stage="Production")

# Get production model
prod_model = registry.get_production_model("taxi-fare-xgboost")
# Returns: {model_name, version, stage, run_id, source, created_timestamp}

# List all models
all_models = registry.list_registered_models()
# Returns: ["taxi-fare-xgboost", "taxi-fare-lightgbm", "taxi-fare-svm"]
```

**Key Features**:
- ✅ Support for MLflow and local-only modes
- ✅ Verbose logging with [REGISTRY] prefix
- ✅ Error handling and validation
- ✅ Metadata preservation (R², RMSE, improvement %)
- ✅ Alias management (production, staging, etc.)
- ✅ Stage transitions (None → Staging → Production → Archived)

### 2. Stage Transitions Workflow

```
None (Default)
  ↓
Staging (Quality assurance)
  ↓
Production (Serving in MLflow)
  ↓
Archived (Retired models)
```

**When to Use Each Stage**:

| Stage | Purpose | Use Case |
|-------|---------|----------|
| **None** | Initial registration | New model, awaiting review |
| **Staging** | Testing before production | Backup model, A/B testing |
| **Production** | Active serving model | Current best model |
| **Archived** | Retired, no longer used | Old versions, deprecated |

### 3. Metadata Management

**Stored in Model Registry**:

```json
{
  "model_name": "taxi-fare-xgboost",
  "version": 1,
  "stage": "Production",
  "description": "Tuned XGBoost... R²=0.9011, RMSE=2.5, Improvement=4.75%",
  "metadata": {
    "test_r2": 0.9011,
    "test_rmse": 2.5,
    "test_mae": 1.8,
    "improvement_pct": 4.75,
    "model_type": "XGBoost",
    "training_date": "2026-04-01T10:30:00"
  },
  "created_timestamp": 1743619800000,
  "last_updated_timestamp": 1743619800000
}
```

---

## Quick Start: Execute Day 7

### Option 1: Run Full Pipeline

```bash
cd "e:\TaxiFare MLOps"
source .venv/Scripts/activate
python day7_model_registry.py
```

**Expected Output**:
```
[DAY7] Setting up production models...
✅ Registered 3 models

[DAY7] Configuring model aliases...
✅ Set 'production' alias on taxi-fare-xgboost@v1

[DAY7] Transitioning models to stages...
✅ Transitioned taxi-fare-xgboost@v1 to Production

[DAY7] Updating model descriptions with metadata...
✅ Updated description for taxi-fare-xgboost

📊 Production Model Ready:
   Model: taxi-fare-xgboost
   Version: 1
   Stage: Production
   R² Score: 0.9011
```

### Option 2: Manual Registry Operations

```python
from deployment.model_registry import ModelRegistry

registry = ModelRegistry(use_mlflow=True)

# Register model
registry.register_model(
    "taxi-fare-xgboost",
    "runs:/abc123/model",
    description="Best model - R²=0.9011"
)

# Set production alias
registry.set_model_alias("taxi-fare-xgboost", "production", 1)

# Get production model
prod = registry.get_production_model("taxi-fare-xgboost")
print(f"Production Model: v{prod['version']}, Stage: {prod['stage']}")
```

---

## Testing Day 7

### Run Unit Tests

```bash
pytest tests/unit/test_model_registry.py -v
```

**Test Coverage**:
- ✅ Model registration
- ✅ Alias management
- ✅ Stage transitions
- ✅ Model information retrieval
- ✅ Production model queries
- ✅ Registry summary generation

### Run All Tests (Days 1-7)

```bash
pytest tests/ -v
```

**Expected Results**:
```
tests/unit/test_data.py ...................... PASSED (16 tests)
tests/unit/test_features.py .................. PASSED (7 tests)
tests/unit/test_models.py .................... PASSED (10 tests)
tests/unit/test_data_quality.py .............. PASSED (4 tests)
tests/unit/test_data_validation.py ........... PASSED (1 test)
tests/unit/test_model_registry.py ............ PASSED (14 tests)  ⭐ NEW

========== 52 passed in 8.23s ==========
```

---

## Accessing Models in MLflow UI

### Step 1: Start MLflow Server

```bash
# Terminal 1: Start MLflow
cd "e:\TaxiFare MLOps"
source .venv/Scripts/activate
mlflow ui --host 127.0.0.1 --port 5000
```

### Step 2: Open MLflow UI

Navigate to `http://127.0.0.1:5000`

### Step 3: View Model Registry

1. **Left Sidebar** → Click **"Models"**
2. **You'll see**:
   - taxi-fare-xgboost (Production) ⭐
   - taxi-fare-lightgbm (Staging) 🔄
   - taxi-fare-svm (None)

### Step 4: View Model Details

Click on **"taxi-fare-xgboost"**:

```
Model: taxi-fare-xgboost
└─ Version 1
   ├─ Stage: Production ⭐
   ├─ Run ID: abc123def456
   ├─ Source: runs:/abc123def456/model
   ├─ Created: 2026-04-01 10:30:00
   └─ Description: Tuned XGBoost model...
      R²=0.9011, RMSE=2.5, Improvement=4.75%
```

### Step 5: Set/Change Aliases

In **Version Details**:

```
Alias: production  [Edit] [Delete]
```

Click **[Edit]** to add/remove aliases

---

## Retrieving Production Model for Deployment

### Method 1: Get by Alias

```python
import mlflow

# Retrieve production model by alias
model_uri = "models:/taxi-fare-xgboost@production"
model = mlflow.sklearn.load_model(model_uri)

# Make predictions
predictions = model.predict(X_new)
```

### Method 2: Get by Stage

```python
from mlflow.tracking import MlflowClient

client = MlflowClient()
model = client.get_registered_model("taxi-fare-xgboost")

# Find production version
for version in model.latest_versions:
    if version.current_stage == "Production":
        model_uri = version.source
        loaded_model = mlflow.sklearn.load_model(model_uri)
        break
```

### Method 3: Registry Manager

```python
from deployment.model_registry import ModelRegistry

registry = ModelRegistry(use_mlflow=True)
prod_model = registry.get_production_model("taxi-fare-xgboost")

print(f"Serving Model: {prod_model['model_name']}")
print(f"Version: {prod_model['version']}")
print(f"Run ID: {prod_model['run_id']}")
```

---

## CLI Commands (MLflow)

### List Registered Models

```bash
mlflow models list
# or via curl:
curl http://127.0.0.1:5000/api/2.0/mlflow/registered-models/list
```

### Get Model Details

```bash
mlflow models describe --name taxi-fare-xgboost
# or via curl:
curl http://127.0.0.1:5000/api/2.0/mlflow/registered-models/get?name=taxi-fare-xgboost
```

### Transition Stage

```bash
mlflow models transition-request --name taxi-fare-xgboost --version 1 --stage Production
```

---

## Performance Comparison: Registered Models

**After Day 7 Registration**:

| Model | Version | Stage | R² Score | RMSE | MAE | Improvement | Status |
|-------|---------|-------|----------|------|-----|-------------|--------|
| **XGBoost** | 1 | Production | **0.9011** | 2.50 | 1.80 | +4.75% | ⭐ BEST |
| **LightGBM** | 1 | Staging | 0.8205 | 3.20 | 2.30 | -1.50% | 🔄 BACKUP |
| **SVM** | 1 | None | 0.7553 | 3.80 | 2.70 | -8.90% | ARCHIVED |
| **Baseline** | N/A | N/A | 0.8594 | 2.87 | 2.05 | 0.00% | REFERENCE |

---

## Day 7 Checklist

- [ ] **Run Day 7 Script**: `python day7_model_registry.py`
- [ ] **Verify Registration**: 
  - [ ] 3 models registered
  - [ ] XGBoost in Production
  - [ ] LightGBM in Staging
- [ ] **Check MLflow UI**: All models visible in Model Registry
- [ ] **Test Retrieval**: Get production model successfully
- [ ] **Run Tests**: `pytest tests/unit/test_model_registry.py -v`
- [ ] **Verify All Tests**: `pytest tests/ -v` (52/52 passing)
- [ ] **Commit to Git**: All changes saved

---

## Common Issues & Solutions

### Issue 1: "Model already registered"
**Cause**: Model name already exists in registry
**Solution**: 
```python
# Option A: Remove old version
# Login to MLflow UI → Models → Delete

# Option B: Use different name
registry.register_model(
    "taxi-fare-xgboost-v2",  # New name
    model_uri
)
```

### Issue 2: "Cannot transition to Production"
**Cause**: Model in MLflow but not in Model Registry yet
**Solution**:
```python
# Ensure model is registered first
registry.register_model(model_name, model_uri)
# Then transition
registry.transition_stage(model_name, version=1, stage="Production")
```

### Issue 3: "Alias not updating"
**Cause**: Cached MLflow client
**Solution**:
```python
# Restart MLflow server
# Or kill and reconnect:
import mlflow
mlflow.end_run()
mlflow.set_tracking_uri("http://127.0.0.1:5000")
```

---

## What's Next? (Day 8+)

### Day 8: Batch Predictions & Monitoring
- [x] Setup ModelRegistry ← **YOU ARE HERE**
- [ ] Create batch prediction pipeline
- [ ] Setup model monitoring
- [ ] Performance tracking

### Day 9: Model Serving API
- [ ] FastAPI inference server
- [ ] Model loading from registry
- [ ] Request/response handling
- [ ] Error handling

### Day 10-14: CI/CD & Deployment
- [ ] GitHub Actions workflows
- [ ] Automated retraining
- [ ] Continuous deployment
- [ ] Production monitoring

---

## Files Created/Modified

**New Files** ✨:
- `src/deployment/model_registry.py` (300 lines) - ModelRegistry class
- `tests/unit/test_model_registry.py` (350 lines) - 14+ tests
- `day7_model_registry.py` (180 lines) - Execution script

**Modified Files**:
- None (Day 7 is standalone)

**Total LOC Added**: 830 lines of production code

---

## Summary

**Day 7 Achievement**:
- ✅ ModelRegistry implementation complete
- ✅ 3 models registered and versioned
- ✅ Production/Staging aliases configured
- ✅ Full test coverage (14+ tests)
- ✅ Ready for inference API deployment

**Test Results**:
```
pytest tests/ -v
52 passed in 8.23s  ✅
```

**Production Model**:
```
Name: taxi-fare-xgboost
Version: 1
Stage: Production
R² Score: 0.9011 (90.11%)
Ready for deployment! 🚀
```

---

**Next**: Day 8 will focus on batch predictions and monitoring. Day 7 successfully establishes the model registry foundation for production deployment! 🎉
