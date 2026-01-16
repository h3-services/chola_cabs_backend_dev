# 🚀 Hostinger VPS Deployment Guide

## Server Details
- **IP**: 72.62.196.30
- **SSH**: `ssh root@72.62.196.30`
- **Database**: MySQL on same server
- **Port**: 8000

---

## 📋 Quick Deployment (One Command)

### Step 1: SSH into VPS
```bash
ssh root@72.62.196.30
```

### Step 2: Run Deployment Script
```bash
curl -sSL https://raw.githubusercontent.com/h3-services/chola_cabs_backend_dev/main/deploy_vps.sh | bash
```

---

## 🔧 Manual Deployment Steps

### 1. SSH into Server
```bash
ssh root@72.62.196.30
```

### 2. Clone Repository
```bash
cd /root
git clone https://github.com/h3-services/chola_cabs_backend_dev.git
cd chola_cabs_backend_dev
```

### 3. Setup Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure Environment
```bash
cp .env.production .env
# Edit if needed: nano .env
```

### 5. Create Upload Directories
```bash
mkdir -p uploads/drivers/{photos,aadhar,licence}
mkdir -p uploads/vehicles/{rc,fc,front,back,left,right}
```

### 6. Setup Systemd Service
```bash
cp chola-cabs.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable chola-cabs
systemctl start chola-cabs
```

### 7. Check Status
```bash
systemctl status chola-cabs
```

---

## 🌐 Access Your API

- **API Base**: http://72.62.196.30:8000
- **Documentation**: http://72.62.196.30:8000/docs
- **Health Check**: http://72.62.196.30:8000/health
- **Stats**: http://72.62.196.30:8000/api/v1/stats

---

## 📊 Service Management

### Check Status
```bash
systemctl status chola-cabs
```

### View Logs (Real-time)
```bash
journalctl -u chola-cabs -f
```

### View Last 100 Lines
```bash
journalctl -u chola-cabs -n 100
```

### Restart Service
```bash
systemctl restart chola-cabs
```

### Stop Service
```bash
systemctl stop chola-cabs
```

### Start Service
```bash
systemctl start chola-cabs
```

---

## 🔄 Update Deployment

When you push new code to GitHub:

```bash
ssh root@72.62.196.30
cd /root/chola_cabs_backend_dev
git pull
systemctl restart chola-cabs
```

---

## 🐛 Troubleshooting

### Check if Service is Running
```bash
systemctl status chola-cabs
```

### Check Logs for Errors
```bash
journalctl -u chola-cabs -n 50
```

### Test Database Connection
```bash
mysql -h 72.62.196.30 -u myuser -p cab_app
# Password: Hope3Services@2026
```

### Check Port 8000
```bash
netstat -tulpn | grep 8000
```

### Manual Test Run
```bash
cd /root/chola_cabs_backend_dev
source venv/bin/activate
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

---

## 🔒 Security Notes

1. **Firewall**: Ensure port 8000 is open
   ```bash
   ufw allow 8000
   ```

2. **HTTPS**: Consider setting up Nginx with SSL
3. **Environment**: Never commit `.env` file
4. **Database**: Use strong passwords

---

## 📝 Quick Commands Reference

```bash
# Deploy/Update
cd /root/chola_cabs_backend_dev && git pull && systemctl restart chola-cabs

# View logs
journalctl -u chola-cabs -f

# Check status
systemctl status chola-cabs

# Restart
systemctl restart chola-cabs
```

---

## ✅ Post-Deployment Checklist

- [ ] API responds at http://72.62.196.30:8000
- [ ] Health check returns "healthy"
- [ ] Database connection works
- [ ] Can create driver via API
- [ ] Can create vehicle via API
- [ ] Can create trip via API
- [ ] File uploads work
- [ ] Service auto-starts on reboot

---

## 🆘 Support

If issues occur:
1. Check logs: `journalctl -u chola-cabs -n 100`
2. Verify database: `mysql -h 72.62.196.30 -u myuser -p cab_app`
3. Check service: `systemctl status chola-cabs`
4. Test manually: `source venv/bin/activate && python -m uvicorn app.main:app`
