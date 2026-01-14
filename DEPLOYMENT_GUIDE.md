# 🚀 Hostinger VPS Deployment Guide - Cab Booking API

Complete step-by-step guide to deploy your FastAPI application to Hostinger VPS.

---

## 📋 Prerequisites

- ✅ VPS IP: `72.62.196.30`
- ✅ SSH access as root
- ✅ Database already running on VPS
- ✅ Application code ready

---

## 🎯 Deployment Steps

### Step 1: Connect to VPS

```bash
ssh root@72.62.196.30
```

### Step 2: Update System & Install Dependencies

```bash
# Update system packages
apt update && apt upgrade -y

# Install Python 3 and pip
apt install python3 python3-pip python3-venv -y

# Install nginx for reverse proxy
apt install nginx -y

# Install git (if needed)
apt install git -y

# Install supervisor (for process management)
apt install supervisor -y
```

### Step 3: Create Application Directory

```bash
# Create app directory
mkdir -p /var/www/cab_booking_api
cd /var/www/cab_booking_api

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate
```

### Step 4: Upload Application Files

**Option A: Using Git (Recommended)**
```bash
# If you have a git repository
git clone https://github.com/PraveenCoder2007/cab_app.git .
```

**Option B: Using SCP from Local Machine**
```bash
# Run this from your LOCAL machine (Windows PowerShell)
scp -r d:\cab_ap\* root@72.62.196.30:/var/www/cab_booking_api/
```

**Option C: Manual Upload**
- Use FileZilla or WinSCP
- Upload all files from `d:\cab_ap` to `/var/www/cab_booking_api/`

### Step 5: Install Python Dependencies

```bash
# Make sure you're in the virtual environment
source /var/www/cab_booking_api/venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Install additional production dependencies
pip install gunicorn
```

### Step 6: Configure Environment Variables

```bash
# Create production .env file
nano /var/www/cab_booking_api/.env
```

**Add this content:**
```env
# Database Configuration
DB_HOST=72.62.196.30
DB_PORT=3306
DB_USER=myuser
DB_PASSWORD=Hope3Services@2026
DB_NAME=cab_app

# Application Configuration
APP_NAME=Cab Booking API
APP_VERSION=1.0.0
DEBUG=False

# Security
SECRET_KEY=your_production_secret_key_change_this_to_random_string

# Server Configuration
HOST=0.0.0.0
PORT=8000

# Upload Configuration
UPLOAD_DIR=/var/www/cab_booking_api/uploads
BASE_URL=http://72.62.196.30/uploads
```

**Save and exit** (Ctrl+X, then Y, then Enter)

### Step 7: Create Uploads Directory

```bash
# Create uploads directory
mkdir -p /var/www/cab_booking_api/uploads
chmod 755 /var/www/cab_booking_api/uploads
```

### Step 8: Test Application

```bash
# Activate virtual environment
source /var/www/cab_booking_api/venv/bin/activate

# Test run
cd /var/www/cab_booking_api
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# If it works, press Ctrl+C to stop
```

### Step 9: Create Systemd Service

```bash
# Create service file
nano /etc/systemd/system/cab-api.service
```

**Add this content:**
```ini
[Unit]
Description=Cab Booking FastAPI Application
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/cab_booking_api
Environment="PATH=/var/www/cab_booking_api/venv/bin"
ExecStart=/var/www/cab_booking_api/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app --bind 0.0.0.0:8000
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**Save and exit** (Ctrl+X, then Y, then Enter)

### Step 10: Start and Enable Service

```bash
# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable cab-api

# Start the service
systemctl start cab-api

# Check status
systemctl status cab-api

# View logs
journalctl -u cab-api -f
```

### Step 11: Configure Nginx Reverse Proxy

```bash
# Create nginx configuration
nano /etc/nginx/sites-available/cab-api
```

**Add this content:**
```nginx
server {
    listen 80;
    server_name 72.62.196.30;

    # API endpoints
    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # WebSocket support (if needed)
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # Root and docs
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Static files (uploads)
    location /uploads {
        alias /var/www/cab_booking_api/uploads;
        autoindex off;
    }

    # Increase upload size limit
    client_max_body_size 10M;
}
```

**Save and exit** (Ctrl+X, then Y, then Enter)

### Step 12: Enable Nginx Configuration

```bash
# Create symbolic link
ln -s /etc/nginx/sites-available/cab-api /etc/nginx/sites-enabled/

# Remove default nginx site (optional)
rm /etc/nginx/sites-enabled/default

# Test nginx configuration
nginx -t

# Restart nginx
systemctl restart nginx

# Enable nginx to start on boot
systemctl enable nginx
```

### Step 13: Configure Firewall

```bash
# Allow HTTP
ufw allow 80/tcp

# Allow HTTPS (for future SSL)
ufw allow 443/tcp

# Allow SSH (important!)
ufw allow 22/tcp

# Enable firewall
ufw enable

# Check status
ufw status
```

---

## ✅ Verification

### Test Your API

```bash
# From VPS
curl http://localhost:8000/health

# From anywhere
curl http://72.62.196.30/health
curl http://72.62.196.30/api/v1/drivers
```

### Access Swagger UI

Open in browser:
- **API Documentation**: http://72.62.196.30/docs
- **Alternative Docs**: http://72.62.196.30/redoc
- **Health Check**: http://72.62.196.30/health

---

## 🔧 Management Commands

### Service Management

```bash
# Start service
systemctl start cab-api

# Stop service
systemctl stop cab-api

# Restart service
systemctl restart cab-api

# Check status
systemctl status cab-api

# View logs
journalctl -u cab-api -f

# View last 100 lines
journalctl -u cab-api -n 100
```

### Update Application

```bash
# Stop service
systemctl stop cab-api

# Pull latest code (if using git)
cd /var/www/cab_booking_api
git pull

# Or upload new files via SCP

# Activate virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Restart service
systemctl start cab-api

# Check status
systemctl status cab-api
```

### Nginx Management

```bash
# Test configuration
nginx -t

# Restart nginx
systemctl restart nginx

# View nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

---

## 🔒 Security Recommendations

### 1. Change Secret Key

```bash
# Generate a secure secret key
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Update .env file with the generated key
nano /var/www/cab_booking_api/.env
```

### 2. Setup SSL Certificate (HTTPS)

```bash
# Install certbot
apt install certbot python3-certbot-nginx -y

# Get SSL certificate (replace with your domain)
certbot --nginx -d yourdomain.com

# Auto-renewal is set up automatically
```

### 3. Restrict Database Access

```bash
# Only allow localhost connections to MySQL
# Edit MySQL config
nano /etc/mysql/mysql.conf.d/mysqld.cnf

# Set bind-address = 127.0.0.1
```

### 4. Setup Fail2Ban

```bash
# Install fail2ban
apt install fail2ban -y

# Enable and start
systemctl enable fail2ban
systemctl start fail2ban
```

---

## 📊 Monitoring

### Check Application Health

```bash
# CPU and Memory usage
htop

# Disk usage
df -h

# Service status
systemctl status cab-api

# Active connections
netstat -tulpn | grep :8000
```

### View Application Logs

```bash
# Real-time logs
journalctl -u cab-api -f

# Last 100 lines
journalctl -u cab-api -n 100

# Today's logs
journalctl -u cab-api --since today

# Errors only
journalctl -u cab-api -p err
```

---

## 🐛 Troubleshooting

### Service Won't Start

```bash
# Check logs
journalctl -u cab-api -n 50

# Check if port is in use
lsof -i :8000

# Kill process if needed
kill -9 <PID>

# Restart service
systemctl restart cab-api
```

### Database Connection Error

```bash
# Test database connection
mysql -h 72.62.196.30 -u myuser -p cab_app

# Check .env file
cat /var/www/cab_booking_api/.env

# Verify database credentials
```

### Nginx Errors

```bash
# Check nginx error log
tail -f /var/log/nginx/error.log

# Test configuration
nginx -t

# Restart nginx
systemctl restart nginx
```

### Permission Issues

```bash
# Fix ownership
chown -R root:root /var/www/cab_booking_api

# Fix permissions
chmod -R 755 /var/www/cab_booking_api
chmod -R 755 /var/www/cab_booking_api/uploads
```

---

## 📝 Quick Reference

### Important Paths

- **Application**: `/var/www/cab_booking_api`
- **Virtual Environment**: `/var/www/cab_booking_api/venv`
- **Uploads**: `/var/www/cab_booking_api/uploads`
- **Service File**: `/etc/systemd/system/cab-api.service`
- **Nginx Config**: `/etc/nginx/sites-available/cab-api`
- **Environment File**: `/var/www/cab_booking_api/.env`

### Important URLs

- **API Base**: http://72.62.196.30/api/v1
- **Swagger UI**: http://72.62.196.30/docs
- **ReDoc**: http://72.62.196.30/redoc
- **Health Check**: http://72.62.196.30/health

### Important Commands

```bash
# Service management
systemctl {start|stop|restart|status} cab-api

# View logs
journalctl -u cab-api -f

# Update code
cd /var/www/cab_booking_api && git pull && systemctl restart cab-api

# Check nginx
nginx -t && systemctl restart nginx
```

---

## 🎉 Success Checklist

- [ ] VPS updated and dependencies installed
- [ ] Application files uploaded
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file configured
- [ ] Systemd service created and running
- [ ] Nginx configured and running
- [ ] Firewall configured
- [ ] API accessible from internet
- [ ] Swagger UI working
- [ ] Database connection working
- [ ] Uploads directory configured

---

## 📞 Support

If you encounter any issues:

1. Check service logs: `journalctl -u cab-api -f`
2. Check nginx logs: `tail -f /var/log/nginx/error.log`
3. Verify database connection
4. Check firewall settings: `ufw status`
5. Verify .env configuration

---

**Deployment Date**: 2026-01-14  
**Server**: Hostinger VPS (72.62.196.30)  
**Application**: Cab Booking API v1.0.0
