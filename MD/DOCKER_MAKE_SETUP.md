# 🐳 Docker Setup Guide for Windows - Running Make Commands

**Problem**: `make` is not available on Windows  
**Solution**: Use Docker to run make commands  

---

## ⚡ Quick Start (5 minutes)

### Option 1: Using Batch File (Simple)
```bash
# Navigate to project root
cd E:\TaxiFare MLOps

# Run any make command through Docker
docker-make.bat lint
docker-make.bat test
docker-make.bat setup
docker-make.bat train
```

### Option 2: Using PowerShell (More Flexible)
```powershell
# Navigate to project root
cd E:\TaxiFare MLOps

# Run any make command through Docker
.\docker-make.ps1 lint
.\docker-make.ps1 test
.\docker-make.ps1 setup
.\docker-make.ps1 train
```

### Option 3: Using Docker Directly
```bash
# Build development container
cd docker
docker-compose --profile dev build

# Start development container
docker-compose --profile dev up -d

# Run make command inside container
docker exec -it taxi-fare-dev make lint
docker exec -it taxi-fare-dev make test
docker exec -it taxi-fare-dev make setup

# Stop container when done
docker-compose --profile dev down
```

---

## 📋 Prerequisites

### 1. Install Docker Desktop for Windows
- Download from: https://www.docker.com/products/docker-desktop
- Install and restart your computer
- Verify installation:
```bash
docker --version
docker-compose --version
```

### 2. Enable WSL2 (Windows Subsystem for Linux 2)
- Docker Desktop on Windows requires WSL2
- Installation guide: https://docs.microsoft.com/en-us/windows/wsl/install

### 3. Verify Docker is Running
```bash
# Check if Docker daemon is active
docker ps

# Expected output: container list (may be empty)
# If you get "Cannot connect to Docker daemon", start Docker Desktop
```

---

## 🎯 Available Commands

### Using Batch File
```bash
docker-make.bat lint          # Run linting
docker-make.bat format        # Auto-format code
docker-make.bat test          # Run all tests
docker-make.bat test-unit     # Run unit tests only
docker-make.bat test-cov      # Run tests with coverage
docker-make.bat train         # Run training pipeline
docker-make.bat setup         # Install dependencies
docker-make.bat bash          # Open interactive bash shell
docker-make.bat stop          # Stop dev container
docker-make.bat build         # Rebuild dev container
```

### Using PowerShell
```powershell
.\docker-make.ps1 lint
.\docker-make.ps1 format
.\docker-make.ps1 test
.\docker-make.ps1 test-unit
.\docker-make.ps1 test-cov
.\docker-make.ps1 train
.\docker-make.ps1 setup
.\docker-make.ps1 bash
.\docker-make.ps1 stop
.\docker-make.ps1 build
```

### Using Docker Directly
```bash
# Terminal 1: Start dev container (keeps running)
cd docker
docker-compose --profile dev up -d

# Terminal 2: Run commands
docker exec -it taxi-fare-dev make lint
docker exec -it taxi-fare-dev make test
docker exec -it taxi-fare-dev make train

# Go to bash shell
docker exec -it taxi-fare-dev /bin/bash

# Stop container
docker-compose --profile dev down
```

---

## 🚀 Step-by-Step Usage

### Method 1: Batch File (Recommended for Quick Use)

```bash
# Step 1: Open PowerShell in project root
cd "E:\TaxiFare MLOps"

# Step 2: Run your make command
docker-make.bat lint

# First run will:
# 1. Build the Docker image (2-5 minutes)
# 2. Start the container
# 3. Run the make command

# Subsequent runs will be faster (container already running)

# Step 3: Stop when done
docker-make.bat stop
```

### Method 2: PowerShell Wrapper (Better Error Handling)

```powershell
# Step 1: Open PowerShell as Administrator in project root
cd "E:\TaxiFare MLOps"

# Step 2: Allow script execution (first time only)
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser

# Step 3: Run your make command
.\docker-make.ps1 test

# Step 4: View results (same as batch file method)
```

### Method 3: Full Docker Control

```bash
# Step 1: Navigate to docker directory
cd E:\TaxiFare MLOps\docker

# Step 2: Build the development image (one time)
docker-compose --profile dev build

# Step 3: Start the container (background mode)
docker-compose --profile dev up -d

# Step 4: Run commands (new terminal)
docker exec -it taxi-fare-dev make lint
docker exec -it taxi-fare-dev make test
docker exec -it taxi-fare-dev make train

# Step 5: Interactive work (optional)
docker exec -it taxi-fare-dev /bin/bash
# Now you're inside the container - run any commands

# Step 6: Stop container when done
docker-compose --profile dev down
```

---

## 📊 Mapping Make Targets to Commands

When you use the wrapper scripts/Docker, all original make commands work:

```bash
docker-make.bat setup          ← make setup
docker-make.bat lint           ← make lint
docker-make.bat format         ← make format
docker-make.bat test           ← make test
docker-make.bat test-unit      ← make test-unit
docker-make.bat test-cov       ← make test-cov
docker-make.bat train          ← make train
docker-make.bat serve          ← make serve
docker-make.bat dashboard      ← make dashboard
docker-make.bat clean          ← make clean
docker-make.bat all            ← make all
```

---

## 🐧 Container Details

### What's Inside the Dev Container?
- Python 3.10 with all dependencies
- `make` command available
- Git, curl, build tools
- All project files mounted
- Write access to local files

### Volume Mounts
```
Project files          → /app (read/write)
pytest cache           → /app/.pytest_cache
HTML coverage reports  → /app/htmlcov
MLflow runs           → /app/mlruns
Logs                  → /app/logs
```

### Network Access
- Container can access localhost
- Ports mapped to host machine
- Isolated network namespace

---

## 🐛 Troubleshooting

### Issue: "Docker is not installed"
```bash
# Solution: Install Docker Desktop
# Download: https://www.docker.com/products/docker-desktop
# After installation: restart computer and verify
docker --version
```

### Issue: "Cannot connect to Docker daemon"
```bash
# Solution: Start Docker Desktop
# Click the Docker icon in system tray or:
# Start → Docker Desktop

# Verify Docker is running:
docker ps
```

### Issue: Container won't start
```bash
# Solution 1: Check Docker logs
docker logs taxi-fare-dev

# Solution 2: Rebuild from scratch
docker-make.bat build

# Solution 3: Check disk space (Docker needs 10GB+ free)
```

### Issue: "Permission denied" when running bash
```bash
# Solution: Run PowerShell as Administrator
# Right-click PowerShell → "Run as administrator"
# Then run: .\docker-make.ps1 bash
```

### Issue: Slow Docker performance
```bash
# Solution 1: Allocate more CPU/RAM to Docker
# Docker Desktop Settings → Resources → increase CPU & Memory

# Solution 2: Check system load
docker stats

# Solution 3: Restart Docker
# Docker Desktop → Restart
```

### Issue: "Port 8000 already in use"
```bash
# Solution: Find and stop the process
# Option 1: Restart Docker
docker restart taxi-fare-api

# Option 2: Kill process on port 8000
# Use a tool like netstat or TaskManager
```

---

## 📝 Example Workflows

### Workflow 1: Run Full Test Suite
```bash
docker-make.bat test
# Runs all tests inside container
# Results displayed in terminal
# Exit code is 0 if all pass
```

### Workflow 2: Check Code Quality
```bash
docker-make.bat lint
# Runs ruff, black, isort checks
# Shows any linting errors
```

### Workflow 3: Auto-Format Code
```bash
docker-make.bat format
# Auto-formats all code files
# Updates files on your machine
```

### Workflow 4: Run Training Pipeline
```bash
docker-make.bat train
# Runs complete training pipeline
# Creates models and artifacts
# Shows progress in terminal
```

### Workflow 5: Interactive Development
```bash
docker-make.bat bash
# Opens interactive bash shell
# Type any Linux commands
# Run Python, Git, etc. directly
# Type 'exit' when done
```

---

## 🔄 Daily Workflow

### First Time Setup
```bash
# One time setup (takes 5-10 minutes)
docker-make.bat setup

# Or step by step:
docker-make.bat lint
docker-make.bat test
docker-make.bat train
```

### Daily Development
```bash
# Each day, run your commands:
docker-make.bat lint          # Check code quality
docker-make.bat test          # Run tests
docker-make.bat test-cov      # Check coverage
docker-make.bat train         # Retrain models

# When done:
docker-make.bat stop          # Stop container to free resources
```

---

## 💾 Container Persistence

### Data Persistence
- Code changes are saved immediately (mounted volumes)
- Test results and artifacts are saved
- MLflow runs are persisted
- Logs are saved to disk

### Container Removal
```bash
# Stop container (can restart)
docker-make.bat stop

# Remove container but keep image
docker rm taxi-fare-dev

# Complete cleanup (remove everything)
docker system prune -a
```

---

## 🎁 Advanced Usage

### Run Container and Keep It Running
```bash
cd docker
docker-compose --profile dev up -d
# Container stays running in background
```

### Multiple Simultaneous Commands
```bash
# Terminal 1: Start container
docker-compose --profile dev up -d

# Terminal 2: Run tests
docker exec -it taxi-fare-dev make test

# Terminal 3 (same PC, parallel): Run training
docker exec -it taxi-fare-dev make train
# Both run in parallel inside one container
```

### Custom Make Command
```bash
# If you need to run a specific make target not listed:
docker exec -it taxi-fare-dev make <your-target>
```

### View Container Logs
```bash
docker logs -f taxi-fare-dev
# Shows live container output
```

---

## 📊 Performance Tips

### Speed Up Build
```bash
# Use cached build (usually instant after first build)
docker-compose --profile dev up -d

# Force rebuild (slower, ~2 minutes)
docker-compose --profile dev build --no-cache
```

### Free Up Space
```bash
# Remove unused containers and images
docker system prune

# Remove everything (careful!)
docker system prune -a
```

### Monitor Resources
```bash
# See container resource usage
docker stats
```

---

## ✨ Summary

| Task | Command |
|------|---------|
| **Setup** | `docker-make.bat setup` |
| **Lint** | `docker-make.bat lint` |
| **Test** | `docker-make.bat test` |
| **Train** | `docker-make.bat train` |
| **Format** | `docker-make.bat format` |
| **Coverage** | `docker-make.bat test-cov` |
| **Shell** | `docker-make.bat bash` |
| **Stop** | `docker-make.bat stop` |
| **Rebuild** | `docker-make.bat build` |

---

**Setup Time**: ~5 minutes  
**Build Time (first time)**: ~3-5 minutes  
**Subsequent Commands**: <1 minute  

---

## 🎯 Next Steps

1. ✅ Install Docker Desktop
2. ✅ Verify Docker installation (`docker --version`)
3. ✅ Navigate to project: `cd E:\TaxiFare MLOps`
4. ✅ Run first command: `docker-make.bat lint`
5. ✅ Run tests: `docker-make.bat test`
6. ✅ Done! You can now use make on Windows!

---

**Last Updated**: April 8, 2026  
**Tested On**: Windows 11 with Docker Desktop 4.x  
**Status**: ✅ Ready to Use
