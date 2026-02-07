import sys
from app.database import SessionLocal
from app.models import VehicleTariffConfig

db = SessionLocal()
try:
    tariffs = db.query(VehicleTariffConfig).all()
    
    for t in tariffs:
        print(f"'{t.tariff_id}', '{t.vehicle_type}', '{t.one_way_per_km}', '{t.round_trip_per_km}', '{t.driver_allowance}', '{t.one_way_min_km}', '{t.round_trip_min_km}', '{t.is_active}', '{t.created_at}', '{t.updated_at}'")
    
finally:
    db.close()
