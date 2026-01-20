#!/bin/bash

echo "=== Checking Chola Cabs Service Status ==="
sudo systemctl status chola-cabs --no-pager

echo -e "\n=== Recent Service Logs ==="
sudo journalctl -u chola-cabs -n 20 --no-pager

echo -e "\n=== Check if service is running from correct directory ==="
ps aux | grep uvicorn

echo -e "\n=== Check current working directory in service ==="
sudo systemctl show chola-cabs -p WorkingDirectory

echo -e "\n=== Test API health ==="
curl -s http://localhost:8000/health || echo "Health check failed"

echo -e "\n=== Check uploads directory structure ==="
ls -la /root/cab_app/uploads/ 2>/dev/null || echo "Uploads directory not found at /root/cab_app/uploads/"
ls -la /root/chola_cabs_backend_dev/uploads/ 2>/dev/null || echo "Uploads directory not found at /root/chola_cabs_backend_dev/uploads/"