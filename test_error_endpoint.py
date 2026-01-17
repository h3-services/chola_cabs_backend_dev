#!/usr/bin/env python3
"""
Quick test for error handling endpoint
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models import ErrorHandling
from sqlalchemy import text

def test_error_endpoint():
    """Test the error handling endpoint functionality"""
    print("Testing Error Handling Endpoint...")
    
    try:
        # Test database connection
        db = SessionLocal()
        print("[OK] Database connection successful")
        
        # Test if error_handling table exists
        result = db.execute(text("SHOW TABLES LIKE 'error_handling'"))
        table_exists = result.fetchone()
        
        if table_exists:
            print("[OK] error_handling table exists")
            
            # Test query
            try:
                errors = db.query(ErrorHandling).limit(5).all()
                print(f"[OK] Query successful, found {len(errors)} error records")
                
                # Print first error if exists
                if errors:
                    first_error = errors[0]
                    print(f"  Sample error: ID={first_error.error_id}, Type={first_error.error_type}")
                else:
                    print("  No error records found in database")
                    
            except Exception as e:
                print(f"[ERROR] Query failed: {e}")
                
        else:
            print("[ERROR] error_handling table does not exist")
            
        db.close()
        
    except Exception as e:
        print(f"[ERROR] Database connection failed: {e}")

if __name__ == "__main__":
    test_error_endpoint()