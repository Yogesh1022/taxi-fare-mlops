# Kubernetes Deployment Scripts
# Day 11: Kubernetes Deployment Tasks
# Author: GitHub Copilot
# Date: April 11, 2026

# Prerequisites:
# - kubectl installed and configured
# - Kustomize installed (or kubectl with kustomize support)
# - Docker image pushed to registry
# - Kubernetes cluster accessible

# Colors for output
$Colors = @{
    Success = @{ ForegroundColor = 'Green'; BackgroundColor = 'Black' }
    Info    = @{ ForegroundColor = 'Cyan'; BackgroundColor = 'Black' }
    Warning = @{ ForegroundColor = 'Yellow'; BackgroundColor = 'Black' }
    Error   = @{ ForegroundColor = 'Red'; BackgroundColor = 'Black' }
}

# Script header
Write-Host "================================" @Colors.Info
Write-Host "Kubernetes Deployment Script" @Colors.Info
Write-Host "Project: Taxi Fare Prediction" @Colors.Info
Write-Host "Date: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')" @Colors.Info
Write-Host "================================" @Colors.Info
Write-Host ""

# Function to check prerequisites
function Test-Prerequisites {
    param (
        [string]$Executable,
        [string]$Name
    )
    
    Write-Host "Checking $Name..." @Colors.Info
    if (Get-Command $Executable -ErrorAction SilentlyContinue) {
        Write-Host "✓ $Name found" @Colors.Success
        return $true
    } else {
        Write-Host "✗ $Name NOT found - Please install it first" @Colors.Error
        return $false
    }
}

# Function to apply manifests by environment
function Deploy-Environment {
    param (
        [string]$Environment = "prod",
        [string]$Action = "apply"
    )
    
    Write-Host ""
    Write-Host "=== Deploying to $Environment ===" @Colors.Info
    
    $KustomizePath = "k8s/overlays/$Environment"
    
    if (-not (Test-Path $KustomizePath)) {
        Write-Host "✗ Kustomization path not found: $KustomizePath" @Colors.Error
        return $false
    }
    
    try {
        # Build manifests using Kustomize
        Write-Host "Building manifests for $Environment..." @Colors.Info
        $Manifests = kubectl kustomize $KustomizePath
        
        if ($LASTEXITCODE -ne 0) {
            Write-Host "✗ Failed to build manifests" @Colors.Error
            return $false
        }
        
        # Apply or validate
        if ($Action -eq "apply") {
            Write-Host "Applying manifests to $Environment..." @Colors.Info
            $Manifests | kubectl apply -f -
        } elseif ($Action -eq "dry-run") {
            Write-Host "Dry-run: Would apply the following manifests..." @Colors.Warning
            $Manifests | kubectl apply --dry-run=client -f -
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Successfully deployed to $Environment" @Colors.Success
            return $true
        } else {
            Write-Host "✗ Deployment failed" @Colors.Error
            return $false
        }
    }
    catch {
        Write-Host "✗ Error during deployment: $_" @Colors.Error
        return $false
    }
}

# Function to check deployment status
function Get-DeploymentStatus {
    param (
        [string]$Namespace = "taxi-fare-prod"
    )
    
    Write-Host ""
    Write-Host "=== Deployment Status for $Namespace ===" @Colors.Info
    
    try {
        kubectl get deployments -n $Namespace -o wide
        kubectl get pods -n $Namespace -o wide
        kubectl get services -n $Namespace -o wide
        kubectl get ingress -n $Namespace -o wide
    }
    catch {
        Write-Host "✗ Error fetching status: $_" @Colors.Error
    }
}

# Function to scale deployment
function Set-DeploymentReplicas {
    param (
        [string]$Deployment = "taxi-fare-api",
        [int]$Replicas = 3,
        [string]$Namespace = "taxi-fare-prod"
    )
    
    Write-Host ""
    Write-Host "Scaling $Deployment to $Replicas replicas..." @Colors.Info
    
    kubectl scale deployment $Deployment -n $Namespace --replicas=$Replicas
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✓ Successfully scaled" @Colors.Success
    } else {
        Write-Host "✗ Scaling failed" @Colors.Error
    }
}

# Function to view logs
function Get-PodLogs {
    param (
        [string]$Namespace = "taxi-fare-prod",
        [string]$LabelSelector = "app=taxi-fare-api",
        [int]$TailLines = 50
    )
    
    Write-Host ""
    Write-Host "=== Pod Logs ($LabelSelector) ===" @Colors.Info
    
    try {
        kubectl logs -n $Namespace -l $LabelSelector --tail=$TailLines -f
    }
    catch {
        Write-Host "✗ Error fetching logs: $_" @Colors.Error
    }
}

# Function to port forward
function Start-PortForward {
    param (
        [string]$Namespace = "taxi-fare-prod",
        [string]$ServiceName = "taxi-fare-api",
        [int]$LocalPort = 8000,
        [int]$RemotePort = 8000
    )
    
    Write-Host ""
    Write-Host "Setting up port forward: localhost:$LocalPort -> $ServiceName:$RemotePort" @Colors.Info
    
    try {
        kubectl port-forward -n $Namespace svc/$ServiceName $LocalPort:$RemotePort
    }
    catch {
        Write-Host "✗ Port forward failed: $_" @Colors.Error
    }
}

# Function to delete deployment
function Remove-Deployment {
    param (
        [string]$Environment = "prod"
    )
    
    Write-Host ""
    Write-Host "WARNING: This will delete all resources in $Environment environment!" @Colors.Warning
    $Confirm = Read-Host "Are you sure? (yes/no)"
    
    if ($Confirm -eq "yes") {
        $KustomizePath = "k8s/overlays/$Environment"
        kubernetes kustomize $KustomizePath | kubectl delete -f -
        Write-Host "✓ Resources deleted" @Colors.Success
    } else {
        Write-Host "Cancelled" @Colors.Warning
    }
}

# Main menu
function Show-Menu {
    Write-Host ""
    Write-Host "=== Deployment Options ===" @Colors.Info
    Write-Host "1. Deploy to Production"
    Write-Host "2. Deploy to Staging"
    Write-Host "3. Deploy to Development"
    Write-Host "4. Check Status"
    Write-Host "5. Scale Deployment"
    Write-Host "6. View Logs"
    Write-Host "7. Port Forward"
    Write-Host "8. Dry-run (validate only)"
    Write-Host "9. Exit"
    Write-Host ""
}

# Check prerequisites
$PrerequisitesMet = $true
$PrerequisitesMet = $PrerequisitesMet -and (Test-Prerequisites "kubectl" "kubectl")
$PrerequisitesMet = $PrerequisitesMet -and (Test-Prerequisites "kustomize" "kustomize (or kubectl with kustomize)")

if (-not $PrerequisitesMet) {
    Write-Host ""
    Write-Host "✗ Prerequisites not met. Please install required tools." @Colors.Error
    exit 1
}

Write-Host "✓ All prerequisites met!" @Colors.Success

# Interactive menu
while ($true) {
    Show-Menu
    $Choice = Read-Host "Select an option (1-9)"
    
    switch ($Choice) {
        "1" {
            $DryRun = Read-Host "Do dry-run first? (yes/no)"
            if ($DryRun -eq "yes") {
                Deploy-Environment -Environment "prod" -Action "dry-run"
                $Proceed = Read-Host "Proceed with deployment? (yes/no)"
                if ($Proceed -eq "yes") {
                    Deploy-Environment -Environment "prod" -Action "apply"
                }
            } else {
                Deploy-Environment -Environment "prod" -Action "apply"
            }
        }
        "2" {
            Deploy-Environment -Environment "staging" -Action "apply"
        }
        "3" {
            Deploy-Environment -Environment "dev" -Action "apply"
        }
        "4" {
            $Namespace = Read-Host "Enter namespace (default: taxi-fare-prod)"
            if ([string]::IsNullOrWhiteSpace($Namespace)) { $Namespace = "taxi-fare-prod" }
            Get-DeploymentStatus -Namespace $Namespace
        }
        "5" {
            $Deployment = Read-Host "Enter deployment name (default: taxi-fare-api)"
            $Replicas = Read-Host "Enter number of replicas (default: 3)"
            $Namespace = Read-Host "Enter namespace (default: taxi-fare-prod)"
            
            if ([string]::IsNullOrWhiteSpace($Deployment)) { $Deployment = "taxi-fare-api" }
            if ([string]::IsNullOrWhiteSpace($Replicas)) { $Replicas = 3 }
            if ([string]::IsNullOrWhiteSpace($Namespace)) { $Namespace = "taxi-fare-prod" }
            
            Set-DeploymentReplicas -Deployment $Deployment -Replicas $Replicas -Namespace $Namespace
        }
        "6" {
            $Namespace = Read-Host "Enter namespace (default: taxi-fare-prod)"
            if ([string]::IsNullOrWhiteSpace($Namespace)) { $Namespace = "taxi-fare-prod" }
            Get-PodLogs -Namespace $Namespace
        }
        "7" {
            $Namespace = Read-Host "Enter namespace (default: taxi-fare-prod)"
            $Service = Read-Host "Enter service name (default: taxi-fare-api)"
            $LocalPort = Read-Host "Enter local port (default: 8000)"
            $RemotePort = Read-Host "Enter remote port (default: 8000)"
            
            if ([string]::IsNullOrWhiteSpace($Namespace)) { $Namespace = "taxi-fare-prod" }
            if ([string]::IsNullOrWhiteSpace($Service)) { $Service = "taxi-fare-api" }
            if ([string]::IsNullOrWhiteSpace($LocalPort)) { $LocalPort = 8000 }
            if ([string]::IsNullOrWhiteSpace($RemotePort)) { $RemotePort = 8000 }
            
            Start-PortForward -Namespace $Namespace -ServiceName $Service -LocalPort $LocalPort -RemotePort $RemotePort
        }
        "8" {
            $Environment = Read-Host "Enter environment (prod/staging/dev, default: prod)"
            if ([string]::IsNullOrWhiteSpace($Environment)) { $Environment = "prod" }
            Deploy-Environment -Environment $Environment -Action "dry-run"
        }
        "9" {
            Write-Host "Exiting..." @Colors.Info
            exit 0
        }
        default {
            Write-Host "✗ Invalid option" @Colors.Error
        }
    }
}
