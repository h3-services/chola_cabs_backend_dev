# 🚀 DEPLOY TO HOSTINGER VPS - STEP BY STEP GUIDE

## 📋 Pre-Deployment Checklist

- [x] Code updated with photo_url fix
- [x] Changes committed to Git
- [ ] Push changes to GitHub
- [ ] SSH into VPS
- [ ] Deploy application

---

## STEP 1: Push Latest Changes to GitHub

Run these commands in PowerShell (Windows):

```powershell
# Navigate to project directory
cd d:\cab_ap

# Push to GitHub
git push origin main
```

---

## STEP 2: SSH into Your VPS

```powershell
ssh root@72.62.196.30
```

**Password:** Enter your VPS root password when prompted

---

## STEP 3: Initial Setup (First Time Only)

If this is your first deployment, run these commands on the VPS:

```bash
# Update system
apt update && apt upgrade -y

# Install required packages
apt install -y python3 python3-pip python3-venv nginx git mysql-client

# Create application directory
mkdir -p /var/www/cab_booking_api
cd /var/www/cab_booking_api

# Clone your repository
git clone https://github.com/YOUR_USERNAME/chola_cabs_backend_dev.git .

# Or if already cloned, just pull latest
git pull origin main
```

---

## STEP 4: Setup Environment File

```bash
# Copy environment template
cp env.production.template .env

# Edit environment file
nano .env
```

**Update these values in .env:**

```env
# Database Configuration
DB_HOST=72.62.196.30
DB_PORT=3306
DB_USER=myuser
DB_PASSWORD=Hope3Services@2026
DB_NAME=cab_app

# Generate new secret key
SECRET_KEY=YOUR_GENERATED_SECRET_KEY_HERE

# Upload Configuration
UPLOAD_DIR=/var/www/cab_booking_api/uploads
BASE_URL=http://72.62.196.30/uploads

# CORS Settings
ALLOWED_ORIGINS=*
```

**Generate Secret Key:**
```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as SECRET_KEY in .env

**Save and Exit:** Press `Ctrl+X`, then `Y`, then `Enter`

---

## STEP 5: Run Deployment Script

```bash
# Make scripts executable
chmod +x deploy.sh setup_uploads.sh

# Run deployment script
./deploy.sh
```

This will:
- Install all dependencies
- Create virtual environment
- Setup systemd service
- Configure Nginx
- Start the API

---

## STEP 6: Setup Upload Directories

```bash
# Run upload setup script
./setup_uploads.sh
```

Or manually create directories:

```bash
# Create upload directories
mkdir -p /var/www/cab_booking_api/uploads/drivers/photos
mkdir -p /var/www/cab_booking_api/uploads/drivers/aadhar
mkdir -p /var/www/cab_booking_api/uploads/drivers/licence
mkdir -p /var/www/cab_booking_api/uploads/vehicles/rc
mkdir -p /var/www/cab_booking_api/uploads/vehicles/fc
mkdir -p /var/www/cab_booking_api/uploads/vehicles/front
mkdir -p /var/www/cab_booking_api/uploads/vehicles/back
mkdir -p /var/www/cab_booking_api/uploads/vehicles/left
mkdir -p /var/www/cab_booking_api/uploads/vehicles/right

# Set permissions
chown -R www-data:www-data /var/www/cab_booking_api/uploads
chmod -R 755 /var/www/cab_booking_api/uploads
```

---

## STEP 7: Verify Deployment

### Check Service Status

```bash
# Check if API service is running
systemctl status cab-api

# If not running, start it
systemctl start cab-api

# Check Nginx status
systemctl status nginx
```

### View Logs

```bash
# View API logs (real-time)
journalctl -u cab-api -f

# Press Ctrl+C to stop viewing logs

# View last 50 lines
journalctl -u cab-api -n 50
```

### Test API Endpoints

```bash
# Test root endpoint
curl http://72.62.196.30/

# Test API docs
curl http://72.62.196.30/docs

# Test drivers endpoint (should show photo_url)
curl http://72.62.196.30/drivers/

# Test specific driver
curl http://72.62.196.30/drivers/YOUR_DRIVER_ID
```

---

## STEP 8: Test Photo Upload

```bash
# Create a test image (or upload your own)
echo "fake image content" > /tmp/test.jpg

# Upload photo (replace DRIVER_ID with actual ID)
curl -X POST "http://72.62.196.30/api/v1/uploads/driver/DRIVER_ID/photo" \
  -F "file=@/tmp/test.jpg"

# Verify photo is accessible
curl -I http://72.62.196.30/uploads/drivers/photos/FILENAME.jpg
```

---

## 🔄 UPDATING DEPLOYMENT (After Code Changes)

When you make changes to your code:

### On Windows (Your Local Machine):

```powershell
cd d:\cab_ap

# Commit changes
git add .
git commit -m "Your commit message"
git push origin main
```

### On VPS:

```bash
# SSH into VPS
ssh root@72.62.196.30

# Navigate to app directory
cd /var/www/cab_booking_api

# Pull latest changes
git pull origin main

# Activate virtual environment
source venv/bin/activate

# Install any new dependencies
pip install -r requirements.txt

# Restart service
systemctl restart cab-api

# Check status
systemctl status cab-api

# View logs
journalctl -u cab-api -f
```

---

## 🐛 TROUBLESHOOTING

### API Not Starting

```bash
# Check detailed logs
journalctl -u cab-api -n 100 --no-pager

# Check if port 8000 is in use
netstat -tulpn | grep 8000

# Try running manually to see errors
cd /var/www/cab_booking_api
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Database Connection Error

```bash
# Test database connection
mysql -h 72.62.196.30 -u myuser -p cab_app

# If fails, check .env file
cat .env | grep DB_

# Verify database credentials
```

### Photo Upload Fails

```bash
# Check upload directory permissions
ls -la /var/www/cab_booking_api/uploads/drivers/photos/

# Fix permissions
chown -R www-data:www-data /var/www/cab_booking_api/uploads
chmod -R 755 /var/www/cab_booking_api/uploads

# Check Nginx configuration
nginx -t

# Restart Nginx
systemctl restart nginx
```

### Photo URL Returns 404

```bash
# Check if file exists
ls -la /var/www/cab_booking_api/uploads/drivers/photos/

# Check Nginx error logs
tail -f /var/log/nginx/error.log

# Verify Nginx is serving /uploads
curl -I http://72.62.196.30/uploads/
```

---

## 📊 MONITORING COMMANDS

```bash
# Check service status
systemctl status cab-api

# View real-time logs
journalctl -u cab-api -f

# Check system resources
htop

# Check disk usage
df -h

# Check upload directory size
du -sh /var/www/cab_booking_api/uploads/

# Check Nginx access logs
tail -f /var/log/nginx/access.log

# Check Nginx error logs
tail -f /var/log/nginx/error.log
```

---

## 🔐 SECURITY CHECKLIST

- [ ] Changed SECRET_KEY in .env
- [ ] Firewall configured (ports 22, 80, 443)
- [ ] Database uses strong password
- [ ] Upload directory has correct permissions (755)
- [ ] Nginx configured with upload size limit
- [ ] Regular backups configured

---

## 📱 ACCESS YOUR API

Once deployed, your API will be accessible at:

- **API Root:** http://72.62.196.30/
- **API Documentation:** http://72.62.196.30/docs
- **Drivers Endpoint:** http://72.62.196.30/drivers/
- **Upload Photo:** http://72.62.196.30/api/v1/uploads/driver/{id}/photo
- **Static Files:** http://72.62.196.30/uploads/

---

## ✅ DEPLOYMENT COMPLETE!

Your Cab Booking API is now running on Hostinger VPS with:
- ✅ Profile photo upload support
- ✅ Photo URLs in driver API responses
- ✅ Static file serving via Nginx
- ✅ Automatic service restart on reboot
- ✅ Production-ready configuration

---

## 📞 QUICK REFERENCE

**Start Service:** `systemctl start cab-api`  
**Stop Service:** `systemctl stop cab-api`  
**Restart Service:** `systemctl restart cab-api`  
**View Logs:** `journalctl -u cab-api -f`  
**Test API:** `curl http://72.62.196.30/`  
**Update Code:** `git pull && systemctl restart cab-api`

---

**Need Help?** Check the detailed guides:
- [PHOTO_API_GUIDE.md](file:///d:/cab_ap/PHOTO_API_GUIDE.md)
- [VPS_DEPLOYMENT_CHECKLIST.md](file:///d:/cab_ap/VPS_DEPLOYMENT_CHECKLIST.md)
