#!/bin/bash
# Import GADB Docker images to k3s
# Run this script on the k3s master node (192.168.0.18)

set -e

echo "🚀 Importing GADB images to k3s..."

# Check if tar files exist
if [ ! -f /tmp/gadb-backend.tar ]; then
    echo "❌ Error: /tmp/gadb-backend.tar not found"
    echo "Please copy the image files to this node first:"
    echo "  scp /tmp/gadb-backend.tar <user>@192.168.0.18:/tmp/"
    exit 1
fi

if [ ! -f /tmp/gadb-frontend.tar ]; then
    echo "❌ Error: /tmp/gadb-frontend.tar not found"
    echo "Please copy the image files to this node first:"
    echo "  scp /tmp/gadb-frontend.tar <user>@192.168.0.18:/tmp/"
    exit 1
fi

# Import backend image
echo "📦 Importing backend image..."
sudo k3s ctr images import /tmp/gadb-backend.tar
if [ $? -eq 0 ]; then
    echo "✅ Backend image imported successfully"
else
    echo "❌ Failed to import backend image"
    exit 1
fi

# Import frontend image
echo "📦 Importing frontend image..."
sudo k3s ctr images import /tmp/gadb-frontend.tar
if [ $? -eq 0 ]; then
    echo "✅ Frontend image imported successfully"
else
    echo "❌ Failed to import frontend image"
    exit 1
fi

# Verify images
echo ""
echo "🔍 Verifying imported images..."
sudo k3s ctr images ls | grep gadb

echo ""
echo "✅ Image import complete!"
echo ""
echo "Next steps:"
echo "1. Check pod status: kubectl get pods -n gadb"
echo "2. Wait for all pods to be Running"
echo "3. Initialize database: kubectl exec -n gadb deployment/backend -- alembic upgrade head"
echo "4. Add DNS entry: echo '192.168.0.18 gadb.local' | sudo tee -a /etc/hosts"
echo "5. Access application: http://gadb.local"
