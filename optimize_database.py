#!/usr/bin/env python3
"""
Database optimization for faster API calls
"""

# Add these indexes to your database for faster queries
OPTIMIZATION_QUERIES = [
    # Trip table indexes
    "CREATE INDEX IF NOT EXISTS idx_trips_status ON trips(trip_status);",
    "CREATE INDEX IF NOT EXISTS idx_trips_driver ON trips(assigned_driver_id);",
    "CREATE INDEX IF NOT EXISTS idx_trips_created ON trips(created_at);",
    "CREATE INDEX IF NOT EXISTS idx_trips_vehicle_type ON trips(vehicle_type);",
    
    # Driver table indexes
    "CREATE INDEX IF NOT EXISTS idx_drivers_available ON drivers(is_available, is_approved);",
    "CREATE INDEX IF NOT EXISTS idx_drivers_phone ON drivers(phone_number);",
    
    # Tariff config indexes
    "CREATE INDEX IF NOT EXISTS idx_tariff_vehicle_active ON vehicle_tariff_config(vehicle_type, is_active);",
    
    # Composite indexes for common queries
    "CREATE INDEX IF NOT EXISTS idx_trips_status_created ON trips(trip_status, created_at);",
    "CREATE INDEX IF NOT EXISTS idx_trips_driver_status ON trips(assigned_driver_id, trip_status);"
]

def optimize_database():
    """Run database optimization queries"""
    import mysql.connector
    import os
    from dotenv import load_dotenv
    
    load_dotenv()
    
    conn = mysql.connector.connect(
        host=os.getenv('DB_HOST'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD'),
        database=os.getenv('DB_NAME')
    )
    
    cursor = conn.cursor()
    
    for query in OPTIMIZATION_QUERIES:
        try:
            cursor.execute(query)
            print(f"✓ {query}")
        except Exception as e:
            print(f"✗ {query} - Error: {e}")
    
    conn.commit()
    conn.close()
    print("Database optimization completed!")

if __name__ == "__main__":
    optimize_database()