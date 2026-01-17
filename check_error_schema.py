#!/usr/bin/env python3
"""
Check the actual database schema for error_handling table
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from sqlalchemy import text

def check_error_table_schema():
    """Check the actual schema of error_handling table"""
    print("Checking error_handling table schema...")
    
    try:
        db = SessionLocal()
        
        # Get table structure
        result = db.execute(text("DESCRIBE error_handling"))
        columns = result.fetchall()
        
        print("Table structure:")
        for col in columns:
            print(f"  {col[0]}: {col[1]} (Null: {col[2]}, Key: {col[3]}, Default: {col[4]}, Extra: {col[5]})")
        
        # Get sample data
        result = db.execute(text("SELECT * FROM error_handling LIMIT 1"))
        sample = result.fetchone()
        
        if sample:
            print(f"\nSample data:")
            print(f"  error_id: {sample[0]} (type: {type(sample[0])})")
            print(f"  error_type: {sample[1]}")
            print(f"  error_code: {sample[2]} (type: {type(sample[2])})")
            print(f"  error_description: {sample[3]}")
            print(f"  created_at: {sample[4]}")
        
        db.close()
        
    except Exception as e:
        print(f"[ERROR] Failed: {e}")

if __name__ == "__main__":
    check_error_table_schema()