# GADB Kubernetes Deployment

Kubernetes manifests for deploying GADB to your K3s cluster.

## Prerequisites

1. Access to K3s cluster at 192.168.0.18
2. Harbor registry configured at 192.168.0.18:30002
3. kubectl configured with cluster access

## Deployment Steps

### 1. Build and Push Docker Image

```bash
# Build backend image
cd backend
docker build -t 192.168.0.18:30002/gadb/backend:latest .

# Push to Harbor registry
docker push 192.168.0.18:30002/gadb/backend:latest
```

### 2. Update Secrets

Edit `secret.yaml` with production values:

```bash
# Generate base64 encoded secrets
echo -n "your-postgres-password" | base64
echo -n "your-secret-key" | base64
```

### 3. Deploy to Kubernetes

```bash
# Apply all manifests
kubectl apply -f namespace.yaml
kubectl apply -f secret.yaml
kubectl apply -f configmap.yaml
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n gadb --timeout=300s

# Deploy backend and workers
kubectl apply -f backend.yaml
kubectl apply -f celery.yaml
```

### 4. Run Database Migrations

```bash
# Get backend pod name
BACKEND_POD=$(kubectl get pods -n gadb -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -n gadb $BACKEND_POD -- alembic upgrade head
```

### 5. Verify Deployment

```bash
# Check all pods are running
kubectl get pods -n gadb

# Check services
kubectl get services -n gadb

# Test API endpoint
curl http://192.168.0.18:30089/health
```

## Access URLs

- **Backend API**: http://192.168.0.18:30089
- **API Docs**: http://192.168.0.18:30089/docs
- **Frontend** (when deployed): http://192.168.0.18:30091

## Troubleshooting

### Check Pod Logs

```bash
# Backend logs
kubectl logs -n gadb -l app=backend -f

# Celery worker logs
kubectl logs -n gadb -l app=celery-worker -f

# Postgres logs
kubectl logs -n gadb -l app=postgres -f
```

### Database Connection Issues

```bash
# Test database connection from backend pod
kubectl exec -n gadb $BACKEND_POD -- psql -h postgres-service -U gadb -d gadb -c "SELECT version();"
```

### Reset Database (Development Only)

```bash
# Delete and recreate postgres PVC
kubectl delete -f postgres.yaml -n gadb
kubectl apply -f postgres.yaml -n gadb

# Wait and run migrations
kubectl wait --for=condition=ready pod -l app=postgres -n gadb --timeout=300s
kubectl exec -n gadb $BACKEND_POD -- alembic upgrade head
```

## Updating the Application

```bash
# Build new image
cd backend
docker build -t 192.168.0.18:30002/gadb/backend:latest .
docker push 192.168.0.18:30002/gadb/backend:latest

# Restart deployments to pull new image
kubectl rollout restart deployment/backend -n gadb
kubectl rollout restart deployment/celery-worker -n gadb
kubectl rollout restart deployment/celery-beat -n gadb

# Monitor rollout
kubectl rollout status deployment/backend -n gadb
```

## Scaling

```bash
# Scale backend replicas
kubectl scale deployment/backend -n gadb --replicas=3

# Scale celery workers
kubectl scale deployment/celery-worker -n gadb --replicas=4
```

## Port Allocations

As documented in `/Users/jon/Documents/code/kubernetes/PORT-ALLOCATIONS.md`:

- **30089**: Backend API (GADB)
- **30091**: Frontend (GADB) - reserved for future use
- **30092**: pgAdmin (optional) - reserved for future use

## Monitoring

The deployment integrates with your existing Prometheus/Grafana stack:

- Prometheus scrapes metrics at http://192.168.0.18:30090
- Grafana dashboards at http://192.168.0.18:30030

## Storage

- PostgreSQL uses `local-storage` StorageClass
- PVC size: 20Gi (adjustable in postgres.yaml)
- Storage location: `/mnt/kubernetes-storage` on cluster nodes
