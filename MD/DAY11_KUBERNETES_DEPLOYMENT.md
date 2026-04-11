# 🚀 Kubernetes Deployment Guide - Day 11

**Status**: ✅ Complete  
**Date**: April 11, 2026  
**Project**: Taxi Fare Prediction - MLOps  
**Task**: Kubernetes Deployment Setup

---

## 📖 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [File Structure](#file-structure)
5. [Quick Start](#quick-start)
6. [Deployments](#deployments)
7. [Services](#services)
8. [Ingress](#ingress)
9. [Autoscaling](#autoscaling)
10. [Storage](#storage)
11. [RBAC](#rbac)
12. [Troubleshooting](#troubleshooting)
13. [Best Practices](#best-practices)

---

## 📋 Overview

This Day 11 task implements complete Kubernetes deployment for the Taxi Fare Prediction service with:

✅ **Multi-environment setup**: Production, Staging, Development  
✅ **High availability**: 3-10 replicas with auto-scaling  
✅ **Load balancing**: Service mesh ready  
✅ **Persistent storage**: Models and data volumes  
✅ **Monitoring ready**: Prometheus metrics and logging  
✅ **Security**: RBAC, secrets management, network policies  
✅ **Ingress**: TLS termination and routing  

---

## 🏗️ Architecture

### Components

```
┌─────────────────────────────────────────────────────┐
│                    Kubernetes Cluster               │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │          Ingress (NGINX)                     │  │
│  │  - TLS Termination                           │  │
│  │  - Load Distribution                         │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                  │
│  ┌──────────────▼──────────────────────────────┐  │
│  │       Service (ClusterIP + Headless)        │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                  │
│  ┌──────────────▼──────────────────────────────┐  │
│  │         Deployment (3-10 Replicas)          │  │
│  │  ┌────────────────────────────────────────┐ │  │
│  │  │ Pod 1 (taxi-fare-api container)        │ │  │
│  │  │ - FastAPI app                          │ │  │
│  │  │ - Prometheus metrics                   │ │  │
│  │  │ - Health checks                        │ │  │
│  │  └────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────┐ │  │
│  │  │ Pod 2 (taxi-fare-api container)        │ │  │
│  │  └────────────────────────────────────────┘ │  │
│  │  ┌────────────────────────────────────────┐ │  │
│  │  │ Pod 3 (taxi-fare-api container)        │ │  │
│  │  └────────────────────────────────────────┘ │  │
│  └──────────────┬───────────────────────────────┘  │
│                 │                                  │
│  ┌──────────────▼──────────────────────────────┐  │
│  │   HPA (Scales 3-10 based on metrics)        │  │
│  │  - CPU Utilization: 70%                     │  │
│  │  - Memory Utilization: 80%                  │  │
│  │  - Custom Metrics: req/sec, queue depth     │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │          ConfigMaps & Secrets                │  │
│  │  - Application Config                        │  │
│  │  - Database Credentials                      │  │
│  │  - API Keys                                  │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │    Persistent Volumes & Claims               │  │
│  │  - Models Volume (ReadOnlyMany)              │  │
│  │  - MLflow Volume (ReadWriteOnce)             │  │
│  │  - Logs Volume (EmptyDir)                    │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

### Data Flow

```
Internet Request
      │
      ▼
  Ingress (NGINX)
      │
      ▼
  Service (Load Balance)
      │
      ▼
  Pods (3-10 replicas)
      │
      ▼
  Persistent Storage
```

---

## ✅ Prerequisites

### Required Software
- **kubectl** (1.24+) - Kubernetes CLI
- **kustomize** (5.0+) - Configuration management
- **Docker** - Container runtime
- **kubectly** (optional) - Context switcher

### Required Access
- Kubernetes cluster (1.24+)
- Context configured (production, staging, development)
- Storage provisioner (for PVCs)
- Ingress controller (NGINX)
- Image registry access

### System Requirements
- Cluster nodes: 2+ with 2 cores each minimum
- Storage: 30GB for models and MLflow
- Network: 10x 1 Gbps bandwidth

### Permissions
- Create namespaces
- Create deployments, services, ingress
- Create persistent volumes/claims
- Create service accounts and RBAC

---

## 📁 File Structure

```
k8s/
├── base/                          # Base manifests
│   ├── namespace.yaml             # Namespace definitions
│   ├── deployment.yaml            # API & MLflow deployments
│   ├── service.yaml               # ClusterIP, Headless services
│   ├── configmap.yaml             # ConfigMaps for config
│   ├── secret.yaml                # Secrets for credentials
│   ├── hpa.yaml                   # Horizontal Pod Autoscaler
│   ├── pvc.yaml                   # Persistent Volumes & Claims
│   ├── ingress.yaml               # Ingress configuration
│   ├── rbac.yaml                  # RBAC & ServiceAccounts
│   └── kustomization.yaml         # Base kustomization
│
├── overlays/                      # Environment-specific overrides
│   ├── prod/                      # Production (5 replicas, high resources)
│   │   └── kustomization.yaml
│   ├── staging/                   # Staging (2 replicas, medium resources)
│   │   └── kustomization.yaml
│   └── dev/                       # Development (1 replica, minimal resources)
│       └── kustomization.yaml
│
├── deploy.ps1                     # Deployment script (PowerShell)
├── deploy.sh                      # Deployment script (Bash)
└── README.md                      # This file
```

---

## 🚀 Quick Start

### 1. **Setup Cluster Context**

```bash
# List available contexts
kubectl config get-contexts

# Switch to cluster
kubectl config use-context my-cluster

# Verify connection
kubectl cluster-info
```

### 2. **Deploy to Production**

```powershell
# PowerShell (Windows)
cd k8s
.\deploy.ps1

# Select: 1 (Deploy to Production)
# Then: Select "yes" for dry-run first
```

```bash
# Bash (Linux/MacOS)
cd k8s
chmod +x deploy.sh
./deploy.sh

# Select: 1 (Deploy to Production)
# Then: Select "yes" for dry-run first
```

### 3. **Verify Deployment**

```bash
# Check namespaces
kubectl get namespaces

# Check production deployment
kubectl get all -n taxi-fare-prod

# Check pods
kubectl get pods -n taxi-fare-prod -o wide

# Check services
kubectl get services -n taxi-fare-prod

# Check ingress
kubectl get ingress -n taxi-fare-prod
```

### 4. **Access Application**

```bash
# Get Ingress IP (if using LoadBalancer)
kubectl get ingress -n taxi-fare-prod

# Port forward locally (if no Ingress IP)
kubectl port-forward -n taxi-fare-prod svc/taxi-fare-api 8000:8000

# Access API
curl http://localhost:8000/docs
```

---

## 📦 Deployments

### API Deployment: `taxi-fare-api`

**File**: `base/deployment.yaml`

**Specifications**:
- **Container Image**: `taxi-fare-ml:latest`
- **Port**: 8000 (HTTP) + 8001 (Metrics)
- **Resources**: 
  - Requests: 500m CPU, 512Mi Memory
  - Limits: 1000m CPU, 1Gi Memory
- **Replicas**: 3 (prod), 2 (staging), 1 (dev)
- **Strategy**: RollingUpdate (maxSurge: 1, maxUnavailable: 0)

**Health Checks**:
```yaml
Liveness Probe:
  - Path: /health
  - Initial Delay: 30s
  - Period: 10s
  - Timeout: 5s
  - Failure Threshold: 3

Readiness Probe:
  - Path: /ready
  - Initial Delay: 10s
  - Period: 5s
  - Timeout: 3s
  - Failure Threshold: 2
```

**Volumes**:
- Models: `/app/models` (read-only)
- Logs: `/app/logs` (read-write)
- Config: `/app/config` (read-only)

**Environment Variables**:
```bash
ENVIRONMENT=production         # From ConfigMap
LOG_LEVEL=INFO                 # From ConfigMap
MLFLOW_TRACKING_URI=...        # From ConfigMap
DATABASE_URL=...               # From Secret
API_KEY=...                    # From Secret
WORKERS=4                      # From ConfigMap
```

### MLflow Service Deployment

**File**: `base/deployment.yaml`

**Specifications**:
- **Container Image**: `ghcr.io/mlflow/mlflow:v2.7.0`
- **Port**: 5000
- **Resources**:
  - Requests: 250m CPU, 512Mi Memory
  - Limits: 500m CPU, 1Gi Memory
- **Replicas**: 1 (prod), 1 (staging), 1 (dev)

---

## ⚙️ Services

### Service: `taxi-fare-api`

**Type**: ClusterIP (internal routing)  
**Port**: 8000 (HTTP) + 8001 (Metrics)  
**Session Affinity**: ClientIP (3600s timeout)

**DNS Name**: `taxi-fare-api.taxi-fare-prod.svc.cluster.local`

### Service: `mlflow-service`

**Type**: ClusterIP  
**Port**: 5000

**DNS Name**: `mlflow-service.taxi-fare-prod.svc.cluster.local`

### Headless Service: `taxi-fare-api-headless`

**Use**: StatefulSet DNS resolution  
**DNS Name**: `taxi-fare-api-0.taxi-fare-api-headless.taxi-fare-prod.svc.cluster.local`

---

## 🌐 Ingress

### Ingress: `taxi-fare-ingress`

**File**: `base/ingress.yaml`

**Specifications**:
- **Host**: `api.taxi-fare.example.com`
- **TLS**: Enabled with Let's Encrypt (cert-manager)
- **Rate Limiting**: 100 requests/IP, 20 requests/second
- **CORS**: Enabled
- **Backend**: taxi-fare-api:8000

**Configuration**:
```yaml
Rules:
  - Host: api.taxi-fare.example.com
    Paths:
      / -> taxi-fare-api:8000
      /metrics -> taxi-fare-api:8001

TLS:
  - Certificate: Let's Encrypt (auto-renew)
  - Domain: api.taxi-fare.example.com

Annotations:
  - Rate limit: 100 req/IP
  - RPS limit: 20 req/sec
  - CORS: Enabled
  - Body size: 10MB
```

### Additional Ingress Rules

**Staging**: `staging-api.taxi-fare.example.com`  
**Development**: `dev-api.taxi-fare.example.com`

---

## 📈 Autoscaling (HPA)

### API Autoscaler

**File**: `base/hpa.yaml`

**Settings**:
- **Min Replicas**: 3
- **Max Replicas**: 10
- **Target CPU**: 70%
- **Target Memory**: 80%
- **Custom Metrics**: 
  - HTTP requests/second: 1000
  - Queue depth: 30

**Scaling Behavior**:
```yaml
Scale Up:
  - Max 50% increase or 2 pods per minute
  - Stabilization: 60 seconds

Scale Down:
  - Max 50% decrease or 1 pod per minute
  - Stabilization: 300 seconds
```

### MLflow Autoscaler

- **Min Replicas**: 1
- **Max Replicas**: 3
- **Target CPU**: 80%
- **Target Memory**: 90%

---

## 💾 Storage

### Persistent Volumes

#### Models Volume (PV: `taxi-fare-models-pv`)
- **Size**: 10Gi
- **Access Mode**: ReadOnlyMany
- **Storage Class**: fast-ssd
- **Type**: hostPath (`/data/models`)
- **Mount Path**: `/app/models` (read-only)

#### MLflow Volume (PV: `mlflow-pv`)
- **Size**: 20Gi
- **Access Mode**: ReadWriteOnce
- **Storage Class**: standard
- **Type**: hostPath (`/data/mlflow`)
- **Mount Path**: `/mlflow`

### Storage Classes

#### `fast-ssd`
- **Provisioner**: kubernetes.io/host-path
- **Type**: pd-ssd
- **VolumeBinding**: WaitForFirstConsumer
- **Expansion**: Allowed

#### `standard`
- **Provisioner**: kubernetes.io/host-path
- **Type**: pd-standard
- **VolumeBinding**: Immediate
- **Expansion**: Allowed

---

## 🔐 Security (RBAC)

### Service Accounts

#### `taxi-fare-api`
- **Namespace**: taxi-fare-prod
- **Permissions**:
  - Read pods, pod logs
  - Read ConfigMaps, Secrets
  - Create events
  - Read deployments

#### `mlflow-service`
- **Namespace**: taxi-fare-prod
- **Permissions**:
  - Read pods
  - Read persistent volumes
  - Read secrets

### Roles & RoleBindings

**Principle**: Least privilege - each service account has minimal required permissions

### Secrets Management

**Key Secrets**:
```yaml
database_url: postgresql://user:pass@host:5432/db
api_key: your-secret-key
jwt_secret: your-jwt-secret
admin_password: admin_password
tls_cert: (certificate)
tls_key: (private key)
```

**Best Practices**:
- Use external secret managers (HashiCorp Vault, AWS Secrets Manager)
- Rotate secrets quarterly
- Use separate secrets for each environment
- Never commit secrets to version control

---

## 🔍 ConfigMaps

**File**: `base/configmap.yaml`

### Application Config

```yaml
environment: production
log_level: INFO
workers: 4
api_host: 0.0.0.0
api_port: 8000
mlflow_uri: http://mlflow-service:5000
```

### Logging Config

JSON formatted with rotating file handlers (10MB, 5 backups)

### NGINX Config

Proxy configuration with:
- Least connections load balancing
- Health check `/health`
- Timeout settings (60s default)

---

## 📊 Monitoring & Metrics

### Prometheus Integration

**Scrape Config**:
```yaml
- Endpoint: :8001/metrics
- Interval: 30s
- Timeout: 10s
```

**Default Metrics**:
- HTTP request count
- Request latency
- Model prediction time
- Error rate

### Logging

**Default Path**: `/app/logs/app.log`

**Format**: 
```
YYYY-MM-DD HH:MM:SS [LEVEL] logger_name: message
```

**Log Levels**:
- DEBUG: Development
- INFO: Production
- WARNING: Alert
- ERROR: Critical issues

---

## 🛠️ Common Tasks

### 1. Deploy to Production

```bash
# Interactive
./deploy.ps1      # PowerShell
./deploy.sh       # Bash

# Command line
kubectl kustomize k8s/overlays/prod | kubectl apply -f -

# Dry-run (validate)
kubectl kustomize k8s/overlays/prod | kubectl apply --dry-run=client -f -
```

### 2. Scale Manually

```bash
# Scale to specific number of replicas
kubectl scale deployment taxi-fare-api -n taxi-fare-prod --replicas=5

# Check scaling status
kubectl get deployment taxi-fare-api -n taxi-fare-prod -w
```

### 3. View Logs

```bash
# Latest logs from deployment
kubectl logs -n taxi-fare-prod deploy/taxi-fare-api --tail=100

# Follow logs in real-time
kubectl logs -n taxi-fare-prod -l app=taxi-fare-api -f

# Logs from specific pod
kubectl logs -n taxi-fare-prod taxi-fare-api-abc123-xyz789
```

### 4. Port Forward

```bash
# API
kubectl port-forward -n taxi-fare-prod svc/taxi-fare-api 8000:8000

# MLflow
kubectl port-forward -n taxi-fare-prod svc/mlflow-service 5000:5000

# Access at http://localhost:8000
```

### 5. Execute Commands in Pod

```bash
# Interactive shell
kubectl exec -it -n taxi-fare-prod taxi-fare-api-abc123-xyz789 /bin/bash

# Run single command
kubectl exec -n taxi-fare-prod taxi-fare-api-abc123-xyz789 -- ls /app
```

### 6. Update Deployment

```bash
# Set new image
kubectl set image deployment/taxi-fare-api \
  taxi-fare-api=taxi-fare-ml:v2.0.0 \
  -n taxi-fare-prod

# Watch rollout
kubectl rollout status deploy/taxi-fare-api -n taxi-fare-prod -w

# Rollback if issues
kubectl rollout undo deploy/taxi-fare-api -n taxi-fare-prod
```

### 7. Check Resource Usage

```bash
# Node resources
kubectl top nodes

# Pod resources
kubectl top pods -n taxi-fare-prod

# Set resource requests/limits
kubectl set resources deploy taxi-fare-api \
  -n taxi-fare-prod \
  --requests=cpu=500m,memory=512Mi \
  --limits=cpu=1000m,memory=1Gi
```

---

## 🐛 Troubleshooting

### Issue: Pods not starting

```bash
# Check pod status
kubectl describe pod -n taxi-fare-prod taxi-fare-api-xyz

# Check events
kubectl get events -n taxi-fare-prod --sort-by='.lastTimestamp'

# Check node status
kubectl get nodes
kubectl describe node <node-name>
```

### Issue: CrashLoopBackOff

**Cause**: Container crashes immediately after starting

**Solution**:
```bash
# Check logs
kubectl logs -n taxi-fare-prod taxi-fare-api-xyz --previous

# Check resource availability
kubectl describe nodes

# Increase resource limits
kubectl set resources deploy taxi-fare-api -n taxi-fare-prod \
  --limits=cpu=2000m,memory=2Gi
```

### Issue: ImagePullBackOff

**Cause**: Docker image not found in registry

**Solution**:
```bash
# Check image name
kubectl get deployment -n taxi-fare-prod -o yaml | grep image:

# Verify image in registry
docker pull taxi-fare-ml:latest

# Update deployment with correct image
kubectl set image deployment/taxi-fare-api \
  taxi-fare-api=taxi-fare-ml:latest \
  -n taxi-fare-prod
```

### Issue: PVC stuck in Pending

**Cause**: Storage provisioner not available

**Solution**:
```bash
# Check PVC status
kubectl get pvc -n taxi-fare-prod

# Check storage classes
kubectl get storageclass

# Create storage manually if needed
mkdir -p /data/models /data/mlflow
chmod 777 /data/models /data/mlflow
```

### Issue: High latency/slow requests

**Solution**:
```bash
# Check pod resource usage
kubectl top pods -n taxi-fare-prod

# Scale up
kubectl scale deployment taxi-fare-api -n taxi-fare-prod --replicas=8

# Check network policies
kubectl get networkpolicies -n taxi-fare-prod
```

---

## ✅ Best Practices

### 1. Resource Management
- ✅ Always set resource requests and limits
- ✅ Monitor actual usage and adjust
- ✅ Use HPA for auto-scaling
- ✅ Reserve resources for system pods

### 2. High Availability
- ✅ Minimum 3 replicas in production
- ✅ Pod anti-affinity for distribution
- ✅ Use multiple availability zones
- ✅ Implement circuit breakers

### 3. Security
- ✅ Use network policies
- ✅ Implement RBAC
- ✅ Use secrets management
- ✅ Scan images for vulnerabilities
- ✅ Use non-root containers

### 4. Observability
- ✅ Setup comprehensive logging
- ✅ Export Prometheus metrics
- ✅ Setup distributed tracing
- ✅ Create meaningful alerts
- ✅ Track all deployments

### 5. Updates & Deployments
- ✅ Use rolling updates
- ✅ Test in staging first
- ✅ Keep old replicas until new are ready
- ✅ Have rollback plan
- ✅ Use gitops for deployment

### 6. Cost Optimization
- ✅ Use resource requests for scheduling
- ✅ Implement namespace resource quotas
- ✅ Use spot/preemptible instances
- ✅ Regular audit and cleanup
- ✅ Right-size resources

### 7. Backup & Recovery
- ✅ Daily backup of persistent volumes
- ✅ Test restore procedures regularly
- ✅ Document recovery procedures
- ✅ Store backups off-cluster
- ✅ Have RTO/RPO targets

---

## 📚 Additional Resources

### Official Documentation
- [Kubernetes Official Docs](https://kubernetes.io/docs/)
- [Kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Kustomize Documentation](https://kustomize.io/)

### Tools
- [kubectx](https://github.com/ahmetb/kubectx) - Context switcher
- [k9s](https://k9scli.io/) - Terminal UI
- [Helm](https://helm.sh/) - Package manager
- [Istio](https://istio.io/) - Service mesh

### Related Documentation
- See [DAY12_MONITORING.md](../MD/DAY12_MONITORING.md) for monitoring setup
- See [DAY13_DRIFT_DETECTION.md](../MD/DAY13_DRIFT_DETECTION.md) for drift monitoring
- See [DAY14_GOVERNANCE.md](../MD/DAY14_GOVERNANCE.md) for governance

---

## ✨ Summary

**Day 11 Completion Checklist**:

- ✅ Create Kubernetes manifests (Deployment, Service, Ingress)
- ✅ Setup replica sets for high availability (3-10 replicas)
- ✅ Configure HPA (Horizontal Pod Autoscaling)
- ✅ Implement persistent volumes for model storage
- ✅ Setup namespace isolation (dev, staging, prod)
- ✅ Create deployment scripts (PowerShell & Bash)
- ✅ Document complete setup with examples
- ✅ Provide troubleshooting guide
- ✅ Best practices documented

**Next Steps**: 
- Day 12: Advanced Monitoring & Observability
- Day 13: Drift Detection & Monitoring Strategies
- Day 14: Governance & Compliance Framework

---

**Status**: 🟢 Day 11 COMPLETE  
**Date**: April 11, 2026  
**Configuration**: Production-ready Kubernetes setup with 3 environments  
