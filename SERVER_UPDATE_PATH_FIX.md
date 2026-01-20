# Server Update Commands - Fix Upload Path

## Run these commands on your Hostinger VPS:

```bash
# 1. Navigate to correct directory
cd /root/chola_cabs_backend_dev

# 2. Pull latest changes
git pull origin main

# 3. Create uploads directory if it doesn't exist
mkdir -p uploads/drivers/{photos,aadhar,licence}
mkdir -p uploads/vehicles/{front,back,left,right,rc,fc}

# 4. Set proper permissions
chmod -R 755 uploads/

# 5. Restart service
sudo systemctl restart chola-cabs

# 6. Check status
sudo systemctl status chola-cabs

# 7. Test the API
curl -s http://localhost:8000/health
```

## What was fixed:
- Changed default upload directory from `/root/cab_app/uploads` to `/root/chola_cabs_backend_dev/uploads`
- This matches where your service is actually running from

## After update, test:
- PUT /api/v1/uploads/driver/{driver_id}/photo should work now