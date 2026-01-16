"""
Test POST Create Vehicle endpoint
"""
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000/api/v1"

# First, create a driver (needed for vehicle)
print("="*60)
print("Step 1: Creating a driver first...")
print("="*60)

driver_data = {
    "name": f"Test Driver {datetime.now().timestamp()}",
    "phone_number": str(int(datetime.now().timestamp()) % 10000000000),
    "email": f"driver{int(datetime.now().timestamp())}@test.com",
    "primary_location": "Delhi",
    "licence_number": f"DL{int(datetime.now().timestamp())}"
}

response = requests.post(f"{BASE_URL}/drivers", json=driver_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 201:
    driver_id = response.json()['driver_id']
    print(f"\n✅ Driver created successfully!")
    print(f"Driver ID: {driver_id}")
    
    # Now create a vehicle
    print("\n" + "="*60)
    print("Step 2: Creating a vehicle for this driver...")
    print("="*60)
    
    vehicle_data = {
        "driver_id": driver_id,
        "vehicle_type": "sedan",
        "vehicle_brand": "Maruti",
        "vehicle_model": "Swift",
        "vehicle_number": f"DL01AB{int(datetime.now().timestamp()) % 10000}",
        "vehicle_color": "Red",
        "seating_capacity": 4
    }
    
    print(f"\nPOST Request to: {BASE_URL}/vehicles")
    print(f"Data: {json.dumps(vehicle_data, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/vehicles", json=vehicle_data)
    print(f"\nStatus: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print(f"\n✅ Vehicle created successfully!")
        vehicle_id = response.json()['vehicle_id']
        
        # Verify by getting the vehicle
        print("\n" + "="*60)
        print("Step 3: Verifying - Getting the created vehicle...")
        print("="*60)
        
        response = requests.get(f"{BASE_URL}/vehicles/{vehicle_id}")
        print(f"Status: {response.status_code}")
        print(f"Vehicle Details: {json.dumps(response.json(), indent=2)}")
        
        if response.status_code == 200:
            print(f"\n✅ Vehicle retrieved successfully!")
    else:
        print(f"\n❌ Failed to create vehicle")
else:
    print(f"\n❌ Failed to create driver")
