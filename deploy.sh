#!/bin/bash
# VPS Deployment Script - Run this on your server

set -e

echo "🚀 Starting deployment..."

# Update system
apt update && apt upgrade -y

# Install dependencies
apt install -y python3 python3-pip python3-venv nginx git

# Create project directory
cd /root
if [ ! -d "cab_app" ]; then
    git clone https://github.com/h3-services/chola_cabs_backend_dev.git cab_app
fi
cd cab_app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python packages
pip install --upgrade pip
pip install -r requirements.txt

# Create upload directories
mkdir -p /root/uploads/drivers/{photos,aadhar,licence}
mkdir -p /root/uploads/vehicles/{rc,fc,front,back,left,right}
chmod -R 755 /root/uploads

# Create .env file
cat > .env <<EOF
DB_HOST=72.62.196.30
DB_PORT=3306
DB_USER=myuser
DB_PASSWORD=Hope3Services@2026
DB_NAME=cab_app

APP_NAME=Cab Booking API
APP_VERSION=1.0.0
DEBUG=False

SECRET_KEY=$(openssl rand -hex 32)

HOST=0.0.0.0
PORT=8000

UPLOAD_DIR=/root/uploads
BASE_URL=http://72.62.196.30/uploads
EOF

# Create systemd service
cat > /etc/systemd/system/cab-api.service <<EOF
[Unit]
Description=Cab Booking API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/cab_app
Environment=PATH=/root/cab_app/venv/bin
ExecStart=/root/cab_app/venv/bin/python app/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

# Configure Nginx
cat > /etc/nginx/sites-available/cab-api <<EOF
server {
    listen 80;
    server_name 72.62.196.30;
    client_max_body_size 10M;

    location /uploads/ {
        alias /root/uploads/;
        autoindex off;
        expires 30d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    }
}
EOF

ln -sf /etc/nginx/sites-available/cab-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t && systemctl restart nginx

# Start API service
systemctl daemon-reload
systemctl enable cab-api
systemctl start cab-api

echo "✅ Deployment complete!"
echo ""
echo "📝 API running at: http://72.62.196.30"
echo "📝 Docs at: http://72.62.196.30/docs"
echo ""
echo "Check status: systemctl status cab-api"
echo "View logs: journalctl -u cab-api -f"
