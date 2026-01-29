# Driver Map Locations Feature

## Overview
Added an endpoint to fetch all active driver locations with essential details for displaying on the admin dashboard map.

## API Endpoint

**GET** `/drivers/locations/map`

### Response
Returns a list of driver locations with simplified details:

```json
[
  {
    "driver_id": "uuid...",
    "latitude": 12.9716,
    "longitude": 77.5946,
    "last_updated": "2026-01-29T10:00:00",
    "driver_name": "Sanjeev",
    "photo_url": "https://api.cholacabs.in/uploads/drivers/photos/..."
  }
]
```

## Code Changes
- **Schemas**: Updated `DriverLocationWithDetails`.
- **CRUD**: Added `get_all` to `CRUDDriverLocation` with eager loading.
- **Router**: Added `/drivers/locations/map` endpoint.

## Deployment
1. Pull latest code.
2. Restart service.
