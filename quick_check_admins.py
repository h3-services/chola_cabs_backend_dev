"""
Quick check for admins table
"""
from app.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    # Check if table exists
    result = conn.execute(text("SHOW TABLES LIKE 'admins'"))
    exists = result.fetchone()
    
    if exists:
        print("✅ ADMINS TABLE EXISTS\n")
        
        # Show structure
        result = conn.execute(text("DESCRIBE admins"))
        print("Table Structure:")
        print("-" * 80)
        for row in result:
            print(f"{row[0]:<20} {row[1]:<20} {row[2]:<10} {row[3]:<10} {row[4] or ''}")
        
        # Count records
        result = conn.execute(text("SELECT COUNT(*) FROM admins"))
        count = result.scalar()
        print(f"\nTotal Records: {count}")
        
        # Show sample data
        if count > 0:
            result = conn.execute(text("SELECT * FROM admins LIMIT 5"))
            print("\nSample Data:")
            print("-" * 80)
            for row in result:
                print(row)
    else:
        print("❌ ADMINS TABLE DOES NOT EXIST")
        
        # Show all tables
        result = conn.execute(text("SHOW TABLES"))
        print("\nAvailable tables:")
        for row in result:
            print(f"  - {row[0]}")
