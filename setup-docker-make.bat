@echo off
REM Quick Start Script for Docker Make Setup
REM This script checks prerequisites and sets up everything for you

setlocal enabledelayedexpansion

echo.
echo ========================================
echo   Taxi Fare MLOps - Docker Make Setup
echo ========================================
echo.

REM Check if Docker is installed
echo [1/4] Checking Docker installation...
docker --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Docker is not installed!
    echo.
    echo Please install Docker Desktop for Windows:
    echo   https://www.docker.com/products/docker-desktop
    echo.
    echo After installation, restart your computer and run this script again.
    echo.
    pause
    exit /b 1
) else (
    for /f "tokens=*" %%i in ('docker --version') do set DOCKER_VERSION=%%i
    echo   ✓ Docker found: !DOCKER_VERSION!
)

REM Check if Docker daemon is running
echo.
echo [2/4] Checking Docker daemon...
docker ps >nul 2>&1
if errorlevel 1 (
    echo.
    echo ERROR: Docker daemon is not running!
    echo.
    echo Please start Docker Desktop and run this script again.
    echo.
    pause
    exit /b 1
) else (
    echo   ✓ Docker daemon is running
)

REM Check if in correct directory
echo.
echo [3/4] Checking project directory...
if not exist "Makefile" (
    echo.
    echo ERROR: No Makefile found in current directory!
    echo.
    echo Please run this script from the project root:
    echo   cd E:\TaxiFare MLOps
    echo.
    pause
    exit /b 1
) else (
    echo   ✓ Project files found
)

REM Build Docker image
echo.
echo [4/4] Building Docker development environment...
echo   (This may take 3-5 minutes on first run)
echo.
cd docker
docker-compose --profile dev build

if errorlevel 1 (
    echo.
    echo ERROR: Docker build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   ✓ Setup Complete!
echo ========================================
echo.
echo You can now run make commands using:
echo.
echo   From project root directory:
echo   docker-make.bat ^<command^>
echo.
echo Available commands:
echo   docker-make.bat lint          - Check code quality
echo   docker-make.bat test          - Run all tests
echo   docker-make.bat setup         - Install dependencies
echo   docker-make.bat train         - Run training pipeline
echo   docker-make.bat format        - Auto-format code
echo   docker-make.bat bash          - Open bash shell
echo   docker-make.bat stop          - Stop container
echo.
echo Quick examples:
echo   docker-make.bat lint
echo   docker-make.bat test
echo   docker-make.bat train
echo.
echo For more information, see: DOCKER_MAKE_SETUP.md
echo.
pause
