#!/bin/bash

# Restart the cab API service
echo "Restarting cab API service..."
sudo systemctl restart cab-api

# Wait for service to start
sleep 3

# Check service status
echo "Checking service status..."
sudo systemctl status cab-api --no-pager

# Test the fix on your specific trip
echo -e "\nTesting the odometer fix..."
python3 test_odometer_fix.py

echo -e "\nTesting fare calculation..."
python3 test_fare_calculation.py

echo -e "\nDeployment complete! The odometer automation fix is now live."