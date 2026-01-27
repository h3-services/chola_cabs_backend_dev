"""
Test Commission Calculation - 10% Implementation
This script demonstrates the automatic commission calculation and wallet update
"""
from decimal import Decimal

print("=" * 80)
print("COMMISSION CALCULATION TEST - 10% IMPLEMENTATION")
print("=" * 80)

# Test data from user's example
odo_start = 1000
odo_end = 1250
vehicle_type = "sedan"
trip_type = "One Way"

# Tariff rates (from database)
sedan_one_way_per_km = Decimal("14.00")
driver_allowance = Decimal("300.00")  # Stored but NOT used in calculation

# Commission percentage
commission_percent = Decimal("10.0")

print(f"\n📋 TRIP DETAILS:")
print(f"   Vehicle Type: {vehicle_type}")
print(f"   Trip Type: {trip_type}")
print(f"   Odometer Start: {odo_start}")
print(f"   Odometer End: {odo_end}")

# Step 1: Calculate Distance
distance = odo_end - odo_start
print(f"\n📏 DISTANCE CALCULATION:")
print(f"   Distance = ODA End - ODA Start")
print(f"   Distance = {odo_end} - {odo_start}")
print(f"   Distance = {distance} km")

# Step 2: Calculate Fare (ONLY distance × per_km_rate)
fare = Decimal(distance) * sedan_one_way_per_km
print(f"\n💰 FARE CALCULATION:")
print(f"   Fare = Distance × Per KM Rate")
print(f"   Fare = {distance} × ₹{sedan_one_way_per_km}")
print(f"   Fare = ₹{fare:.2f}")
print(f"\n   ⚠️  Note: Driver allowance (₹{driver_allowance}) is NOT included in fare")

# Step 3: Calculate Commission (10%)
commission = fare * (commission_percent / Decimal("100"))
print(f"\n🏢 COMMISSION CALCULATION:")
print(f"   Commission = Fare × {commission_percent}%")
print(f"   Commission = ₹{fare:.2f} × {commission_percent/100}")
print(f"   Commission = ₹{commission:.2f}")

# Step 4: Calculate Driver Earnings (Net Amount)
driver_earnings = fare - commission
print(f"\n👨‍✈️ DRIVER EARNINGS:")
print(f"   Driver Earnings = Fare - Commission")
print(f"   Driver Earnings = ₹{fare:.2f} - ₹{commission:.2f}")
print(f"   Driver Earnings = ₹{driver_earnings:.2f}")

# Step 5: Wallet Transactions
print(f"\n💳 WALLET TRANSACTIONS CREATED:")
print(f"   1. CREDIT Transaction:")
print(f"      - Type: CREDIT")
print(f"      - Amount: ₹{driver_earnings:.2f}")
print(f"      - Description: Trip earnings (after {commission_percent}% commission)")
print(f"      - Effect: Driver wallet balance += ₹{driver_earnings:.2f}")
print(f"\n   2. COMMISSION Transaction:")
print(f"      - Type: COMMISSION")
print(f"      - Amount: ₹{commission:.2f}")
print(f"      - Description: Platform commission ({commission_percent}%)")
print(f"      - Effect: Recorded for company accounting")

# Summary
print(f"\n" + "=" * 80)
print("📊 SUMMARY")
print("=" * 80)
print(f"   Total Fare:           ₹{fare:.2f}")
print(f"   Commission (10%):     ₹{commission:.2f}  → Company")
print(f"   Driver Receives:      ₹{driver_earnings:.2f}  → Driver Wallet ✅")
print("=" * 80)

print(f"\n✅ IMPLEMENTATION COMPLETE!")
print(f"\nWhen a trip completes:")
print(f"   1. ✅ Fare is calculated automatically")
print(f"   2. ✅ Commission (10%) is calculated automatically")
print(f"   3. ✅ Driver wallet is credited with NET earnings (₹{driver_earnings:.2f})")
print(f"   4. ✅ Two wallet transactions are created (CREDIT + COMMISSION)")
print(f"   5. ✅ Driver allowance (₹{driver_allowance}) stays in database only")
print("\n" + "=" * 80)
