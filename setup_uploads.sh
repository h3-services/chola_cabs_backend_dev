#!/bin/bash
# Server Setup Script for File Uploads with IP Access

echo "🚀 Setting up file upload system..."

# Create upload directories
mkdir -p /root/uploads/drivers/{photos,aadhar,licence}
mkdir -p /root/uploads/vehicles/{rc,fc,front,back,left,right}

# Set permissions
chmod -R 755 /root/uploads

echo "✅ Upload directories created"

# Configure Nginx to serve static files
cat > /etc/nginx/sites-available/uploads <<'EOF'
server {
    listen 80;
    server_name 72.62.196.30;

    # Serve uploaded files
    location /uploads/ {
        alias /root/uploads/;
        autoindex off;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Proxy API requests
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        client_max_body_size 10M;
    }
}
EOF

# Enable site
ln -sf /etc/nginx/sites-available/uploads /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Test and reload Nginx
nginx -t && systemctl reload nginx

echo "✅ Nginx configured"
echo ""
echo "📝 Update your .env file with:"
echo "UPLOAD_DIR=/root/uploads"
echo "BASE_URL=http://72.62.196.30/uploads"
echo ""
echo "✅ Setup complete!"
