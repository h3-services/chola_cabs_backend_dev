# Document URL Fields Added to API Responses

## Summary
Added document URL fields to the API responses for both **Drivers** and **Vehicles** tables, similar to how `photo_url` was already working.

## Changes Made

### 1. Driver API (`app/routers/drivers.py`)

Added the following URL fields to driver responses:
- `aadhar_url` - URL for Aadhar card document
- `licence_url` - URL for driving licence document

**Endpoints Updated:**
- `GET /api/v1/drivers/` - Get all drivers
- `GET /api/v1/drivers/{driver_id}` - Get driver by ID

**Example Response:**
```json
{
  "driver_id": "uuid-here",
  "name": "Driver Name",
  "phone_number": "1234567890",
  "email": "driver@example.com",
  "photo_url": "http://your-domain.com/uploads/drivers/profile/photo.jpg",
  "aadhar_url": "http://your-domain.com/uploads/drivers/aadhar/aadhar.jpg",
  "licence_url": "http://your-domain.com/uploads/drivers/licence/licence.jpg",
  ...
}
```

---

### 2. Vehicle API (`app/routers/vehicles.py`)

Added the following URL fields to vehicle responses:
- `rc_book_url` - URL for RC Book document
- `fc_certificate_url` - URL for FC Certificate document
- `vehicle_front_url` - URL for vehicle front photo
- `vehicle_back_url` - URL for vehicle back photo
- `vehicle_left_url` - URL for vehicle left side photo
- `vehicle_right_url` - URL for vehicle right side photo

**Endpoints Updated:**
- `GET /api/v1/vehicles/` - Get all vehicles
- `GET /api/v1/vehicles/{vehicle_id}` - Get vehicle by ID
- `GET /api/v1/vehicles/driver/{driver_id}` - Get vehicles by driver

**Example Response:**
```json
{
  "vehicle_id": 1,
  "driver_id": "uuid-here",
  "vehicle_type": "Sedan",
  "vehicle_number": "KA01AB1234",
  "rc_book_url": "http://your-domain.com/uploads/vehicles/rc/rc_book.jpg",
  "fc_certificate_url": "http://your-domain.com/uploads/vehicles/fc/fc_cert.jpg",
  "vehicle_front_url": "http://your-domain.com/uploads/vehicles/photos/front.jpg",
  "vehicle_back_url": "http://your-domain.com/uploads/vehicles/photos/back.jpg",
  "vehicle_left_url": "http://your-domain.com/uploads/vehicles/photos/left.jpg",
  "vehicle_right_url": "http://your-domain.com/uploads/vehicles/photos/right.jpg",
  ...
}
```

---

## Database Schema (Already Exists)

These URL fields already exist in the database models (`app/models.py`):

**Driver Model:**
- `photo_url` (Text)
- `aadhar_url` (Text)
- `licence_url` (Text)

**Vehicle Model:**
- `rc_book_url` (Text)
- `fc_certificate_url` (Text)
- `vehicle_front_url` (Text)
- `vehicle_back_url` (Text)
- `vehicle_left_url` (Text)
- `vehicle_right_url` (Text)

---

## Upload Endpoints (Already Exist)

The upload endpoints in `app/routers/uploads.py` already handle uploading these documents and saving the URLs to the database:

**Driver Uploads:**
- `POST /api/v1/uploads/driver/{driver_id}/photo`
- `POST /api/v1/uploads/driver/{driver_id}/aadhar`
- `POST /api/v1/uploads/driver/{driver_id}/licence`

**Vehicle Uploads:**
- `POST /api/v1/uploads/vehicle/{vehicle_id}/rc`
- `POST /api/v1/uploads/vehicle/{vehicle_id}/fc`
- `POST /api/v1/uploads/vehicle/{vehicle_id}/front`
- `POST /api/v1/uploads/vehicle/{vehicle_id}/back`
- `POST /api/v1/uploads/vehicle/{vehicle_id}/left`
- `POST /api/v1/uploads/vehicle/{vehicle_id}/right`

---

## Next Steps

1. **Restart the API** if it's running to apply the changes
2. **Test the endpoints** to verify URLs are being returned
3. **Update your UI** to display these document URLs (images, links, etc.)

## Testing

You can test the changes by:

```bash
# Get all drivers and check for URL fields
curl http://localhost:8000/api/v1/drivers/

# Get a specific driver
curl http://localhost:8000/api/v1/drivers/{driver_id}

# Get all vehicles
curl http://localhost:8000/api/v1/vehicles/

# Get a specific vehicle
curl http://localhost:8000/api/v1/vehicles/{vehicle_id}
```

All document URLs will now be included in the responses, just like `photo_url` was already working!
