#!/bin/bash
# Kubernetes Deployment Script (Linux/MacOS)
# Day 11: Kubernetes Deployment Tasks
# Author: GitHub Copilot
# Date: April 11, 2026

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Script header
echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}Kubernetes Deployment Script${NC}"
echo -e "${BLUE}Project: Taxi Fare Prediction${NC}"
echo -e "${BLUE}Date: $(date +'%Y-%m-%d %H:%M:%S')${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Function to check prerequisites
check_prerequisite() {
    local cmd=$1
    local name=$2
    
    echo -e "${BLUE}Checking $name...${NC}"
    if command -v $cmd &> /dev/null; then
        echo -e "${GREEN}✓ $name found${NC}"
        return 0
    else
        echo -e "${RED}✗ $name NOT found - Please install it first${NC}"
        return 1
    fi
}

# Function to deploy to environment
deploy_environment() {
    local env=$1
    local action=${2:-apply}
    
    echo ""
    echo -e "${BLUE}=== Deploying to $env ===${NC}"
    
    local kustomize_path="k8s/overlays/$env"
    
    if [ ! -d "$kustomize_path" ]; then
        echo -e "${RED}✗ Kustomization path not found: $kustomize_path${NC}"
        return 1
    fi
    
    if [ "$action" == "apply" ]; then
        echo -e "${BLUE}Applying manifests to $env...${NC}"
        kubectl kustomize "$kustomize_path" | kubectl apply -f -
    elif [ "$action" == "dry-run" ]; then
        echo -e "${YELLOW}Dry-run: Would apply the following manifests...${NC}"
        kubectl kustomize "$kustomize_path" | kubectl apply --dry-run=client -f -
    fi
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Successfully deployed to $env${NC}"
        return 0
    else
        echo -e "${RED}✗ Deployment failed${NC}"
        return 1
    fi
}

# Function to check status
check_status() {
    local namespace=${1:-taxi-fare-prod}
    
    echo ""
    echo -e "${BLUE}=== Deployment Status for $namespace ===${NC}"
    
    echo -e "\n${YELLOW}Deployments:${NC}"
    kubectl get deployments -n "$namespace" -o wide
    
    echo -e "\n${YELLOW}Pods:${NC}"
    kubectl get pods -n "$namespace" -o wide
    
    echo -e "\n${YELLOW}Services:${NC}"
    kubectl get services -n "$namespace" -o wide
    
    echo -e "\n${YELLOW}Ingress:${NC}"
    kubectl get ingress -n "$namespace" -o wide
}

# Function to scale deployment
scale_deployment() {
    local deployment=$1
    local replicas=$2
    local namespace=${3:-taxi-fare-prod}
    
    echo ""
    echo -e "${BLUE}Scaling $deployment to $replicas replicas...${NC}"
    
    kubectl scale deployment "$deployment" -n "$namespace" --replicas="$replicas"
    
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Successfully scaled${NC}"
    else
        echo -e "${RED}✗ Scaling failed${NC}"
    fi
}

# Function to view logs
view_logs() {
    local namespace=${1:-taxi-fare-prod}
    local label_selector=${2:-app=taxi-fare-api}
    local tail=${3:-50}
    
    echo ""
    echo -e "${BLUE}=== Pod Logs ($label_selector) ===${NC}"
    
    kubectl logs -n "$namespace" -l "$label_selector" --tail="$tail" -f
}

# Function to setup port forward
port_forward() {
    local namespace=${1:-taxi-fare-prod}
    local service=${2:-taxi-fare-api}
    local local_port=${3:-8000}
    local remote_port=${4:-8000}
    
    echo ""
    echo -e "${BLUE}Setting up port forward: localhost:$local_port -> $service:$remote_port${NC}"
    
    kubectl port-forward -n "$namespace" "svc/$service" "$local_port:$remote_port"
}

# Function to show menu
show_menu() {
    echo ""
    echo -e "${BLUE}=== Deployment Options ===${NC}"
    echo "1. Deploy to Production"
    echo "2. Deploy to Staging"
    echo "3. Deploy to Development"
    echo "4. Check Status"
    echo "5. Scale Deployment"
    echo "6. View Logs"
    echo "7. Port Forward"
    echo "8. Dry-run (validate only)"
    echo "9. Exit"
    echo ""
}

# Check prerequisites
echo -e "${GREEN}Checking prerequisites...${NC}"
check_prerequisite kubectl kubectl || exit 1
check_prerequisite kustomize kustomize || echo -e "${YELLOW}Note: kubectl must have kustomize support${NC}"

echo -e "${GREEN}✓ All prerequisites met!${NC}"

# Main loop
if [ $# -eq 0 ]; then
    # Interactive mode
    while true; do
        show_menu
        read -p "Select an option (1-9): " choice
        
        case $choice in
            1)
                read -p "Do dry-run first? (yes/no): " dryrun
                if [ "$dryrun" == "yes" ]; then
                    deploy_environment prod dry-run
                    read -p "Proceed with deployment? (yes/no): " proceed
                    if [ "$proceed" == "yes" ]; then
                        deploy_environment prod apply
                    fi
                else
                    deploy_environment prod apply
                fi
                ;;
            2)
                deploy_environment staging apply
                ;;
            3)
                deploy_environment dev apply
                ;;
            4)
                read -p "Enter namespace (default: taxi-fare-prod): " ns
                ns=${ns:-taxi-fare-prod}
                check_status "$ns"
                ;;
            5)
                read -p "Enter deployment name: " deployment
                read -p "Enter number of replicas: " replicas
                read -p "Enter namespace (default: taxi-fare-prod): " ns
                ns=${ns:-taxi-fare-prod}
                scale_deployment "$deployment" "$replicas" "$ns"
                ;;
            6)
                read -p "Enter namespace (default: taxi-fare-prod): " ns
                ns=${ns:-taxi-fare-prod}
                view_logs "$ns"
                ;;
            7)
                read -p "Enter namespace (default: taxi-fare-prod): " ns
                read -p "Enter service name (default: taxi-fare-api): " svc
                read -p "Enter local port (default: 8000): " lport
                read -p "Enter remote port (default: 8000): " rport
                ns=${ns:-taxi-fare-prod}
                svc=${svc:-taxi-fare-api}
                lport=${lport:-8000}
                rport=${rport:-8000}
                port_forward "$ns" "$svc" "$lport" "$rport"
                ;;
            8)
                read -p "Enter environment (prod/staging/dev, default: prod): " env
                env=${env:-prod}
                deploy_environment "$env" dry-run
                ;;
            9)
                echo -e "${BLUE}Exiting...${NC}"
                exit 0
                ;;
            *)
                echo -e "${RED}✗ Invalid option${NC}"
                ;;
        esac
    done
else
    # Command line mode
    case $1 in
        deploy:prod)
            deploy_environment prod apply
            ;;
        deploy:staging)
            deploy_environment staging apply
            ;;
        deploy:dev)
            deploy_environment dev apply
            ;;
        status)
            check_status "${2:-taxi-fare-prod}"
            ;;
        scale)
            scale_deployment "$2" "$3" "${4:-taxi-fare-prod}"
            ;;
        logs)
            view_logs "${2:-taxi-fare-prod}"
            ;;
        portforward)
            port_forward "${2:-taxi-fare-prod}" "${3:-taxi-fare-api}" "${4:-8000}" "${5:-8000}"
            ;;
        *)
            echo -e "${RED}Unknown command: $1${NC}"
            exit 1
            ;;
    esac
fi
