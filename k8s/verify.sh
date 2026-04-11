#!/bin/bash
# Verification script for Day 11 Kubernetes deployment
# Run this to verify all files are created correctly

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${CYAN}================================${NC}"
echo -e "${CYAN}Day 11 Kubernetes Deployment Verification${NC}"
echo -e "${CYAN}================================${NC}"
echo ""

# Expected files
files=(
    # Base manifests
    "k8s/base/namespace.yaml"
    "k8s/base/deployment.yaml"
    "k8s/base/service.yaml"
    "k8s/base/configmap.yaml"
    "k8s/base/secret.yaml"
    "k8s/base/ingress.yaml"
    "k8s/base/hpa.yaml"
    "k8s/base/pvc.yaml"
    "k8s/base/rbac.yaml"
    "k8s/base/kustomization.yaml"
    
    # Overlays
    "k8s/overlays/prod/kustomization.yaml"
    "k8s/overlays/staging/kustomization.yaml"
    "k8s/overlays/dev/kustomization.yaml"
    
    # Scripts
    "k8s/deploy.ps1"
    "k8s/deploy.sh"
    "k8s/README.md"
    
    # Documentation
    "MD/DAY11_KUBERNETES_DEPLOYMENT.md"
    "MD/DAY11_COMPLETION_SUMMARY.md"
    "MD/DAY11_STATUS_UPDATE.md"
)

# Check files
echo -e "${YELLOW}Checking files...${NC}"
files_found=0
files_missing=0

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "${GREEN}✓${NC} $file"
        ((files_found++))
    else
        echo -e "${RED}✗${NC} $file - NOT FOUND"
        ((files_missing++))
    fi
done

echo ""
echo -e "${CYAN}================================${NC}"
echo -e "${CYAN}Summary${NC}"
echo -e "${CYAN}================================${NC}"
echo -e "Files Found: ${GREEN}$files_found${NC}"
if [ $files_missing -eq 0 ]; then
    echo -e "Files Missing: ${GREEN}$files_missing${NC}"
else
    echo -e "Files Missing: ${RED}$files_missing${NC}"
fi
echo ""

# Check file sizes
echo -e "${YELLOW}File Sizes:${NC}"
total_size=0

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        size=$(stat -f%z "$file" 2>/dev/null || stat -c%s "$file" 2>/dev/null)
        size_kb=$((size / 1024))
        total_size=$((total_size + size))
        echo "  $file - ${size_kb}KB"
    fi
done

total_size_kb=$((total_size / 1024))
total_size_mb=$((total_size / 1024 / 1024))
echo -e "${CYAN}Total Size: ${total_size_kb}KB (${total_size_mb}MB)${NC}"
echo ""

# Verify YAML syntax
echo -e "${YELLOW}Verifying YAML files...${NC}"

yaml_files=(
    "k8s/base/deployment.yaml"
    "k8s/base/service.yaml"
)

for yaml_file in "${yaml_files[@]}"; do
    if [ -f "$yaml_file" ]; then
        if grep -q "^apiVersion:" "$yaml_file" && grep -q "^kind:" "$yaml_file"; then
            echo -e "${GREEN}✓${NC} $yaml_file - Valid YAML structure"
        else
            echo -e "${RED}✗${NC} $yaml_file - Invalid YAML structure"
        fi
    fi
done

echo ""
echo -e "${CYAN}================================${NC}"
echo -e "${CYAN}Verification Complete!${NC}"
echo -e "${CYAN}================================${NC}"

if [ $files_missing -eq 0 ]; then
    echo -e "${GREEN}✅ All files present and accounted for!${NC}"
    echo ""
    echo -e "${YELLOW}Next steps:${NC}"
    echo "1. Review k8s/README.md for quick start guide"
    echo "2. Run deployment script: ./k8s/deploy.sh"
    echo "3. Or read full guide: MD/DAY11_KUBERNETES_DEPLOYMENT.md"
else
    echo -e "${RED}❌ Some files are missing. Please create them first.${NC}"
fi

echo ""
