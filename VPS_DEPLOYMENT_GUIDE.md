# VPS Deployment Instructions for Document URL Changes

## ✅ Code Successfully Pushed to GitHub

**Commit:** Add document URLs to driver and vehicle API responses
- Include aadhar_url and licence_url in driver endpoints
- Include all vehicle document URLs (RC, FC, photos) in vehicle endpoints

---

## 🚀 Deploy to Hostinger VPS

### Option 1: Using the Deploy Script (Recommended)

1. **Copy the deploy script to your VPS:**
   ```bash
   scp deploy_document_urls.sh root@your-vps-ip:/root/
   ```

2. **SSH into your VPS:**
   ```bash
   ssh root@your-vps-ip
   ```

3. **Run the deploy script:**
   ```bash
   chmod +x /root/deploy_document_urls.sh
   /root/deploy_document_urls.sh
   ```

---

### Option 2: Manual Deployment

**SSH into your VPS and run these commands:**

```bash
# Navigate to application directory
cd /var/www/cab-api

# Pull latest changes
git pull origin main

# Restart the service
sudo systemctl restart cab-api

# Check service status
sudo systemctl status cab-api
```

---

## 🧪 Test the Changes

After deployment, test the endpoints to verify document URLs are being returned:

### Test Driver Endpoints:
```bash
# Get all drivers
curl http://your-domain.com/api/v1/drivers/

# Get specific driver
curl http://your-domain.com/api/v1/drivers/{driver_id}
```

**Expected Response (new fields):**
```json
{
  "driver_id": "...",
  "name": "...",
  "photo_url": "http://...",
  "aadhar_url": "http://...",      ← NEW
  "licence_url": "http://...",     ← NEW
  ...
}
```

### Test Vehicle Endpoints:
```bash
# Get all vehicles
curl http://your-domain.com/api/v1/vehicles/

# Get specific vehicle
curl http://your-domain.com/api/v1/vehicles/{vehicle_id}
```

**Expected Response (new fields):**
```json
{
  "vehicle_id": 1,
  "vehicle_number": "...",
  "rc_book_url": "http://...",           ← NEW
  "fc_certificate_url": "http://...",    ← NEW
  "vehicle_front_url": "http://...",     ← NEW
  "vehicle_back_url": "http://...",      ← NEW
  "vehicle_left_url": "http://...",      ← NEW
  "vehicle_right_url": "http://...",     ← NEW
  ...
}
```

---

## 📋 What Changed

### Files Modified:
1. **`app/routers/drivers.py`**
   - Added `aadhar_url` and `licence_url` to all driver responses

2. **`app/routers/vehicles.py`**
   - Added 6 document URL fields to all vehicle responses
   - RC book, FC certificate, and 4 vehicle photo URLs

### Files Added:
- **`DOCUMENT_URLS_UPDATE.md`** - Detailed documentation of changes

---

## ⚠️ Important Notes

1. **No Database Changes Required** - All URL columns already exist in the database
2. **No Breaking Changes** - This is a backward-compatible update (only adds fields)
3. **Upload Endpoints** - Already exist and work correctly
4. **Existing Data** - URLs will be `null` for records without uploaded documents

---

## 🔍 Troubleshooting

If the service fails to start:

```bash
# Check service logs
sudo journalctl -u cab-api -n 50 --no-pager

# Check if port is in use
sudo netstat -tulpn | grep 8000

# Restart service
sudo systemctl restart cab-api
```

---

## ✨ Next Steps

After successful deployment:
1. ✅ Test the API endpoints
2. ✅ Update your UI to display the document URLs
3. ✅ Test file uploads to ensure URLs are being saved correctly

---

**Deployment Date:** 2026-01-15
**Branch:** main
**Commit Hash:** 7e6cc4d
