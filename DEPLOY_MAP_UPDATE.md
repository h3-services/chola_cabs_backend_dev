# Deploy Map Update (v2)

## Changes
The `/drivers/locations/map` endpoint has been updated to include **phone number**:
- `driver_id`
- `latitude`
- `longitude`
- `last_updated`
- `driver_name`
- `phone_number` (NEW)
- `photo_url`

## Deployment Steps

Run these commands on your VPS:

```bash
cd /root/cab_app
git pull origin main
systemctl restart cab-api
```

## Verify
Test the endpoint:
```bash
curl http://localhost:8000/api/v1/drivers/locations/map
```
