# Fare Calculation Logic - Documentation

## ✅ **Current Implementation**

### **Fare Calculation Formula:**
```
Fare = Odometer Distance × Per KM Rate
```

**Where:**
- **Odometer Distance** = `odo_end - odo_start` (in kilometers)
- **Per KM Rate** = Based on trip type:
  - One Way: `tariff.one_way_per_km`
  - Round Trip: `tariff.round_trip_per_km`

---

## 📊 **What is Stored vs What is Calculated**

### **Stored in Database (VehicleTariffConfig):**
```sql
vehicle_tariff_config:
  - vehicle_type (e.g., "Sedan", "SUV")
  - one_way_per_km (e.g., 12.00)
  - round_trip_per_km (e.g., 10.00)
  - driver_allowance (e.g., 500.00) ✅ STORED BUT NOT USED IN FARE
  - one_way_min_km (e.g., 130)
  - round_trip_min_km (e.g., 750)
```

### **Calculated for Trip:**
```python
# Step 1: Get odometer readings
odo_start = 1000  # Starting odometer reading
odo_end = 1250    # Ending odometer reading

# Step 2: Calculate distance
distance_km = odo_end - odo_start  # = 250 km

# Step 3: Get per km rate from tariff
per_km_rate = tariff.one_way_per_km  # = 12.00

# Step 4: Calculate fare (ONLY distance × rate)
fare = distance_km × per_km_rate  # = 250 × 12.00 = 3000.00

# NOTE: driver_allowance is NOT added to fare!
```

---

## 🎯 **Important Notes**

### **✅ What IS Included in Fare:**
1. **Odometer distance** (`odo_end - odo_start`)
2. **Per kilometer rate** (from tariff config)

### **❌ What is NOT Included in Fare:**
1. **Driver allowance** - Stored in tariff config but NOT added to fare
2. **Minimum kilometers** - Only used for validation, not calculation
3. **Any fixed charges** - Not part of current calculation

---

## 💡 **Why Driver Allowance is Stored**

The `driver_allowance` field is stored in the tariff configuration for:
- **Reference purposes** - To know what allowance is given
- **Admin dashboard** - To display allowance information
- **Future calculations** - May be used for driver settlements
- **Reporting** - To track allowance vs commission

**But it is NOT added to the trip fare calculation!**

---

## 📝 **Example Calculations**

### **Example 1: One Way Trip (Sedan)**

**Tariff Config:**
```json
{
  "vehicle_type": "Sedan",
  "one_way_per_km": 12.00,
  "driver_allowance": 500.00
}
```

**Trip Data:**
```json
{
  "trip_type": "One Way",
  "odo_start": 1000,
  "odo_end": 1250
}
```

**Calculation:**
```
Distance = 1250 - 1000 = 250 km
Fare = 250 × 12.00 = ₹3,000.00

Note: driver_allowance (500.00) is NOT added!
```

---

### **Example 2: Round Trip (SUV)**

**Tariff Config:**
```json
{
  "vehicle_type": "SUV",
  "round_trip_per_km": 10.00,
  "driver_allowance": 600.00
}
```

**Trip Data:**
```json
{
  "trip_type": "Round Trip",
  "odo_start": 5000,
  "odo_end": 5400
}
```

**Calculation:**
```
Distance = 5400 - 5000 = 400 km
Billable Distance = 750 km (Minimum 750 km applied)
Fare = 750 × 10.00 = ₹7,500.00

Note: driver_allowance (600.00) is NOT added!
```

---

## 🔍 **Commission Calculation**

### **For Company/Platform:**

**Commission is calculated based on the fare:**
```
Fare = Distance × Per KM Rate
Commission = Fare × Commission Percentage

Example:
Fare = ₹3,000
Commission (10%) = ₹3,000 × 0.10 = ₹300
Driver Receives = ₹3,000 - ₹300 = ₹2,700
```

**Driver allowance is separate and not part of commission calculation!**

---

## 📊 **Database Schema**

### **VehicleTariffConfig Table:**
```sql
CREATE TABLE vehicle_tariff_config (
  tariff_id VARCHAR(36) PRIMARY KEY,
  vehicle_type VARCHAR(50) NOT NULL,
  one_way_per_km DECIMAL(8,2) NOT NULL,      -- Used in fare calculation ✅
  round_trip_per_km DECIMAL(8,2) NOT NULL,   -- Used in fare calculation ✅
  driver_allowance DECIMAL(8,2) NOT NULL,    -- Stored but NOT used in fare ❌
  one_way_min_km INT NOT NULL,               -- For validation only
  round_trip_min_km INT NOT NULL,            -- Minimum 750 KM applied in calculation
  is_active BOOLEAN DEFAULT TRUE,
  created_at DATETIME,
  updated_at DATETIME
);
```

### **Trip Table:**
```sql
CREATE TABLE trips (
  trip_id VARCHAR(36) PRIMARY KEY,
  trip_type VARCHAR(50),           -- "One Way" or "Round Trip"
  vehicle_type VARCHAR(50),        -- Links to tariff config
  odo_start INT,                   -- Starting odometer ✅
  odo_end INT,                     -- Ending odometer ✅
  distance_km DECIMAL(8,2),        -- Calculated: odo_end - odo_start
  fare DECIMAL(10,2),              -- Calculated: distance × per_km_rate
  ...
);
```

---

## 🎯 **Code Implementation**

### **Location:** `app/crud/crud_trip.py`

```python
def calculate_fare(self, db: Session, trip: Trip) -> Optional[Decimal]:
    """
    Calculate fare for a trip based on tariff configuration
    
    IMPORTANT: 
    - Fare is calculated ONLY based on odometer distance difference
    - driver_allowance is stored in tariff config but NOT added to fare
    - Round Trip: Min 750 KM applied if distance is less
    """
    if not trip.odo_start or not trip.odo_end:
        return None
    
    # Get tariff config
    tariff = db.query(VehicleTariffConfig).filter(
        VehicleTariffConfig.vehicle_type == trip.vehicle_type,
        VehicleTariffConfig.is_active == True
    ).first()
    
    if not tariff:
        return None
    
    # Calculate distance from odometer readings
    distance_km = trip.odo_end - trip.odo_start
    
    # Calculate fare based ONLY on distance × per_km_rate
    # NOTE: driver_allowance is NOT included in fare calculation
    if trip.trip_type == "One Way":
        fare = Decimal(distance_km) * tariff.one_way_per_km
    elif trip.trip_type == "Round Trip":
        billable_distance = max(distance_km, Decimal("750"))
        fare = billable_distance * tariff.round_trip_per_km
    else:
        fare = Decimal(distance_km) * tariff.one_way_per_km
    
    return fare
```

---

## ✅ **Summary**

### **Fare Calculation:**
- ✅ **Uses**: Odometer distance × Per KM rate
- ❌ **Does NOT use**: Driver allowance
- ✅ **Formula**: `fare = billable_distance × per_km_rate` (Where billable_distance applies minimum KM rules: 130km for One Way, 750km for Round Trip)

### **Driver Allowance:**
- ✅ **Stored** in tariff config
- ❌ **NOT added** to fare
- ✅ **Used for**: Reference, reporting, settlements

### **Commission:**
- ✅ **Calculated** based on fare only
- ✅ **Formula**: `commission = fare × commission_percentage`
- ❌ **Does NOT include** driver allowance

---

**Status**: ✅ **Implementation Correct**

The current implementation already follows your requirement:
- Stores driver allowance in tariff config
- Does NOT add it to fare calculation
- Calculates fare based on odometer distance with **Minimum KM** rules (750km for Round Trip)
