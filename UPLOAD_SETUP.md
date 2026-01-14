# Quick Setup for File Uploads (IP-Based)

## 1. SSH into your server
```bash
ssh root@72.62.196.30
```

## 2. Navigate to your project
```bash
cd /root/cab_app
```

## 3. Run setup script
```bash
chmod +x setup_uploads.sh
./setup_uploads.sh
```

## 4. Update .env file
```bash
nano .env
```

Add these lines:
```env
UPLOAD_DIR=/root/uploads
BASE_URL=http://72.62.196.30/uploads
```

## 5. Restart your API service
```bash
systemctl restart cab-api
```

## ✅ Done! Test the upload

### Using curl:
```bash
curl -X POST "http://72.62.196.30/api/v1/uploads/driver/DRV001/photo" \
  -F "file=@/path/to/photo.jpg"
```

### Response:
```json
{
  "photo_url": "http://72.62.196.30/uploads/drivers/photos/20240101_120000_photo.jpg"
}
```

## 📁 File Structure
```
/root/uploads/
├── drivers/
│   ├── photos/
│   ├── aadhar/
│   └── licence/
└── vehicles/
    ├── rc/
    ├── fc/
    ├── front/
    ├── back/
    ├── left/
    └── right/
```

## 🔗 Access Files
Files will be accessible at:
- `http://72.62.196.30/uploads/drivers/photos/filename.jpg`
- `http://72.62.196.30/uploads/drivers/aadhar/filename.pdf`
- etc.

## 📝 API Endpoints
- `POST /api/v1/uploads/driver/{driver_id}/photo`
- `POST /api/v1/uploads/driver/{driver_id}/aadhar`
- `POST /api/v1/uploads/driver/{driver_id}/licence`
- `POST /api/v1/uploads/vehicle/{vehicle_id}/rc`
- `POST /api/v1/uploads/vehicle/{vehicle_id}/fc`
- `POST /api/v1/uploads/vehicle/{vehicle_id}/photo/{position}`

Position: `front`, `back`, `left`, `right`
