# Cab Booking API - Complete Documentation

**Version:** 1.0.0  
**Base URL:** `http://your-domain.com` or `http://72.62.196.30:8000`  
**API Prefix:** `/api/v1`

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Base Endpoints](#base-endpoints)
4. [Driver APIs](#driver-apis)
5. [Vehicle APIs](#vehicle-apis)
6. [Trip APIs](#trip-apis)
7. [Payment APIs](#payment-apis)
8. [Wallet Transaction APIs](#wallet-transaction-apis)
9. [Tariff Configuration APIs](#tariff-configuration-apis)
10. [File Upload APIs](#file-upload-apis)
11. [Raw Data APIs](#raw-data-apis)
12. [Error Handling](#error-handling)
13. [Response Codes](#response-codes)

---

## Overview

The Cab Booking API is a production-ready RESTful API for managing a complete cab booking system. It provides endpoints for managing drivers, vehicles, trips, payments, wallet transactions, and tariff configurations.

### Key Features

- ✅ Driver management with KYC verification
- ✅ Vehicle registration and approval
- ✅ Trip booking and assignment
- ✅ Payment processing
- ✅ Wallet transactions
- ✅ Dynamic tariff configuration
- ✅ File uploads for documents and photos
- ✅ CORS enabled for cross-origin requests

---

## Authentication

Currently, the API does not require authentication. **For production use, implement proper authentication mechanisms.**

---

## Base Endpoints

### 1. Root Endpoint

**GET** `/`

Get API information and status.

**Response:**
```json
{
  "message": "Cab Booking API",
  "version": "1.0.0",
  "status": "running",
  "docs": "/docs",
  "redoc": "/redoc"
}
```

---

### 2. Health Check

**GET** `/health`

Check API and database health status.

**Response:**
```json
{
  "status": "healthy",
  "database": "connected",
  "version": "1.0.0"
}
```

---

### 3. API Statistics

**GET** `/api/v1/stats`

Get system-wide statistics.

**Response:**
```json
{
  "drivers": {
    "total": 50,
    "active": 35,
    "inactive": 15
  },
  "vehicles": {
    "total": 45,
    "approved": 40,
    "pending_approval": 5
  },
  "trips": {
    "total": 1250,
    "pending": 5,
    "completed": 1200
  }
}
```

---

## Driver APIs

Base Path: `/api/v1/drivers`

### 1. Get All Drivers

**GET** `/api/v1/drivers/`

Get all drivers with pagination.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100)

**Response:**
```json
[
  {
    "driver_id": "uuid-string",
    "name": "John Doe",
    "phone_number": "9876543210",
    "email": "john@example.com",
    "kyc_verified": true,
    "primary_location": "Bangalore",
    "photo_url": "http://domain.com/uploads/drivers/photos/photo.jpg",
    "aadhar_url": "http://domain.com/uploads/drivers/aadhar/aadhar.jpg",
    "licence_url": "http://domain.com/uploads/drivers/licence/licence.jpg",
    "wallet_balance": 5000.00,
    "is_available": true,
    "is_approved": true,
    "created_at": "2026-01-15T10:30:00",
    "updated_at": "2026-01-15T10:30:00"
  }
]
```

---

### 2. Get Driver by ID

**GET** `/api/v1/drivers/{driver_id}`

Get specific driver details.

**Path Parameters:**
- `driver_id` (string, required): Driver's unique ID

**Response:** Same as single driver object above

---

### 3. Create Driver

**POST** `/api/v1/drivers/`

Create a new driver.

**Request Body:**
```json
{
  "name": "John Doe",
  "phone_number": "9876543210",
  "email": "john@example.com",
  "primary_location": "Bangalore",
  "licence_number": "KA01234567890",
  "aadhar_number": "123456789012",
  "licence_expiry": "2028-12-31"
}
```

**Response:**
```json
{
  "driver_id": "generated-uuid",
  "name": "John Doe",
  "phone_number": "9876543210",
  "email": "john@example.com",
  "message": "Driver created successfully"
}
```

---

### 4. Update Driver

**PUT** `/api/v1/drivers/{driver_id}`

Update driver information.

**Path Parameters:**
- `driver_id` (string, required): Driver's unique ID

**Request Body:** (All fields optional)
```json
{
  "name": "John Updated",
  "email": "newemail@example.com",
  "primary_location": "Mumbai",
  "is_available": false
}
```

**Response:** Updated driver object

---

### 5. Update Driver Availability

**PATCH** `/api/v1/drivers/{driver_id}/availability`

Update driver's availability status.

**Path Parameters:**
- `driver_id` (string, required): Driver's unique ID

**Query Parameters:**
- `is_available` (boolean, required): Availability status

**Response:**
```json
{
  "message": "Driver availability updated to available",
  "driver_id": "uuid-string",
  "is_available": true
}
```

---

### 6. Get Driver Wallet Balance

**GET** `/api/v1/drivers/{driver_id}/wallet-balance`

Get driver's current wallet balance.

**Response:**
```json
{
  "driver_id": "uuid-string",
  "wallet_balance": 5000.00,
  "name": "John Doe"
}
```

---

### 7. Delete Driver

**DELETE** `/api/v1/drivers/{driver_id}`

Delete a driver.

**Response:**
```json
{
  "message": "Driver deleted successfully",
  "driver_id": "uuid-string"
}
```

---

## Vehicle APIs

Base Path: `/api/v1/vehicles`

### 1. Get All Vehicles

**GET** `/api/v1/vehicles/`

Get all vehicles with pagination.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100)

**Response:**
```json
[
  {
    "vehicle_id": 1,
    "driver_id": "uuid-string",
    "vehicle_type": "Sedan",
    "vehicle_brand": "Toyota",
    "vehicle_model": "Camry",
    "vehicle_number": "KA01AB1234",
    "vehicle_color": "White",
    "seating_capacity": 4,
    "vehicle_approved": true,
    "rc_book_url": "http://domain.com/uploads/vehicles/rc/rc.jpg",
    "fc_certificate_url": "http://domain.com/uploads/vehicles/fc/fc.jpg",
    "vehicle_front_url": "http://domain.com/uploads/vehicles/front/front.jpg",
    "vehicle_back_url": "http://domain.com/uploads/vehicles/back/back.jpg",
    "vehicle_left_url": "http://domain.com/uploads/vehicles/left/left.jpg",
    "vehicle_right_url": "http://domain.com/uploads/vehicles/right/right.jpg",
    "created_at": "2026-01-15T10:30:00",
    "updated_at": "2026-01-15T10:30:00"
  }
]
```

---

### 2. Get Vehicle by ID

**GET** `/api/v1/vehicles/{vehicle_id}`

Get specific vehicle details.

**Path Parameters:**
- `vehicle_id` (int, required): Vehicle's unique ID

**Response:** Same as single vehicle object above

---

### 3. Get Vehicles by Driver

**GET** `/api/v1/vehicles/driver/{driver_id}`

Get all vehicles belonging to a specific driver.

**Path Parameters:**
- `driver_id` (string, required): Driver's unique ID

**Response:** Array of vehicle objects

---

### 4. Create Vehicle

**POST** `/api/v1/vehicles/`

Add a new vehicle to a driver.

**Request Body:**
```json
{
  "driver_id": "uuid-string",
  "vehicle_type": "Sedan",
  "vehicle_brand": "Toyota",
  "vehicle_model": "Camry",
  "vehicle_number": "KA01AB1234",
  "vehicle_color": "White",
  "seating_capacity": 4,
  "rc_expiry_date": "2028-12-31",
  "fc_expiry_date": "2027-06-30"
}
```

**Response:**
```json
{
  "vehicle_id": 1,
  "driver_id": "uuid-string",
  "vehicle_number": "KA01AB1234",
  "message": "Vehicle created successfully"
}
```

---

### 5. Update Vehicle

**PUT** `/api/v1/vehicles/{vehicle_id}`

Update vehicle information.

**Path Parameters:**
- `vehicle_id` (int, required): Vehicle's unique ID

**Request Body:** (All fields optional)
```json
{
  "vehicle_color": "Black",
  "seating_capacity": 5
}
```

**Response:**
```json
{
  "vehicle_id": 1,
  "message": "Vehicle updated successfully"
}
```

---

### 6. Approve Vehicle

**PATCH** `/api/v1/vehicles/{vehicle_id}/approve`

Approve a vehicle for operations.

**Response:**
```json
{
  "message": "Vehicle approved successfully",
  "vehicle_id": 1,
  "vehicle_number": "KA01AB1234",
  "approved": true
}
```

---

### 7. Delete Vehicle

**DELETE** `/api/v1/vehicles/{vehicle_id}`

Delete a vehicle.

**Response:**
```json
{
  "message": "Vehicle deleted successfully",
  "vehicle_id": 1,
  "vehicle_number": "KA01AB1234"
}
```

---

## Trip APIs

Base Path: `/api/v1/trips`

### 1. Get All Trips

**GET** `/api/v1/trips/`

Get all trips with optional status filter.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip (default: 0)
- `limit` (int, optional): Maximum records to return (default: 100)
- `status_filter` (string, optional): Filter by trip status

**Trip Statuses:**
- `pending` - Trip created, awaiting driver assignment
- `assigned` - Driver assigned to trip
- `started` - Trip in progress
- `completed` - Trip completed
- `cancelled` - Trip cancelled

**Response:**
```json
[
  {
    "trip_id": 1,
    "customer_name": "Jane Smith",
    "customer_phone": "9876543210",
    "pickup_address": "123 Main St, Bangalore",
    "drop_address": "456 Park Ave, Bangalore",
    "trip_type": "one_way",
    "vehicle_type": "Sedan",
    "assigned_driver_id": "uuid-string",
    "trip_status": "completed",
    "distance_km": 25.5,
    "fare": 850.00,
    "started_at": "2026-01-15T10:00:00",
    "ended_at": "2026-01-15T11:30:00",
    "created_at": "2026-01-15T09:45:00"
  }
]
```

---

### 2. Get Trip by ID

**GET** `/api/v1/trips/{trip_id}`

Get specific trip details.

**Path Parameters:**
- `trip_id` (int, required): Trip's unique ID

**Response:** Same as single trip object above

---

### 3. Create Trip

**POST** `/api/v1/trips/`

Create a new trip booking.

**Request Body:**
```json
{
  "customer_name": "Jane Smith",
  "customer_phone": "9876543210",
  "pickup_address": "123 Main St, Bangalore",
  "drop_address": "456 Park Ave, Bangalore",
  "trip_type": "one_way",
  "vehicle_type": "Sedan",
  "planned_start_at": "2026-01-15T10:00:00",
  "passenger_count": 2
}
```

**Response:**
```json
{
  "trip_id": 1,
  "customer_name": "Jane Smith",
  "trip_status": "pending",
  "message": "Trip created successfully"
}
```

---

### 4. Update Trip

**PUT** `/api/v1/trips/{trip_id}`

Update trip information.

**Request Body:** (All fields optional)
```json
{
  "pickup_address": "Updated address",
  "distance_km": 30.0,
  "fare": 1000.00
}
```

---

### 5. Assign Driver to Trip

**PATCH** `/api/v1/trips/{trip_id}/assign-driver`

Assign a driver to a trip.

**Query Parameters:**
- `driver_id` (string, required): Driver's unique ID

**Response:**
```json
{
  "message": "Driver assigned successfully",
  "trip_id": 1,
  "driver_id": "uuid-string",
  "driver_name": "John Doe"
}
```

---

### 6. Update Trip Status

**PATCH** `/api/v1/trips/{trip_id}/status`

Update trip status.

**Query Parameters:**
- `new_status` (string, required): New status (pending, assigned, started, completed, cancelled)

**Response:**
```json
{
  "message": "Trip status updated to completed",
  "trip_id": 1,
  "status": "completed"
}
```

---

### 7. Get Trips by Driver

**GET** `/api/v1/trips/driver/{driver_id}`

Get all trips assigned to a specific driver.

**Path Parameters:**
- `driver_id` (string, required): Driver's unique ID

**Response:** Array of trip objects

---

### 8. Create Driver Request

**POST** `/api/v1/trips/{trip_id}/driver-request`

Create a driver request for a trip.

**Query Parameters:**
- `driver_id` (int, required): Driver's ID

**Response:**
```json
{
  "message": "Driver request created successfully",
  "request_id": 1,
  "trip_id": 1,
  "driver_id": "uuid-string"
}
```

---

### 9. Delete Trip

**DELETE** `/api/v1/trips/{trip_id}`

Delete a trip.

**Response:**
```json
{
  "message": "Trip deleted successfully",
  "trip_id": 1
}
```

---

## Payment APIs

Base Path: `/api/v1/payments`

### 1. Get All Payments

**GET** `/api/v1/payments/`

Get all payment transactions.

**Query Parameters:**
- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Maximum records to return

**Response:**
```json
[
  {
    "payment_id": 1,
    "driver_id": "uuid-string",
    "amount": 5000.00,
    "transaction_id": "TXN123456",
    "transaction_type": "credit",
    "status": "completed",
    "created_at": "2026-01-15T10:30:00"
  }
]
```

---

### 2. Get Payment by ID

**GET** `/api/v1/payments/{payment_id}`

Get specific payment details.

---

### 3. Create Payment

**POST** `/api/v1/payments/`

Create a new payment transaction.

**Request Body:**
```json
{
  "driver_id": "uuid-string",
  "amount": 5000.00,
  "transaction_id": "TXN123456",
  "transaction_type": "credit",
  "status": "pending"
}
```

**Transaction Types:**
- `credit` - Money added to driver account
- `debit` - Money deducted from driver account

**Status Values:**
- `pending` - Payment initiated
- `completed` - Payment successful
- `failed` - Payment failed

---

### 4. Update Payment

**PUT** `/api/v1/payments/{payment_id}`

Update payment information.

---

### 5. Delete Payment

**DELETE** `/api/v1/payments/{payment_id}`

Delete a payment transaction.

---

### 6. Get Payments by Driver

**GET** `/api/v1/payments/driver/{driver_id}`

Get all payments for a specific driver.

---

## Wallet Transaction APIs

Base Path: `/api/v1/wallet-transactions`

### 1. Get All Wallet Transactions

**GET** `/api/v1/wallet-transactions/`

Get all wallet transactions.

**Response:**
```json
[
  {
    "wallet_id": 1,
    "driver_id": "uuid-string",
    "trip_id": 1,
    "payment_id": 1,
    "amount": 850.00,
    "transaction_type": "credit",
    "created_at": "2026-01-15T11:30:00"
  }
]
```

---

### 2. Get Wallet Transaction by ID

**GET** `/api/v1/wallet-transactions/{transaction_id}`

Get specific wallet transaction details.

---

### 3. Create Wallet Transaction

**POST** `/api/v1/wallet-transactions/`

Create a new wallet transaction.

**Request Body:**
```json
{
  "driver_id": "uuid-string",
  "trip_id": 1,
  "amount": 850.00,
  "transaction_type": "credit"
}
```

> **Note:** This automatically updates the driver's wallet balance.

---

### 4. Update Wallet Transaction

**PUT** `/api/v1/wallet-transactions/{transaction_id}`

Update wallet transaction information.

---

### 5. Delete Wallet Transaction

**DELETE** `/api/v1/wallet-transactions/{transaction_id}`

Delete a wallet transaction.

---

### 6. Get Wallet Transactions by Driver

**GET** `/api/v1/wallet-transactions/driver/{driver_id}`

Get all wallet transactions for a specific driver.

---

## Tariff Configuration APIs

Base Path: `/api/v1/tariff-config`

### 1. Get All Tariff Configurations

**GET** `/api/v1/tariff-config/`

Get all tariff configurations.

**Response:**
```json
[
  {
    "tariff_id": 1,
    "vehicle_type": "Sedan",
    "one_way_per_km": 12.00,
    "round_trip_per_km": 10.00,
    "driver_allowance": 500.00,
    "one_way_min_km": 80,
    "round_trip_min_km": 250,
    "is_active": true,
    "created_at": "2026-01-15T10:00:00",
    "updated_at": "2026-01-15T10:00:00"
  }
]
```

---

### 2. Get Tariff Config by ID

**GET** `/api/v1/tariff-config/{config_id}`

Get specific tariff configuration.

---

### 3. Create Tariff Configuration

**POST** `/api/v1/tariff-config/`

Create a new tariff configuration.

**Request Body:**
```json
{
  "vehicle_type": "SUV",
  "one_way_per_km": 15.00,
  "round_trip_per_km": 12.00,
  "driver_allowance": 600.00,
  "one_way_min_km": 80,
  "round_trip_min_km": 250,
  "is_active": true
}
```

---

### 4. Update Tariff Configuration

**PUT** `/api/v1/tariff-config/{config_id}`

Update tariff configuration.

---

### 5. Delete Tariff Configuration

**DELETE** `/api/v1/tariff-config/{config_id}`

Delete a tariff configuration.

---

### 6. Get Tariff by Vehicle Type

**GET** `/api/v1/tariff-config/vehicle-type/{vehicle_type}`

Get all tariff configurations for a specific vehicle type.

---

### 7. Get Active Tariff Configuration

**GET** `/api/v1/tariff-config/active/{vehicle_type}`

Get the active tariff configuration for a vehicle type.

---

## File Upload APIs

Base Path: `/api/v1/uploads`

### Driver Document Uploads

#### 1. Upload Driver Photo

**POST** `/api/v1/uploads/driver/{driver_id}/photo`

Upload driver profile photo.

**Request:**
- Content-Type: `multipart/form-data`
- Body: `file` (image file)

**Allowed Formats:** .jpg, .jpeg, .png, .pdf

**Response:**
```json
{
  "photo_url": "http://domain.com/uploads/drivers/photos/20260115_103000_photo.jpg"
}
```

---

#### 2. Upload Aadhar Card

**POST** `/api/v1/uploads/driver/{driver_id}/aadhar`

Upload driver's Aadhar card document.

**Response:**
```json
{
  "aadhar_url": "http://domain.com/uploads/drivers/aadhar/20260115_103000_aadhar.jpg"
}
```

---

#### 3. Upload Driving Licence

**POST** `/api/v1/uploads/driver/{driver_id}/licence`

Upload driver's driving licence.

**Response:**
```json
{
  "licence_url": "http://domain.com/uploads/drivers/licence/20260115_103000_licence.jpg"
}
```

---

### Vehicle Document Uploads

#### 4. Upload RC Book

**POST** `/api/v1/uploads/vehicle/{vehicle_id}/rc`

Upload vehicle RC book.

**Response:**
```json
{
  "rc_book_url": "http://domain.com/uploads/vehicles/rc/20260115_103000_rc.jpg"
}
```

---

#### 5. Upload FC Certificate

**POST** `/api/v1/uploads/vehicle/{vehicle_id}/fc`

Upload vehicle FC certificate.

**Response:**
```json
{
  "fc_certificate_url": "http://domain.com/uploads/vehicles/fc/20260115_103000_fc.jpg"
}
```

---

#### 6. Upload Vehicle Photos

**POST** `/api/v1/uploads/vehicle/{vehicle_id}/photo/{position}`

Upload vehicle photos from different angles.

**Path Parameters:**
- `position` (string, required): Photo position - `front`, `back`, `left`, or `right`

**Response:**
```json
{
  "vehicle_front_url": "http://domain.com/uploads/vehicles/front/20260115_103000_front.jpg"
}
```

---

## Raw Data APIs

Base Path: `/api/v1/raw`

These endpoints use raw SQL queries to bypass validation (useful for debugging).

### 1. Get Drivers (Raw)

**GET** `/api/v1/raw/drivers`

Get drivers using raw SQL (limited to 10 records).

---

### 2. Get Vehicles (Raw)

**GET** `/api/v1/raw/vehicles`

Get vehicles using raw SQL (limited to 10 records).

---

### 3. Get Trips (Raw)

**GET** `/api/v1/raw/trips`

Get trips using raw SQL (limited to 10 records).

---

## Error Handling

The API uses standard HTTP status codes and returns errors in the following format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common Error Responses

**404 Not Found:**
```json
{
  "detail": "Driver not found"
}
```

**400 Bad Request:**
```json
{
  "detail": "Phone number already registered"
}
```

**500 Internal Server Error:**
```json
{
  "detail": "Error fetching stats: Database connection failed"
}
```

---

## Response Codes

| Code | Description |
|------|-------------|
| 200 | OK - Request successful |
| 201 | Created - Resource created successfully |
| 400 | Bad Request - Invalid input data |
| 404 | Not Found - Resource not found |
| 500 | Internal Server Error - Server error |

---

## Interactive Documentation

The API provides interactive documentation:

- **Swagger UI:** `http://your-domain.com/docs`
- **ReDoc:** `http://your-domain.com/redoc`

These interfaces allow you to:
- View all endpoints
- Test API calls directly
- See request/response schemas
- Download OpenAPI specification

---

## Example Usage

### Using cURL

#### Create a Driver
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

#### Upload Driver Photo
```bash
curl -X POST "http://72.62.196.30:8000/api/v1/uploads/driver/{driver_id}/photo" \
  -F "file=@/path/to/photo.jpg"
```

#### Get All Trips
```bash
curl "http://72.62.196.30:8000/api/v1/trips/?status_filter=completed"
```

---

### Using Python (requests)

```python
import requests

BASE_URL = "http://72.62.196.30:8000"

# Create a driver
response = requests.post(
    f"{BASE_URL}/api/v1/drivers/",
    json={
        "name": "John Doe",
        "phone_number": "9876543210",
        "email": "john@example.com",
        "primary_location": "Bangalore"
    }
)
driver = response.json()
print(f"Created driver: {driver['driver_id']}")

# Upload photo
with open("photo.jpg", "rb") as f:
    files = {"file": f}
    response = requests.post(
        f"{BASE_URL}/api/v1/uploads/driver/{driver['driver_id']}/photo",
        files=files
    )
    print(response.json())

# Get all drivers
response = requests.get(f"{BASE_URL}/api/v1/drivers/")
drivers = response.json()
print(f"Total drivers: {len(drivers)}")
```

---

### Using JavaScript (fetch)

```javascript
const BASE_URL = "http://72.62.196.30:8000";

// Create a driver
async function createDriver() {
  const response = await fetch(`${BASE_URL}/api/v1/drivers/`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      name: "John Doe",
      phone_number: "9876543210",
      email: "john@example.com",
      primary_location: "Bangalore"
    })
  });
  
  const driver = await response.json();
  console.log('Created driver:', driver.driver_id);
  return driver;
}

// Get all trips
async function getTrips() {
  const response = await fetch(`${BASE_URL}/api/v1/trips/`);
  const trips = await response.json();
  console.log('Total trips:', trips.length);
  return trips;
}
```

---

## Best Practices

1. **Pagination:** Always use `skip` and `limit` parameters for large datasets
2. **Error Handling:** Always check response status codes and handle errors
3. **File Uploads:** Ensure files are in allowed formats (.jpg, .jpeg, .png, .pdf)
4. **Status Updates:** Follow the correct trip status flow: pending → assigned → started → completed
5. **Wallet Transactions:** Always verify driver balance before debit operations
6. **Vehicle Approval:** Approve vehicles only after verifying all documents

---

## Support & Contact

For API support or questions:
- **Documentation:** `/docs` or `/redoc`
- **Health Check:** `/health`
- **API Stats:** `/api/v1/stats`

---

**Last Updated:** January 15, 2026  
**API Version:** 1.0.0
