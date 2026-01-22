#!/bin/bash
# Quick Fix Script for Connection Issues

echo "=== Cab API Connection Troubleshooting ==="

# 1. Check if service is running
echo "1. Checking service status..."
sudo systemctl status cab-api

# 2. Check if port is listening
echo "2. Checking if port 8000 is listening..."
sudo ss -tlnp | grep :8000

# 3. Try to start the service
echo "3. Starting cab-api service..."
sudo systemctl start cab-api

# 4. Enable service for auto-start
echo "4. Enabling service for auto-start..."
sudo systemctl enable cab-api

# 5. Check firewall
echo "5. Checking firewall status..."
sudo ufw status

# 6. Open port 8000 if needed
echo "6. Opening port 8000..."
sudo ufw allow 8000

# 7. Check recent logs
echo "7. Checking recent logs..."
sudo journalctl -u cab-api -n 20 --no-pager

echo "=== Fix completed. Try accessing the API now ==="