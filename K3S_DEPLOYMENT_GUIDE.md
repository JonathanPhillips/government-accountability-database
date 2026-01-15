# K3s Deployment Guide for GADB

**Date**: 2026-01-12
**Cluster**: 192.168.0.18:6443
**Domain**: gadb.local

## Prerequisites

Your k3s cluster is ready with:
- ✅ Traefik ingress controller
- ✅ 2 nodes (kubernetes master, nuc1 worker)
- ✅ LoadBalancer IPs: 192.168.0.18, 192.168.0.105

## Current Status (2026-01-12 17:32)

**Deployment Progress:**
- ✅ Kubernetes manifests applied successfully
- ✅ Namespace `gadb` created
- ✅ All services, deployments, and PVCs created
- ✅ PostgreSQL pod running (1/1 ready)
- ✅ Redis pod running (1/1 ready)
- ⏳ Backend, frontend, and celery pods in ImagePullBackOff (waiting for images)
- ✅ Docker images saved to tar files and ready for import

**Ready for Step 1**: Import the Docker images to your k3s nodes to complete the deployment.

## Step 1: Import Docker Images to k3s

The Docker images have been saved to tar files. Import them to your k3s nodes:

```bash
# On the k3s master node (192.168.0.18):
sudo k3s ctr images import /tmp/gadb-backend.tar
sudo k3s ctr images import /tmp/gadb-frontend.tar

# Verify images are imported:
sudo k3s ctr images ls | grep gadb
```

**Image files location**: `/tmp/gadb-backend.tar` (267MB), `/tmp/gadb-frontend.tar` (25MB)

## Step 2: Deploy to k3s

From your local machine (where kubectl is configured):

```bash
cd /Users/jon/Documents/code/govt_accountability

# Deploy all resources with kustomize:
kubectl apply -k k8s/base/

# Or deploy individually:
kubectl apply -f k8s/base/namespace.yaml
kubectl apply -f k8s/base/secrets.yaml
kubectl apply -f k8s/base/postgres.yaml
kubectl apply -f k8s/base/redis.yaml
kubectl apply -f k8s/base/backend.yaml
kubectl apply -f k8s/base/frontend.yaml
kubectl apply -f k8s/base/ingress.yaml
```

## Step 3: Initialize Database

Wait for postgres to be ready, then run migrations:

```bash
# Wait for postgres
kubectl wait --for=condition=ready pod -l app=postgres -n gadb --timeout=300s

# Run migrations
kubectl exec -n gadb deployment/backend -- alembic upgrade head

# Create admin user
kubectl exec -n gadb deployment/backend -- python3 << 'EOF'
from app.database import SessionLocal
from app.models.user import User
from app.models.base import UserRoleEnum
from app.utils.auth import get_password_hash

db = SessionLocal()
try:
    admin = User(
        email='admin@gadb.local',
        username='admin',
        hashed_password=get_password_hash('changeme123'),
        full_name='Administrator',
        role=UserRoleEnum.ADMIN,
        is_superuser=True,
        is_active=True
    )
    db.add(admin)
    db.commit()
    print("✅ Admin user created")
except Exception as e:
    print(f"Error: {e}")
finally:
    db.close()
EOF
```

## Step 4: Configure DNS

Add to your `/etc/hosts` or DNS server:

```bash
192.168.0.18  gadb.local
192.168.0.105 gadb.local
```

Or on your local machine:
```bash
echo "192.168.0.18 gadb.local" | sudo tee -a /etc/hosts
```

## Step 5: Access the Application

**URL**: http://gadb.local

**Admin Credentials**:
- Email: `admin@gadb.local`
- Password: `changeme123`

⚠️ **Change password immediately after first login!**

## Verification Commands

```bash
# Check all pods are running
kubectl get pods -n gadb

# Check services
kubectl get svc -n gadb

# Check ingress
kubectl get ingress -n gadb

# View logs
kubectl logs -n gadb deployment/backend --tail=50
kubectl logs -n gadb deployment/frontend --tail=50

# Check pod status details
kubectl describe pod -n gadb -l app=backend
```

## Expected Output

```
NAME                              READY   STATUS    RESTARTS   AGE
backend-xxxxxxxxx-xxxxx           1/1     Running   0          2m
celery-beat-xxxxxxxxx-xxxxx       1/1     Running   0          2m
celery-worker-xxxxxxxxx-xxxxx     1/1     Running   0          2m
frontend-xxxxxxxxx-xxxxx          1/1     Running   0          2m
postgres-xxxxxxxxx-xxxxx          1/1     Running   0          2m
redis-xxxxxxxxx-xxxxx             1/1     Running   0          2m
```

## Troubleshooting

### Images Not Found
```bash
# Check if images exist on nodes:
ssh jon@192.168.0.18 "sudo k3s ctr images ls | grep gadb"

# Re-import if needed:
scp /tmp/gadb-backend.tar jon@192.168.0.18:/tmp/
scp /tmp/gadb-frontend.tar jon@192.168.0.18:/tmp/
ssh jon@192.168.0.18 "sudo k3s ctr images import /tmp/gadb-backend.tar"
```

### Pods Not Starting
```bash
# Check events:
kubectl describe pod -n gadb <pod-name>

# Check logs:
kubectl logs -n gadb <pod-name>

# Force restart:
kubectl rollout restart deployment -n gadb
```

### Database Connection Issues
```bash
# Check postgres is ready:
kubectl exec -n gadb deployment/postgres -- psql -U gadb_user -d gadb -c "SELECT 1"

# Check backend can connect:
kubectl exec -n gadb deployment/backend -- python3 -c "from app.database import engine; engine.connect(); print('OK')"
```

### Ingress Not Working
```bash
# Check Traefik is running:
kubectl get svc -n kube-system traefik

# Check ingress details:
kubectl describe ingress -n gadb gadb-ingress

# Test from inside cluster:
kubectl run -it --rm debug --image=curlimages/curl --restart=Never -- curl http://frontend.gadb.svc.cluster.local
```

## Configuration

### Resource Requests/Limits

**Backend**:
- Requests: 256Mi RAM, 250m CPU
- Limits: 1Gi RAM, 1 CPU
- Replicas: 2

**Frontend**:
- Requests: 64Mi RAM, 50m CPU
- Limits: 256Mi RAM, 500m CPU
- Replicas: 2

**Celery Worker**:
- Requests: 512Mi RAM, 500m CPU
- Limits: 2Gi RAM, 2 CPU
- Replicas: 2

**PostgreSQL**:
- Requests: 256Mi RAM, 250m CPU
- Limits: 1Gi RAM, 500m CPU
- Storage: 10Gi PVC

**Redis**:
- Requests: 128Mi RAM, 100m CPU
- Limits: 512Mi RAM, 500m CPU

### Ingestion System

The same RSS feeds configured in Docker Compose are available:
- ProPublica
- The Intercept
- BBC News
- EFF
- NPR News

Ingestion data will persist in the PostgreSQL PVC.

## Updating the Application

### Update Backend
```bash
# Build new image
docker build -t gadb-backend:latest backend/

# Save and import
docker save -o /tmp/gadb-backend.tar gadb-backend:latest
scp /tmp/gadb-backend.tar jon@192.168.0.18:/tmp/
ssh jon@192.168.0.18 "sudo k3s ctr images import /tmp/gadb-backend.tar"

# Restart deployment
kubectl rollout restart deployment/backend -n gadb
kubectl rollout restart deployment/celery-worker -n gadb
kubectl rollout restart deployment/celery-beat -n gadb
```

### Update Frontend
```bash
# Build new image
cd frontend && npm run build
docker build -t gadb-frontend:latest -f Dockerfile --target production .

# Save and import
docker save -o /tmp/gadb-frontend.tar gadb-frontend:latest
scp /tmp/gadb-frontend.tar jon@192.168.0.18:/tmp/
ssh jon@192.168.0.18 "sudo k3s ctr images import /tmp/gadb-frontend.tar"

# Restart deployment
kubectl rollout restart deployment/frontend -n gadb
```

## Backup and Restore

### Database Backup
```bash
# Create backup
kubectl exec -n gadb deployment/postgres -- pg_dump -U gadb_user gadb > gadb-backup-$(date +%Y%m%d).sql

# Restore backup
kubectl exec -i -n gadb deployment/postgres -- psql -U gadb_user gadb < gadb-backup-20260112.sql
```

### PVC Backup
```bash
# List PVCs
kubectl get pvc -n gadb

# Backup using velero or custom solution
```

## Monitoring

```bash
# Watch pods
kubectl get pods -n gadb -w

# Stream logs
kubectl logs -f -n gadb deployment/backend
kubectl logs -f -n gadb deployment/celery-worker

# Check resource usage
kubectl top pods -n gadb
kubectl top nodes
```

## Uninstall

```bash
# Delete all resources
kubectl delete namespace gadb

# Or use kustomize
kubectl delete -k k8s/base/
```

## Next Steps

1. ✅ Deploy to k3s
2. ⏳ Configure SSL/TLS with cert-manager
3. ⏳ Set up proper domain (not .local)
4. ⏳ Configure Prometheus monitoring
5. ⏳ Set up log aggregation
6. ⏳ Configure automated backups
7. ⏳ Add horizontal pod autoscaling
