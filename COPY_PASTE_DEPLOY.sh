#!/bin/bash
# COPY AND PASTE THESE COMMANDS INTO YOUR VPS TERMINAL
# After running: ssh root@72.62.196.30

# ============================================
# STEP 1: Clone Repository (First Time)
# ============================================
cd /var/www
git clone https://github.com/h3-services/chola_cabs_backend_dev.git cab_booking_api
cd cab_booking_api

# ============================================
# STEP 2: Setup Environment
# ============================================
cp env.production.template .env

# Generate secret key and copy it
python3 -c "import secrets; print(secrets.token_urlsafe(32))"

# Edit .env file (paste the secret key above when prompted)
nano .env

# ============================================
# STEP 3: Deploy
# ============================================
chmod +x deploy.sh setup_uploads.sh
./deploy.sh
./setup_uploads.sh

# ============================================
# STEP 4: Check Status
# ============================================
systemctl status cab-api
curl http://72.62.196.30/
curl http://72.62.196.30/drivers/

# ============================================
# DONE! API is running at http://72.62.196.30/
# ============================================
