@echo off
REM Docker Make Wrapper - For running make commands on Windows
REM Usage: docker-make.bat lint
REM        docker-make.bat test
REM        docker-make.bat setup

setlocal enabledelayedexpansion

if "%1"=="" (
    echo Docker Make - Run make commands in Docker container
    echo.
    echo Usage: docker-make.bat ^<command^> [args...]
    echo.
    echo Examples:
    echo   docker-make.bat setup        - Install dependencies
    echo   docker-make.bat lint         - Run linting
    echo   docker-make.bat test         - Run all tests
    echo   docker-make.bat test-unit    - Run unit tests
    echo   docker-make.bat test-cov     - Run tests with coverage
    echo   docker-make.bat train        - Run training pipeline
    echo   docker-make.bat bash         - Open bash shell in container
    echo.
    exit /b 0
)

REM Check if container is running
docker ps | findstr taxi-fare-dev >nul
if errorlevel 1 (
    echo [INFO] Dev container not running. Building and starting...
    echo.
    cd docker
    docker-compose --profile dev build
    docker-compose --profile dev up -d
    cd ..
    timeout /t 3
    echo.
)

REM Handle special commands
if /i "%1"=="bash" (
    docker exec -it taxi-fare-dev /bin/bash
) else if /i "%1"=="stop" (
    echo [INFO] Stopping dev container...
    docker-compose --profile dev down
) else if /i "%1"=="build" (
    echo [INFO] Rebuilding dev container...
    cd docker
    docker-compose --profile dev build --no-cache
    docker-compose --profile dev up -d
    cd ..
) else (
    REM Run make command
    echo [INFO] Running: make %*
    echo.
    docker exec -it taxi-fare-dev make %*
)
