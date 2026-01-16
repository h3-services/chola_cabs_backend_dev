# Commands to Find and Deploy the Application

## Step 1: Find the Application Directory

Run these commands to locate your application:

```bash
# Check common locations
ls -la /var/www/
ls -la /home/
ls -la /root/

# Search for the application
find /var/www -name "main.py" 2>/dev/null
find /home -name "main.py" 2>/dev/null
find /root -name "main.py" 2>/dev/null

# Check systemd service to find the working directory
systemctl cat cab-api

# Or check if service exists with different name
systemctl list-units --type=service | grep -i cab
systemctl list-units --type=service | grep -i api
```

## Step 2: Once You Find the Directory

Replace `<APP_DIRECTORY>` with the actual path and run:

```bash
cd <APP_DIRECTORY> && \
git pull origin main && \
systemctl restart cab-api && \
systemctl status cab-api --no-pager
```

---

## Common Possible Locations:

- `/root/cab-api`
- `/home/cab-api`
- `/opt/cab-api`
- `/var/www/html/cab-api`
- `/srv/cab-api`

---

## Quick Check Commands

**Copy and paste these to find your app:**

```bash
# Method 1: Check service file
systemctl cat cab-api | grep -i "WorkingDirectory\|ExecStart"

# Method 2: Search for main.py
find / -name "main.py" -path "*/app/*" 2>/dev/null | grep -v ".venv"

# Method 3: Check running processes
ps aux | grep -i uvicorn
ps aux | grep -i python | grep -i main.py
```
