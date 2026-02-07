from app.database import SessionLocal
from app.models import VehicleTariffConfig

db = SessionLocal()
try:
    tariffs = db.query(VehicleTariffConfig).all()
    print("\n=== Vehicle Tariff Configuration ===\n")
    print(f"{'Tariff ID':<40} {'Vehicle Type':<15} {'One Way/km':<12} {'Round Trip/km':<15} {'Allowance':<12} {'Min KM (OW)':<12} {'Min KM (RT)':<12} {'Active':<8}")
    print("-" * 140)
    
    for t in tariffs:
        print(f"{t.tariff_id:<40} {t.vehicle_type:<15} {str(t.one_way_per_km):<12} {str(t.round_trip_per_km):<15} {str(t.driver_allowance):<12} {t.one_way_min_km:<12} {t.round_trip_min_km:<12} {t.is_active}")
    
    print("\n=== Commission Calculation Example (Sedan, One Way) ===")
    sedan_tariff = db.query(VehicleTariffConfig).filter(VehicleTariffConfig.vehicle_type == 'sedan').first()
    if sedan_tariff:
        odo_start = 1000
        odo_end = 1250
        distance = odo_end - odo_start
        fare = distance * float(sedan_tariff.one_way_per_km)
        commission_percent = 10.0  # Updated to 10%
        commission = fare * (commission_percent / 100)
        driver_receives = fare - commission
        
        print(f"\nOdometer Start: {odo_start}")
        print(f"Odometer End: {odo_end}")
        print(f"Distance: {distance} km")
        print(f"Per KM Rate: ₹{sedan_tariff.one_way_per_km}")
        print(f"Fare: ₹{fare:.2f}")
        print(f"Commission ({commission_percent}%): ₹{commission:.2f}")
        print(f"Driver Receives: ₹{driver_receives:.2f}")
    
finally:
    db.close()
