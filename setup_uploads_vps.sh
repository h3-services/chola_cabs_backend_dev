#!/bin/bash
# Setup uploads directory on VPS

echo "Creating uploads directory structure..."

# Create main uploads directory
mkdir -p /root/cab_app/uploads

# Create subdirectories for drivers
mkdir -p /root/cab_app/uploads/drivers/photos
mkdir -p /root/cab_app/uploads/drivers/aadhar
mkdir -p /root/cab_app/uploads/drivers/licence

# Create subdirectories for vehicles
mkdir -p /root/cab_app/uploads/vehicles/rc
mkdir -p /root/cab_app/uploads/vehicles/fc
mkdir -p /root/cab_app/uploads/vehicles/front
mkdir -p /root/cab_app/uploads/vehicles/back
mkdir -p /root/cab_app/uploads/vehicles/left
mkdir -p /root/cab_app/uploads/vehicles/right

# Set permissions (readable and writable by the app)
chmod -R 755 /root/cab_app/uploads

echo "✅ Uploads directory structure created!"
echo ""
echo "Directory structure:"
tree /root/cab_app/uploads/ || ls -R /root/cab_app/uploads/

echo ""
echo "Disk usage:"
du -sh /root/cab_app/uploads/
