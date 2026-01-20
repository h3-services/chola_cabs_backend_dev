# VPS Upload Directory Setup Commands

Run these commands on your VPS to create the uploads directory:

```bash
# SSH into VPS
ssh root@72.62.196.30

# Create uploads directory structure
mkdir -p /root/cab_app/uploads/drivers/{photos,aadhar,licence}
mkdir -p /root/cab_app/uploads/vehicles/{rc,fc,front,back,left,right}

# Set permissions
chmod -R 755 /root/cab_app/uploads

# Verify structure
ls -la /root/cab_app/uploads/

# Check it's working
cd /root/cab_app/uploads/
pwd
```

## Alternative: Let the app create it automatically

The directory will be created automatically when:
1. The API starts (main.py creates UPLOAD_DIR)
2. First file is uploaded

To trigger automatic creation, just restart the service:
```bash
systemctl restart cab-api
```

The code in `app/main.py` line 45 will create it:
```python
os.makedirs(UPLOAD_DIR, exist_ok=True)
```

## Verify it was created
```bash
ls -la /root/cab_app/uploads/
# Should show the directory exists
```
