"""Test failing endpoints to see exact error"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

print("="*60)
print("Testing GET All Payments")
print("="*60)
try:
    response = requests.get(f"{BASE_URL}/payments", timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Success: {response.json()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*60)
print("Testing POST Create Payment")
print("="*60)
payment_data = {
    "driver_id": "8d6b361d-22c3-474c-950d-74fd766310a3",  # Use existing driver
    "amount": 500.00,
    "transaction_type": "CASH",
    "status": "SUCCESS",
    "transaction_id": "TEST123"
}
try:
    response = requests.post(f"{BASE_URL}/payments", json=payment_data, timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code in [200, 201]:
        print(f"Success: {response.json()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*60)
print("Testing GET All Wallet Transactions")
print("="*60)
try:
    response = requests.get(f"{BASE_URL}/wallet-transactions", timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Success: {response.json()}")
    else:
        print(f"Error: {response.text}")
except Exception as e:
    print(f"Exception: {e}")
