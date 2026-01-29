# Deployment Commands for VPS

## Current Status
✅ Code pulled successfully from GitHub
- Updated files: 3
- New files: 1 (DRIVER_ASSIGNMENT_FIX.md)

## Next Steps

Run these commands on your VPS to complete the deployment:

```bash
# 1. Restart the cab API service
systemctl restart cab-api

# 2. Check if the service is running properly
systemctl status cab-api

# 3. View real-time logs (optional - press Ctrl+C to exit)
journalctl -u cab-api -f

# 4. Test the API health
curl http://localhost:8000/health

# 5. Test the API docs
curl http://localhost:8000/docs
```

## Quick One-Liner

If you just want to restart and check status:

```bash
systemctl restart cab-api && systemctl status cab-api
```

## Troubleshooting

If the service fails to start:

```bash
# Check detailed logs
journalctl -u cab-api -n 50 --no-pager

# Check if port 8000 is in use
netstat -tulpn | grep 8000

# Manually test the app
cd /root/cab_app
source venv/bin/activate
python -m uvicorn app.main:app --reload
```

## Verify Changes

After restarting, test the driver assignment:

1. Open admin panel: `http://admin.cholacabs.in`
2. Navigate to a pending trip
3. Try to assign both:
   - ✅ Available driver (green indicator)
   - ✅ Unavailable driver (red indicator)
4. Both should work now!

---

**Note:** The service name is `cab-api` based on your deployment configuration.
