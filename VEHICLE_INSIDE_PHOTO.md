# Vehicle Inside Photo Support

## Database Changes
The `vehicles` table has been updated to include a new column:
```sql
ALTER TABLE vehicles ADD COLUMN vehicle_inside_url VARCHAR(255) NULL;
```
*(You mentioned you already added this to your DB)*

## Code Changes

### 1. Models (`app/models.py`)
- Updated `Vehicle` model to include `vehicle_inside_url`.

### 2. Schemas (`app/schemas.py`)
- Updated `VehicleResponse` to return the new URL.
- Updated `VehicleUpdate` to allow optional updates.

### 3. Uploads (`app/routers/uploads.py`)
- Updated `upload_vehicle_photo` endpoint to accept `position="inside"`.
- Updated `reupload_vehicle_photo` endpoint to accept `position="inside"`.

## Usage
You can now upload a photo for the vehicle interior:

**POST** `api/v1/uploads/vehicle/{vehicle_id}/photo/inside`
```bash
curl -X POST "http://your-api/api/v1/uploads/vehicle/123/photo/inside" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@inside_photo.jpg"
```
