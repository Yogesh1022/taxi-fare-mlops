# Taxi Fare Prediction - MLOps System

A complete end-to-end MLOps system for predicting NYC taxi fare amounts using regression models. This project demonstrates production-grade machine learning practices including data versioning, experiment tracking, model deployment, and monitoring.

## 🎯 Objective

Predict the `total_amount` (taxi fare) from NYC taxi trip data using multiple ML models with full MLOps infrastructure.

## 📊 Project Status

**Day 1 - Project Bootstrap (Complete)**
- ✅ Repository structure initialized  
- ✅ Environment reproducibility (pyproject.toml, requirements.txt)
- ✅ Docker containerization
- ✅ Makefile automation
- ✅ CI/CD workflow (GitHub Actions)

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Docker & Docker Compose (optional)
- Git

### Setup

```bash
# Clone repository
git clone https://github.com/your-org/taxi-fare-prediction.git
cd taxi-fare-prediction

# Setup environment (creates venv and installs dependencies)
make setup

# Verify installation
python -m src.models.train --help
```

**Expected time:** <15 minutes on fresh machine

## 📁 Project Structure

```
mlops-taxi-fare-prediction/
├── data/
│   ├── raw/           # Original, immutable data
│   ├── interim/       # Intermediate processed data
│   ├── processed/     # Final features for modeling
│   └── external/      # Third-party data sources
├── notebooks/         # Jupyter notebooks (research)
├── src/
│   ├── data/          # Data loading, validation, splitting
│   ├── features/      # Feature transformers and pipelines
│   ├── models/        # Model training, tuning, evaluation
│   ├── deployment/    # API and dashboard code
│   └── utils/         # Shared utilities and config
├── pipelines/         # Orchestration scripts
├── tests/
│   ├── unit/          # Unit tests
│   ├── integration/   # End-to-end tests
│   └── contract/      # API contract tests
├── mlops/
│   ├── mlflow/        # Experiment tracking
│   ├── monitoring/    # Production monitoring
│   └── governance/    # Model governance
├── docker/            # Dockerfile and Docker Compose
├── .github/workflows/ # GitHub Actions CI/CD
├── pyproject.toml     # Python project metadata and dependencies
├── requirements.txt   # Pip dependencies (for Docker)
├── Makefile           # Automation commands
└── README.md          # This file
```

## 🛠️ Commands

All commands use `make`. See available commands:

```bash
make help
```

### Common Workflows

```bash
# Setup environment
make setup

# Run code quality checks
make lint

# Auto-format code
make format

# Run tests
make test
make test-unit
make test-cov        # with coverage report

# Training
make train

# Start services
make serve           # FastAPI server
make dashboard       # Streamlit dashboard

# Docker
make docker-build    # Build images
make docker-up       # Start services
make docker-down     # Stop services

# Cleanup
make clean           # Remove cache, build artifacts
```

## 📦 Dependencies

### Core ML Stack
- **pandas, numpy**: Data manipulation
- **scikit-learn, xgboost, lightgbm**: Models
- **joblib**: Model serialization

### MLOps Tools
- **MLflow**: Experiment tracking & model registry
- **Optuna**: Hyperparameter optimization
- **DVC**: Data versioning (future)

### API & UI
- **FastAPI**: Inference API
- **Streamlit**: Dashboard
- **Pydantic**: Data validation

### Infrastructure
- **Docker**: Containerization
- **GitHub Actions**: CI/CD automation

### Development
- **pytest**: Testing framework
- **ruff, black, isort**: Code quality
- **mypy**: Type checking

See `pyproject.toml` for complete version specs.

## ✅ Acceptance Criteria (Day 1)

- [x] New machine can run project in <15 minutes → `make setup` works
- [x] Container builds successfully
- [x] `python -m src.models.train` executes without environment errors
- [x] Makefile provides setup, lint, test, train, serve commands
- [x] GitHub Actions CI runs on PRs

## 📅 Implementation Roadmap

| Day | Task | Status |
|-----|------|--------|
| 1 | Project Bootstrap | ✅ Done |
| 2 | Data Versioning & Contracts | ⏳ Next |
| 3 | Feature Engineering Pipeline | ⏳ |
| 4 | Multi-Model Training | ⏳ |
| 5 | Hyperparameter Optimization | ⏳ |
| 6 | Experiment Tracking & Model Registry | ⏳ |
| 7 | Testing & Quality Gates | ⏳ |
| 8 | Inference API | ⏳ |
| 9 | Dashboard & Batch Prediction | ⏳ |
| 10 | CI Pipeline Automation | ⏳ |
| 11 | CD & Deployment | ⏳ |
| 12 | Monitoring & Drift Detection | ⏳ |
| 13 | Governance & Audit Trails | ⏳ |
| 14 | Documentation & Handoff | ⏳ |

## 🧪 Testing

```bash
# Run all tests
make test

# Run specific test category
make test-unit          # Unit tests only
make test-integration   # Integration tests

# With coverage
make test-cov
```

Tests are located in `tests/` with categories:
- `unit/`: Individual component tests
- `integration/`: End-to-end workflow tests
- `contract/`: API schema validation tests

## 📝 Configuration

Key configuration files:

- `.python-version`: Python version (3.10.13)
- `pyproject.toml`: Project metadata, dependencies, tool config
- `.env`: Local environment variables (create as needed)
- `docker-compose.yml`: Service orchestration

## 🐳 Docker Usage

Build and run services:

```bash
make docker-build
make docker-up
```

Access services:
- API: http://localhost:8000
- Dashboard: http://localhost:8501

## 🤝 Contributing

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make changes and commit: `git commit -am 'Add feature'`
3. Run checks: `make lint format test`
4. Push and create PR: `git push origin feature/your-feature`

CI will automatically run tests and linting.

## 📚 Documentation

- [Architecture Guide](docs/architecture.md) - System design
- [Runbook](docs/runbook.md) - Operations guide
- [API Contract](docs/api_contract.md) - Endpoint specifications

## 📊 Data

Place raw taxi data in `data/raw/`. Expected columns:
- `trip_distance`
- `fare_amount`
- `extra`
- `tip_amount`
- `total_amount`
- Temporal features (pickup_datetime, etc.)

## 🚦 Status Badges

![Tests](https://github.com/your-org/taxi-fare-prediction/workflows/CI%20Pipeline/badge.svg)
![Docker Builds](https://github.com/your-org/taxi-fare-prediction/actions/workflows/docker-build.yml/badge.svg)

## 📞 Contact

For questions or issues, please create a GitHub issue.

## 📄 License

MIT License - see LICENSE file for details.

---

**Next Steps:** See [Day 2 - Data Versioning](docs/day2-data-versioning.md) for the next phase.
