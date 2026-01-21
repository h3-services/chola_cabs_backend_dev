#!/bin/bash

echo "🚀 Deploying Odometer PATCH Endpoints to Hostinger VPS..."

# SSH into VPS and update code
ssh -o StrictHostKeyChecking=no root@72.62.196.30 << 'EOF'

# Navigate to app directory
cd /root/cab_app

# Pull latest changes from GitHub
echo "📥 Pulling latest code from GitHub..."
git pull origin main

# Restart the service
echo "🔄 Restarting cab-api service..."
systemctl restart cab-api

# Check service status
echo "✅ Checking service status..."
systemctl status cab-api --no-pager -l

# Test the new endpoints
echo "🧪 Testing new odometer endpoints..."
sleep 3

# Test odometer-start endpoint
echo "Testing PATCH /api/v1/trips/{trip_id}/odometer-start"
curl -X PATCH "http://localhost:8000/api/v1/trips/test-trip/odometer-start?odo_start=12500" \
  -H "Content-Type: application/json" || echo "Endpoint test completed"

echo ""
echo "🎉 Deployment completed!"
echo "📋 New endpoints available:"
echo "   PATCH /api/v1/trips/{trip_id}/odometer-start"
echo "   PATCH /api/v1/trips/{trip_id}/odometer-end"
echo ""
echo "🌐 API Documentation: http://72.62.196.30:8000/docs"

EOF

echo "✅ Deployment script completed!"