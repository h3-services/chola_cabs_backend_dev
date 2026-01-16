"""
Quick API Test Script - Check all endpoints
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def test_endpoint(method, endpoint, name, data=None):
    """Test a single endpoint"""
    url = f"{API_BASE}{endpoint}" if not endpoint.startswith('http') else endpoint
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5)
        elif method == "PATCH":
            response = requests.patch(url, json=data, timeout=5)
        
        status = "PASS" if response.status_code in [200, 201] else "FAIL"
        print(f"[{status}] {name} - Status: {response.status_code}")
        return response.status_code in [200, 201], response
        
    except requests.exceptions.ConnectionError:
        print(f"[FAIL] {name} - Connection refused (Server not running?)")
        return False, None
    except Exception as e:
        print(f"[FAIL] {name} - Error: {str(e)}")
        return False, None

print("=" * 60)
print("CAB BOOKING API - QUICK TEST")
print("=" * 60)
print(f"Testing: {BASE_URL}\n")

# System Endpoints
print("\n--- SYSTEM ENDPOINTS ---")
test_endpoint("GET", BASE_URL, "Root Endpoint")
test_endpoint("GET", f"{BASE_URL}/health", "Health Check")
test_endpoint("GET", "/stats", "API Statistics")

# Drivers API
print("\n--- DRIVERS API ---")
test_endpoint("GET", "/drivers", "Get All Drivers")

driver_data = {
    "name": "Test Driver",
    "phone_number": "9876543210",
    "email": f"test{int(datetime.now().timestamp())}@example.com",
    "primary_location": "Mumbai",
    "licence_number": f"MH{int(datetime.now().timestamp())}"
}
success, response = test_endpoint("POST", "/drivers", "Create Driver", driver_data)
driver_id = None
if success and response:
    try:
        driver_id = response.json().get('driver_id')
        if driver_id:
            test_endpoint("GET", f"/drivers/{driver_id}", "Get Driver by ID")
            test_endpoint("PATCH", f"/drivers/{driver_id}/availability?is_available=true", "Update Availability")
            test_endpoint("GET", f"/drivers/{driver_id}/wallet-balance", "Get Wallet Balance")
    except:
        pass

# Vehicles API
print("\n--- VEHICLES API ---")
test_endpoint("GET", "/vehicles", "Get All Vehicles")

if driver_id:
    vehicle_data = {
        "driver_id": driver_id,
        "vehicle_type": "sedan",
        "vehicle_brand": "Toyota",
        "vehicle_model": "Camry",
        "vehicle_number": f"MH01AB{int(datetime.now().timestamp()) % 10000}",
        "vehicle_color": "White",
        "seating_capacity": 4
    }
    success, response = test_endpoint("POST", "/vehicles", "Create Vehicle", vehicle_data)
    vehicle_id = None
    if success and response:
        try:
            vehicle_id = response.json().get('vehicle_id')
            if vehicle_id:
                test_endpoint("GET", f"/vehicles/{vehicle_id}", "Get Vehicle by ID")
                test_endpoint("PATCH", f"/vehicles/{vehicle_id}/approve", "Approve Vehicle")
                test_endpoint("GET", f"/vehicles/driver/{driver_id}", "Get Vehicles by Driver")
        except:
            pass

# Trips API
print("\n--- TRIPS API ---")
test_endpoint("GET", "/trips", "Get All Trips")

trip_data = {
    "customer_name": "Test Customer",
    "customer_phone": "9876543211",
    "pickup_address": "Mumbai Airport",
    "drop_address": "Bandra West",
    "trip_type": "one_way",
    "vehicle_type": "sedan",
    "passenger_count": 2
}
success, response = test_endpoint("POST", "/trips", "Create Trip", trip_data)
trip_id = None
if success and response:
    try:
        trip_id = response.json().get('trip_id')
        if trip_id:
            test_endpoint("GET", f"/trips/{trip_id}", "Get Trip by ID")
            if driver_id:
                test_endpoint("PATCH", f"/trips/{trip_id}/assign-driver/{driver_id}", "Assign Driver to Trip")
                test_endpoint("GET", f"/trips/driver/{driver_id}", "Get Trips by Driver")
            test_endpoint("PATCH", f"/trips/{trip_id}/status?new_status=started", "Update Trip Status")
    except:
        pass

# Payments API
print("\n--- PAYMENTS API ---")
test_endpoint("GET", "/payments", "Get All Payments")

# Wallet Transactions API
print("\n--- WALLET TRANSACTIONS API ---")
test_endpoint("GET", "/wallet-transactions", "Get All Wallet Transactions")

if driver_id:
    wallet_data = {
        "driver_id": driver_id,
        "transaction_type": "credit",
        "amount": 1000.00
    }
    test_endpoint("POST", "/wallet-transactions", "Create Wallet Transaction", wallet_data)
    test_endpoint("GET", f"/wallet-transactions/driver/{driver_id}", "Get Wallet Transactions by Driver")

# Tariff Config API
print("\n--- TARIFF CONFIG API ---")
test_endpoint("GET", "/tariff-config", "Get All Tariff Configs")

tariff_data = {
    "vehicle_type": "sedan",
    "one_way_per_km": 12.00,
    "one_way_min_km": 5,
    "round_trip_per_km": 10.00,
    "round_trip_min_km": 10,
    "driver_allowance": 200.00,
    "is_active": True
}
test_endpoint("POST", "/tariff-config", "Create Tariff Config", tariff_data)

# Raw Data API
print("\n--- RAW DATA API ---")
test_endpoint("GET", "/raw/drivers", "Get Raw Drivers Data")
test_endpoint("GET", "/raw/vehicles", "Get Raw Vehicles Data")
test_endpoint("GET", "/raw/trips", "Get Raw Trips Data")

print("\n" + "=" * 60)
print("TEST COMPLETED")
print("=" * 60)
