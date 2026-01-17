#!/usr/bin/env python3
"""
Test current error handling API status
"""
import requests
import json

def test_error_api_comprehensive():
    """Test all error handling endpoints"""
    base_url = "http://72.62.196.30:8000"
    
    print("=== Testing Error Handling API ===")
    
    # Test 1: GET all errors
    print("\n1. Testing GET /api/v1/errors/")
    try:
        response = requests.get(f"{base_url}/api/v1/errors/?skip=0&limit=5", timeout=10)
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
    
    # Test 2: GET specific error
    print("\n2. Testing GET /api/v1/errors/{error_id}")
    try:
        # First get an error ID
        response = requests.get(f"{base_url}/api/v1/errors/?skip=0&limit=1", timeout=10)
        if response.status_code == 200 and response.json():
            error_id = response.json()[0]['error_id']
            response = requests.get(f"{base_url}/api/v1/errors/{error_id}", timeout=10)
            print(f"   Status: {response.status_code}")
            if response.status_code == 200:
                print(f"   Success: {response.json()}")
            else:
                print(f"   Error: {response.text}")
        else:
            print("   Skipped: No errors to test with")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 3: POST new error
    print("\n3. Testing POST /api/v1/errors/")
    try:
        new_error = {
            "error_type": "TEST",
            "error_code": 999,
            "error_description": "Test error for API validation"
        }
        response = requests.post(f"{base_url}/api/v1/errors/", 
                               json=new_error, timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 201:
            print(f"   Success: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")
    
    # Test 4: Health check
    print("\n4. Testing Health Check")
    try:
        response = requests.get(f"{base_url}/health", timeout=10)
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            print(f"   Health: {response.json()}")
        else:
            print(f"   Error: {response.text}")
    except Exception as e:
        print(f"   Exception: {e}")

if __name__ == "__main__":
    test_error_api_comprehensive()