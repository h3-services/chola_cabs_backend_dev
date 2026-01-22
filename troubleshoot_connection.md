# Connection Troubleshooting Guide

## 1. Check if API is Running Locally
```bash
# Test local connection first
curl http://localhost:8000/health
# or
curl http://127.0.0.1:8000/health
```

## 2. Check Server Status (if deployed)
```bash
# SSH into your server
ssh username@api.cholacabs.in

# Check if service is running
sudo systemctl status cab-api

# Check if port 8000 is listening
sudo netstat -tlnp | grep :8000
# or
sudo ss -tlnp | grep :8000
```

## 3. Check Firewall Settings
```bash
# Check if port 8000 is open
sudo ufw status
sudo iptables -L

# Open port 8000 if needed
sudo ufw allow 8000
```

## 4. Check DNS Resolution
```bash
# Test if domain resolves
nslookup api.cholacabs.in
ping api.cholacabs.in
```

## 5. Common Fixes

### Start the Service
```bash
# If service is stopped
sudo systemctl start cab-api
sudo systemctl enable cab-api

# Check logs
sudo journalctl -u cab-api -f
```

### Check Application Logs
```bash
# View recent logs
sudo journalctl -u cab-api -n 100

# Check for errors
sudo journalctl -u cab-api | grep -i error
```

### Restart Service
```bash
sudo systemctl restart cab-api
```