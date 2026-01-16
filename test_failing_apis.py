"""Test payments and wallet transactions endpoints"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

print("\n" + "="*60)
print("Testing Payments API")
print("="*60)
try:
    response = requests.get(f"{BASE_URL}/payments", timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 500:
        print(f"Error: {response.text}")
    else:
        print(f"Success: {response.json()}")
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*60)
print("Testing Wallet Transactions API")
print("="*60)
try:
    response = requests.get(f"{BASE_URL}/wallet-transactions", timeout=5)
    print(f"Status: {response.status_code}")
    if response.status_code == 500:
        print(f"Error: {response.text}")
    else:
        print(f"Success: {response.json()}")
except Exception as e:
    print(f"Exception: {e}")
