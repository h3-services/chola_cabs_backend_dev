
from sqlalchemy import create_engine, inspect
import os
import sys

# Add the current directory to sys.path
sys.path.append(os.getcwd())
from app.database import DATABASE_URL

def check_columns():
    print(f"Connecting to database to verify columns...")
    engine = create_engine(DATABASE_URL)
    inspector = inspect(engine)
    
    # 1. Check TRIPS table (where we added the fields)
    print("\n--- Checking 'trips' table ---")
    trips_columns = [col['name'] for col in inspector.get_columns("trips")]
    
    expected_fields = [
        "waiting_charges", "inter_state_permit_charges", "driver_allowance", 
        "luggage_cost", "pet_cost", "toll_charges", "night_allowance", "total_amount"
    ]
    
    found_all = True
    for field in expected_fields:
        if field in trips_columns:
            print(f"✅ Found column: {field}")
        else:
            print(f"❌ MISSING column: {field}")
            found_all = False
            
    if found_all:
        print("\nSUCCESS: All new fields are present in the 'trips' table.")
    else:
        print("\nWARNING: Some fields are missing from the 'trips' table.")

    # 2. Check VEHICLE_TARIFF_CONFIG table (for comparison)
    print("\n--- Checking 'vehicle_tariff_config' table ---")
    config_columns = [col['name'] for col in inspector.get_columns("vehicle_tariff_config")]
    print(f"Columns found: {config_columns}")

if __name__ == "__main__":
    check_columns()
