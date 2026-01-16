# Hostinger VPS Deployment Guide

## Prerequisites
- Hostinger VPS with SSH access
- Domain name (optional)
- MySQL database credentials

## Step 1: Connect to Hostinger VPS
```bash
ssh root@your-hostinger-ip
```

## Step 2: Update System
```bash
apt update && apt upgrade -y
apt install python3 python3-pip python3-venv git nginx mysql-client -y
```

## Step 3: Clone Repository
```bash
cd /root
git clone https://github.com/h3-services/chola_cabs_backend_dev.git
cd chola_cabs_backend_dev
```

## Step 4: Setup Virtual Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Step 5: Configure Environment
```bash
nano .env
```

Add:
```env
DB_HOST=72.62.196.30
DB_PORT=3306
DB_USER=myuser
DB_PASSWORD=Hope3Services@2026
DB_NAME=cab_app

APP_NAME=Chola Cabs API
APP_VERSION=1.0.0
DEBUG=False

HOST=0.0.0.0
PORT=8000

UPLOAD_DIR=/root/chola_cabs_backend_dev/uploads
```

## Step 6: Create Systemd Service
```bash
nano /etc/systemd/system/chola-cabs.service
```

Add:
```ini
[Unit]
Description=Chola Cabs API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/root/chola_cabs_backend_dev
Environment=PATH=/root/chola_cabs_backend_dev/venv/bin
ExecStart=/root/chola_cabs_backend_dev/venv/bin/python app/main.py
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

## Step 7: Start Service
```bash
systemctl daemon-reload
systemctl enable chola-cabs
systemctl start chola-cabs
systemctl status chola-cabs
```

## Step 8: Configure Nginx (Optional - for domain)
```bash
nano /etc/nginx/sites-available/chola-cabs
```

Add:
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /uploads/ {
        alias /root/chola_cabs_backend_dev/uploads/;
    }
}
```

Enable:
```bash
ln -s /etc/nginx/sites-available/chola-cabs /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx
```

## Step 9: Configure Firewall
```bash
ufw allow 8000/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 22/tcp
ufw enable
```

## Step 10: Test API
```bash
curl http://localhost:8000/health
curl http://your-hostinger-ip:8000/health
```

## Access Points
- **Direct**: http://your-hostinger-ip:8000
- **With Domain**: http://your-domain.com
- **API Docs**: http://your-hostinger-ip:8000/docs
- **Health Check**: http://your-hostinger-ip:8000/health

## Update Deployment
```bash
cd /root/chola_cabs_backend_dev
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
systemctl restart chola-cabs
```

## Monitoring
```bash
# Check service status
systemctl status chola-cabs

# View logs
journalctl -u chola-cabs -f

# Restart service
systemctl restart chola-cabs
```

## SSL Certificate (Optional - Let's Encrypt)
```bash
apt install certbot python3-certbot-nginx -y
certbot --nginx -d your-domain.com
```

## Troubleshooting
```bash
# Check if port is in use
lsof -i :8000

# Check service logs
journalctl -u chola-cabs -n 100

# Test database connection
mysql -h 72.62.196.30 -u myuser -p cab_app
```
