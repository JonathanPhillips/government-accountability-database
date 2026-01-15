# K3s Deployment Guide for GADB

This guide covers deploying the Government Accountability Database to a K3s cluster.

## Prerequisites

- K3s cluster running
- `kubectl` configured to access your cluster
- Harbor registry accessible at `harbor.local` (or update image references)
- Domain name configured (update in `base/ingress.yaml`)

## Initial Setup

### 1. Build and Push Docker Images

```bash
# Build backend image
cd backend
docker build -t harbor.local/gadb/backend:latest .
docker push harbor.local/gadb/backend:latest

# Build frontend image
cd ../frontend
docker build -f Dockerfile.prod -t harbor.local/gadb/frontend:latest .
docker push harbor.local/gadb/frontend:latest
```

### 2. Update Secrets

Edit `k8s/base/secrets.yaml` and update the following:
- `POSTGRES_PASSWORD`: Strong database password
- `DATABASE_URL`: Update with the new password
- `SECRET_KEY`: Generate a new secret key

```bash
# Generate a secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Update Ingress Domain

Edit `k8s/base/ingress.yaml` and replace `gadb.example.com` with your actual domain.

## Deployment

### Deploy to K3s

```bash
# Apply all resources
kubectl apply -k k8s/base/

# Check deployment status
kubectl get pods -n gadb
kubectl get services -n gadb
kubectl get ingress -n gadb
```

### Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n gadb

# Check logs
kubectl logs -n gadb deployment/backend
kubectl logs -n gadb deployment/frontend
kubectl logs -n gadb deployment/celery-worker
kubectl logs -n gadb deployment/celery-beat

# Check services
kubectl get svc -n gadb
```

### Run Database Migrations

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pods -n gadb -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -n gadb $BACKEND_POD -- alembic upgrade head
```

## Access the Application

Once deployed, access the application at:
- **Frontend**: https://gadb.example.com (or your configured domain)
- **API Docs**: https://gadb.example.com/api/docs

## Scaling

```bash
# Scale backend
kubectl scale deployment/backend -n gadb --replicas=3

# Scale Celery workers
kubectl scale deployment/celery-worker -n gadb --replicas=4
```

## Monitoring

```bash
# Watch pods
kubectl get pods -n gadb -w

# View logs
kubectl logs -f -n gadb deployment/backend
kubectl logs -f -n gadb deployment/celery-worker

# Get pod metrics (if metrics-server installed)
kubectl top pods -n gadb
```

## Troubleshooting

### Pod not starting

```bash
kubectl describe pod -n gadb <pod-name>
kubectl logs -n gadb <pod-name>
```

### Database connection issues

```bash
# Check postgres pod
kubectl get pods -n gadb -l app=postgres
kubectl logs -n gadb statefulset/postgres

# Test connection from backend
BACKEND_POD=$(kubectl get pods -n gadb -l app=backend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -n gadb $BACKEND_POD -- python -c "from app.database import engine; engine.connect()"
```

### Ingress not working

```bash
# Check ingress
kubectl describe ingress -n gadb gadb-ingress

# Check Traefik logs
kubectl logs -n kube-system deployment/traefik
```

## Updating

### Update Backend

```bash
# Build and push new image
cd backend
docker build -t harbor.local/gadb/backend:v1.1.0 .
docker push harbor.local/gadb/backend:v1.1.0

# Update deployment
kubectl set image deployment/backend backend=harbor.local/gadb/backend:v1.1.0 -n gadb
kubectl set image deployment/celery-worker celery-worker=harbor.local/gadb/backend:v1.1.0 -n gadb
kubectl set image deployment/celery-beat celery-beat=harbor.local/gadb/backend:v1.1.0 -n gadb

# Watch rollout
kubectl rollout status deployment/backend -n gadb
```

### Update Frontend

```bash
# Build and push new image
cd frontend
docker build -f Dockerfile.prod -t harbor.local/gadb/frontend:v1.1.0 .
docker push harbor.local/gadb/frontend:v1.1.0

# Update deployment
kubectl set image deployment/frontend frontend=harbor.local/gadb/frontend:v1.1.0 -n gadb

# Watch rollout
kubectl rollout status deployment/frontend -n gadb
```

## Backup

### Database Backup

```bash
# Create backup
kubectl exec -n gadb statefulset/postgres -- pg_dump -U gadb gadb > gadb-backup-$(date +%Y%m%d).sql

# Restore backup
kubectl exec -i -n gadb statefulset/postgres -- psql -U gadb gadb < gadb-backup-20260112.sql
```

## Cleanup

```bash
# Delete all resources
kubectl delete namespace gadb

# Or delete specific resources
kubectl delete -k k8s/base/
```

## Production Considerations

1. **Secrets Management**: Consider using sealed-secrets or external secrets operator
2. **SSL Certificates**: Configure cert-manager for automatic HTTPS
3. **Monitoring**: Set up Prometheus and Grafana
4. **Logging**: Configure centralized logging (ELK, Loki, etc.)
5. **Backups**: Set up automated database backups
6. **Resource Limits**: Adjust resource requests/limits based on actual usage
7. **High Availability**: Run multiple replicas of all services
8. **Persistent Storage**: Ensure proper backup of PVCs
