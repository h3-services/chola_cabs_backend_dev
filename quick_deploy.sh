#!/bin/bash
# Quick VPS Deployment Script
# Run this after SSH into your VPS: ssh root@72.62.196.30

set -e

echo "🚀 Starting Cab Booking API Deployment..."
echo ""

# Step 1: Navigate to app directory or clone
if [ -d "/var/www/cab_booking_api" ]; then
    echo "📂 App directory exists, pulling latest changes..."
    cd /var/www/cab_booking_api
    git pull origin main
else
    echo "📂 Cloning repository..."
    mkdir -p /var/www
    cd /var/www
    git clone https://github.com/h3-services/chola_cabs_backend_dev.git cab_booking_api
    cd cab_booking_api
fi

echo ""
echo "✅ Code updated!"
echo ""

# Step 2: Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Creating from template..."
    cp env.production.template .env
    echo ""
    echo "🔴 IMPORTANT: You need to edit .env file!"
    echo "Run: nano .env"
    echo ""
    echo "Update these values:"
    echo "  - SECRET_KEY (generate with: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\")"
    echo "  - DB_PASSWORD (if different)"
    echo "  - BASE_URL (your domain or IP)"
    echo ""
    read -p "Press Enter after you've edited .env file..."
fi

# Step 3: Run deployment script
echo ""
echo "🔧 Running deployment script..."
chmod +x deploy.sh
./deploy.sh

# Step 4: Setup uploads
echo ""
echo "📁 Setting up upload directories..."
chmod +x setup_uploads.sh
./setup_uploads.sh

# Step 5: Verify deployment
echo ""
echo "✅ Deployment complete!"
echo ""
echo "🔍 Verifying deployment..."
echo ""

# Check service status
echo "Service Status:"
systemctl status cab-api --no-pager | head -n 10

echo ""
echo "🧪 Testing API..."
sleep 2

# Test API
if curl -s http://localhost:8000/ > /dev/null; then
    echo "✅ API is responding!"
else
    echo "❌ API is not responding. Check logs: journalctl -u cab-api -f"
fi

echo ""
echo "📊 Quick Commands:"
echo "  View logs:     journalctl -u cab-api -f"
echo "  Restart API:   systemctl restart cab-api"
echo "  Check status:  systemctl status cab-api"
echo "  Test API:      curl http://72.62.196.30/"
echo "  API Docs:      http://72.62.196.30/docs"
echo ""
echo "🎉 Deployment finished!"
