#!/bin/bash
# Hostinger VPS Deployment Script

echo "=== Hostinger VPS Deployment ==="

# Pull latest changes
echo "Pulling latest code..."
git pull origin main

# Restart the service
echo "Restarting cab-api service..."
sudo systemctl restart cab-api

# Check service status
echo "Checking service status..."
sudo systemctl status cab-api --no-pager

# Test the fixed endpoint
echo "Testing error handling endpoint..."
sleep 3
curl -X 'GET' 'http://72.62.196.30:8000/api/v1/errors/?skip=0&limit=5' -H 'accept: application/json'

echo ""
echo "=== Deployment Complete ==="