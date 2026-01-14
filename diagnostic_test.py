"""
Quick API Diagnostic - Check specific failing endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_endpoint(url, method="GET"):
    """Test endpoint and show detailed error"""
    print(f"\n{'='*60}")
    print(f"Testing: {method} {url}")
    print('='*60)
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        else:
            response = requests.post(url, json={}, timeout=5)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response:")
        try:
            print(json.dumps(response.json(), indent=2))
        except:
            print(response.text)
    except Exception as e:
        print(f"Error: {e}")

# Test the failing endpoints
print("\n🔍 DIAGNOSTIC TEST - Checking Failing Endpoints\n")

# System endpoints (should work)
test_endpoint(f"{BASE_URL}/stats")

# Failing endpoints
test_endpoint(f"{BASE_URL}/tariff-config")
test_endpoint(f"{BASE_URL}/payments")
test_endpoint(f"{BASE_URL}/wallet-transactions")

print("\n" + "="*60)
print("Diagnostic complete!")
print("="*60)
