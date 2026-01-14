# 🚀 VPS Deployment Guide

## ⚠️ SECURITY FIRST
**Change your root password immediately!**
```bash
ssh root@72.62.196.30
passwd
# Enter new secure password
```

## 📦 Step 1: Upload Files to Server

### Option A: Using Git (Recommended)
```bash
ssh root@72.62.196.30
cd /root
git clone https://github.com/PraveenCoder2007/cab_app.git
cd cab_app
```

### Option B: Using SCP from Windows
```powershell
# From your Windows machine
scp -r d:\cab_ap root@72.62.196.30:/root/cab_app
```

## 🔧 Step 2: Run Deployment Script

```bash
ssh root@72.62.196.30
cd /root/cab_app
chmod +x deploy.sh
./deploy.sh
```

This will:
- ✅ Install Python, Nginx, dependencies
- ✅ Create virtual environment
- ✅ Setup upload directories
- ✅ Configure environment variables
- ✅ Create systemd service
- ✅ Configure Nginx
- ✅ Start the API

## 🎯 Step 3: Verify Deployment

### Check API Status
```bash
systemctl status cab-api
```

### View Logs
```bash
journalctl -u cab-api -f
```

### Test API
```bash
curl http://72.62.196.30/health
```

## 🌐 Access Your API

- **API**: http://72.62.196.30
- **Docs**: http://72.62.196.30/docs
- **Health**: http://72.62.196.30/health

## 📤 Test File Upload

```bash
# Create test driver first
curl -X POST "http://72.62.196.30/api/v1/drivers" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Driver",
    "phone_number": "9876543210",
    "email": "test@example.com"
  }'

# Upload photo
curl -X POST "http://72.62.196.30/api/v1/uploads/driver/DRV001/photo" \
  -F "file=@/path/to/photo.jpg"
```

## 🔄 Update Deployment

```bash
ssh root@72.62.196.30
cd /root/cab_app
git pull
systemctl restart cab-api
```

## 🛠️ Useful Commands

```bash
# Start service
systemctl start cab-api

# Stop service
systemctl stop cab-api

# Restart service
systemctl restart cab-api

# View logs
journalctl -u cab-api -f

# Check Nginx
systemctl status nginx
nginx -t
```

## 🔍 Troubleshooting

### API not starting?
```bash
journalctl -u cab-api -n 50
```

### Database connection error?
```bash
mysql -h 72.62.196.30 -u myuser -p cab_app
```

### Nginx error?
```bash
nginx -t
tail -f /var/log/nginx/error.log
```

## 📝 Environment Variables

Located at: `/root/cab_app/.env`

```env
DB_HOST=72.62.196.30
DB_PORT=3306
DB_USER=myuser
DB_PASSWORD=Hope3Services@2026
DB_NAME=cab_app

UPLOAD_DIR=/root/uploads
BASE_URL=http://72.62.196.30/uploads
```

## ✅ Done!

Your API is now live at: **http://72.62.196.30**
