#!/usr/bin/env python3
"""
Test the error handling endpoint locally
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import ErrorHandling
from app.schemas import ErrorHandlingResponse
from typing import List

def test_local_endpoint():
    """Test the error handling endpoint logic locally"""
    print("Testing Error Handling Endpoint Logic...")
    
    try:
        db = SessionLocal()
        
        # Simulate the endpoint logic
        skip = 0
        limit = 100
        
        # Query errors
        errors = db.query(ErrorHandling).offset(skip).limit(limit).all()
        print(f"[OK] Found {len(errors)} error records")
        
        # Try to serialize each error
        serialized_errors = []
        for error in errors:
            try:
                error_response = ErrorHandlingResponse.model_validate(error)
                serialized_errors.append(error_response.model_dump())
            except Exception as e:
                print(f"[ERROR] Failed to serialize error {error.error_id}: {e}")
                return False
        
        print(f"[OK] Successfully serialized all {len(serialized_errors)} errors")
        if serialized_errors:
            print(f"  Sample: {serialized_errors[0]}")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_local_endpoint()
    if success:
        print("\n[SUCCESS] All fixes are working correctly!")
        print("The server needs to be restarted to pick up the changes.")
    else:
        print("\n[FAILED] There are still issues to fix.")