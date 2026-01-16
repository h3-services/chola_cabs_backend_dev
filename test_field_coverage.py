"""
Test script to verify all table fields are returned in GET API responses
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_drivers_endpoint():
    """Test drivers GET endpoint for complete field coverage"""
    print("\n" + "="*60)
    print("Testing Drivers Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/drivers/")
    if response.status_code == 200:
        drivers = response.json()
        if drivers:
            driver = drivers[0]
            print(f"\nDriver fields returned: {len(driver.keys())}")
            print("\nFields:")
            for key in sorted(driver.keys()):
                print(f"  ✓ {key}: {type(driver[key]).__name__}")
            
            # Check for expected fields
            expected_fields = [
                'driver_id', 'name', 'phone_number', 'email', 'kyc_verified',
                'primary_location', 'photo_url', 'aadhar_url', 'licence_url',
                'licence_number', 'aadhar_number', 'licence_expiry',
                'wallet_balance', 'device_id', 'is_available', 'is_approved',
                'errors', 'created_at', 'updated_at'
            ]
            missing = [f for f in expected_fields if f not in driver]
            if missing:
                print(f"\n❌ Missing fields: {missing}")
            else:
                print(f"\n✅ All expected fields present!")
        else:
            print("No drivers found in database")
    else:
        print(f"❌ Error: {response.status_code}")

def test_vehicles_endpoint():
    """Test vehicles GET endpoint for complete field coverage"""
    print("\n" + "="*60)
    print("Testing Vehicles Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/vehicles/")
    if response.status_code == 200:
        vehicles = response.json()
        if vehicles:
            vehicle = vehicles[0]
            print(f"\nVehicle fields returned: {len(vehicle.keys())}")
            print("\nFields:")
            for key in sorted(vehicle.keys()):
                print(f"  ✓ {key}: {type(vehicle[key]).__name__}")
            
            # Check for expected fields
            expected_fields = [
                'vehicle_id', 'driver_id', 'vehicle_type', 'vehicle_brand',
                'vehicle_model', 'vehicle_number', 'vehicle_color', 'seating_capacity',
                'rc_expiry_date', 'fc_expiry_date', 'vehicle_approved',
                'rc_book_url', 'fc_certificate_url', 'vehicle_front_url',
                'vehicle_back_url', 'vehicle_left_url', 'vehicle_right_url',
                'errors', 'created_at', 'updated_at'
            ]
            missing = [f for f in expected_fields if f not in vehicle]
            if missing:
                print(f"\n❌ Missing fields: {missing}")
            else:
                print(f"\n✅ All expected fields present!")
        else:
            print("No vehicles found in database")
    else:
        print(f"❌ Error: {response.status_code}")

def test_trips_endpoint():
    """Test trips GET endpoint for complete field coverage"""
    print("\n" + "="*60)
    print("Testing Trips Endpoint")
    print("="*60)
    
    response = requests.get(f"{BASE_URL}/trips/")
    if response.status_code == 200:
        trips = response.json()
        if trips:
            trip = trips[0]
            print(f"\nTrip fields returned: {len(trip.keys())}")
            print("\nFields:")
            for key in sorted(trip.keys()):
                print(f"  ✓ {key}: {type(trip[key]).__name__}")
            
            # Check for expected fields
            expected_fields = [
                'trip_id', 'customer_name', 'customer_phone', 'pickup_address',
                'drop_address', 'trip_type', 'vehicle_type', 'assigned_driver_id',
                'trip_status', 'distance_km', 'odo_start', 'odo_end', 'fare',
                'started_at', 'ended_at', 'planned_start_at', 'planned_end_at',
                'is_manual_assignment', 'passenger_count', 'errors',
                'created_at', 'updated_at'
            ]
            missing = [f for f in expected_fields if f not in trip]
            if missing:
                print(f"\n❌ Missing fields: {missing}")
            else:
                print(f"\n✅ All expected fields present!")
        else:
            print("No trips found in database")
    else:
        print(f"❌ Error: {response.status_code}")

if __name__ == "__main__":
    print("\n" + "="*60)
    print("API Field Coverage Verification Test")
    print("="*60)
    
    try:
        test_drivers_endpoint()
        test_vehicles_endpoint()
        test_trips_endpoint()
        
        print("\n" + "="*60)
        print("Test Complete!")
        print("="*60 + "\n")
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Could not connect to API server at", BASE_URL)
        print("Make sure the server is running with: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
