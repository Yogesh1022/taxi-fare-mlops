@echo off
REM Setup script for Windows development

echo.
echo 🚀 Setting up Taxi Fare Prediction MLOps System...
echo.

REM Check Python version
python --version
echo ✓ Python version checked
echo.

REM Create logs directory
if not exist logs mkdir logs
echo ✓ Created logs directory
echo.

REM Install in development mode
echo 📦 Installing dependencies...
python -m pip install --upgrade pip setuptools wheel
python -m pip install -e ".[dev]"
echo ✓ Dependencies installed
echo.

REM Setup pre-commit hooks
echo 🔧 Setting up pre-commit hooks...
pre-commit install
echo ✓ Pre-commit hooks installed
echo.

REM Create .env from template
if not exist .env (
    copy .env.example .env
    echo ✓ Created .env from template
) else (
    echo ✓ .env already exists
)
echo.

REM Initialize data directories
echo 📁 Initializing data directories...
if not exist data\raw mkdir data\raw
if not exist data\interim mkdir data\interim
if not exist data\processed mkdir data\processed
if not exist data\external mkdir data\external
if not exist models mkdir models
if not exist mlruns mkdir mlruns
echo ✓ Data directories initialized
echo.

echo ✅ Setup complete!
echo.
echo Next steps:
echo 1. Activate environment: .venv\Scripts\activate
echo 2. Verify: python -m src.models.train --help
echo 3. Run tests: make test
echo 4. View commands: make help
echo.
