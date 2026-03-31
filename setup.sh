#!/bin/bash
# Setup script for local development

set -e

echo "🚀 Setting up Taxi Fare Prediction MLOps System..."

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "✓ Python version: $PYTHON_VERSION"

# Create logs directory
mkdir -p logs
echo "✓ Created logs directory"

# Install in development mode
echo "📦 Installing dependencies..."
pip install --upgrade pip setuptools wheel
pip install -e ".[dev]"
echo "✓ Dependencies installed"

# Setup git hooks
echo "🔧 Setting up pre-commit hooks..."
pre-commit install
echo "✓ Pre-commit hooks installed"

# Create .env from template
if [ ! -f .env ]; then
    cp .env.example .env
    echo "✓ Created .env from template"
fi

# Initialize data directories
echo "📁 Initializing data directories..."
mkdir -p data/raw data/interim data/processed data/external
mkdir -p models mlruns
echo "✓ Data directories initialized"

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Activate environment: source venv/bin/activate (Linux/Mac) or .venv\\Scripts\\Activate (Windows)"
echo "2. Verify: python -m src.models.train --help"
echo "3. Run tests: make test"
echo "4. View commands: make help"
