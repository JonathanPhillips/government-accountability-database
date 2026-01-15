# GADB Deployment Guide

Complete deployment guide for the Government Accountability Database.

## Table of Contents

1. [Local Development](#local-development)
2. [K3s Cluster Deployment](#k3s-cluster-deployment)
3. [Testing](#testing)
4. [Troubleshooting](#troubleshooting)

---

## Local Development

### Prerequisites

- Python 3.11+
- Docker and Docker Compose
- Node.js 18+ (for frontend, Phase 2)

### Option 1: Docker Compose (Recommended)

```bash
# Clone and navigate to project
cd govt_accountability

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Run database migrations
docker-compose exec backend alembic upgrade head

# Access API
open http://localhost:8000/docs
```

### Option 2: Local Python Environment

```bash
# Create virtual environment
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment
cp .env.example .env
# Edit .env with your settings

# Run database migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Running Tests

```bash
# Backend tests
cd backend
pytest tests/ -v

# With coverage
pytest tests/ -v --cov=app --cov-report=html

# Open coverage report
open htmlcov/index.html
```

---

## K3s Cluster Deployment

### Prerequisites

- Access to K3s cluster at 192.168.0.18
- kubectl configured with cluster access
- Harbor registry at 192.168.0.18:30002

### Step 1: Build and Push Docker Image

```bash
cd backend

# Build image
docker build -t 192.168.0.18:30002/gadb/backend:latest .

# Login to Harbor (if needed)
docker login 192.168.0.18:30002
# Username: admin
# Password: Harbor12345

# Push image
docker push 192.168.0.18:30002/gadb/backend:latest

# Verify upload
curl -k https://192.168.0.18:30003/api/v2.0/projects/gadb/repositories
```

### Step 2: Update Production Secrets

```bash
cd kubernetes

# Generate secure passwords
POSTGRES_PASS=$(openssl rand -base64 24)
SECRET_KEY=$(openssl rand -base64 32)

# Encode for Kubernetes
echo -n "$POSTGRES_PASS" | base64
echo -n "$SECRET_KEY" | base64

# Update secret.yaml with these values
# Replace the data values in secret.yaml
```

### Step 3: Deploy Infrastructure

```bash
# Create namespace
kubectl apply -f namespace.yaml

# Deploy secrets and config
kubectl apply -f secret.yaml
kubectl apply -f configmap.yaml

# Deploy database and Redis
kubectl apply -f postgres.yaml
kubectl apply -f redis.yaml

# Wait for database to be ready
kubectl wait --for=condition=ready pod -l app=postgres -n gadb --timeout=300s
```

### Step 4: Run Database Migrations

```bash
# Deploy backend first
kubectl apply -f backend.yaml

# Wait for backend pod
kubectl wait --for=condition=ready pod -l app=backend -n gadb --timeout=120s

# Get backend pod name
BACKEND_POD=$(kubectl get pods -n gadb -l app=backend -o jsonpath='{.items[0].metadata.name}')

# Run migrations
kubectl exec -n gadb $BACKEND_POD -- alembic upgrade head

# Verify migrations
kubectl exec -n gadb $BACKEND_POD -- alembic current
```

### Step 5: Deploy Workers

```bash
# Deploy Celery workers
kubectl apply -f celery.yaml

# Verify all pods are running
kubectl get pods -n gadb
```

### Step 6: Verify Deployment

```bash
# Check all resources
kubectl get all -n gadb

# Test API health endpoint
curl http://192.168.0.18:30089/health

# View API documentation
open http://192.168.0.18:30089/docs

# Check backend logs
kubectl logs -n gadb -l app=backend -f
```

---

## Testing

### Backend Unit Tests

```bash
# Local testing
cd backend
pytest tests/test_models.py -v

# Docker Compose testing
docker-compose exec backend pytest tests/ -v
```

### API Integration Tests (Phase 1.2)

```bash
# Will be created in Phase 1.2
pytest tests/test_api_*.py -v
```

### E2E Tests with Playwright (Phase 2)

```bash
# Will be created in Phase 2
npx playwright test
```

---

## Troubleshooting

### Common Issues

#### Database Connection Failed

```bash
# Check postgres pod is running
kubectl get pods -n gadb -l app=postgres

# Check postgres logs
kubectl logs -n gadb -l app=postgres

# Verify service
kubectl get svc -n gadb postgres-service

# Test connection from backend pod
kubectl exec -n gadb $BACKEND_POD -- env | grep DATABASE_URL
```

#### Backend Pod Crashing

```bash
# Check pod status
kubectl describe pod -n gadb -l app=backend

# View logs
kubectl logs -n gadb -l app=backend

# Common fixes:
# 1. Check DATABASE_URL is correct
# 2. Verify postgres is ready
# 3. Ensure migrations were run
# 4. Check image was pushed correctly
```

#### Image Pull Errors

```bash
# Verify image exists in Harbor
curl -k https://192.168.0.18:30003/api/v2.0/projects/gadb/repositories/backend/artifacts

# Re-tag and push
docker tag 192.168.0.18:30002/gadb/backend:latest 192.168.0.18:30002/gadb/backend:v1
docker push 192.168.0.18:30002/gadb/backend:v1

# Update deployment to use :v1 tag
```

#### Port Already in Use

Verify port allocations in `/Users/jon/Documents/code/kubernetes/PORT-ALLOCATIONS.md`:

- 30089: GADB Backend
- 30091: GADB Frontend (reserved)

```bash
# Check what's using a port on the cluster
kubectl get svc --all-namespaces | grep 30089
```

### Monitoring

```bash
# Access Grafana
open http://192.168.0.18:30030

# Access Prometheus
open http://192.168.0.18:30090

# View metrics endpoint (once implemented)
curl http://192.168.0.18:30089/metrics
```

### Scaling

```bash
# Scale backend
kubectl scale deployment/backend -n gadb --replicas=3

# Scale celery workers
kubectl scale deployment/celery-worker -n gadb --replicas=4

# Verify scaling
kubectl get pods -n gadb
```

### Database Backup and Restore

```bash
# Backup
kubectl exec -n gadb $POSTGRES_POD -- pg_dump -U gadb gadb > backup-$(date +%Y%m%d).sql

# Restore
kubectl exec -i -n gadb $POSTGRES_POD -- psql -U gadb gadb < backup-20250111.sql
```

### Complete Teardown

```bash
# Delete all GADB resources
kubectl delete namespace gadb

# Or selective deletion
kubectl delete -f kubernetes/celery.yaml
kubectl delete -f kubernetes/backend.yaml
kubectl delete -f kubernetes/redis.yaml
kubectl delete -f kubernetes/postgres.yaml
kubectl delete -f kubernetes/configmap.yaml
kubectl delete -f kubernetes/secret.yaml
kubectl delete -f kubernetes/namespace.yaml
```

---

---

## Production Deployment (Docker Compose)

### Environment Setup

1. **Clone Repository**
```bash
git clone https://github.com/JonathanPhillips/government-accountability-database.git
cd govt_accountability
```

2. **Configure Backend Environment**
```bash
cd backend
cp .env.production.example .env

# Edit .env and update:
# - SECRET_KEY (generate with: openssl rand -hex 32)
# - POSTGRES_PASSWORD
# - REDIS_PASSWORD
# - CORS_ORIGINS
# - SMTP credentials
```

3. **Configure Frontend Environment**
```bash
cd ../frontend
cp .env.production.example .env.production

# Update VITE_API_URL with your production API URL
```

### Production Deployment

```bash
# From project root
docker-compose -f docker-compose.prod.yml up -d

# Initialize database
docker exec gadb-backend-prod /app/scripts/init_database.sh

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### SSL/TLS Setup with Let's Encrypt

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Obtain certificate
certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal (add to crontab)
0 12 * * * /usr/bin/certbot renew --quiet
```

### Database Backups

```bash
# Set up automated backups (daily at 2 AM)
crontab -e

# Add:
0 2 * * * docker exec gadb-backend-prod /app/scripts/backup_database.sh
```

### Monitoring

**Health Endpoints:**
- Liveness: `https://api.yourdomain.com/health`
- Readiness: `https://api.yourdomain.com/health/ready`

**View Logs:**
```bash
# All services
docker-compose -f docker-compose.prod.yml logs -f

# Specific service
docker-compose -f docker-compose.prod.yml logs -f backend

# Application logs
docker exec gadb-backend-prod tail -f /app/logs/app.log
```

### Scaling

```bash
# Scale backend instances
docker-compose -f docker-compose.prod.yml up -d --scale backend=3

# Scale celery workers
docker-compose -f docker-compose.prod.yml up -d --scale celery-worker=4
```

### Security Checklist

- [ ] Change default admin password (admin@gadb.local / changeme123)
- [ ] Use strong SECRET_KEY (32+ characters)
- [ ] Configure SSL/TLS certificates
- [ ] Set up firewall rules (ufw/iptables)
- [ ] Enable rate limiting
- [ ] Configure automated backups
- [ ] Set up monitoring and alerting
- [ ] Review and restrict CORS origins
- [ ] Disable debug mode (DEBUG=False)
- [ ] Use strong database passwords
- [ ] Restrict SSH access
- [ ] Keep Docker and dependencies updated

### Backup and Restore

**Manual Backup:**
```bash
docker exec gadb-backend-prod /app/scripts/backup_database.sh
```

**Restore from Backup:**
```bash
# Copy backup to container
docker cp backup_file.sql.gz gadb-backend-prod:/backups/

# Restore
docker exec -it gadb-backend-prod /app/scripts/restore_database.sh /backups/backup_file.sql.gz
```

**S3 Backup Configuration:**
```bash
# Add to backend/.env
S3_BACKUP_BUCKET=your-backup-bucket
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

### Updating the Application

```bash
# Pull latest changes
git pull origin main

# Rebuild and restart
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Run migrations
docker exec gadb-backend-prod alembic upgrade head
```

### Troubleshooting Production

**Check Service Health:**
```bash
docker-compose -f docker-compose.prod.yml ps
curl https://api.yourdomain.com/health
```

**View Container Stats:**
```bash
docker stats
```

**Restart Services:**
```bash
docker-compose -f docker-compose.prod.yml restart backend
```

**Database Connection Issues:**
```bash
# Check database
docker exec gadb-postgres-prod pg_isready -U gadb

# Test from backend
docker exec gadb-backend-prod python -c "from app.database import SessionLocal; db = SessionLocal(); print('Connection OK')"
```

---

## Testing

### Backend Tests

```bash
# Unit tests
cd backend
pytest tests/ -v

# With coverage
pytest tests/ --cov=app --cov-report=html

# Integration tests
pytest tests/test_integration_*.py -v -m integration
```

### Frontend Tests

```bash
cd frontend

# Component tests
npm test -- --run

# E2E tests
npm run test:e2e

# With UI
npm run test:e2e:ui
```

### Full Test Suite

```bash
# From project root
./scripts/run_all_tests.sh
```

---

## Performance Optimization

### Database Optimization

```bash
# Inside PostgreSQL container
docker exec -it gadb-postgres-prod psql -U gadb -d gadb_prod

# Run VACUUM ANALYZE
VACUUM ANALYZE;

# Create indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incidents_date ON incidents(incident_date);
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_incidents_severity ON incidents(severity);
```

### Redis Caching

Caching is automatically enabled for:
- Analytics queries (5 minute TTL)
- Category lookups (10 minute TTL)

### Static Asset Optimization

- Gzip compression enabled in nginx
- Static assets cached for 1 year
- CDN recommended for production

---

## Next Steps

1. Complete Phase 1.2: CRUD API endpoints ✅
2. Develop Phase 1.3: Seed data ✅
3. Build Phase 2: Frontend ✅
4. Implement Phase 3: Ingestion pipeline ✅
5. **Current**: Phase 10 - Production deployment

See `notes_prompts.md` for complete project specification.
