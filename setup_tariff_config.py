#!/usr/bin/env python3
"""
Setup tariff configuration with exact pricing structure
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import VehicleTariffConfig
from app.database import get_database_url
import uuid

def setup_tariff_config():
    """Setup tariff configuration with exact pricing"""
    
    # Database connection
    DATABASE_URL = get_database_url()
    engine = create_engine(DATABASE_URL)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    
    try:
        # Clear existing tariff configs
        db.query(VehicleTariffConfig).delete()
        
        # Tariff configurations based on your requirements
        tariff_configs = [
            {
                "vehicle_type": "sedan",
                "one_way_per_km": 14.00,
                "round_trip_per_km": 13.00,
                "driver_allowance": 300.00,
                "one_way_min_km": 130,
                "round_trip_min_km": 250,
                "is_active": True
            },
            {
                "vehicle_type": "suv",
                "one_way_per_km": 19.00,
                "round_trip_per_km": 18.00,
                "driver_allowance": 400.00,
                "one_way_min_km": 130,
                "round_trip_min_km": 250,
                "is_active": True
            },
            {
                "vehicle_type": "innova",
                "one_way_per_km": 19.00,
                "round_trip_per_km": 18.00,
                "driver_allowance": 400.00,
                "one_way_min_km": 130,
                "round_trip_min_km": 250,
                "is_active": True
            }
        ]
        
        # Insert tariff configurations
        for config_data in tariff_configs:
            config_data['tariff_id'] = str(uuid.uuid4())
            
            tariff_config = VehicleTariffConfig(**config_data)
            db.add(tariff_config)
        
        db.commit()
        print("✅ Tariff configuration setup completed successfully!")
        
        # Display created configurations
        configs = db.query(VehicleTariffConfig).all()
        print(f"\n📋 Created {len(configs)} tariff configurations:")
        for config in configs:
            print(f"  • {config.vehicle_type.upper()}: ₹{config.one_way_per_km}/km (One Way), ₹{config.round_trip_per_km}/km (Round Trip)")
            print(f"    Driver Allowance: ₹{config.driver_allowance}, Min KM: {config.one_way_min_km} (One Way), {config.round_trip_min_km} (Round Trip)")
        
    except Exception as e:
        db.rollback()
        print(f"❌ Error setting up tariff configuration: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    setup_tariff_config()