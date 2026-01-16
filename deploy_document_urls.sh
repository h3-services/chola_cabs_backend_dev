#!/bin/bash

echo "=========================================="
echo "Deploying Document URL Changes"
echo "=========================================="

# Navigate to application directory
cd /var/www/cab-api || { echo "Error: Directory not found"; exit 1; }

echo "✓ In application directory: /var/www/cab-api"

# Pull latest changes from GitHub
echo ""
echo "Pulling latest changes from GitHub..."
git pull origin main

if [ $? -eq 0 ]; then
    echo "✓ Code updated successfully"
else
    echo "✗ Failed to pull changes"
    exit 1
fi

# Restart the service
echo ""
echo "Restarting cab-api service..."
systemctl restart cab-api

if [ $? -eq 0 ]; then
    echo "✓ Service restarted successfully"
else
    echo "✗ Failed to restart service"
    exit 1
fi

# Wait a moment for service to start
sleep 2

# Check service status
echo ""
echo "Checking service status..."
systemctl status cab-api --no-pager | head -n 10

echo ""
echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
echo ""
echo "Test the changes with:"
echo "  curl http://localhost:8000/api/v1/drivers/ | jq"
echo "  curl http://localhost:8000/api/v1/vehicles/ | jq"
echo ""
echo "New fields added:"
echo "  Drivers: aadhar_url, licence_url"
echo "  Vehicles: rc_book_url, fc_certificate_url, vehicle_*_url"
echo ""
