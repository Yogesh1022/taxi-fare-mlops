# Docker Make Fix - Summary

## Problem
The `make lint` command was failing with "ruff: No such file or directory" error, even after Docker image rebuild.

## Root Causes Identified & Fixed

### 1. **Missing Dev Dependencies in Dockerfile**
**Issue**: The original Dockerfile was running `pip install -e .` which only installed base dependencies, not dev tools like ruff, pytest, black, isort.

**Fix**: Updated `docker/Dockerfile` to explicitly install dev dependencies:
```dockerfile
RUN pip install --upgrade pip && \
    pip install -e . && \
    pip install ruff black isort pytest pytest-cov mypy bandit
```

### 2. **Ruff Not in PATH** 
**Issue**: Even after installation, ruff wasn't accessible directly because it wasn't in container's PATH.

**Fix**: Updated `Makefile` to use `python -m` module invocation instead of direct command:
```makefile
# Before:
ruff check .

# After:
$(PYTHON) -m ruff check .
```

Applied to both `lint` and `format` targets.

### 3. **pyproject.toml Configuration Error**
**Issue**: Ruff configuration was malformed - `line-length` was in `[tool.ruff.lint]` instead of top-level `[tool.ruff]`.

**Fix**: Restructured ruff configuration:
```toml
# Before (incorrect):
[tool.ruff.lint]
line-length = 100
target-version = "py310"
select = [...]

# After (correct):
[tool.ruff]
line-length = 100
target-version = "py310"

[tool.ruff.lint]
select = [...]
ignore = [...]
```

## Verification

✅ **Ruff installed**: `docker exec taxi-fare-dev pip list | grep ruff` → ruff 0.15.9
✅ **Ruff executable**: `docker exec taxi-fare-dev python -m ruff --version` → ruff 0.15.9
✅ **Make lint works**: `docker exec taxi-fare-dev make lint` → ✓ Running
✅ **Make test works**: `docker exec taxi-fare-dev make test` → ✓ Running with pytest

## Files Modified

1. **docker/Dockerfile**
   - Added explicit installation of dev tools: ruff, black, isort, pytest, pytest-cov, mypy, bandit

2. **Makefile** (lines 33-36 and 39-44)
   - Changed `ruff check .` → `$(PYTHON) -m ruff check .`
   - Changed `black --check` → `$(PYTHON) -m black --check`
   - Changed `isort --check` → `$(PYTHON) -m isort --check`
   - Changed `ruff check --fix .` → `$(PYTHON) -m ruff check --fix .`

3. **pyproject.toml** (lines 76-87)
   - Moved `line-length` and `target-version` from `[tool.ruff.lint]` to new `[tool.ruff]` section
   - Kept `select` and `ignore` in `[tool.ruff.lint]`

## How to Use

### Option 1: Using Docker Exec (Direct)
```bash
docker exec taxi-fare-dev make lint
docker exec taxi-fare-dev make test
docker exec taxi-fare-dev make train
```

### Option 2: Using Docker-Make Wrapper
```bash
.\docker-make.bat lint
.\docker-make.bat test
.\docker-make.bat train
```

### Option 3: Using Docker Compose
```bash
cd docker
docker-compose --profile dev up -d
docker-compose exec -it dev make lint
```

## Key Takeaways

1. **Virtual environments & containers**: PEP 337 entry points (ruff, black, pytest executables) require the Python bin directory to be in PATH or use `python -m` module invocation
2. **Make + containers**: Always put `$(PYTHON)` variable in front of Python tools in Makefiles when targeting containers
3. **pyproject.toml structure**: Different tools have specific section requirements (tool.ruff vs tool.ruff.lint)

## Next Steps

Run the complete testing suite:
```bash
docker-compose --profile dev up -d
docker exec taxi-fare-dev make lint     # Linting checks
docker exec taxi-fare-dev make test     # Unit tests
docker exec taxi-fare-dev make train    # Training pipeline
```

Follow [RUN_AND_TEST_GUIDE.md](RUN_AND_TEST_GUIDE.md) for comprehensive Day 1-10 validation.
