# 🚖 Fare & Cost Calculation Logic (V2)

## 📌 Overview

This document details the complete logic for calculating Trip Fares, Extra Charges, Total Cost to Customer, and Driver Commission.

---

## 💰 1. The Core Formulae

### **A. Base Fare Calculation**
The Base Fare is calculated strictly based on the **Distance** traveled and the **Vehicle Tariff**. This is the amount used for calculating the platform commission.

```math
Base Fare = Billable Distance × Per KM Rate
```

*   **Billable Distance**: The greater of `Actual Distance` or `Minimum Distance`.
*   **Per KM Rate**: Derived from `VehicleTariffConfig` based on vehicle type and trip type.

**Minimum Distance Rules:**
*   **One Way**: Minimum **130 KM** (or as configured in DB)
*   **Round Trip**: Minimum **250 KM** (or as configured in DB)

---

### **B. Total Customer Cost**
The total amount the customer pays includes the Base Fare plus all legitimate extra charges.

```math
Total Cost = Base Fare + Extra Charges
```

**Where Extra Charges include:**
1.  **Waiting Charges**: Cost for delays (e.g., ₹150).
2.  **Inter-State Permit**: Fee for crossing state lines (e.g., ₹800).
3.  **Driver Allowance**: Daily allowance for the driver (e.g., ₹400).
4.  **Luggage Cost**: Extra charge for heavy luggage (e.g., ₹300).
5.  **Pet Cost**: Charge for carrying pets (e.g., ₹0).
6.  **Toll Charges**: Actual toll fees paid (e.g., ₹550).
7.  **Night Allowance**: Extra charge for night driving (e.g., ₹0).

> **Note**: These extra charges are passed **100% to the driver** and are **NOT** subject to platform commission.

---

### **C. Driver Commission (Wallet Deduction)**
The platform commission is deducted from the Driver's Wallet.

```math
Commission = Base Fare × Commission %
```

*   **Commission %**: Default is 10%, or as configured in `VehicleTariffConfig`.
*   **Important**: Commission is **NOT** applied to the Extra Charges.

---

## 📝 2. Calculation Examples

### **Scenario: One Way Trip (Innova)**

**Tariff Config:**
*   Rate: ₹15/km
*   Min KM: 130 km
*   Commission: 10%

**Trip Data:**
*   Distance: 216 km
*   Waiting: ₹150
*   Permit: ₹800
*   Allowance: ₹400
*   Luggage: ₹300
*   Toll: ₹550

#### **Step 1: Calculate Base Fare**
*   Actual Distance: 216 km
*   Minimum Distance: 130 km
*   **Billable Distance**: 216 km (since 216 > 130)
*   **Base Fare** = 216 × ₹15 = **₹3,240.00**

#### **Step 2: Calculate Total Cost (For Customer)**
*   Sum of Extras: 150 + 800 + 400 + 300 + 550 = **₹2,200**
*   **Total Cost** = ₹3,240 (Fare) + ₹2,200 (Extras)
*   **Total Cost = ₹5,440.00**

#### **Step 3: Calculate Commission (From Driver)**
*   **Commission** = ₹3,240 × 10% = **₹324.00**

---

## 🗄️ 3. Database Schema

The `trips` table has been updated to store these values explicitly.

| Column Name | Type | Description |
| :--- | :--- | :--- |
| `distance_km` | DECIMAL | Actual distance traveled |
| `fare` | DECIMAL | **Base Fare** (Subject to commission) |
| `total_amount` | DECIMAL | **Total Cost** (Fare + Extras) |
| `waiting_charges` | DECIMAL | Extra Charge |
| `inter_state_permit_charges` | DECIMAL | Extra Charge |
| `driver_allowance` | DECIMAL | Extra Charge |
| `luggage_cost` | DECIMAL | Extra Charge |
| `pet_cost` | DECIMAL | Extra Charge |
| `toll_charges` | DECIMAL | Extra Charge |
| `night_allowance` | DECIMAL | Extra Charge |

---

## 🔌 4. API Implementation Guide

### **Update Trip (Before Closing)**
When the driver enters the extra charges in the app, send a `PUT` or `PATCH` request to update the trip details.

**Endpoint:** `PUT /trips/{trip_id}`

**Request Body:**
```json
{
  "waiting_charges": 150.00,
  "inter_state_permit_charges": 800.00,
  "driver_allowance": 400.00,
  "luggage_cost": 300.00,
  "toll_charges": 550.00,
  "night_allowance": 0.00
}
```

### **Close Trip (End Odometer)**
When the trip is ended, the system automatically calculates the final amounts.

**Endpoint:** `PATCH /trips/{trip_id}/odometer/end`
**Query Param:** `odo_end=12345`

**Response:**
```json
{
  "trip_id": "...",
  "distance_km": 216.0,
  "fare": 3240.0,
  "total_amount": 5440.0,
  "commission_deducted": 324.0,
  "wallet_updated": true
}
```
