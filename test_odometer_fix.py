"""
Test script to verify odometer-based trip status automation
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/trips"

def test_odometer_automation():
    """Test the odometer automation fix"""
    
    # Your specific trip ID
    trip_id = "3bd094d1-4fa7-411d-a3ca-58fadc52a966"
    
    print("Testing odometer-based trip status automation...")
    print(f"Trip ID: {trip_id}")
    
    # 1. Get current trip status
    print("\n1. Getting current trip status...")
    response = requests.get(f"{BASE_URL}/{trip_id}")
    if response.status_code == 200:
        trip = response.json()
        print(f"Current Status: {trip['trip_status']}")
        print(f"Odo Start: {trip['odo_start']}")
        print(f"Odo End: {trip['odo_end']}")
        print(f"Distance: {trip['distance_km']}")
        print(f"Fare: {trip['fare']}")
        print(f"Ended At: {trip['ended_at']}")
    else:
        print(f"Error getting trip: {response.status_code} - {response.text}")
        return
    
    # 2. Fix this specific trip's status
    print("\n2. Fixing trip status based on odometer readings...")
    response = requests.patch(f"{BASE_URL}/{trip_id}/fix-status")
    if response.status_code == 200:
        result = response.json()
        print(f"Fix Result: {result['message']}")
        print(f"Old Status: {result['old_status']}")
        print(f"New Status: {result['new_status']}")
        print(f"Distance: {result['distance_km']}")
        print(f"Fare: {result['fare']}")
        print(f"Ended At: {result['ended_at']}")
    else:
        print(f"Error fixing trip: {response.status_code} - {response.text}")
        return
    
    # 3. Verify the fix worked
    print("\n3. Verifying the fix...")
    response = requests.get(f"{BASE_URL}/{trip_id}")
    if response.status_code == 200:
        trip = response.json()
        print(f"Final Status: {trip['trip_status']}")
        print(f"Distance: {trip['distance_km']} km")
        print(f"Fare: ₹{trip['fare']}")
        print(f"Ended At: {trip['ended_at']}")
        
        if trip['trip_status'] == 'COMPLETED' and trip['ended_at']:
            print("✅ SUCCESS: Trip automatically completed!")
        else:
            print("❌ FAILED: Trip status not updated correctly")
    else:
        print(f"Error verifying trip: {response.status_code} - {response.text}")

def test_bulk_fix():
    """Test fixing all incomplete trips"""
    print("\n\n=== BULK FIX TEST ===")
    
    response = requests.patch(f"{BASE_URL}/fix-incomplete-trips")
    if response.status_code == 200:
        result = response.json()
        print(f"Bulk Fix Result: {result['message']}")
        print(f"Fixed Trips: {result['fixed_trips']}")
    else:
        print(f"Error in bulk fix: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_odometer_automation()
    test_bulk_fix()