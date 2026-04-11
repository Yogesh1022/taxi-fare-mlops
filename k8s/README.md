# Kubernetes Configuration - Quick Start

**Status**: ✅ Complete - Day 11 Task  
**Date**: April 11, 2026  
**Version**: 1.0.0

---

## 🚀 Quick Start (5 Minutes)

### 1. Prerequisites
```bash
# Check if installed
kubectl version --client
kustomize version
docker --version
```

### 2. Deploy to Production
```powershell
# Windows PowerShell
cd k8s
.\deploy.ps1
# Select: 1 (Deploy to Production)
```

```bash
# Linux/MacOS
cd k8s
chmod +x deploy.sh
./deploy.sh
# Select: 1 (Deploy to Production)
```

### 3. Verify Deployment
```bash
kubectl get all -n taxi-fare-prod
kubectl get pods -n taxi-fare-prod -o wide
```

### 4. Access Application
```bash
# Port forward
kubectl port-forward -n taxi-fare-prod svc/taxi-fare-api 8000:8000

# Visit
http://localhost:8000/docs
```

---

## 📁 Structure

```
k8s/
├── base/                    # Base configuration
│   ├── deployment.yaml      # API & MLflow deployments
│   ├── service.yaml         # Services
│   ├── configmap.yaml       # Configuration
│   ├── secret.yaml          # Secrets
│   ├── hpa.yaml             # Auto-scaling
│   ├── pvc.yaml             # Storage
│   ├── ingress.yaml         # Ingress rules
│   ├── rbac.yaml            # Security
│   ├── namespace.yaml       # Namespaces
│   └── kustomization.yaml   # Base config
│
├── overlays/                # Environment overrides
│   ├── prod/                # Production
│   ├── staging/             # Staging
│   └── dev/                 # Development
│
├── deploy.ps1               # PowerShell script
├── deploy.sh                # Bash script
└── README.md                # This file
```

---

## 🎯 Common Commands

### Deploy
```bash
# To production
kubectl kustomize overlays/prod | kubectl apply -f -

# To staging
kubectl kustomize overlays/staging | kubectl apply -f -

# Dry-run (validate)
kubectl kustomize overlays/prod | kubectl apply --dry-run=client -f -
```

### Check Status
```bash
# All resources
kubectl get all -n taxi-fare-prod

# Just pods
kubectl get pods -n taxi-fare-prod -o wide

# Detailed info
kubectl describe deployment taxi-fare-api -n taxi-fare-prod
```

### Scale
```bash
# Manual scale
kubectl scale deploy taxi-fare-api -n taxi-fare-prod --replicas=5

# Check auto-scaling
kubectl get hpa -n taxi-fare-prod -w
```

### Logs & Debug
```bash
# View logs
kubectl logs -n taxi-fare-prod deploy/taxi-fare-api --tail=100 -f

# Execute in pod
kubectl exec -it -n taxi-fare-prod <pod-name> /bin/bash

# Port forward
kubectl port-forward -n taxi-fare-prod svc/taxi-fare-api 8000:8000
```

### Update
```bash
# Set new image
kubectl set image deploy/taxi-fare-api \
  taxi-fare-api=taxi-fare-ml:v2.0.0 \
  -n taxi-fare-prod

# Watch rollout
kubectl rollout status deploy/taxi-fare-api -n taxi-fare-prod -w

# Rollback
kubectl rollout undo deploy/taxi-fare-api -n taxi-fare-prod
```

---

## 📊 Environment Specifications

### Production
- **Replicas**: 5 (auto-scale 3-10)
- **CPU**: 500m requests, 1000m limits
- **Memory**: 512Mi requests, 1Gi limits
- **HPA**: CPU 70%, Memory 80%

### Staging
- **Replicas**: 2
- **CPU**: 500m requests, 1000m limits
- **Memory**: 512Mi requests, 1Gi limits

### Development
- **Replicas**: 1
- **CPU**: 250m requests, 500m limits
- **Memory**: 256Mi requests, 512Mi limits

---

## 🐛 Troubleshooting

### Pod not starting?
```bash
kubectl describe pod -n taxi-fare-prod <pod-name>
kubectl logs -n taxi-fare-prod <pod-name>
kubectl get events -n taxi-fare-prod --sort-by='.lastTimestamp'
```

### Image not found?
```bash
# Verify image
docker pull taxi-fare-ml:latest

# Check deployment
kubectl get deploy -n taxi-fare-prod -o yaml | grep image:
```

### Storage issues?
```bash
# Check PVC
kubectl get pvc -n taxi-fare-prod

# Check storage class
kubectl get storageclass

# Check PV
kubectl get pv
```

### Network issues?
```bash
# Check ingress
kubectl get ingress -n taxi-fare-prod

# Check service
kubectl get svc -n taxi-fare-prod

# Check endpoints
kubectl get endpoints -n taxi-fare-prod
```

---

## 📚 Documentation

For complete documentation, see:
- [DAY11_KUBERNETES_DEPLOYMENT.md](../MD/DAY11_KUBERNETES_DEPLOYMENT.md)
- [DAY11_COMPLETION_SUMMARY.md](../MD/DAY11_COMPLETION_SUMMARY.md)

---

## 🔐 Security Notes

⚠️ **Important**: Before production deployment:

1. **Update Secrets**
   - Change database credentials in `base/secret.yaml`
   - Generate new API keys
   - Generate new JWT secrets
   - Change admin password

2. **Update Hostnames**
   - Change `api.taxi-fare.example.com` in ingress
   - Point DNS records to ingress IP
   - Setup certificates (Let's Encrypt)

3. **Setup TLS**
   - Install cert-manager
   - Configure cluster issuer
   - Update ingress annotations

4. **Setup RBAC**
   - Review roles and permissions
   - Restrict by namespace
   - Use network policies

5. **Setup Monitoring**
   - Install Prometheus
   - Setup Grafana dashboards
   - Configure alerting

---

## ✅ Pre-Deployment Checklist

- [ ] kubectl configured and accessible
- [ ] Kustomize installed
- [ ] Docker image built and pushed
- [ ] Kubernetes cluster available
- [ ] Namespaces to be created
- [ ] Storage provisioner available
- [ ] Ingress controller installed
- [ ] Secrets updated with real values
- [ ] Hostnames updated in ingress
- [ ] DNS records pointing to ingress

---

## 🎯 Next Steps

1. **Deploy to Development** (test kustomize)
2. **Deploy to Staging** (validate manifests)
3. **Deploy to Production** (rollout)
4. **Monitor** (setup Prometheus + Grafana)
5. **Optimize** (adjust resource limits based on metrics)

---

**Status**: 🟢 Ready for Deployment  
**Project**: Taxi Fare Prediction MLOps  
**Date**: April 11, 2026  
