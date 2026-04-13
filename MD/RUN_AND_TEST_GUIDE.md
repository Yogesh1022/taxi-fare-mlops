# 🚀 Complete Run & Test Guide - Days 1-10 Implementation

**Last Updated**: April 8, 2026  
**Project Status**: ✅ 10/14 Days Complete (71%)  
**Focus**: End-to-End MLOps Pipeline with 10 Production Enhancements

---

## 📋 Quick Navigation

- [Initial Setup](#initial-setup)
- [Day-by-Day Execution](#day-by-day-execution)
  - [Days 1-7: Training Pipeline](#days-1-7-training-pipeline)
  - [Days 8-9: Batch & Inference](#days-8-9-batch--inference)
  - [Day 10: CI/CD Pipeline](#day-10-cicd-pipeline)
- [Additional Improvements](#additional-improvements--high-priority--medium-priority)
- [Automated Testing Suite](#automated-testing-suite)
- [Troubleshooting](#troubleshooting)

---

## ✅ Initial Setup

### Step 1: Prerequisites Check

```bash
# Navigate to project directory
cd "E:\TaxiFare MLOps"

# Check Python version (3.10+)
python --version

# Check pip
pip --version

# Check Git
git --version
```

**Expected Output:**
- Python 3.10.x or higher
- pip 23.x or higher
- git 2.x or higher

### Step 2: Environment Setup

```bash
# Create and activate virtual environment
python -m venv .venv

# Windows activation
.venv\Scripts\activate

# Verify activation (should show (.venv) prefix)
python -m pip install --upgrade pip
```

### Step 3: Install Dependencies

```bash
# Install project with development dependencies
pip install -e ".[dev]"

# Verify installation
python -m models.train --help
```

**Expected Output:** Help message showing model training options

### Step 4: Verify Data

```bash
# Check raw data exists
ls data/raw/

# Expected files:
# - train.csv
# - test.csv
```

**Expected Output:**
```
train.csv  (10MB+)
test.csv   (2MB+)
```

---

## 🗂️ Day-by-Day Execution

### **Days 1-7: Training Pipeline**

#### 📌 Day 1: Foundation & Data Validation

**What Gets Done:**
- ✅ Data ingestion (CSV → DataFrame)
- ✅ Data validation (schema, nulls, ranges)
- ✅ Exploratory data analysis
- ✅ Data splitting (train/test)

**Run Day 1:**

```bash
# 1. Run data ingestion and validation
python -m data.ingest

# 2. Validate data pipeline
python -m data.validate_run

# 3. Check generated files
ls data/processed/
```

**Expected Output:**
```
✓ Data loaded: shape (rows, cols)
✓ Validation passed: 95%+ records valid
✓ Files created:
  - processed/train_processed.csv
  - processed/test_processed.csv
  - mlops/data_quality/validation_metrics.json
```

**Test Day 1:**

```bash
# Run unit tests for data module
pytest tests/unit/test_data.py -v

# Expected: All tests pass ✓
```

---

#### 📌 Day 2: Feature Engineering

**What Gets Done:**
- ✅ Feature transformation (scaling, encoding)
- ✅ Feature creation (derived features)
- ✅ Feature pipeline creation
- ✅ Feature preprocessing

**Run Day 2:**

```bash
# 1. Load data
python -c "
import pandas as pd
from features.pipeline import FeaturePipeline

# Load raw data
df = pd.read_csv('data/raw/train.csv')
print(f'Data shape: {df.shape}')

# Apply feature pipeline
pipeline = FeaturePipeline()
X, y = pipeline.fit_transform(df)
print(f'Features shape: {X.shape}')
print(f'Features: {X.columns.tolist()}')
"

# 2. Run feature tests
pytest tests/unit/test_features.py -v
```

**Expected Output:**
```
✓ Data shape: (8000+, 6+)
✓ Features shape: (8000+, 15)
✓ Feature scaling applied
✓ All unit tests pass
```

---

#### 📌 Day 3: Baseline Models

**What Gets Done:**
- ✅ Train baseline models (Linear, Ridge, Lasso)
- ✅ Model evaluation (MAE, RMSE, R²)
- ✅ Baseline performance established
- ✅ Model comparison

**Run Day 3:**

```bash
# 1. Train baseline models
python -c "
from models.train import train_baseline_models
from features.pipeline import FeaturePipeline
import pandas as pd

# Load and prepare data
df = pd.read_csv('data/raw/train.csv')
pipeline = FeaturePipeline()
X, y = pipeline.fit_transform(df)

# Train baselines
results = train_baseline_models(X, y)
print(results)
"

# 2. Test baseline models
pytest tests/unit/test_models.py -v -k baseline
```

**Expected Output:**
```
✓ Linear Regression R²: 0.65+
✓ Ridge Regression R²: 0.66+
✓ Lasso Regression R²: 0.64+
✓ Best model: Ridge
✓ All unit tests pass
```

---

#### 📌 Day 4: Tree Models & Optimization

**What Gets Done:**
- ✅ Train tree-based models (XGBoost, LightGBM, CatBoost)
- ✅ Model performance comparison
- ✅ Grid search hyperparameter tuning
- ✅ Performance benchmarking

**Run Day 4:**

```bash
# 1. Train tree models
python pipelines/training_pipeline.py --models xgboost lgbm catboost

# 2. Compare model performance
python -c "
from models.evaluate import compare_models
import json

results = compare_models()
print(json.dumps(results, indent=2))
"

# 3. Test model training
pytest tests/unit/test_models.py -v -k tree
```

**Expected Output:**
```
✓ XGBoost R²: 0.82+
✓ LightGBM R²: 0.83+
✓ CatBoost R²: 0.84+
✓ Best model: CatBoost
✓ Hyperparameter tuning complete
```

---

#### 📌 Day 5: Advanced Tuning & Optimization

**What Gets Done:**
- ✅ Hyperparameter optimization (Optuna/Bayesian)
- ✅ Cross-validation tuning
- ✅ Performance analysis and bottleneck detection
- ✅ Optimization recommendations

**Run Day 5:**

```bash
# 1. Run hyperparameter tuning (Optuna)
python -c "
from models.tune import optimize_hyperparameters

best_params, best_value = optimize_hyperparameters(
    n_trials=50,
    model_type='xgboost'
)
print(f'Best params: {best_params}')
print(f'Best R²: {best_value}')
"

# 2. Analyze bottlenecks
python -c "
from models.evaluate import analyze_bottlenecks
results = analyze_bottlenecks()
print(results)
"

# 3. Test tuning pipeline
pytest tests/integration/test_pipeline.py::test_hyperparameter_tuning -v
```

**Expected Output:**
```
✓ Optuna running: 50 trials
✓ Best R²: 0.86+
✓ Tuning time: 180+ seconds
✓ Performance gains identified
```

---

#### 📌 Day 6: MLflow Integration

**What Gets Done:**
- ✅ MLflow server setup
- ✅ Experiment tracking
- ✅ Run logging (metrics, parameters, artifacts)
- ✅ Model registry

**Run Day 6:**

```bash
# 1. Start MLflow server
mlflow server --host 0.0.0.0 --port 5000

# (In new terminal, keep server running)

# 2. Run training with MLflow logging
python -c "
import mlflow
from models.train import train_with_mlflow

mlflow.set_tracking_uri('http://localhost:5000')
mlflow.set_experiment('taxi-fare-experiment')

results = train_with_mlflow()
print(results)
"

# 3. Check MLflow UI
# Open browser: http://localhost:5000
# Should see experiments and runs
```

**Expected Output:**
```
✓ MLflow server running on http://localhost:5000
✓ Experiment created: taxi-fare-experiment
✓ Run logged with metrics, params, artifacts
✓ Can view in MLflow UI
```

---

#### 📌 Day 7: Model Registry & Management

**What Gets Done:**
- ✅ Register models in MLflow Registry
- ✅ Model versioning
- ✅ Model staging (Dev → Staging → Production)
- ✅ Model governance setup

**Run Day 7:**

```bash
# 1. Register best model
python -c "
from models.registry import register_model

model_uri = register_model(
    run_id='<best_run_id>',
    model_name='taxi-fare-prediction',
    description='Production taxi fare model'
)
print(f'Registered model: {model_uri}')
"

# 2. Push to model stage
python -c "
from models.registry import transition_model_stage

transition_model_stage(
    model_name='taxi-fare-prediction',
    version=1,
    stage='Staging'
)
print('Model transitioned to Staging')
"

# 3. Test model registry
pytest tests/unit/test_models.py -v -k registry
```

**Expected Output:**
```
✓ Model registered: models:/taxi-fare-prediction/1
✓ Model version: 1
✓ Stage: Staging (ready for testing)
✓ Registry tests pass
```

---

### **Days 8-9: Batch & Inference**

#### 📌 Days 8-9: Batch Predictions & Inference API

**What Gets Done:**
- ✅ Batch prediction pipeline
- ✅ Load model from registry
- ✅ Inference API (FastAPI)
- ✅ API documentation (OpenAPI/Swagger)

**Run Days 8-9:**

```bash
# 1. Generate batch predictions
python -c "
from models.predict import batch_predict
import pandas as pd

# Load test data
test_data = pd.read_csv('data/raw/test.csv')

# Make predictions
results = batch_predict(test_data, model_version='production')
print(f'Predictions: {results[:5]}')
print(f'Total predictions: {len(results)}')
"

# 2. Save predictions
python -c "
from models.predict import batch_predict_and_save
batch_predict_and_save(
    input_file='data/raw/test.csv',
    output_file='data/processed/predictions.csv',
    model_version='production'
)
print('Predictions saved to data/processed/predictions.csv')
"

# 3. Start inference API
uvicorn src.deployment.api:app --reload --port 8000

# (In new terminal)

# 4. Test API endpoints
python -c "
import requests
import json

# Test prediction endpoint
payload = {
    'trip_distance': 3.5,
    'passenger_count': 2,
    'pickup_hour': 14,
    'day_of_week': 3,
    'month': 6
}

response = requests.post(
    'http://localhost:8000/predict',
    json=payload
)
print(json.dumps(response.json(), indent=2))
"

# 5. Test batch endpoint
python -c "
import requests
import pandas as pd

test_data = pd.read_csv('data/raw/test.csv').head(10)

response = requests.post(
    'http://localhost:8000/predict/batch',
    json=test_data.to_dict('records')
)
print(f'Batch prediction status: {response.status_code}')
print(f'Predictions returned: {len(response.json())}')
"

# 6. View API docs
# Open browser: http://localhost:8000/docs
# Should see interactive Swagger UI

# 7. Run integration tests
pytest tests/integration/test_pipeline.py -v
```

**Expected Output:**
```
✓ Batch predictions generated: 1000+ records
✓ Predictions saved successfully
✓ API server running on http://localhost:8000
✓ Single prediction: fare=$15.75
✓ Batch predictions: 10 records processed
✓ API documentation available at /docs
✓ Integration tests pass
```

---

### **Day 10: CI/CD Pipeline**

#### 📌 Day 10: GitHub Actions CI/CD

**What Gets Done:**
- ✅ GitHub Actions workflow setup
- ✅ Automated testing on push
- ✅ Code quality checks
- ✅ Model validation
- ✅ Pre-deployment verification

**Run Day 10:**

```bash
# 1. Run local CI equivalent
bash scripts/run_local_ci.sh

# OR manually run each check:

# 2. Run linting
make lint

# Expected: All checks pass with no errors

# 3. Run all tests
make test

# Expected: All tests pass

# 4. Run coverage analysis
make test-cov

# Expected: 85%+ code coverage

# 5. Validate GitHub workflows
python scripts/validate_workflows.py

# Expected: All workflows valid and properly configured

# 6. Verify Day 10 setup
python scripts/day10_verification.py

# Expected: All checks complete
```

**Expected Output:**
```
✓ Linting: PASS (ruff, black, isort)
✓ Unit tests: 120+ tests PASS
✓ Integration tests: 15+ tests PASS
✓ Code coverage: 87%+
✓ GitHub workflows: Valid and configured
✓ Day 10 verification: PASS
```

**GitHub Actions Workflows (in .github/workflows/):**

```yaml
# 1. ci.yml - Run on every push
   - Run pytest
   - Run linting
   - Run coverage

# 2. model-validation.yml - Run daily
   - Validate model performance
   - Run batch predictions
   - Validate API

# 3. deployment-ready.yml - Manual trigger
   - Pre-deployment checks
   - Security scanning
   - Performance benchmarks
```

---

## 🎁 Additional Improvements | High-Priority + Medium-Priority

### **High-Priority Improvements** (5 modules, 2,800 LOC)

These were implemented in the previous phase:

#### 1. Ensemble Models
```bash
# Test ensemble models
python -c "
from models.ensemble import EnsembleModel

ensemble = EnsembleModel(
    models=['xgboost', 'lgbm', 'catboost'],
    weights=[0.3, 0.3, 0.4]
)
print(f'Ensemble R²: {ensemble.score()}')
"
```

#### 2. Bayesian Hyperparameter Tuning
```bash
# Test Bayesian tuning
python -c "
from models.bayesian_tuning import BayesianOptimizer

optimizer = BayesianOptimizer(n_trials=100)
best_params = optimizer.optimize()
print(f'Best params: {best_params}')
"
```

#### 3. Feature Selection
```bash
# Test feature selection
python -c "
from features.feature_selection import FeatureSelector

selector = FeatureSelector(method='shap')
selected_features = selector.select(X, y, n_features=7)
print(f'Selected {len(selected_features)} features')
"
```

#### 4. Anomaly Detection
```bash
# Test anomaly detection
python -c "
from deployment.drift_detection import AnomalyDetector

detector = AnomalyDetector()
anomalies = detector.detect(X)
print(f'Anomalies detected: {len(anomalies)}')
"
```

#### 5. A/B Testing Framework
```bash
# Test A/B testing
python -c "
from deployment.ab_testing import ABTestingFramework

ab_test = ABTestingFramework(model_a, model_b)
results = ab_test.run_test(X_test, y_test)
print(f'Significant difference: {results.significant}')
"
```

---

### **Medium-Priority Improvements** (5 modules, 3,250 LOC) ✅ JUST COMPLETED

#### 1. SHAP Explainability
```bash
# Test SHAP explanations
python -c "
from models.explainability import ExplainabilityAnalyzer

analyzer = ExplainabilityAnalyzer(trained_model)
explanation = analyzer.explain_prediction(model, X_test, idx=0)
print(f'SHAP values: {explanation}')
print(f'Feature importance: {analyzer.feature_importance_shap()}')
"
```

#### 2. Grafana Monitoring Dashboard
```bash
# Start Prometheus + Grafana
docker-compose -f docker/docker-compose.yml up -d

# Test monitoring
python -c "
from deployment.grafana_integration import create_monitoring_setup

setup = create_monitoring_setup()
print('Monitoring setup created')
print(f'Grafana: http://localhost:3000')
print(f'Prometheus: http://localhost:9090')
"

# Access dashboards:
# - Model Monitoring: http://localhost:3000
# - Data Quality: http://localhost:3000
# - Inference Pipeline: http://localhost:3000
```

#### 3. Model Optimization
```bash
# Test model optimization
python -c "
from deployment.optimization import ModelOptimizer

optimizer = ModelOptimizer(trained_model)
results = optimizer.optimize_all(X_test)

print(f'Original size: {results[\"quantization\"][\"original_size_mb\"]} MB')
print(f'Quantized size: {results[\"quantization\"][\"estimated_size_mb\"]} MB')
print(f'Speedup: {results[\"quantization\"][\"expected_inference_speedup\"]}x')
"
```

#### 4. Great Expectations Data Quality
```bash
# Test data quality framework
python -c "
from data.quality_framework import validate_taxi_dataset

results = validate_taxi_dataset(
    df=test_data,
    name='test_dataset'
)
print(f'Pass rate: {results[\"pass_rate_pct\"]:.1f}%')
print(f'Failed checks: {results[\"failed_checks\"]}')
"
```

#### 5. Enhanced API Documentation
```bash
# Generate and save API documentation
python -c "
from deployment.enhanced_api_docs import APIDocumentationGenerator

docs = APIDocumentationGenerator.generate_complete_documentation()
APIDocumentationGenerator.save_documentation()

print('Documentation generated:')
print('- JSON: mlops/api_docs/api_documentation.json')
print('- Markdown: mlops/api_docs/API_DOCUMENTATION.md')
"

# Access documentation:
# - Swagger UI: http://localhost:8000/docs
# - ReDoc UI: http://localhost:8000/redoc
```

---

## 🧪 Automated Testing Suite

### Run All Tests

```bash
# 1. Run all tests with verbose output
pytest tests/ -v

# 2. Run tests by category
pytest tests/unit/ -v              # Unit tests only
pytest tests/integration/ -v       # Integration tests
pytest tests/contract/ -v          # Contract tests

# 3. Run specific test
pytest tests/unit/test_models.py::test_xgboost -v

# 4. Run with coverage
pytest tests/ --cov=src --cov-report=html

# Open coverage report
start htmlcov/index.html
```

### Test Commands by Day

```bash
# Day 1 Tests
pytest tests/unit/test_data.py -v

# Day 2 Tests
pytest tests/unit/test_features.py -v

# Day 3 Tests
pytest tests/unit/test_models.py::test_baseline -v

# Day 4 Tests
pytest tests/unit/test_models.py -v

# Day 5 Tests
pytest tests/integration/test_pipeline.py::test_hyperparameter_tuning -v

# Day 6 Tests
pytest tests/unit/test_models.py::test_mlflow -v

# Day 7 Tests
pytest tests/unit/test_models.py::test_registry -v

# Day 8-9 Tests
pytest tests/integration/test_pipeline.py -v

# Day 10 Tests
make test
bash scripts/run_local_ci.sh
```

### Code Quality Checks

```bash
# Linting
ruff check .
black --check src/
isort --check-only src/

# Auto-fix linting
black src/ tests/ pipelines/
isort src/ tests/ pipelines/
ruff check --fix .

# Type checking
mypy src/

# Security scanning
pip install bandit
bandit -r src/
```

---

## 🔍 Verification Checklists

### Day 1 Verification ✓
- [ ] Data loaded successfully
- [ ] Validation metrics report generated
- [ ] Train/test split created
- [ ] Data quality > 95%
- [ ] Unit tests pass

### Day 2 Verification ✓
- [ ] Features created correctly
- [ ] Feature scaling applied
- [ ] Feature pipeline works
- [ ] Feature tests pass

### Day 3 Verification ✓
- [ ] Baseline models trained
- [ ] Model performance > R² 0.65
- [ ] Models saved correctly
- [ ] Model tests pass

### Day 4 Verification ✓
- [ ] Tree models trained
- [ ] Best model identified
- [ ] Hyperparameter grid search complete
- [ ] Performance > R² 0.82

### Day 5 Verification ✓
- [ ] Bayesian tuning completes
- [ ] 50+ trials run
- [ ] Performance > R² 0.86
- [ ] Bottlenecks identified

### Day 6 Verification ✓
- [ ] MLflow server running
- [ ] Experiments created
- [ ] Runs logged with metrics
- [ ] MLflow UI accessible

### Day 7 Verification ✓
- [ ] Models registered
- [ ] Versioning working
- [ ] Staging transition works
- [ ] Model governance in place

### Day 8-9 Verification ✓
- [ ] Batch predictions generated
- [ ] API server running
- [ ] Endpoints respond correctly
- [ ] API documentation accessible

### Day 10 Verification ✓
- [ ] All tests pass
- [ ] Code coverage > 85%
- [ ] Linting passes
- [ ] CI/CD workflows configured

### High-Priority Improvements ✓
- [ ] Ensemble models work
- [ ] Bayesian tuning completes
- [ ] Feature selection reduces features
- [ ] Anomaly detection identifies outliers
- [ ] A/B testing runs

### Medium-Priority Improvements ✓
- [ ] SHAP explanations generated
- [ ] Grafana dashboards created
- [ ] Model optimization benchmarked
- [ ] Data quality checks run
- [ ] API documentation generated

---

## 🐛 Troubleshooting

### Issue: "Module not found" error

```bash
# Solution 1: Reinstall package
pip install -e ".[dev]"

# Solution 2: Add to PYTHONPATH
set PYTHONPATH=%cd%;%PYTHONPATH%

# Solution 3: Install in development mode
python setup.py develop
```

### Issue: Data files not found

```bash
# Check data directory
ls data/raw/

# If missing, download data:
python -m data.ingest

# Or check .gitignore for excluded files
cat .gitignore | grep data
```

### Issue: MLflow server won't start

```bash
# Kill process on port 5000
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Start fresh
mlflow server --host 0.0.0.0 --port 5000
```

### Issue: API port already in use

```bash
# Use different port
uvicorn src.deployment.api:app --port 8001

# Or kill process on 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

### Issue: Test failures

```bash
# Run with more verbose output
pytest tests/ -vv --tb=long

# Run specific test with output
pytest tests/unit/test_data.py::test_load_data -s

# Check test config
cat pytest.ini
cat setup.cfg
```

### Issue: Docker container issues

```bash
# Check running containers
docker ps -a

# View container logs
docker logs <container_id>

# Rebuild images
docker-compose -f docker/docker-compose.yml build --no-cache

# Fresh start
docker-compose -f docker/docker-compose.yml down -v
docker-compose -f docker/docker-compose.yml up -d
```

### Issue: Git/GitHub token issues

```bash
# Check token setup
echo $GITHUB_TOKEN

# If not set, use helper script
python scripts/github_token_helper.py

# Verify token works
curl -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user
```

---

## 📊 Monitoring & Metrics

### Key Metrics to Track

```
Data Quality:
  - Null values: < 1%
  - Invalid values: < 0.1%
  - Data drift (PSI): < 0.1

Model Performance:
  - R² Score: > 0.86
  - MAE: < $1.50
  - RMSE: < $2.00
  - MAPE: < 10%

Inference:
  - Latency: < 50ms
  - Throughput: > 1000 req/min
  - Error rate: < 0.1%

Code Quality:
  - Test coverage: > 85%
  - Linting score: 10/10
  - Type coverage: > 90%
```

### Monitor Real-Time Metrics

```bash
# View Prometheus metrics
curl http://localhost:9090/api/v1/series

# View Grafana dashboards
open http://localhost:3000

# Check API metrics
curl http://localhost:8000/metrics
```

---

## 📁 Output Artifacts

### Expected by End of Day 10

```
data/
├── raw/
│   ├── train.csv          (original data)
│   └── test.csv
├── processed/
│   ├── train_processed.csv
│   ├── test_processed.csv
│   └── predictions.csv    (batch predictions)
└── external/

models/
├── best_model.pkl
├── scaler.pkl
└── model_v1.pkl

mlops/
├── data_quality/
│   ├── validation_metrics.json
│   └── data_quality_*.md
├── monitoring/
│   ├── prometheus_metrics.txt
│   ├── grafana_dashboard_*.json
│   └── optimization_results.json
└── api_docs/
    ├── api_documentation.json
    └── API_DOCUMENTATION.md

mlruns/              (MLflow experiments)

logs/
├── training.log
├── inference.log
└── api.log

.github/workflows/
├── ci.yml
├── model-validation.yml
└── deployment-ready.yml
```

---

## ✨ Summary Command

Run everything at once:

```bash
# Complete setup to Day 10
make all

# Verify everything works
bash scripts/run_local_ci.sh

# Run full test suite
pytest tests/ -v

# Check all artifacts
echo "=== Checking artifacts ==="
ls -lah data/processed/
ls -lah models/
ls -lah mlops/
ls -lah mlruns/
```

---

## 🎯 Success Criteria

### ✅ Project is Ready When:

1. **Days 1-7**: Training pipeline executes end-to-end
   - [ ] Data ingestion → Features → Models
   - [ ] Best model > R² 0.86
   - [ ] MLflow tracking working

2. **Days 8-9**: Inference working
   - [ ] API responds to requests
   - [ ] Batch predictions generate correct output
   - [ ] Documentation is complete

3. **Day 10**: CI/CD automated
   - [ ] All tests pass
   - [ ] Code coverage > 85%
   - [ ] GitHub Actions configured

4. **Improvements**: Advanced features working
   - [ ] Ensemble models show improvement
   - [ ] Monitoring dashboards display metrics
   - [ ] SHAP explanations generated
   - [ ] Data quality checks automated

---

**Created**: April 8, 2026  
**Status**: ✅ Complete & Ready to Run  
**Next Steps**: Execute this guide step-by-step, testing each day before moving to the next
