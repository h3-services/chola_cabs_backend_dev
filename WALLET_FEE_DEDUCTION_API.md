# 🚗 Wallet Fee Deduction System - API Documentation

## Overview
Upon trip completion, the system automatically deducts 2% of the KM Cost (distance-based fare only) from the driver's wallet balance. This fee excludes driver allowance.

## 📊 Calculation Formula

```
Wallet Fee = KM Cost × 0.02
New Wallet Balance = Current Balance - Wallet Fee
```

## 🔄 Trip Completion Flow

### 1. Trip Creation
```http
POST /api/v1/trips
Content-Type: application/json

{
  "customer_name": "John Doe",
  "customer_phone": "9876543210",
  "pickup_address": "Airport",
  "drop_address": "City Center",
  "trip_type": "one_way",
  "vehicle_type": "sedan",
  "passenger_count": 2
}
```

### 2. Driver Assignment
```http
PATCH /api/v1/trips/{trip_id}/assign-driver/{driver_id}
```

### 3. Trip Start (Auto-triggered by odometer)
```http
PATCH /api/v1/trips/{trip_id}/odometer-start
Content-Type: application/json

{
  "odo_start": 12000
}
```

### 4. Trip End (Auto-triggers fee deduction)
```http
PATCH /api/v1/trips/{trip_id}/odometer-end
Content-Type: application/json

{
  "odo_end": 12150
}
```

## 💰 Fee Calculation Example

**Scenario:**
- Distance: 150 KM
- Vehicle Type: Sedan
- Trip Type: One Way
- Per KM Rate: ₹12
- Minimum KM: 130
- Driver Allowance: ₹500
- Driver's Current Wallet: ₹1000

**Calculation:**
```
Billable KM = max(150, 130) = 150 KM
KM Cost = 150 × ₹12 = ₹1800
Driver Allowance = ₹500
Total Fare = ₹1800 + ₹500 = ₹2300

Wallet Fee = ₹1800 × 0.02 = ₹36
New Wallet Balance = ₹1000 - ₹36 = ₹964
```

## 📋 API Responses After Trip Completion

### Trip Details Response
```json
{
  "trip_id": "uuid-here",
  "trip_status": "COMPLETED",
  "distance_km": 150.0,
  "fare": 2300.0,
  "odo_start": 12000,
  "odo_end": 12150,
  "ended_at": "2024-01-16T10:30:00Z"
}
```

### Driver Wallet Balance
```http
GET /api/v1/drivers/{driver_id}/wallet-balance
```

**Response:**
```json
{
  "driver_id": "driver-uuid",
  "wallet_balance": 964.0,
  "name": "Driver Name"
}
```

### Wallet Transaction Record
```http
GET /api/v1/wallet-transactions/driver/{driver_id}
```

**Response:**
```json
[
  {
    "wallet_id": "transaction-uuid",
    "driver_id": "driver-uuid",
    "trip_id": "trip-uuid",
    "amount": 36.0,
    "transaction_type": "DEBIT",
    "created_at": "2024-01-16T10:30:00Z"
  }
]
```

## 🎯 Key API Endpoints for UI

### Check Trip Fare Breakdown
```http
GET /api/v1/trips/{trip_id}/fare-breakdown
```

**Response:**
```json
{
  "trip_id": "uuid",
  "vehicle_type": "sedan",
  "trip_type": "One Way",
  "actual_distance_km": 150.0,
  "billable_km": 150.0,
  "per_km_rate": 12.0,
  "distance_fare": 1800.0,
  "driver_allowance": 500.0,
  "total_fare": 2300.0,
  "wallet_fee_deducted": 36.0
}
```

### Monitor Driver Wallet
```http
GET /api/v1/drivers/{driver_id}/wallet-balance
```

### View All Wallet Transactions
```http
GET /api/v1/wallet-transactions/driver/{driver_id}
```

## ⚠️ Important Notes

1. **Fee Calculation**: Only KM cost is used for 2% calculation, NOT total fare
2. **Negative Balance**: System allows negative wallet balance
3. **Auto-Deduction**: Fee is deducted automatically when trip status becomes "COMPLETED"
4. **Transaction Record**: Every deduction creates a wallet transaction for audit
5. **Driver Earnings**: Driver receives full fare amount separately from wallet deduction

## 🔍 UI Implementation Guide

### Display Trip Completion Summary
```javascript
// After trip completion, show:
{
  "trip_fare": "₹2300",
  "km_cost": "₹1800", 
  "driver_allowance": "₹500",
  "wallet_fee_deducted": "₹36",
  "new_wallet_balance": "₹964"
}
```

### Wallet Balance Updates
- Update driver wallet balance in real-time after trip completion
- Show wallet transaction history with trip references
- Display negative balances clearly for admin action

### Admin Dashboard
- Track total wallet fees collected
- Monitor drivers with negative balances
- View fee deduction reports by date/driver