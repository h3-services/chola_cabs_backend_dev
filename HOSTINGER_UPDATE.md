# Hostinger Update Commands

## SSH to Hostinger VPS
```bash
ssh root@72.62.196.30
```

## Update the code
```bash
cd /root/cab_app
git pull origin main
```

## Copy updated files to service directory
```bash
cp -r /root/cab_app/app/* /var/www/cab_booking_api/app/
```

## Restart the service
```bash
sudo systemctl restart cab-api
sudo systemctl status cab-api
```

## Test the APIs
```bash
# Test error handling API
curl -X 'GET' 'http://72.62.196.30:8000/api/v1/errors/?skip=0&limit=5' -H 'accept: application/json'

# Test trip stats API
curl -X 'GET' 'http://72.62.196.30:8000/api/v1/trips/stats' -H 'accept: application/json'

# Test available drivers API
curl -X 'GET' 'http://72.62.196.30:8000/api/v1/trips/available-drivers' -H 'accept: application/json'
```

## If there are any issues, check logs
```bash
sudo journalctl -u cab-api --since "1 minute ago" --no-pager
```