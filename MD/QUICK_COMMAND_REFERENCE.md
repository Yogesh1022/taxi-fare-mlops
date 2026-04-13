# 🎯 Quick Command Reference - Days 1-10

**For fast command lookup - see RUN_AND_TEST_GUIDE.md for detailed explanations**

---

## ⚡ Quick Setup (5 minutes)

```bash
cd "E:\TaxiFare MLOps"
python -m venv .venv
.venv\Scripts\activate
pip install -e ".[dev]"
python -m models.train --help  # Verify
```

---

## 📅 Day-by-Day Quick Commands

### **DAY 1: Data Ingestion & Validation**
```bash
# Run
python -m data.ingest
python -m data.validate_run

# Test
pytest tests/unit/test_data.py -v
```

### **DAY 2: Feature Engineering**
```bash
# Run
python -c "from features.pipeline import FeaturePipeline; p = FeaturePipeline()"

# Test
pytest tests/unit/test_features.py -v
```

### **DAY 3: Baseline Models**
```bash
# Run
python -c "from models.train import train_baseline_models; train_baseline_models(X, y)"

# Test
pytest tests/unit/test_models.py -v -k baseline
```

### **DAY 4: Tree Models**
```bash
# Run
python pipelines/training_pipeline.py --models xgboost lgbm catboost

# Test
pytest tests/unit/test_models.py -v -k tree
```

### **DAY 5: Hyperparameter Tuning**
```bash
# Run
python -c "from models.tune import optimize_hyperparameters; optimize_hyperparameters(n_trials=50)"

# Test
pytest tests/integration/test_pipeline.py::test_hyperparameter_tuning -v
```

### **DAY 6: MLflow Integration**
```bash
# Terminal 1 - Start MLflow
mlflow server --host 0.0.0.0 --port 5000

# Terminal 2 - Run training
python -c "from models.train import train_with_mlflow; train_with_mlflow()"

# View: http://localhost:5000
```

### **DAY 7: Model Registry**
```bash
# Run
python -c "from models.registry import register_model; register_model(run_id='<id>')"
python -c "from models.registry import transition_model_stage; transition_model_stage()"

# Test
pytest tests/unit/test_models.py -v -k registry
```

### **DAYS 8-9: Batch & API**
```bash
# Terminal 1 - Start API
uvicorn src.deployment.api:app --reload --port 8000

# Terminal 2 - Test
python -c "from models.predict import batch_predict; batch_predict(test_data)"
curl -X POST http://localhost:8000/predict -H "Content-Type: application/json" -d '{"trip_distance": 3.5}'

# Test
pytest tests/integration/test_pipeline.py -v

# View docs: http://localhost:8000/docs
```

### **DAY 10: CI/CD**
```bash
# Run all checks
bash scripts/run_local_ci.sh

# OR individually:
make lint
make test
make test-cov
python scripts/validate_workflows.py
python scripts/day10_verification.py
```

---

## 🧪 Complete Test Suite

```bash
# All tests
pytest tests/ -v

# By type
pytest tests/unit/ -v          # Unit only
pytest tests/integration/ -v   # Integration only
pytest tests/contract/ -v      # Contract only

# With coverage
pytest tests/ --cov=src --cov-report=html
start htmlcov/index.html

# Specific test
pytest tests/unit/test_models.py::test_xgboost -v
```

---

## 🎁 High-Priority Improvements (Already Done)

```bash
# 1. Ensemble Models
pytest tests/unit/test_ensemble.py -v

# 2. Bayesian Tuning
pytest tests/unit/test_bayesian_tuning.py -v

# 3. Feature Selection
pytest tests/unit/test_feature_selection.py -v

# 4. Anomaly Detection
pytest tests/unit/test_drift_detection.py -v

# 5. A/B Testing
pytest tests/unit/test_ab_testing.py -v
```

---

## 🚀 Medium-Priority Improvements (Just Added!)

```bash
# 1. SHAP Explainability
python -c "from models.explainability import ExplainabilityAnalyzer; analyzer = ExplainabilityAnalyzer(model)"
pytest tests/unit/test_explainability.py -v

# 2. Grafana Monitoring
python -c "from deployment.grafana_integration import create_monitoring_setup; create_monitoring_setup()"
docker-compose -f docker/docker-compose.yml up -d  # If using Docker

# 3. Model Optimization
python -c "from deployment.optimization import ModelOptimizer; opt = ModelOptimizer(model)"
pytest tests/unit/test_optimization.py -v

# 4. Great Expectations
python -c "from data.quality_framework import validate_taxi_dataset; validate_taxi_dataset(df)"
pytest tests/unit/test_quality_framework.py -v

# 5. Enhanced API Docs
python -c "from deployment.enhanced_api_docs import APIDocumentationGenerator; APIDocumentationGenerator.save_documentation()"
```

---

## 🔧 Makefile Commands

```bash
make setup          # Install dependencies
make lint           # Run linting
make format         # Auto-format code
make test           # Run all tests
make test-unit      # Unit tests only
make test-cov       # Tests with coverage
make train          # Run training pipeline
make serve          # Start API server
make dashboard      # Start Streamlit dashboard
make docker-build   # Build Docker images
make docker-up      # Start Docker services
make clean          # Clean cache/artifacts
make all            # Setup + lint + test + train
```

---

## 📊 Monitoring & Access Points

```
MLflow UI:           http://localhost:5000
Swagger API Docs:    http://localhost:8000/docs
ReDoc Docs:          http://localhost:8000/redoc
Grafana Dashboards:  http://localhost:3000
Prometheus Metrics:  http://localhost:9090
```

---

## 🐛 Quick Fixes

```bash
# Module not found
pip install -e ".[dev]"   # Reinstall

# Port already in use
# Kill process on port 8000
taskkill /F /IM python.exe

# Data files missing
python -m data.ingest    # Re-download

# MLflow issues
mlflow server --host 0.0.0.0 --port 5000    # Restart

# Test failures
pytest tests/ -vv --tb=long    # Verbose output

# Code formatting
make format    # Auto-fix
```

---

## ✨ Complete End-to-End

```bash
# From scratch in one go (takes ~30 min)
make all && bash scripts/run_local_ci.sh && pytest tests/ -v
```

---

## 📋 Verification Checklist

- [ ] Data ingestion works (Day 1)
- [ ] Features created (Day 2)
- [ ] Baseline models train (Day 3)
- [ ] Tree models train (Day 4)
- [ ] Tuning completes (Day 5)
- [ ] MLflow tracking works (Day 6)
- [ ] Models registered (Day 7)
- [ ] API responds (Days 8-9)
- [ ] All tests pass (Day 10)
- [ ] Improvements integrated (High + Medium)

---

## 📚 Documentation Files

- **RUN_AND_TEST_GUIDE.md** - Detailed walkthrough (THIS!)
- **HIGH_PRIORITY_IMPROVEMENTS_REPORT.md** - Improvements phase 1
- **MEDIUM_PRIORITY_IMPROVEMENTS_REPORT.md** - Improvements phase 2
- **COMPLETE_IMPROVEMENTS_SUMMARY.md** - All 10 improvements overview
- **PROJECT_ANALYSIS_REPORT.md** - Full project analysis
- **DAY10_CI_CD_PIPELINE.md** - CI/CD details

---

**Last Updated**: April 8, 2026  
**Status**: ✅ Ready to Run
