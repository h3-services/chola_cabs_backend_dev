#!/usr/bin/env python3
"""
Test imports and basic functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all imports work correctly"""
    print("Testing imports...")
    
    try:
        from app.database import SessionLocal, get_db
        print("[OK] Database imports OK")
    except Exception as e:
        print(f"[ERROR] Database import error: {e}")
        return False
    
    try:
        from app.models import ErrorHandling
        print("[OK] ErrorHandling model import OK")
    except Exception as e:
        print(f"[ERROR] ErrorHandling model import error: {e}")
        return False
    
    try:
        from app.schemas import ErrorHandlingCreate, ErrorHandlingResponse
        print("[OK] Schema imports OK")
    except Exception as e:
        print(f"[ERROR] Schema import error: {e}")
        return False
    
    try:
        from app.routers.error_handling import router
        print("[OK] Router import OK")
    except Exception as e:
        print(f"[ERROR] Router import error: {e}")
        return False
    
    return True

def test_basic_query():
    """Test basic database query"""
    print("\nTesting basic query...")
    
    try:
        from app.database import SessionLocal
        from app.models import ErrorHandling
        
        db = SessionLocal()
        count = db.query(ErrorHandling).count()
        print(f"[OK] Query successful: {count} records")
        db.close()
        return True
    except Exception as e:
        print(f"[ERROR] Query error: {e}")
        return False

if __name__ == "__main__":
    imports_ok = test_imports()
    if imports_ok:
        query_ok = test_basic_query()
        if query_ok:
            print("\n[SUCCESS] All basic tests passed")
        else:
            print("\n[FAILED] Query test failed")
    else:
        print("\n[FAILED] Import test failed")