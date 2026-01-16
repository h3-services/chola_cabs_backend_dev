#!/bin/bash

echo "=========================================="
echo "Chola Cabs Backend - VPS Deployment"
echo "=========================================="

# Update system
echo "Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "Installing Python and dependencies..."
apt install -y python3 python3-pip python3-venv git

# Navigate to home directory
cd /root

# Clone repository
echo "Cloning repository..."
if [ -d "chola_cabs_backend_dev" ]; then
    echo "Directory exists, pulling latest changes..."
    cd chola_cabs_backend_dev
    git pull
else
    git clone https://github.com/h3-services/chola_cabs_backend_dev.git
    cd chola_cabs_backend_dev
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "Installing Python packages..."
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment file
echo "Setting up environment file..."
cp .env.production .env

# Create uploads directory
echo "Creating uploads directory..."
mkdir -p uploads/drivers/{photos,aadhar,licence}
mkdir -p uploads/vehicles/{rc,fc,front,back,left,right}

# Setup systemd service
echo "Setting up systemd service..."
cp chola-cabs.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable chola-cabs
systemctl restart chola-cabs

# Check status
echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
systemctl status chola-cabs --no-pager
echo ""
echo "API URL: http://72.62.196.30:8000"
echo "API Docs: http://72.62.196.30:8000/docs"
echo "Health Check: http://72.62.196.30:8000/health"
echo ""
echo "Useful commands:"
echo "  systemctl status chola-cabs    # Check status"
echo "  systemctl restart chola-cabs   # Restart service"
echo "  journalctl -u chola-cabs -f    # View logs"
echo "=========================================="
