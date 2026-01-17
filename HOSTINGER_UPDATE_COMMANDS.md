# Hostinger VPS Update Commands

## SSH to Hostinger VPS
```bash
ssh root@72.62.196.30
```

## Navigate to project directory
```bash
cd /root/cab_app
```

## Pull latest changes
```bash
git pull origin main
```

## Restart the service
```bash
sudo systemctl restart cab-api
```

## Check service status
```bash
sudo systemctl status cab-api
```

## Test the fixed endpoint
```bash
curl -X 'GET' 'http://72.62.196.30:8000/api/v1/errors/?skip=0&limit=5' -H 'accept: application/json'
```

## View logs if needed
```bash
sudo journalctl -u cab-api -f
```