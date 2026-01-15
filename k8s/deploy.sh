#!/bin/bash
set -e

echo "=== GADB K3s Deployment Script ==="
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Check prerequisites
echo -e "${YELLOW}Checking prerequisites...${NC}"
command -v kubectl >/dev/null 2>&1 || { echo -e "${RED}kubectl is required but not installed${NC}"; exit 1; }
command -v docker >/dev/null 2>&1 || { echo -e "${RED}docker is required but not installed${NC}"; exit 1; }
echo -e "${GREEN}✓ Prerequisites satisfied${NC}"
echo ""

# Build and push images
read -p "Build and push Docker images? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Building backend image...${NC}"
    cd ../backend
    docker build -t harbor.local/gadb/backend:latest .
    docker push harbor.local/gadb/backend:latest
    echo -e "${GREEN}✓ Backend image built and pushed${NC}"
    
    echo -e "${YELLOW}Building frontend image...${NC}"
    cd ../frontend
    docker build -f Dockerfile.prod -t harbor.local/gadb/frontend:latest .
    docker push harbor.local/gadb/frontend:latest
    echo -e "${GREEN}✓ Frontend image built and pushed${NC}"
    
    cd ../k8s
fi
echo ""

# Deploy to K3s
echo -e "${YELLOW}Deploying to K3s...${NC}"
kubectl apply -k base/
echo -e "${GREEN}✓ Resources applied${NC}"
echo ""

# Wait for pods
echo -e "${YELLOW}Waiting for pods to be ready...${NC}"
kubectl wait --for=condition=ready pod -l app=postgres -n gadb --timeout=120s
kubectl wait --for=condition=ready pod -l app=redis -n gadb --timeout=60s
kubectl wait --for=condition=ready pod -l app=backend -n gadb --timeout=120s
kubectl wait --for=condition=ready pod -l app=frontend -n gadb --timeout=60s
echo -e "${GREEN}✓ All pods ready${NC}"
echo ""

# Run migrations
read -p "Run database migrations? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}Running database migrations...${NC}"
    BACKEND_POD=$(kubectl get pods -n gadb -l app=backend -o jsonpath='{.items[0].metadata.name}')
    kubectl exec -n gadb $BACKEND_POD -- alembic upgrade head
    echo -e "${GREEN}✓ Migrations complete${NC}"
fi
echo ""

# Show status
echo -e "${YELLOW}Deployment Status:${NC}"
kubectl get pods -n gadb
echo ""
kubectl get services -n gadb
echo ""
kubectl get ingress -n gadb
echo ""

echo -e "${GREEN}=== Deployment Complete ===${NC}"
echo ""
echo "Access the application at the ingress URL above"
echo "API Documentation: https://your-domain.com/api/docs"
