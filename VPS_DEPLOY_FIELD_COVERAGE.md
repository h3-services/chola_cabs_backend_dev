# VPS Deployment Commands - Copy and Paste

## Step 1: Connect to VPS
```bash
ssh root@72.62.196.30
```

## Step 2: Navigate to Application Directory
```bash
cd /root/cab_app
```

## Step 3: Pull Latest Code
```bash
git pull origin main
```

## Step 4: Restart Service
```bash
systemctl restart cab-api
```

## Step 5: Check Service Status
```bash
systemctl status cab-api
```

## Step 6: Test API Health
```bash
curl http://localhost:8000/health | python3 -m json.tool
```

## Step 7: Verify Complete Fields (Optional)
```bash
# Test drivers endpoint
curl http://localhost:8000/api/v1/drivers/ | python3 -m json.tool | head -n 50

# Test vehicles endpoint
curl http://localhost:8000/api/v1/vehicles/ | python3 -m json.tool | head -n 50

# Test trips endpoint
curl http://localhost:8000/api/v1/trips/ | python3 -m json.tool | head -n 50
```

## All-in-One Command (Run after SSH login)
```bash
cd /root/cab_app && git pull origin main && systemctl restart cab-api && sleep 2 && systemctl status cab-api --no-pager && curl http://localhost:8000/health | python3 -m json.tool
```

---

## What Changed in This Deployment

### Drivers Endpoint
- Added: `licence_number`, `aadhar_number`, `licence_expiry`, `device_id`, `errors`
- Total fields: **19**

### Vehicles Endpoint
- Added: `rc_expiry_date`, `fc_expiry_date`, `errors`
- Total fields: **20**

### Trips Endpoint
- Added: `distance_km`, `odo_start`, `odo_end`, `started_at`, `ended_at`, `updated_at`, `planned_start_at`, `planned_end_at`, `is_manual_assignment`, `passenger_count`, `errors`
- Total fields: **22**

All GET endpoints now return complete data sets with no missing fields!
