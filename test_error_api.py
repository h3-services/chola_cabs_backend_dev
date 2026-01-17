#!/usr/bin/env python3
"""
Test the actual error handling API endpoint
"""
import requests
import json

def test_error_api():
    """Test the error handling API endpoint"""
    print("Testing Error Handling API...")
    
    base_url = "http://72.62.196.30:8000"
    
    try:
        # Test GET /api/v1/errors/
        response = requests.get(f"{base_url}/api/v1/errors/?skip=0&limit=100")
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"[OK] API call successful")
            print(f"  Found {len(data)} error records")
            if data:
                print(f"  First error: {data[0]}")
        else:
            print(f"[ERROR] API call failed")
            print(f"  Response: {response.text}")
            
    except Exception as e:
        print(f"[ERROR] Request failed: {e}")

if __name__ == "__main__":
    test_error_api()