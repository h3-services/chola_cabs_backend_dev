# Windows Local Setup - File Uploads

## ✅ Quick Start (No Server Access Needed!)

### 1. Update your `.env` file
```env
UPLOAD_DIR=d:/cab_ap/uploads
BASE_URL=http://localhost:8000/uploads
```

### 2. Start your API
```bash
cd d:\cab_ap
python app/main.py
```

### 3. Test Upload with Postman

**Upload Driver Photo:**
```
POST http://localhost:8000/api/v1/uploads/driver/DRV001/photo
Body: form-data
  Key: file
  Type: File
  Value: [Select your image]
```

**Response:**
```json
{
  "photo_url": "http://localhost:8000/uploads/drivers/photos/20240101_120000_photo.jpg"
}
```

### 4. View Uploaded File
Open in browser: `http://localhost:8000/uploads/drivers/photos/20240101_120000_photo.jpg`

## 📁 Files Saved To
```
d:\cab_ap\uploads\
├── drivers\
│   ├── photos\
│   ├── aadhar\
│   └── licence\
└── vehicles\
    ├── rc\
    ├── fc\
    ├── front\
    ├── back\
    ├── left\
    └── right\
```

## 🎯 All Upload Endpoints

| Endpoint | Description |
|----------|-------------|
| `POST /api/v1/uploads/driver/{driver_id}/photo` | Driver photo |
| `POST /api/v1/uploads/driver/{driver_id}/aadhar` | Aadhar card |
| `POST /api/v1/uploads/driver/{driver_id}/licence` | Driving licence |
| `POST /api/v1/uploads/vehicle/{vehicle_id}/rc` | RC book |
| `POST /api/v1/uploads/vehicle/{vehicle_id}/fc` | FC certificate |
| `POST /api/v1/uploads/vehicle/{vehicle_id}/photo/front` | Vehicle front photo |
| `POST /api/v1/uploads/vehicle/{vehicle_id}/photo/back` | Vehicle back photo |
| `POST /api/v1/uploads/vehicle/{vehicle_id}/photo/left` | Vehicle left photo |
| `POST /api/v1/uploads/vehicle/{vehicle_id}/photo/right` | Vehicle right photo |

## 🚀 When You Get Server Access

Update `.env` to:
```env
UPLOAD_DIR=/root/uploads
BASE_URL=http://72.62.196.30/uploads
```

Then on server, run:
```bash
mkdir -p /root/uploads/drivers/{photos,aadhar,licence}
mkdir -p /root/uploads/vehicles/{rc,fc,front,back,left,right}
chmod -R 755 /root/uploads
```

Configure Nginx to serve `/uploads` from `/root/uploads`

## ✅ That's It!
Your file upload system is ready to use locally. URLs are automatically saved to database fields.
