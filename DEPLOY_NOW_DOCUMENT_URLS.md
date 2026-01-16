# 🚀 DEPLOY DOCUMENT URL CHANGES TO VPS

## Quick Deploy (Copy & Paste)

### Step 1: SSH into VPS
```bash
ssh root@72.62.196.30
```

### Step 2: Run Deployment Commands

**Copy and paste this entire block:**

```bash
cd /var/www/cab-api && \
git pull origin main && \
systemctl restart cab-api && \
systemctl status cab-api --no-pager
```

---

## ✅ What This Does

1. **Navigate** to the application directory
2. **Pull** latest changes from GitHub
3. **Restart** the cab-api service
4. **Show** service status

---

## 🧪 Test After Deployment

### Test Driver API:
```bash
curl http://localhost:8000/api/v1/drivers/ | jq '.[0]'
```

**Look for these NEW fields:**
- `aadhar_url`
- `licence_url`

### Test Vehicle API:
```bash
curl http://localhost:8000/api/v1/vehicles/ | jq '.[0]'
```

**Look for these NEW fields:**
- `rc_book_url`
- `fc_certificate_url`
- `vehicle_front_url`
- `vehicle_back_url`
- `vehicle_left_url`
- `vehicle_right_url`

---

## 📋 Changes Deployed

### Modified Files:
- ✅ `app/routers/drivers.py` - Added aadhar_url, licence_url
- ✅ `app/routers/vehicles.py` - Added 6 vehicle document URLs

### GitHub Repository:
```
https://github.com/h3-services/chola_cabs_backend_dev.git
```

### VPS Details:
- **IP:** 72.62.196.30
- **User:** root
- **App Directory:** /var/www/cab-api
- **Service:** cab-api

---

## ⚠️ If Something Goes Wrong

### Check Service Logs:
```bash
journalctl -u cab-api -n 50 --no-pager
```

### Check if Service is Running:
```bash
systemctl status cab-api
```

### Restart Service Manually:
```bash
systemctl restart cab-api
```

### Check Port 8000:
```bash
netstat -tulpn | grep 8000
```

---

## 🎯 Expected Result

After deployment, all driver and vehicle API responses will include document URLs:

**Before:**
```json
{
  "driver_id": "123",
  "name": "John Doe",
  "photo_url": "http://..."
}
```

**After:**
```json
{
  "driver_id": "123",
  "name": "John Doe",
  "photo_url": "http://...",
  "aadhar_url": "http://...",     ← NEW
  "licence_url": "http://..."     ← NEW
}
```

---

**Ready to deploy? Just copy the commands above!** 🚀
