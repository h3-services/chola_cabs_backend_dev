"""Test POST Create Payment with detailed error"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Use a known existing driver
driver_id = "2f299936-83d5-4806-aa0a-f01841f9c265"

payment_data = {
    "driver_id": driver_id,
    "amount": 500.00,
    "transaction_type": "CASH",
    "status": "SUCCESS",
    "transaction_id": "TEST12345"
}

print("Testing POST Create Payment")
print(f"URL: {BASE_URL}/payments")
print(f"Data: {json.dumps(payment_data, indent=2)}")

try:
    response = requests.post(f"{BASE_URL}/payments", json=payment_data, timeout=5)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {response.text}")
    
    if response.status_code in [200, 201]:
        print("\n✅ Success!")
        print(json.dumps(response.json(), indent=2))
    else:
        print("\n❌ Failed")
        
except Exception as e:
    print(f"\nException: {e}")
    import traceback
    traceback.print_exc()
