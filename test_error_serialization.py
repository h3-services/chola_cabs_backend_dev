#!/usr/bin/env python3
"""
Test the error handling API endpoint directly
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models import ErrorHandling
from app.schemas import ErrorHandlingResponse
from pydantic import ValidationError

def test_error_serialization():
    """Test if error records can be serialized properly"""
    print("Testing Error Serialization...")
    
    try:
        db = SessionLocal()
        
        # Get first error record
        error = db.query(ErrorHandling).first()
        
        if error:
            print(f"Found error record: {error.error_id}")
            print(f"  Type: {error.error_type}")
            print(f"  Code: {error.error_code}")
            print(f"  Description: {error.error_description}")
            print(f"  Created: {error.created_at}")
            
            # Try to serialize with Pydantic
            try:
                error_response = ErrorHandlingResponse.model_validate(error)
                print("[OK] Pydantic serialization successful")
                print(f"  Serialized: {error_response.model_dump()}")
            except ValidationError as e:
                print(f"[ERROR] Pydantic validation failed: {e}")
            except Exception as e:
                print(f"[ERROR] Serialization failed: {e}")
                
        else:
            print("No error records found")
            
        db.close()
        
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")

if __name__ == "__main__":
    test_error_serialization()