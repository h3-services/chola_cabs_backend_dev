# Driver Live Location Feature

## Overview
A new dedicated table `driver_live_location` has been added to store real-time driver coordinates. This segregates high-frequency location updates from the main `drivers` table, improving performance and database organization.

## Database Changes
- **New Table:** `driver_live_location`
  - `driver_id` (PK, FK to drivers)
  - `latitude` (DECIMAL 10,8)
  - `longitude` (DECIMAL 11,8)
  - `last_updated` (TIMESTAMP)

## Code Changes

### 1. Models (`app/models.py`)
- Added `DriverLiveLocation` class.

### 2. Schemas (`app/schemas.py`)
- Added `DriverLocationUpdate` and `DriverLocationResponse`.

### 3. CRUD (`app/crud/crud_driver_location.py`)
- Created separate CRUD module to handle location operations.

### 4. API (`app/routers/drivers.py`)
- **POST** `/drivers/{driver_id}/location`: Update lat/long.
- **GET** `/drivers/{driver_id}/location`: Get current lat/long.

## Deployment Instructions

1. **Pull Changes:**
   ```bash
   git pull origin main
   ```

2. **Database Migration:**
   Since we added a new table, you need to update the database schema. If using Alembic, run migrations. If running manually, execute the SQL provided in the request:
   ```sql
   CREATE TABLE driver_live_location (
     driver_id CHAR(36) PRIMARY KEY,
     latitude DECIMAL(10,8) NOT NULL,
     longitude DECIMAL(11,8) NOT NULL,
     last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
     CONSTRAINT fk_driver_location_driver FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE
   );
   ```

3. **Restart Service:**
   ```bash
   systemctl restart cab-api
   ```

## Usage Example

**Update Location:**
```http
POST /drivers/{driver_id}/location
Content-Type: application/json

{
  "latitude": 12.9716,
  "longitude": 77.5946
}
```

**Get Location:**
```http
GET /drivers/{driver_id}/location
```
