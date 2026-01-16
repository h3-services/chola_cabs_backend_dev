#!/bin/bash
# VPS Deployment Script for Complete Field Coverage Update
# Run this script on the VPS after SSH login

echo "=========================================="
echo "Deploying Complete Field Coverage Update"
echo "=========================================="

# Navigate to application directory
cd /root/cab_app || { echo "Error: Application directory not found"; exit 1; }

echo "✓ In application directory: $(pwd)"

# Pull latest changes from GitHub
echo ""
echo "Pulling latest code from GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to pull from GitHub"
    exit 1
fi

echo "✓ Code updated successfully"

# Restart the API service
echo ""
echo "Restarting cab-api service..."
systemctl restart cab-api

if [ $? -ne 0 ]; then
    echo "❌ Error: Failed to restart service"
    exit 1
fi

echo "✓ Service restarted successfully"

# Wait a moment for service to start
sleep 2

# Check service status
echo ""
echo "Checking service status..."
systemctl status cab-api --no-pager | head -n 10

# Test API endpoint
echo ""
echo "Testing API endpoint..."
curl -s http://localhost:8000/health | python3 -m json.tool

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "To verify all fields are returned, test these endpoints:"
echo "  curl http://72.62.196.30:8000/api/v1/drivers/ | python3 -m json.tool"
echo "  curl http://72.62.196.30:8000/api/v1/vehicles/ | python3 -m json.tool"
echo "  curl http://72.62.196.30:8000/api/v1/trips/ | python3 -m json.tool"
