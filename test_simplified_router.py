#!/usr/bin/env python3
"""
Test the simplified error handling router locally
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app

def test_simplified_router():
    """Test the simplified error handling router"""
    print("Testing simplified error handling router...")
    
    client = TestClient(app)
    
    # Test GET /api/v1/errors/
    print("\n1. Testing GET /api/v1/errors/")
    try:
        response = client.get("/api/v1/errors/?skip=0&limit=5")
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Success: Found {len(data)} errors")
            if data:
                print(f"   Sample: {data[0]}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test POST /api/v1/errors/
    print("\n2. Testing POST /api/v1/errors/")
    try:
        new_error = {
            "error_type": "TEST_LOCAL",
            "error_code": 998,
            "error_description": "Local test error"
        }
        response = client.post("/api/v1/errors/", json=new_error)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            data = response.json()
            print(f"   Success: Created error {data['error_id']}")
            return data['error_id']
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    return None

if __name__ == "__main__":
    test_simplified_router()