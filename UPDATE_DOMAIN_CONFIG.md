# Update BASE_URL for Production Domain

## Current Configuration Issue

Your photos are currently accessible at:
```
http://72.62.196.30/uploads/drivers/photos/filename.jpg
```

But they should be at:
```
https://api.cholacabs.in/uploads/drivers/photos/filename.jpg
```

## Fix: Update Environment Variable

### On VPS

```bash
# SSH into VPS
ssh root@72.62.196.30

# Edit .env file
nano /root/cab_app/.env

# Update this line:
BASE_URL=https://api.cholacabs.in/uploads

# Save and exit (Ctrl+X, Y, Enter)

# Restart service
systemctl restart cab-api

# Verify
systemctl status cab-api
```

### Complete .env Configuration

```env
# Database
DATABASE_URL=mysql+pymysql://root:your_password@localhost/cab_booking

# Upload Configuration
UPLOAD_DIR=/root/cab_app/uploads
BASE_URL=https://api.cholacabs.in/uploads

# App Configuration
APP_NAME=Cab Booking API
APP_VERSION=1.0.0
DEBUG=False
HOST=0.0.0.0
PORT=8000
```

## Test After Update

```bash
# Upload a test photo
curl -X POST "https://api.cholacabs.in/api/v1/uploads/driver/test-123/photo" \
  -F "file=@test.jpg"

# Response should show:
{
  "photo_url": "https://api.cholacabs.in/uploads/drivers/photos/20260119_151943_test.jpg"
}

# Access the photo
curl -I https://api.cholacabs.in/uploads/drivers/photos/20260119_151943_test.jpg
```

## Verify in Database

New uploads will have URLs like:
```
https://api.cholacabs.in/uploads/drivers/photos/...
```

Old uploads (if any) will still have:
```
http://72.62.196.30/uploads/drivers/photos/...
```

Both will work, but new ones will use the domain!

## Your API Endpoints

All accessible at your domain:
- **Swagger Docs:** https://api.cholacabs.in/docs
- **Admin API:** https://api.cholacabs.in/api/v1/admins/
- **Drivers API:** https://api.cholacabs.in/api/v1/drivers/
- **Uploads:** https://api.cholacabs.in/uploads/...
