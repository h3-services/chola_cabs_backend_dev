# Cab Booking API - Quick Reference

**Base URL:** `http://72.62.196.30:8000`  
**API Prefix:** `/api/v1`

---

## 🚀 Quick Start

### Interactive Documentation
- **Swagger UI:** http://72.62.196.30:8000/docs
- **ReDoc:** http://72.62.196.30:8000/redoc

---

## 📌 Common Endpoints

### System
```
GET  /                    - API info
GET  /health              - Health check
GET  /api/v1/stats        - System statistics
```

### Drivers
```
GET    /api/v1/drivers/                      - List all drivers
GET    /api/v1/drivers/{driver_id}           - Get driver details
POST   /api/v1/drivers/                      - Create driver
PUT    /api/v1/drivers/{driver_id}           - Update driver
DELETE /api/v1/drivers/{driver_id}           - Delete driver
PATCH  /api/v1/drivers/{driver_id}/availability?is_available=true
GET    /api/v1/drivers/{driver_id}/wallet-balance
```

### Vehicles
```
GET    /api/v1/vehicles/                     - List all vehicles
GET    /api/v1/vehicles/{vehicle_id}         - Get vehicle details
GET    /api/v1/vehicles/driver/{driver_id}   - Get driver's vehicles
POST   /api/v1/vehicles/                     - Create vehicle
PUT    /api/v1/vehicles/{vehicle_id}         - Update vehicle
PATCH  /api/v1/vehicles/{vehicle_id}/approve - Approve vehicle
DELETE /api/v1/vehicles/{vehicle_id}         - Delete vehicle
```

### Trips
```
GET    /api/v1/trips/                        - List all trips
GET    /api/v1/trips/{trip_id}               - Get trip details
GET    /api/v1/trips/driver/{driver_id}      - Get driver's trips
POST   /api/v1/trips/                        - Create trip
PUT    /api/v1/trips/{trip_id}               - Update trip
PATCH  /api/v1/trips/{trip_id}/assign-driver?driver_id={id}
PATCH  /api/v1/trips/{trip_id}/status?new_status=completed
DELETE /api/v1/trips/{trip_id}               - Delete trip
```

### Payments
```
GET    /api/v1/payments/                     - List all payments
GET    /api/v1/payments/{payment_id}         - Get payment details
GET    /api/v1/payments/driver/{driver_id}   - Get driver's payments
POST   /api/v1/payments/                     - Create payment
PUT    /api/v1/payments/{payment_id}         - Update payment
DELETE /api/v1/payments/{payment_id}         - Delete payment
```

### Wallet Transactions
```
GET    /api/v1/wallet-transactions/                      - List all transactions
GET    /api/v1/wallet-transactions/{transaction_id}      - Get transaction details
GET    /api/v1/wallet-transactions/driver/{driver_id}    - Get driver's transactions
POST   /api/v1/wallet-transactions/                      - Create transaction
PUT    /api/v1/wallet-transactions/{transaction_id}      - Update transaction
DELETE /api/v1/wallet-transactions/{transaction_id}      - Delete transaction
```

### Tariff Configuration
```
GET    /api/v1/tariff-config/                            - List all configs
GET    /api/v1/tariff-config/{config_id}                 - Get config details
GET    /api/v1/tariff-config/vehicle-type/{type}         - Get configs by type
GET    /api/v1/tariff-config/active/{vehicle_type}       - Get active config
POST   /api/v1/tariff-config/                            - Create config
PUT    /api/v1/tariff-config/{config_id}                 - Update config
DELETE /api/v1/tariff-config/{config_id}                 - Delete config
```

### File Uploads
```
POST   /api/v1/uploads/driver/{driver_id}/photo          - Upload driver photo
POST   /api/v1/uploads/driver/{driver_id}/aadhar         - Upload Aadhar
POST   /api/v1/uploads/driver/{driver_id}/licence        - Upload licence
POST   /api/v1/uploads/vehicle/{vehicle_id}/rc           - Upload RC book
POST   /api/v1/uploads/vehicle/{vehicle_id}/fc           - Upload FC certificate
POST   /api/v1/uploads/vehicle/{vehicle_id}/photo/{position}  - Upload vehicle photo
       (position: front, back, left, right)
```

### Raw Data (Debug)
```
GET    /api/v1/raw/drivers                   - Get drivers (raw SQL)
GET    /api/v1/raw/vehicles                  - Get vehicles (raw SQL)
GET    /api/v1/raw/trips                     - Get trips (raw SQL)
```

---

## 📝 Request Examples

### Create Driver
```bash
curl -X POST "http://72.62.196.30:8000/api/v1/drivers/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "phone_number": "9876543210",
    "email": "john@example.com",
    "primary_location": "Bangalore"
  }'
```

### Create Trip
```bash
curl -X POST "http://72.62.196.30:8000/api/v1/trips/" \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Jane Smith",
    "customer_phone": "9876543210",
    "pickup_address": "123 Main St",
    "drop_address": "456 Park Ave",
    "trip_type": "one_way",
    "vehicle_type": "Sedan"
  }'
```

### Upload File
```bash
curl -X POST "http://72.62.196.30:8000/api/v1/uploads/driver/{driver_id}/photo" \
  -F "file=@photo.jpg"
```

### Get Statistics
```bash
curl "http://72.62.196.30:8000/api/v1/stats"
```

---

## 🔑 Key Concepts

### Trip Statuses
- `pending` → `assigned` → `started` → `completed`
- `cancelled` (can be set at any time)

### Transaction Types
- `credit` - Add money
- `debit` - Deduct money

### Payment Statuses
- `pending` → `completed` / `failed`

### Vehicle Types
- Sedan, SUV, Hatchback, etc. (configurable)

### Trip Types
- `one_way` - Single journey
- `round_trip` - Return journey

---

## 📊 Response Fields

### Driver Object
```json
{
  "driver_id": "uuid",
  "name": "string",
  "phone_number": "string",
  "email": "string",
  "photo_url": "url",
  "aadhar_url": "url",
  "licence_url": "url",
  "wallet_balance": 0.00,
  "is_available": true,
  "is_approved": true
}
```

### Vehicle Object
```json
{
  "vehicle_id": 1,
  "driver_id": "uuid",
  "vehicle_type": "string",
  "vehicle_number": "string",
  "rc_book_url": "url",
  "fc_certificate_url": "url",
  "vehicle_front_url": "url",
  "vehicle_back_url": "url",
  "vehicle_left_url": "url",
  "vehicle_right_url": "url",
  "vehicle_approved": true
}
```

### Trip Object
```json
{
  "trip_id": 1,
  "customer_name": "string",
  "customer_phone": "string",
  "pickup_address": "string",
  "drop_address": "string",
  "trip_type": "one_way",
  "vehicle_type": "string",
  "assigned_driver_id": "uuid",
  "trip_status": "completed",
  "distance_km": 25.5,
  "fare": 850.00
}
```

---

## ⚠️ Common Errors

### 404 Not Found
```json
{"detail": "Driver not found"}
```

### 400 Bad Request
```json
{"detail": "Phone number already registered"}
```

### 400 Invalid File
```json
{"detail": "Invalid file type"}
```

---

## 🎯 Testing Workflow

### 1. Create Driver
```bash
POST /api/v1/drivers/
```

### 2. Upload Documents
```bash
POST /api/v1/uploads/driver/{driver_id}/photo
POST /api/v1/uploads/driver/{driver_id}/aadhar
POST /api/v1/uploads/driver/{driver_id}/licence
```

### 3. Create Vehicle
```bash
POST /api/v1/vehicles/
```

### 4. Upload Vehicle Documents
```bash
POST /api/v1/uploads/vehicle/{vehicle_id}/rc
POST /api/v1/uploads/vehicle/{vehicle_id}/fc
POST /api/v1/uploads/vehicle/{vehicle_id}/photo/front
```

### 5. Approve Vehicle
```bash
PATCH /api/v1/vehicles/{vehicle_id}/approve
```

### 6. Create Trip
```bash
POST /api/v1/trips/
```

### 7. Assign Driver
```bash
PATCH /api/v1/trips/{trip_id}/assign-driver?driver_id={id}
```

### 8. Update Trip Status
```bash
PATCH /api/v1/trips/{trip_id}/status?new_status=started
PATCH /api/v1/trips/{trip_id}/status?new_status=completed
```

### 9. Create Wallet Transaction
```bash
POST /api/v1/wallet-transactions/
```

---

## 📱 Pagination

All list endpoints support pagination:

```bash
GET /api/v1/drivers/?skip=0&limit=10
GET /api/v1/trips/?skip=20&limit=10&status_filter=completed
```

---

## 🔗 Useful Links

- **Full Documentation:** [API_DOCUMENTATION.md](file:///d:/cab_ap/API_DOCUMENTATION.md)
- **Swagger UI:** http://72.62.196.30:8000/docs
- **ReDoc:** http://72.62.196.30:8000/redoc
- **Health Check:** http://72.62.196.30:8000/health
- **API Stats:** http://72.62.196.30:8000/api/v1/stats

---

**Quick Tip:** Use the Swagger UI at `/docs` for interactive testing!
