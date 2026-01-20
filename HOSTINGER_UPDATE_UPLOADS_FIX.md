# Hostinger VPS Update - Uploads API Fix

## Quick Update Commands

```bash
# 1. Navigate to app directory
cd /root/cab_app

# 2. Pull latest changes
git pull origin main

# 3. Restart the service
sudo systemctl restart chola-cabs

# 4. Check service status
sudo systemctl status chola-cabs

# 5. Check logs (optional)
sudo journalctl -u chola-cabs -f --lines=20
```

## What was fixed:
- Fixed PUT endpoints in uploads API that were causing internal server errors
- Removed extra parameters from save_file function calls
- All upload re-upload endpoints now work correctly

## Test the fix:
- Test PUT endpoints: `/api/v1/uploads/driver/{driver_id}/photo`, `/api/v1/uploads/driver/{driver_id}/aadhar`, etc.
- Should return success responses instead of internal server errors

## If service fails to start:
```bash
# Check detailed logs
sudo journalctl -u chola-cabs -n 50

# Check if port is in use
sudo lsof -i :8000

# Manual restart if needed
sudo systemctl stop chola-cabs
sudo systemctl start chola-cabs
```