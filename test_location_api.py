import requests
import json
import uuid

BASE_URL = "http://localhost:8000"

def test_location_update():
    print("Testing Location APIs...")
    
    # 1. Get an existing driver (or list all and pick one)
    print("\n1. Fetching drivers...")
    try:
        response = requests.get(f"{BASE_URL}/drivers")
        if response.status_code != 200:
            print(f"Failed to fetch drivers: {response.status_code}")
            return
            
        drivers = response.json()
        if not drivers:
            print("No drivers found. Please create a driver first.")
            return
            
        driver_id = drivers[0]['driver_id']
        print(f"Using Driver ID: {driver_id}")
    except Exception as e:
        print(f"Error: {e}")
        return

    # 2. Update Location
    print(f"\n2. Updating location for {driver_id}...")
    location_data = {
        "latitude": 12.9716,
        "longitude": 77.5946
    }
    
    try:
        response = requests.post(f"{BASE_URL}/drivers/{driver_id}/location", json=location_data)
        if response.status_code == 200:
            print("✅ Location updated successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Failed to update location: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

    # 3. Get Location
    print(f"\n3. Fetching location for {driver_id}...")
    try:
        response = requests.get(f"{BASE_URL}/drivers/{driver_id}/location")
        if response.status_code == 200:
            print("✅ Location fetched successfully!")
            print(json.dumps(response.json(), indent=2))
        else:
            print(f"❌ Failed to fetch location: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_location_update()
