# Docker Make Wrapper for PowerShell
# Usage: .\docker-make.ps1 lint
#        .\docker-make.ps1 test
#        .\docker-make.ps1 setup

param(
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$MakeArgs
)

$container = "taxi-fare-dev"
$dockerDir = "docker"

function Show-Help {
    Write-Host "Docker Make - Run make commands in Docker container" -ForegroundColor Green
    Write-Host ""
    Write-Host "Usage: .\docker-make.ps1 <command> [args...]" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Examples:" -ForegroundColor Yellow
    Write-Host "  .\docker-make.ps1 setup        - Install dependencies"
    Write-Host "  .\docker-make.ps1 lint         - Run linting"
    Write-Host "  .\docker-make.ps1 test         - Run all tests"
    Write-Host "  .\docker-make.ps1 test-unit    - Run unit tests"
    Write-Host "  .\docker-make.ps1 test-cov     - Run tests with coverage"
    Write-Host "  .\docker-make.ps1 train        - Run training pipeline"
    Write-Host "  .\docker-make.ps1 bash         - Open bash shell in container"
    Write-Host ""
}

if ($MakeArgs.Count -eq 0) {
    Show-Help
    exit 0
}

# Check if Docker is installed
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Host "ERROR: Docker is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Docker Desktop for Windows" -ForegroundColor Yellow
    exit 1
}

# Check if container is running
$containerStatus = docker ps --filter "name=$container" --format "{{.Names}}" 2>$null

if (-not $containerStatus) {
    Write-Host "[INFO] Dev container not running. Building and starting..." -ForegroundColor Cyan
    Write-Host ""
    
    Push-Location $dockerDir
    & docker-compose --profile dev build
    & docker-compose --profile dev up -d
    Pop-Location
    
    Write-Host ""
    Start-Sleep -Seconds 3
}

# Handle special commands
$command = $MakeArgs[0]

switch ($command.ToLower()) {
    "bash" {
        Write-Host "[INFO] Opening bash shell in container..." -ForegroundColor Cyan
        & docker exec -it $container /bin/bash
    }
    "stop" {
        Write-Host "[INFO] Stopping dev container..." -ForegroundColor Cyan
        & docker-compose --profile dev down
    }
    "build" {
        Write-Host "[INFO] Rebuilding dev container..." -ForegroundColor Cyan
        Push-Location $dockerDir
        & docker-compose --profile dev build --no-cache
        & docker-compose --profile dev up -d
        Pop-Location
    }
    "logs" {
        Write-Host "[INFO] Showing container logs..." -ForegroundColor Cyan
        & docker logs -f $container
    }
    default {
        # Run make command
        $allArgs = $MakeArgs -join " "
        Write-Host "[INFO] Running: make $allArgs" -ForegroundColor Cyan
        Write-Host ""
        & docker exec -it $container make @MakeArgs
    }
}
