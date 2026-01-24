#!/usr/bin/env python3
"""
Update tariff configuration with correct pricing structure
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import VehicleTariffConfig
from sqlalchemy.orm import Session
import uuid

def update_tariff_configs():
    """Update tariff configurations with correct pricing"""
    db = next(get_db())
    
    # Tariff configurations based on your pricing structure
    tariff_configs = [
        {
            "vehicle_type": "sedan",
            "one_way_per_km": 14.00,
            "round_trip_per_km": 13.00,
            "driver_allowance": 300.00,
            "one_way_min_km": 130.00,
            "round_trip_min_km": 250.00,
            "is_active": True
        },
        {
            "vehicle_type": "suv",
            "one_way_per_km": 19.00,
            "round_trip_per_km": 18.00,
            "driver_allowance": 400.00,
            "one_way_min_km": 130.00,
            "round_trip_min_km": 250.00,
            "is_active": True
        },
        {
            "vehicle_type": "innova",
            "one_way_per_km": 19.00,
            "round_trip_per_km": 18.00,
            "driver_allowance": 400.00,
            "one_way_min_km": 130.00,
            "round_trip_min_km": 250.00,
            "is_active": True
        }
    ]
    
    try:
        # Deactivate all existing configs
        db.query(VehicleTariffConfig).update({"is_active": False})
        
        # Add new configurations
        for config in tariff_configs:
            # Check if config already exists
            existing = db.query(VehicleTariffConfig).filter(
                VehicleTariffConfig.vehicle_type == config["vehicle_type"],
                VehicleTariffConfig.one_way_per_km == config["one_way_per_km"]
            ).first()
            
            if not existing:
                config["tariff_id"] = str(uuid.uuid4())
                new_config = VehicleTariffConfig(**config)
                db.add(new_config)
                print(f"Added {config['vehicle_type']} tariff configuration")
            else:
                # Update existing config
                for key, value in config.items():
                    if key != "tariff_id":
                        setattr(existing, key, value)
                print(f"Updated {config['vehicle_type']} tariff configuration")
        
        db.commit()
        print("\nTariff configurations updated successfully!")
        
        # Display updated configurations
        print("\nCurrent Active Tariff Configurations:")
        active_configs = db.query(VehicleTariffConfig).filter(VehicleTariffConfig.is_active == True).all()
        
        for config in active_configs:
            print(f"\n{config.vehicle_type.upper()}:")
            print(f"   One Way: ₹{config.one_way_per_km}/km (Min: {config.one_way_min_km} km)")
            print(f"   Round Trip: ₹{config.round_trip_per_km}/km (Min: {config.round_trip_min_km} km)")
            print(f"   Driver Allowance: ₹{config.driver_allowance}")
        
    except Exception as e:
        db.rollback()
        print(f"Error updating tariff configurations: {str(e)}")
    finally:
        db.close()

if __name__ == "__main__":
    update_tariff_configs()