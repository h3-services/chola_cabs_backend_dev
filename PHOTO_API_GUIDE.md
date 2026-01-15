# Profile Photo API Guide

## ✅ Fixed Issues

The driver API endpoints now include `photo_url` in their responses, enabling proper profile photo display in your UI.

## 📡 Available APIs

### 1. Upload Driver Profile Photo

**Endpoint:** `POST /api/v1/uploads/driver/{driver_id}/photo`

**Request:**
```http
POST /api/v1/uploads/driver/{driver_id}/photo
Content-Type: multipart/form-data

Body: file (image file)
```

**Supported formats:** `.jpg`, `.jpeg`, `.png`, `.pdf`

**Response:**
```json
{
  "photo_url": "http://72.62.196.30/uploads/drivers/photos/20260115_123456_photo.jpg"
}
```

### 2. Get Driver Details (with photo_url)

**Endpoint:** `GET /drivers/{driver_id}`

**Response:**
```json
{
  "driver_id": "uuid-here",
  "name": "Driver Name",
  "phone_number": "1234567890",
  "email": "driver@example.com",
  "kyc_verified": true,
  "primary_location": "Location",
  "photo_url": "http://72.62.196.30/uploads/drivers/photos/20260115_123456_photo.jpg",
  "wallet_balance": 1000.00,
  "is_available": true,
  "is_approved": true,
  "created_at": "2026-01-15T12:00:00",
  "updated_at": "2026-01-15T12:00:00"
}
```

### 3. Get All Drivers (with photo_url)

**Endpoint:** `GET /drivers/?skip=0&limit=100`

**Response:**
```json
[
  {
    "driver_id": "uuid-here",
    "name": "Driver Name",
    "phone_number": "1234567890",
    "email": "driver@example.com",
    "kyc_verified": true,
    "primary_location": "Location",
    "photo_url": "http://72.62.196.30/uploads/drivers/photos/20260115_123456_photo.jpg",
    "wallet_balance": 1000.00,
    "is_available": true,
    "is_approved": true,
    "created_at": "2026-01-15T12:00:00",
    "updated_at": "2026-01-15T12:00:00"
  }
]
```

## 🎨 UI Implementation Examples

### Example 1: HTML + JavaScript (Vanilla)

```html
<!DOCTYPE html>
<html>
<head>
    <title>Driver Profile</title>
    <style>
        .driver-card {
            border: 1px solid #ddd;
            border-radius: 8px;
            padding: 20px;
            max-width: 400px;
            margin: 20px auto;
        }
        .profile-photo {
            width: 150px;
            height: 150px;
            border-radius: 50%;
            object-fit: cover;
            display: block;
            margin: 0 auto 20px;
        }
        .driver-info {
            text-align: center;
        }
    </style>
</head>
<body>
    <div id="driverProfile"></div>

    <script>
        const API_BASE = 'http://72.62.196.30';
        
        async function loadDriverProfile(driverId) {
            try {
                const response = await fetch(`${API_BASE}/drivers/${driverId}`);
                const driver = await response.json();
                displayDriver(driver);
            } catch (error) {
                console.error('Error loading driver:', error);
            }
        }
        
        function displayDriver(driver) {
            const photoUrl = driver.photo_url || 'https://via.placeholder.com/150';
            
            const html = `
                <div class="driver-card">
                    <img src="${photoUrl}" alt="${driver.name}" class="profile-photo" 
                         onerror="this.src='https://via.placeholder.com/150'">
                    <div class="driver-info">
                        <h2>${driver.name}</h2>
                        <p>📞 ${driver.phone_number}</p>
                        <p>📧 ${driver.email || 'N/A'}</p>
                        <p>💰 Balance: ₹${driver.wallet_balance}</p>
                        <p>Status: ${driver.is_available ? '✅ Available' : '❌ Unavailable'}</p>
                    </div>
                </div>
            `;
            
            document.getElementById('driverProfile').innerHTML = html;
        }
        
        // Load driver profile (replace with actual driver ID)
        loadDriverProfile('your-driver-id-here');
    </script>
</body>
</html>
```

### Example 2: Upload Photo Form

```html
<!DOCTYPE html>
<html>
<head>
    <title>Upload Driver Photo</title>
    <style>
        .upload-form {
            max-width: 400px;
            margin: 50px auto;
            padding: 20px;
            border: 1px solid #ddd;
            border-radius: 8px;
        }
        .preview {
            width: 200px;
            height: 200px;
            margin: 20px auto;
            border: 2px dashed #ddd;
            display: flex;
            align-items: center;
            justify-content: center;
            overflow: hidden;
        }
        .preview img {
            max-width: 100%;
            max-height: 100%;
        }
    </style>
</head>
<body>
    <div class="upload-form">
        <h2>Upload Driver Photo</h2>
        <input type="text" id="driverId" placeholder="Enter Driver ID" required>
        <div class="preview" id="preview">
            <span>No image selected</span>
        </div>
        <input type="file" id="photoFile" accept="image/jpeg,image/jpg,image/png">
        <button onclick="uploadPhoto()">Upload Photo</button>
        <div id="result"></div>
    </div>

    <script>
        const API_BASE = 'http://72.62.196.30';
        
        // Preview image before upload
        document.getElementById('photoFile').addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    document.getElementById('preview').innerHTML = 
                        `<img src="${e.target.result}" alt="Preview">`;
                };
                reader.readAsDataURL(file);
            }
        });
        
        async function uploadPhoto() {
            const driverId = document.getElementById('driverId').value;
            const fileInput = document.getElementById('photoFile');
            const file = fileInput.files[0];
            
            if (!driverId || !file) {
                alert('Please enter driver ID and select a photo');
                return;
            }
            
            const formData = new FormData();
            formData.append('file', file);
            
            try {
                const response = await fetch(
                    `${API_BASE}/api/v1/uploads/driver/${driverId}/photo`,
                    {
                        method: 'POST',
                        body: formData
                    }
                );
                
                const result = await response.json();
                
                if (response.ok) {
                    document.getElementById('result').innerHTML = 
                        `<p style="color: green;">✅ Photo uploaded successfully!</p>
                         <p>URL: ${result.photo_url}</p>`;
                } else {
                    document.getElementById('result').innerHTML = 
                        `<p style="color: red;">❌ Upload failed: ${result.detail}</p>`;
                }
            } catch (error) {
                document.getElementById('result').innerHTML = 
                    `<p style="color: red;">❌ Error: ${error.message}</p>`;
            }
        }
    </script>
</body>
</html>
```

### Example 3: React Component

```jsx
import React, { useState, useEffect } from 'react';

const API_BASE = 'http://72.62.196.30';

function DriverProfile({ driverId }) {
  const [driver, setDriver] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDriver();
  }, [driverId]);

  const fetchDriver = async () => {
    try {
      const response = await fetch(`${API_BASE}/drivers/${driverId}`);
      const data = await response.json();
      setDriver(data);
    } catch (error) {
      console.error('Error fetching driver:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) return <div>Loading...</div>;
  if (!driver) return <div>Driver not found</div>;

  return (
    <div className="driver-profile">
      <img 
        src={driver.photo_url || 'https://via.placeholder.com/150'} 
        alt={driver.name}
        onError={(e) => e.target.src = 'https://via.placeholder.com/150'}
        style={{
          width: '150px',
          height: '150px',
          borderRadius: '50%',
          objectFit: 'cover'
        }}
      />
      <h2>{driver.name}</h2>
      <p>📞 {driver.phone_number}</p>
      <p>📧 {driver.email || 'N/A'}</p>
      <p>💰 Balance: ₹{driver.wallet_balance}</p>
      <p>Status: {driver.is_available ? '✅ Available' : '❌ Unavailable'}</p>
    </div>
  );
}

function PhotoUpload({ driverId, onUploadSuccess }) {
  const [file, setFile] = useState(null);
  const [preview, setPreview] = useState(null);
  const [uploading, setUploading] = useState(false);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      const reader = new FileReader();
      reader.onloadend = () => setPreview(reader.result);
      reader.readAsDataURL(selectedFile);
    }
  };

  const handleUpload = async () => {
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setUploading(true);
    try {
      const response = await fetch(
        `${API_BASE}/api/v1/uploads/driver/${driverId}/photo`,
        {
          method: 'POST',
          body: formData
        }
      );

      const result = await response.json();
      
      if (response.ok) {
        alert('Photo uploaded successfully!');
        onUploadSuccess && onUploadSuccess(result.photo_url);
      } else {
        alert('Upload failed: ' + result.detail);
      }
    } catch (error) {
      alert('Error: ' + error.message);
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      {preview && <img src={preview} alt="Preview" style={{ width: '200px' }} />}
      <input type="file" accept="image/*" onChange={handleFileChange} />
      <button onClick={handleUpload} disabled={!file || uploading}>
        {uploading ? 'Uploading...' : 'Upload Photo'}
      </button>
    </div>
  );
}

export { DriverProfile, PhotoUpload };
```

## 🚀 Deployment on Hostinger VPS

### File Storage Configuration

The photos are stored on your VPS at:
```
/var/www/cab_booking_api/uploads/drivers/photos/
```

And served via Nginx at:
```
http://72.62.196.30/uploads/drivers/photos/filename.jpg
```

### Important Notes

1. **Upload Directory Permissions**
   ```bash
   sudo mkdir -p /var/www/cab_booking_api/uploads/drivers/photos
   sudo chown -R www-data:www-data /var/www/cab_booking_api/uploads
   sudo chmod -R 755 /var/www/cab_booking_api/uploads
   ```

2. **Environment Variables** (in `.env` on VPS)
   ```
   UPLOAD_DIR=/var/www/cab_booking_api/uploads
   BASE_URL=http://72.62.196.30/uploads
   ```

3. **Nginx Configuration** (already configured in `nginx-cab-api.conf`)
   - Static files served from `/uploads` location
   - 10MB upload size limit
   - 30-day cache for uploaded images

4. **Testing Photo Upload**
   ```bash
   curl -X POST "http://72.62.196.30/api/v1/uploads/driver/YOUR_DRIVER_ID/photo" \
     -F "file=@/path/to/photo.jpg"
   ```

5. **Testing Photo Retrieval**
   ```bash
   curl "http://72.62.196.30/drivers/YOUR_DRIVER_ID"
   ```

## 🔒 Security Considerations

1. **File Validation**: Only `.jpg`, `.jpeg`, `.png`, `.pdf` files are allowed
2. **File Size**: Limited to 10MB (configured in Nginx)
3. **Unique Filenames**: Timestamp prefix prevents overwriting
4. **No Directory Listing**: `autoindex off` in Nginx config

## 📱 Mobile App Integration

For Flutter/React Native apps, use the same endpoints:

```dart
// Flutter example
Future<String> uploadDriverPhoto(String driverId, File imageFile) async {
  var request = http.MultipartRequest(
    'POST',
    Uri.parse('http://72.62.196.30/api/v1/uploads/driver/$driverId/photo'),
  );
  
  request.files.add(await http.MultipartFile.fromPath('file', imageFile.path));
  
  var response = await request.send();
  var responseData = await response.stream.bytesToString();
  var jsonData = json.decode(responseData);
  
  return jsonData['photo_url'];
}
```

## ✅ Checklist for VPS Deployment

- [x] Fixed `photo_url` in driver API responses
- [ ] Deploy updated code to VPS
- [ ] Create upload directories with correct permissions
- [ ] Update `.env` file with production values
- [ ] Restart the API service
- [ ] Test photo upload endpoint
- [ ] Test photo retrieval in driver GET endpoint
- [ ] Verify photos are accessible via browser

## 🆘 Troubleshooting

**Photo not uploading:**
- Check upload directory permissions
- Verify file size is under 10MB
- Check file extension is allowed

**Photo URL returns 404:**
- Verify Nginx is serving `/uploads` location
- Check file exists in `/var/www/cab_booking_api/uploads/drivers/photos/`
- Verify Nginx configuration is loaded

**Photo URL is null:**
- Make sure you uploaded a photo first
- Check database has `photo_url` value for the driver
