# Deploy Map Update

## Changes
The `/drivers/locations/map` endpoint has been updated to return simplified data as requested:
- `driver_id`
- `latitude`
- `longitude`
- `last_updated`
- `driver_name`
- `photo_url`

## Deployment Steps

Run these commands on your VPS:

```bash
cd /root/cab_app
git pull origin main
systemctl restart cab-api
```

## Verify
Test the endpoint (it should now include `photo_url` and exclude unnecessary fields):

```bash
curl http://localhost:8000/api/v1/drivers/locations/map
```
