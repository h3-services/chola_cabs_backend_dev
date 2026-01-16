"""Quick diagnostic - test specific failing endpoints"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("\n" + "="*60)
print("Testing Tariff Config API")
print("="*60)
try:
    response = requests.get(f"{BASE_URL}/tariff-config", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("Testing Payments API")
print("="*60)
try:
    response = requests.get(f"{BASE_URL}/payments", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("Testing Wallet Transactions API")
print("="*60)
try:
    response = requests.get(f"{BASE_URL}/wallet-transactions", timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")

print("\n" + "="*60)
print("Testing Create Trip")
print("="*60)
trip_data = {
    "customer_name": "Test Customer",
    "customer_phone": "9876543211",
    "pickup_address": "Mumbai Airport",
    "drop_address": "Bandra West",
    "trip_type": "one_way",
    "vehicle_type": "sedan",
    "passenger_count": 2
}
try:
    response = requests.post(f"{BASE_URL}/trips", json=trip_data, timeout=5)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.text[:500]}")
except Exception as e:
    print(f"Error: {e}")
