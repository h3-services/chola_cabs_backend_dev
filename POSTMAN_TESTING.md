# Postman Testing Guide

## Setup Instructions

1. **Import Collection**: Import `Cab_Booking_API.postman_collection.json` into Postman
2. **Set Base URL**: Update the `base_url` variable to your server URL
3. **Start Server**: Run `python app/main.py` from the cab_ap directory

## Test Sequence

### 1. Create Tariff Configuration (Required First)
```
POST {{base_url}}/tariff-config
{
  "vehicle_type": "sedan",
  "one_way_per_km": 12.00,
  "one_way_min_km": 5,
  "round_trip_per_km": 10.00,
  "round_trip_min_km": 10,
  "driver_allowance": 200.00,
  "is_active": true
}
```

### 2. Create Driver
```
POST {{base_url}}/drivers
{
  "name": "John Doe",
  "phone_number": "9876543210",
  "email": "john@example.com",
  "primary_location": "Mumbai",
  "licence_number": "MH123456789"
}
```

### 3. Create Vehicle
```
POST {{base_url}}/vehicles
{
  "driver_id": 1,
  "vehicle_type": "sedan",
  "vehicle_brand": "Toyota",
  "vehicle_model": "Camry",
  "vehicle_number": "MH01AB1234",
  "vehicle_color": "White",
  "seating_capacity": 4
}
```

### 4. Approve Vehicle
```
PATCH {{base_url}}/vehicles/1/approve
```

### 5. Create Trip
```
POST {{base_url}}/trips
{
  "customer_name": "Jane Smith",
  "customer_phone": "9876543211",
  "pickup_address": "Mumbai Airport",
  "drop_address": "Bandra West",
  "trip_type": "one_way",
  "vehicle_type": "sedan",
  "passenger_count": 2
}
```

### 6. Assign Driver to Trip
```
PATCH {{base_url}}/trips/1/assign-driver/1
```

## All Available Endpoints

### Drivers
- GET `/drivers` - List all drivers
- GET `/drivers/{id}` - Get driver details
- POST `/drivers` - Create driver
- PUT `/drivers/{id}` - Update driver
- DELETE `/drivers/{id}` - Delete driver
- PATCH `/drivers/{id}/availability` - Update availability
- GET `/drivers/{id}/wallet-balance` - Get wallet balance

### Vehicles
- GET `/vehicles` - List all vehicles
- GET `/vehicles/{id}` - Get vehicle details
- POST `/vehicles` - Create vehicle
- PUT `/vehicles/{id}` - Update vehicle
- DELETE `/vehicles/{id}` - Delete vehicle
- PATCH `/vehicles/{id}/approve` - Approve vehicle
- GET `/vehicles/driver/{id}` - Get vehicles by driver

### Trips
- GET `/trips` - List all trips
- GET `/trips/{id}` - Get trip details
- POST `/trips` - Create trip
- PUT `/trips/{id}` - Update trip
- DELETE `/trips/{id}` - Delete trip
- PATCH `/trips/{id}/assign-driver/{driver_id}` - Assign driver
- PATCH `/trips/{id}/status` - Update status
- GET `/trips/driver/{id}` - Get trips by driver

### Payments
- GET `/payments` - List all payments
- GET `/payments/{id}` - Get payment details
- POST `/payments` - Create payment
- PUT `/payments/{id}` - Update payment
- DELETE `/payments/{id}` - Delete payment
- GET `/payments/trip/{id}` - Get payments by trip

### Wallet Transactions
- GET `/wallet-transactions` - List all transactions
- GET `/wallet-transactions/{id}` - Get transaction details
- POST `/wallet-transactions` - Create transaction
- PUT `/wallet-transactions/{id}` - Update transaction
- DELETE `/wallet-transactions/{id}` - Delete transaction
- GET `/wallet-transactions/driver/{id}` - Get transactions by driver

### Tariff Configuration
- GET `/tariff-config` - List all configs
- GET `/tariff-config/{id}` - Get config details
- POST `/tariff-config` - Create config
- PUT `/tariff-config/{id}` - Update config
- DELETE `/tariff-config/{id}` - Delete config
- GET `/tariff-config/vehicle-type/{type}` - Get configs by vehicle type
- GET `/tariff-config/active/{type}` - Get active config for vehicle type

## Server URLs
- **Local Development**: `http://localhost:8000/api/v1`
- **Production**: `http://your-server-ip:8000/api/v1`
- **Documentation**: `http://localhost:8000/docs`