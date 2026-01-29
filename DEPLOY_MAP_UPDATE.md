# Deploy Map Update (v3)

## Changes
Added standard **Get All Locations** endpoint alias:
- `GET /api/v1/drivers/locations`
- `GET /api/v1/drivers/locations/map` (Still works)

Both return:
- `driver_id`
- `latitude`, `longitude`
- `last_updated`
- `driver_name`
- `phone_number`
- `photo_url`

## Deployment Steps

Run these commands on your VPS:

```bash
cd /root/cab_app
git pull origin main
systemctl restart cab-api
```

## Verify
Test the new standard endpoint:
```bash
curl http://localhost:8000/api/v1/drivers/locations
```
