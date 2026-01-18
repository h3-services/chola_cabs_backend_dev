#!/bin/bash
# Quick VPS Update Script
# Run this on your Hostinger VPS to pull latest changes

echo "======================================================================"
echo "Updating Cab Booking API on Hostinger VPS"
echo "======================================================================"

# Navigate to application directory
cd /var/www/cab_booking_api || { echo "Error: Directory not found"; exit 1; }

echo ""
echo "Step 1: Pulling latest changes from GitHub..."
git pull origin main

if [ $? -ne 0 ]; then
    echo "Error: Git pull failed"
    exit 1
fi

echo ""
echo "Step 2: Restarting cab-api service..."
systemctl restart cab-api

echo ""
echo "Step 3: Checking service status..."
sleep 2
systemctl status cab-api --no-pager

echo ""
echo "======================================================================"
echo "Deployment Complete!"
echo "======================================================================"
echo ""
echo "API Endpoints:"
echo "  - Root:    http://72.62.196.30/"
echo "  - Docs:    http://72.62.196.30/docs"
echo "  - Drivers: http://72.62.196.30/api/v1/drivers/"
echo ""
echo "To view logs: journalctl -u cab-api -f"
echo "======================================================================"
