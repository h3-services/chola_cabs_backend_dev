# VPS Deployment Checklist - Hostinger

## ✅ Recent Changes

### Photo URL Fix (2026-01-15)
- ✅ Added `photo_url` field to driver GET endpoints
- ✅ Updated `GET /drivers/` to return photo URLs
- ✅ Updated `GET /drivers/{driver_id}` to return photo URLs
- ✅ Created comprehensive photo API guide

## 🚀 Deployment Steps

### 1. Prepare Files for Upload

Files to upload to VPS:
```
d:\cab_ap\
├── app/                    # All application code
├── requirements.txt        # Python dependencies
├── .env                    # Production environment (create from template)
├── cab-api.service         # Systemd service file
├── nginx-cab-api.conf      # Nginx configuration
├── deploy.sh               # Deployment script
└── setup_uploads.sh        # Upload directory setup
```

### 2. Connect to VPS

```bash
ssh root@72.62.196.30
```

### 3. Upload Files to VPS

**Option A: Using SCP (from Windows)**
```powershell
scp -r d:\cab_ap root@72.62.196.30:/var/www/cab_booking_api
```

**Option B: Using Git (Recommended)**
```bash
# On VPS
cd /var/www
git clone https://github.com/your-repo/cab_booking_api.git
cd cab_booking_api
```

### 4. Setup Environment

```bash
# On VPS
cd /var/www/cab_booking_api

# Copy and edit environment file
cp env.production.template .env
nano .env

# Update these values in .env:
# - SECRET_KEY (generate new one)
# - DB_PASSWORD (if different)
# - BASE_URL (use your domain or IP)
```

### 5. Install Dependencies

```bash
# Install Python and pip
sudo apt update
sudo apt install python3 python3-pip python3-venv nginx -y

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt
```

### 6. Setup Upload Directories

```bash
# Run setup script
chmod +x setup_uploads.sh
sudo ./setup_uploads.sh

# Or manually:
sudo mkdir -p /var/www/cab_booking_api/uploads/drivers/photos
sudo mkdir -p /var/www/cab_booking_api/uploads/drivers/aadhar
sudo mkdir -p /var/www/cab_booking_api/uploads/drivers/licence
sudo mkdir -p /var/www/cab_booking_api/uploads/vehicles/rc
sudo mkdir -p /var/www/cab_booking_api/uploads/vehicles/fc
sudo mkdir -p /var/www/cab_booking_api/uploads/vehicles/front
sudo mkdir -p /var/www/cab_booking_api/uploads/vehicles/back
sudo mkdir -p /var/www/cab_booking_api/uploads/vehicles/left
sudo mkdir -p /var/www/cab_booking_api/uploads/vehicles/right

# Set permissions
sudo chown -R www-data:www-data /var/www/cab_booking_api/uploads
sudo chmod -R 755 /var/www/cab_booking_api/uploads
```

### 7. Setup Systemd Service

```bash
# Copy service file
sudo cp cab-api.service /etc/systemd/system/

# Edit if needed
sudo nano /etc/systemd/system/cab-api.service

# Enable and start service
sudo systemctl daemon-reload
sudo systemctl enable cab-api
sudo systemctl start cab-api

# Check status
sudo systemctl status cab-api
```

### 8. Setup Nginx

```bash
# Copy Nginx configuration
sudo cp nginx-cab-api.conf /etc/nginx/sites-available/cab-api

# Create symbolic link
sudo ln -s /etc/nginx/sites-available/cab-api /etc/nginx/sites-enabled/

# Remove default site (optional)
sudo rm /etc/nginx/sites-enabled/default

# Test Nginx configuration
sudo nginx -t

# Restart Nginx
sudo systemctl restart nginx
```

### 9. Configure Firewall

```bash
# Allow HTTP and HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp

# Enable firewall
sudo ufw enable
sudo ufw status
```

### 10. Test Deployment

```bash
# Test API directly
curl http://localhost:8000/

# Test through Nginx
curl http://72.62.196.30/

# Test driver endpoint with photo_url
curl http://72.62.196.30/drivers/

# Test photo upload (replace with actual driver ID)
curl -X POST "http://72.62.196.30/api/v1/uploads/driver/YOUR_DRIVER_ID/photo" \
  -F "file=@/path/to/test-photo.jpg"
```

## 🔄 Update Deployment (After Code Changes)

```bash
# On VPS
cd /var/www/cab_booking_api

# Pull latest changes (if using Git)
git pull origin main

# Or upload changed files via SCP
# scp -r d:\cab_ap\app root@72.62.196.30:/var/www/cab_booking_api/

# Activate virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Restart service
sudo systemctl restart cab-api

# Check status
sudo systemctl status cab-api

# Check logs if needed
sudo journalctl -u cab-api -f
```

## 📋 Quick Commands Reference

### Service Management
```bash
# Start service
sudo systemctl start cab-api

# Stop service
sudo systemctl stop cab-api

# Restart service
sudo systemctl restart cab-api

# Check status
sudo systemctl status cab-api

# View logs
sudo journalctl -u cab-api -f
```

### Nginx Management
```bash
# Test configuration
sudo nginx -t

# Reload configuration
sudo systemctl reload nginx

# Restart Nginx
sudo systemctl restart nginx

# Check status
sudo systemctl status nginx

# View error logs
sudo tail -f /var/log/nginx/error.log
```

### Database Connection Test
```bash
# Test MySQL connection from VPS
mysql -h 72.62.196.30 -u myuser -p cab_app
```

## 🐛 Troubleshooting

### API Not Starting
```bash
# Check logs
sudo journalctl -u cab-api -n 50

# Check if port is in use
sudo netstat -tulpn | grep 8000

# Check Python errors
cd /var/www/cab_booking_api
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Photos Not Uploading
```bash
# Check upload directory permissions
ls -la /var/www/cab_booking_api/uploads/drivers/photos/

# Fix permissions
sudo chown -R www-data:www-data /var/www/cab_booking_api/uploads
sudo chmod -R 755 /var/www/cab_booking_api/uploads

# Check Nginx upload size limit
grep client_max_body_size /etc/nginx/sites-available/cab-api
```

### Photos Not Accessible (404)
```bash
# Check Nginx configuration
sudo nginx -t

# Check if files exist
ls -la /var/www/cab_booking_api/uploads/drivers/photos/

# Check Nginx error logs
sudo tail -f /var/log/nginx/error.log
```

### Database Connection Issues
```bash
# Check .env file
cat .env | grep DB_

# Test connection
mysql -h 72.62.196.30 -u myuser -p cab_app

# Check if MySQL allows remote connections
# On database server:
sudo nano /etc/mysql/mysql.conf.d/mysqld.cnf
# Ensure bind-address = 0.0.0.0
```

## 🔐 Security Recommendations

1. **Generate New Secret Key**
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   Update in `.env` file

2. **Setup SSL/HTTPS** (Optional but recommended)
   ```bash
   sudo apt install certbot python3-certbot-nginx
   sudo certbot --nginx -d yourdomain.com
   ```

3. **Restrict Database Access**
   - Only allow connections from VPS IP
   - Use strong passwords
   - Regular backups

4. **Setup Monitoring**
   ```bash
   # Install monitoring tools
   sudo apt install htop iotop
   ```

## 📊 Monitoring

### Check API Health
```bash
curl http://72.62.196.30/
```

### Check System Resources
```bash
# CPU and Memory
htop

# Disk usage
df -h

# Upload directory size
du -sh /var/www/cab_booking_api/uploads/
```

### Check Service Logs
```bash
# Real-time logs
sudo journalctl -u cab-api -f

# Last 100 lines
sudo journalctl -u cab-api -n 100

# Errors only
sudo journalctl -u cab-api -p err
```

## ✅ Post-Deployment Verification

- [ ] API is accessible at `http://72.62.196.30/`
- [ ] Documentation is accessible at `http://72.62.196.30/docs`
- [ ] Driver endpoints return `photo_url` field
- [ ] Photo upload works correctly
- [ ] Uploaded photos are accessible via browser
- [ ] Service starts automatically on reboot
- [ ] Nginx serves static files correctly
- [ ] Database connection is working
- [ ] All CRUD operations work
- [ ] Logs are being generated

## 📱 API Endpoints to Test

```bash
# Health check
curl http://72.62.196.30/

# Get all drivers (with photo_url)
curl http://72.62.196.30/drivers/

# Get specific driver
curl http://72.62.196.30/drivers/{driver_id}

# Upload driver photo
curl -X POST "http://72.62.196.30/api/v1/uploads/driver/{driver_id}/photo" \
  -F "file=@photo.jpg"

# Access uploaded photo
curl http://72.62.196.30/uploads/drivers/photos/filename.jpg
```

## 📞 Support

If you encounter issues:
1. Check service logs: `sudo journalctl -u cab-api -f`
2. Check Nginx logs: `sudo tail -f /var/log/nginx/error.log`
3. Verify environment variables in `.env`
4. Test database connectivity
5. Check file permissions on upload directories

---

**Last Updated:** 2026-01-15
**Status:** Ready for deployment with photo URL support
