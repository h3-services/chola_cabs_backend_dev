"""
Commission Calculation Script - Write to File
Updated Commission: 10%
"""
import sys
from app.database import SessionLocal
from app.models import VehicleTariffConfig
from app.core.constants import DEFAULT_DRIVER_COMMISSION_PERCENT

# Redirect output to file
output_file = open("commission_report.txt", "w", encoding="utf-8")
original_stdout = sys.stdout
sys.stdout = output_file

print("=" * 80)
print("VEHICLE TARIFF CONFIGURATION - DATABASE DATA")
print("=" * 80)

db = SessionLocal()
try:
    tariffs = db.query(VehicleTariffConfig).all()
    
    print(f"\nTotal Tariff Configurations: {len(tariffs)}\n")
    
    for t in tariffs:
        print(f"Tariff ID: {t.tariff_id}")
        print(f"Vehicle Type: {t.vehicle_type}")
        print(f"One Way Per KM: ₹{t.one_way_per_km}")
        print(f"Round Trip Per KM: ₹{t.round_trip_per_km}")
        print(f"Driver Allowance: ₹{t.driver_allowance}")
        print(f"One Way Min KM: {t.one_way_min_km}")
        print(f"Round Trip Min KM: {t.round_trip_min_km}")
        print(f"Active: {t.is_active}")
        print(f"Created: {t.created_at}")
        print(f"Updated: {t.updated_at}")
        print("-" * 80)
    
    print("\n" + "=" * 80)
    print("COMMISSION CALCULATION - UPDATED TO 10%")
    print("=" * 80)
    print(f"\nCurrent Commission Percentage: {DEFAULT_DRIVER_COMMISSION_PERCENT}%\n")
    
    # Example calculation with Sedan
    sedan_tariff = db.query(VehicleTariffConfig).filter(
        VehicleTariffConfig.vehicle_type == 'sedan'
    ).first()
    
    if sedan_tariff:
        print("EXAMPLE: Sedan One-Way Trip")
        print("-" * 80)
        odo_start = 1000
        odo_end = 1250
        distance = odo_end - odo_start
        fare = distance * float(sedan_tariff.one_way_per_km)
        commission = fare * (DEFAULT_DRIVER_COMMISSION_PERCENT / 100)
        driver_receives = fare - commission
        
        print(f"Odometer Start: {odo_start}")
        print(f"Odometer End: {odo_end}")
        print(f"Distance: {distance} km")
        print(f"Per KM Rate (One Way): ₹{sedan_tariff.one_way_per_km}")
        print(f"\nFare Calculation:")
        print(f"  Fare = Distance × Per KM Rate")
        print(f"  Fare = {distance} × ₹{sedan_tariff.one_way_per_km}")
        print(f"  Fare = ₹{fare:.2f}")
        print(f"\nCommission Calculation:")
        print(f"  Commission = Fare × {DEFAULT_DRIVER_COMMISSION_PERCENT}%")
        print(f"  Commission = ₹{fare:.2f} × {DEFAULT_DRIVER_COMMISSION_PERCENT/100}")
        print(f"  Commission = ₹{commission:.2f}")
        print(f"\nDriver Receives:")
        print(f"  Driver Amount = Fare - Commission")
        print(f"  Driver Amount = ₹{fare:.2f} - ₹{commission:.2f}")
        print(f"  Driver Amount = ₹{driver_receives:.2f}")
        print(f"\nNote: Driver allowance (₹{sedan_tariff.driver_allowance}) is NOT included in fare calculation")
    
    print("\n" + "=" * 80)
    print("Report generated successfully!")
    
finally:
    db.close()
    sys.stdout = original_stdout
    output_file.close()
    print("Report saved to: commission_report.txt")
