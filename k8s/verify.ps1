#!/usr/bin/env pwsh
# Verification script for Day 11 Kubernetes deployment
# Run this to verify all files are created correctly

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Day 11 Kubernetes Deployment Verification" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Define expected files
$ExpectedFiles = @(
    # Base manifests
    "k8s/base/namespace.yaml",
    "k8s/base/deployment.yaml",
    "k8s/base/service.yaml",
    "k8s/base/configmap.yaml",
    "k8s/base/secret.yaml",
    "k8s/base/ingress.yaml",
    "k8s/base/hpa.yaml",
    "k8s/base/pvc.yaml",
    "k8s/base/rbac.yaml",
    "k8s/base/kustomization.yaml",
    
    # Overlays
    "k8s/overlays/prod/kustomization.yaml",
    "k8s/overlays/staging/kustomization.yaml",
    "k8s/overlays/dev/kustomization.yaml",
    
    # Scripts
    "k8s/deploy.ps1",
    "k8s/deploy.sh",
    "k8s/README.md",
    
    # Documentation
    "MD/DAY11_KUBERNETES_DEPLOYMENT.md",
    "MD/DAY11_COMPLETION_SUMMARY.md",
    "MD/DAY11_STATUS_UPDATE.md"
)

# Check files
Write-Host "Checking files..." -ForegroundColor Yellow
$FilesFound = 0
$FilesMissing = 0

foreach ($File in $ExpectedFiles) {
    $FullPath = Join-Path -Path (Get-Location) -ChildPath $File
    if (Test-Path $FullPath -PathType Leaf) {
        Write-Host "✓ $File" -ForegroundColor Green
        $FilesFound++
    } else {
        Write-Host "✗ $File - NOT FOUND" -ForegroundColor Red
        $FilesMissing++
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Summary" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Files Found: $FilesFound" -ForegroundColor Green
Write-Host "Files Missing: $FilesMissing" -ForegroundColor $(if ($FilesMissing -eq 0) { "Green" } else { "Red" })
Write-Host ""

# Check file sizes
Write-Host "File Sizes:" -ForegroundColor Yellow
$TotalSize = 0

foreach ($File in $ExpectedFiles) {
    $FullPath = Join-Path -Path (Get-Location) -ChildPath $File
    if (Test-Path $FullPath -PathType Leaf) {
        $Size = (Get-Item $FullPath).Length
        $SizeKB = [math]::Round($Size / 1KB, 2)
        $TotalSize += $Size
        Write-Host "  $File - $SizeKB KB"
    }
}

$TotalSizeKB = [math]::Round($TotalSize / 1KB, 2)
$TotalSizeMB = [math]::Round($TotalSize / 1MB, 2)
Write-Host "Total Size: $TotalSizeKB KB ($TotalSizeMB MB)" -ForegroundColor Cyan
Write-Host ""

# Verify YAML syntax
Write-Host "Verifying YAML files..." -ForegroundColor Yellow

$YamlFiles = @(
    "k8s/base/deployment.yaml",
    "k8s/base/service.yaml"
)

foreach ($YamlFile in $YamlFiles) {
    $FullPath = Join-Path -Path (Get-Location) -ChildPath $YamlFile
    if (Test-Path $FullPath) {
        try {
            $Content = Get-Content $FullPath -Raw
            # Basic YAML validation
            if ($Content -match "^apiVersion:" -and $Content -match "^kind:") {
                Write-Host "✓ $YamlFile - Valid YAML structure" -ForegroundColor Green
            } else {
                Write-Host "✗ $YamlFile - Invalid YAML structure" -ForegroundColor Red
            }
        } catch {
            Write-Host "✗ $YamlFile - Error reading file" -ForegroundColor Red
        }
    }
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "Verification Complete!" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan

if ($FilesMissing -eq 0) {
    Write-Host "✅ All files present and accounted for!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Yellow
    Write-Host "1. Review k8s/README.md for quick start guide"
    Write-Host "2. Run deployment script: .\k8s\deploy.ps1"
    Write-Host "3. Or read full guide: MD/DAY11_KUBERNETES_DEPLOYMENT.md"
} else {
    Write-Host "❌ Some files are missing. Please create them first." -ForegroundColor Red
}

Write-Host ""
