#!/bin/bash

# Quick Update Script for Cab Booking API
# Use this to update your application after making changes

set -e

APP_DIR="/var/www/cab_booking_api"
VENV_DIR="$APP_DIR/venv"

echo "Updating Cab Booking API..."

# Stop service
echo "Stopping service..."
systemctl stop cab-api

# Navigate to app directory
cd $APP_DIR

# Pull latest code (if using git)
if [ -d ".git" ]; then
    echo "Pulling latest code from git..."
    git pull
fi

# Activate virtual environment
source $VENV_DIR/bin/activate

# Install/update dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Restart service
echo "Restarting service..."
systemctl start cab-api

# Check status
echo ""
echo "Service status:"
systemctl status cab-api --no-pager

echo ""
echo "Update complete!"
echo "View logs: journalctl -u cab-api -f"
