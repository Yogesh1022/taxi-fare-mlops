.PHONY: help setup lint format test train serve clean all

# Variables
PYTHON := python3
PIP := pip

help:
	@echo "Available commands:"
	@echo "  make setup       - Install dependencies and prepare environment"
	@echo "  make lint        - Run linting and type checking (ruff, black, isort)"
	@echo "  make format      - Auto-format code (black, isort)"
	@echo "  make test        - Run all tests"
	@echo "  make test-unit   - Run unit tests only"
	@echo "  make test-cov    - Run tests with coverage report"
	@echo "  make train       - Run training pipeline"
	@echo "  make serve       - Start API server"
	@echo "  make dashboard   - Start Streamlit dashboard"
	@echo "  make docker-build- Build Docker images"
	@echo "  make docker-up   - Start Docker services (compose)"
	@echo "  make clean       - Clean cache and build artifacts"
	@echo "  make all         - Run setup, lint, test, train"

setup:
	@echo "Installing dependencies..."
	$(PIP) install --upgrade pip
	$(PIP) install -e ".[dev]"
	@echo "Environment setup complete!"
	@echo "To verify: python -m src.models.train --help"

lint:
	@echo "Running linters..."
	ruff check .
	black --check src/ tests/ pipelines/
	isort --check-only src/ tests/ pipelines/
	@echo "Linting complete!"

format:
	@echo "Formatting code..."
	black src/ tests/ pipelines/
	isort src/ tests/ pipelines/
	ruff check --fix .
	@echo "Formatting complete!"

test:
	@echo "Running all tests..."
	pytest tests/ -v --tb=short

test-unit:
	@echo "Running unit tests..."
	pytest tests/unit/ -v -m unit

test-cov:
	@echo "Running tests with coverage..."
	pytest tests/ -v --cov=src --cov-report=html --cov-report=term-missing
	@echo "Coverage report generated in htmlcov/index.html"

train:
	@echo "Starting training pipeline..."
	$(PYTHON) -m pipelines.training_pipeline

serve:
	@echo "Starting API server on http://localhost:8000"
	uvicorn src.deployment.api:app --reload --host 0.0.0.0 --port 8000

dashboard:
	@echo "Starting Streamlit dashboard on http://localhost:8501"
	streamlit run src/deployment/dashboard.py

docker-build:
	@echo "Building Docker images..."
	docker-compose -f docker/docker-compose.yml build

docker-up:
	@echo "Starting Docker services..."
	docker-compose -f docker/docker-compose.yml up -d
	@echo "Services running. Check http://localhost:8000 (API) and http://localhost:8501 (Dashboard)"

docker-down:
	@echo "Stopping Docker services..."
	docker-compose -f docker/docker-compose.yml down

clean:
	@echo "Cleaning cache and artifacts..."
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .coverage
	@echo "Cleanup complete!"

all: setup lint test train
	@echo "Full pipeline executed successfully!"
