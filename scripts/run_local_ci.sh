#!/bin/bash
# Local CI Pipeline Runner
# Runs equivalent of GitHub Actions CI pipeline locally

set -e

echo "╔═══════════════════════════════════════════════════════════════╗"
echo "║          LOCAL CI PIPELINE RUNNER                            ║"
echo "║          (Equivalent to GitHub Actions ci.yml)               ║"
echo "╚═══════════════════════════════════════════════════════════════╝"

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
PASSED=0
FAILED=0

# Function to print section header
print_header() {
    echo ""
    echo "╔═══════════════════════════════════════════════════════════════╗"
    echo "║ $1"
    echo "╚═══════════════════════════════════════════════════════════════╝"
}

# Function to print test result
print_result() {
    if [ $1 -eq 0 ]; then
        echo -e "${GREEN}✅ $2 passed${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ $2 failed${NC}"
        ((FAILED++))
    fi
}

# Check prerequisites
print_header "CHECKING PREREQUISITES"

if ! command -v python &> /dev/null; then
    echo -e "${RED}❌ Python not found${NC}"
    exit 1
fi

PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
echo "✅ Python $PYTHON_VERSION"

if ! command -v pytest &> /dev/null; then
    echo -e "${YELLOW}⚠️  pytest not found, installing...${NC}"
    pip install pytest pytest-cov pytest-asyncio -q
fi

# Install dependencies if needed
if [ ! -d ".venv" ] && [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found${NC}"
    echo "ℹ️  Install dependencies with: pip install -r requirements.txt"
fi

# 1. Unit Tests with Coverage
print_header "1. RUNNING UNIT TESTS"

if pytest tests/unit/ -v --tb=short --cov=src --cov-report=term-missing; then
    print_result 0 "Unit tests"
else
    print_result 1 "Unit tests"
fi

# 2. Code Quality Checks
print_header "2. CODE QUALITY CHECKS"

# Black format check
echo "🔍 Checking code formatting with black..."
if black --check src/ tests/ pipelines/ 2>/dev/null; then
    echo -e "${GREEN}✅ Black formatting${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Black formatting issues found${NC}"
    echo "   Run: black src/ tests/ pipelines/"
    ((FAILED++))
fi

# isort check
echo "🔍 Checking import sorting with isort..."
if isort --check-only src/ tests/ pipelines/ 2>/dev/null; then
    echo -e "${GREEN}✅ isort import sorting${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  Import sorting issues found${NC}"
    echo "   Run: isort src/ tests/ pipelines/"
    ((FAILED++))
fi

# flake8 check
echo "🔍 Checking code style with flake8..."
if flake8 src/ tests/ --max-line-length=127 --count --exit-zero > /dev/null 2>&1; then
    echo -e "${GREEN}✅ flake8 code style${NC}"
    ((PASSED++))
else
    echo -e "${YELLOW}⚠️  flake8 style issues found${NC}"
    ((FAILED++))
fi

# 3. Integration Tests
print_header "3. RUNNING INTEGRATION TESTS"

if pytest tests/integration/ -v --tb=short; then
    print_result 0 "Integration tests"
else
    print_result 1 "Integration tests"
fi

# 4. Contract Tests
print_header "4. RUNNING CONTRACT TESTS"

if pytest tests/contract/ -v --tb=short; then
    print_result 0 "Contract tests"
else
    print_result 1 "Contract tests"
fi

# 5. Coverage Report
print_header "5. GENERATING COVERAGE REPORT"

if pytest tests/ --cov=src --cov-report=html --cov-report=term-missing > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Coverage report generated${NC}"
    echo "   📊 View: htmlcov/index.html"
    ((PASSED++))
else
    print_result 1 "Coverage report"
fi

# 6. Summary
print_header "CI PIPELINE SUMMARY"

echo ""
echo "Total Checks: $((PASSED + FAILED))"
echo -e "${GREEN}Passed: $PASSED${NC}"
echo -e "${RED}Failed: $FAILED${NC}"

if [ $FAILED -eq 0 ]; then
    echo ""
    echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${GREEN}║ ✅ ALL CHECKS PASSED - READY FOR DEPLOYMENT                  ║${NC}"
    echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════╝${NC}"
    exit 0
else
    echo ""
    echo -e "${RED}╔═══════════════════════════════════════════════════════════════╗${NC}"
    echo -e "${RED}║ ❌ SOME CHECKS FAILED - FIX ISSUES BEFORE PUSHING            ║${NC}"
    echo -e "${RED}╚═══════════════════════════════════════════════════════════════╝${NC}"
    exit 1
fi
