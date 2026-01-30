#!/bin/bash

# Automated Deployment Script for Cab Booking API
# Run this on your VPS after uploading files

set -e  # Exit on error

echo "========================================="
echo "Cab Booking API - Automated Deployment"
echo "========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
APP_DIR="/var/www/projects/client_side/chola_cabs/backend/cab_app"
APP_USER="root"
VENV_DIR="$APP_DIR/venv"

echo -e "${YELLOW}Step 1: Updating system packages...${NC}"
apt update && apt upgrade -y

echo -e "${YELLOW}Step 2: Installing dependencies...${NC}"
apt install -y python3 python3-pip python3-venv nginx supervisor git

echo -e "${YELLOW}Step 3: Creating application directory...${NC}"
mkdir -p $APP_DIR
cd $APP_DIR

echo -e "${YELLOW}Step 4: Creating virtual environment...${NC}"
if [ ! -d "$VENV_DIR" ]; then
    python3 -m venv $VENV_DIR
fi

echo -e "${YELLOW}Step 5: Activating virtual environment...${NC}"
source $VENV_DIR/bin/activate

echo -e "${YELLOW}Step 6: Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn

echo -e "${YELLOW}Step 7: Creating uploads directory...${NC}"
mkdir -p $APP_DIR/uploads
chmod 755 $APP_DIR/uploads

echo -e "${YELLOW}Step 8: Setting up environment file...${NC}"
if [ ! -f "$APP_DIR/.env" ]; then
    cp $APP_DIR/.env.example $APP_DIR/.env
    echo -e "${RED}WARNING: Please edit .env file with your production settings!${NC}"
    echo "nano $APP_DIR/.env"
fi

echo -e "${YELLOW}Step 9: Creating systemd service...${NC}"
cat > /etc/systemd/system/cab-api.service << 'EOF'
[Unit]
Description=Cab Booking FastAPI Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/projects/client_side/chola_cabs/backend/cab_app
Environment="PATH=/var/www/projects/client_side/chola_cabs/backend/cab_app/venv/bin"
ExecStart=/var/www/projects/client_side/chola_cabs/backend/cab_app/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
EOF

echo -e "${YELLOW}Step 10: Configuring Nginx...${NC}"
cat > /etc/nginx/sites-available/cab-api << 'EOF'
server {
    listen 80;
    server_name 72.61.250.191;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads {
        alias /var/www/projects/client_side/chola_cabs/backend/cab_app/uploads;
        autoindex off;
    }

    client_max_body_size 10M;
}
EOF

# Enable nginx site
ln -sf /etc/nginx/sites-available/cab-api /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

echo -e "${YELLOW}Step 11: Testing Nginx configuration...${NC}"
nginx -t

echo -e "${YELLOW}Step 12: Starting services...${NC}"
systemctl daemon-reload
systemctl enable cab-api
systemctl start cab-api
systemctl restart nginx

echo -e "${YELLOW}Step 13: Configuring firewall...${NC}"
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
echo "y" | ufw enable

echo ""
echo -e "${GREEN}=========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}=========================================${NC}"
echo ""
echo -e "${YELLOW}Service Status:${NC}"
systemctl status cab-api --no-pager

echo ""
echo -e "${YELLOW}Next Steps:${NC}"
echo "1. Edit .env file: nano $APP_DIR/.env"
echo "2. Restart service: systemctl restart cab-api"
echo "3. Check logs: journalctl -u cab-api -f"
echo "4. Test API: curl http://72.61.250.191/health"
echo "5. Access Swagger: http://72.61.250.191/docs"
echo ""
echo -e "${GREEN}Your API is now running!${NC}"
