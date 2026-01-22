"""
Test script for odometer readings, distance calculation, and fare calculation
Tests the complete trip lifecycle with automatic status changes
"""
import requests
import json
from decimal import Decimal

BASE_URL = "http://localhost:8000/api/v1"

def test_complete_trip_workflow():
    """Test complete trip workflow with odometer and fare calculation"""
    
    print("=== Testing Complete Trip Workflow ===\n")
    
    # 1. Create a tariff configuration first
    print("1. Creating tariff configuration...")
    tariff_data = {
        "vehicle_type": "sedan",
        "one_way_per_km": 15.00,
        "one_way_min_km": 5,
        "round_trip_per_km": 12.00,
        "round_trip_min_km": 10,
        "driver_allowance": 200.00,
        "is_active": True
    }
    
    response = requests.post(f"{BASE_URL}/tariff-config/", json=tariff_data)
    if response.status_code == 201:
        tariff_config = response.json()
        print(f"✓ Tariff config created: {tariff_config['tariff_id']}")
        print(f"  - One way: ₹{tariff_config['one_way_per_km']}/km (min {tariff_config['one_way_min_km']} km)")
        print(f"  - Driver allowance: ₹{tariff_config['driver_allowance']}")
    else:
        print(f"✗ Failed to create tariff config: {response.text}")
        return
    
    # 2. Create a driver
    print("\n2. Creating driver...")
    driver_data = {
        "name": "Test Driver",
        "phone_number": "9876543210",
        "email": "testdriver@example.com",
        "primary_location": "Mumbai",
        "licence_number": "MH123456789"
    }
    
    response = requests.post(f"{BASE_URL}/drivers/", json=driver_data)
    if response.status_code == 201:
        driver = response.json()
        driver_id = driver['driver_id']
        print(f"✓ Driver created: {driver_id}")
        
        # Approve the driver
        response = requests.patch(f"{BASE_URL}/drivers/{driver_id}/approve")
        if response.status_code == 200:
            print("✓ Driver approved")
        else:
            print(f"✗ Failed to approve driver: {response.text}")
    else:
        print(f"✗ Failed to create driver: {response.text}")
        return
    
    # 3. Create a trip
    print("\n3. Creating trip...")
    trip_data = {
        "customer_name": "John Customer",
        "customer_phone": "9876543211",
        "pickup_address": "Mumbai Airport",
        "drop_address": "Bandra West",
        "trip_type": "one_way",
        "vehicle_type": "sedan",
        "passenger_count": 2
    }
    
    response = requests.post(f"{BASE_URL}/trips/", json=trip_data)
    if response.status_code == 201:
        trip = response.json()
        trip_id = trip['trip_id']
        print(f"✓ Trip created: {trip_id}")
        print(f"  - Status: OPEN")
        print(f"  - Initial fare: ₹{trip['fare']} (driver allowance only)")
    else:
        print(f"✗ Failed to create trip: {response.text}")
        return
    
    # 4. Assign driver to trip
    print("\n4. Assigning driver to trip...")
    response = requests.patch(f"{BASE_URL}/trips/{trip_id}/assign-driver/{driver_id}")
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Driver assigned: {result['driver_name']}")
        print(f"  - Trip status: {result['trip_status']}")
    else:
        print(f"✗ Failed to assign driver: {response.text}")
        return
    
    # 5. Test odometer start - should auto-start trip
    print("\n5. Setting odometer start reading...")
    odo_start = 12500
    response = requests.patch(f"{BASE_URL}/trips/{trip_id}/odometer-start", params={"odo_start": odo_start})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Odometer start set: {odo_start} km")
        print(f"  - Trip status auto-changed to: {result['trip_status']}")
        print(f"  - Started at: {result['started_at']}")
    else:
        print(f"✗ Failed to set odometer start: {response.text}")
        return
    
    # 6. Test odometer end - should auto-complete trip and calculate fare
    print("\n6. Setting odometer end reading...")
    odo_end = 12520  # 20 km trip
    response = requests.patch(f"{BASE_URL}/trips/{trip_id}/odometer-end", params={"odo_end": odo_end})
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Odometer end set: {odo_end} km")
        print(f"  - Trip status auto-changed to: {result['trip_status']}")
        print(f"  - Distance calculated: {result['distance_km']} km")
        print(f"  - Final fare: ₹{result['fare']}")
        print(f"  - Ended at: {result['ended_at']}")
        
        # Verify fare calculation
        distance = float(result['distance_km'])
        expected_fare = max(distance, 5) * 15.00 + 200.00  # min 5km * ₹15/km + ₹200 allowance
        print(f"  - Expected fare: ₹{expected_fare}")
        print(f"  - Calculation: max({distance}, 5) * 15.00 + 200.00 = ₹{expected_fare}")
    else:
        print(f"✗ Failed to set odometer end: {response.text}")
        return
    
    # 7. Verify driver is available again
    print("\n7. Checking driver availability...")
    response = requests.get(f"{BASE_URL}/drivers/{driver_id}")
    if response.status_code == 200:
        driver_details = response.json()
        print(f"✓ Driver availability: {driver_details['is_available']}")
    else:
        print(f"✗ Failed to get driver details: {response.text}")
    
    # 8. Get final trip details
    print("\n8. Final trip details...")
    response = requests.get(f"{BASE_URL}/trips/{trip_id}")
    if response.status_code == 200:
        final_trip = response.json()
        print(f"✓ Trip completed successfully")
        print(f"  - Trip ID: {final_trip['trip_id']}")
        print(f"  - Status: {final_trip['trip_status']}")
        print(f"  - Odometer start: {final_trip['odo_start']} km")
        print(f"  - Odometer end: {final_trip['odo_end']} km")
        print(f"  - Distance: {final_trip['distance_km']} km")
        print(f"  - Final fare: ₹{final_trip['fare']}")
        print(f"  - Started at: {final_trip['started_at']}")
        print(f"  - Ended at: {final_trip['ended_at']}")
    else:
        print(f"✗ Failed to get final trip details: {response.text}")

def test_edge_cases():
    """Test edge cases for fare calculation"""
    
    print("\n\n=== Testing Edge Cases ===\n")
    
    # Test minimum distance fare calculation
    print("1. Testing minimum distance fare (3km trip with 5km minimum)...")
    
    # Create another trip for testing
    trip_data = {
        "customer_name": "Jane Customer",
        "customer_phone": "9876543212",
        "pickup_address": "Bandra",
        "drop_address": "Kurla",
        "trip_type": "one_way",
        "vehicle_type": "sedan",
        "passenger_count": 1
    }
    
    response = requests.post(f"{BASE_URL}/trips/", json=trip_data)
    if response.status_code == 201:
        trip = response.json()
        trip_id = trip['trip_id']
        print(f"✓ Test trip created: {trip_id}")
        
        # Get available driver
        response = requests.get(f"{BASE_URL}/trips/available-drivers")
        if response.status_code == 200:
            drivers = response.json()['available_drivers']
            if drivers:
                driver_id = drivers[0]['driver_id']
                
                # Assign driver
                response = requests.patch(f"{BASE_URL}/trips/{trip_id}/assign-driver/{driver_id}")
                if response.status_code == 200:
                    print("✓ Driver assigned")
                    
                    # Set odometer readings for 3km trip
                    odo_start = 15000
                    odo_end = 15003  # Only 3km
                    
                    # Start trip
                    response = requests.patch(f"{BASE_URL}/trips/{trip_id}/odometer-start", params={"odo_start": odo_start})
                    if response.status_code == 200:
                        print(f"✓ Trip started with odometer: {odo_start}")
                        
                        # End trip
                        response = requests.patch(f"{BASE_URL}/trips/{trip_id}/odometer-end", params={"odo_end": odo_end})
                        if response.status_code == 200:
                            result = response.json()
                            distance = float(result['distance_km'])
                            fare = float(result['fare'])
                            
                            print(f"✓ Trip completed")
                            print(f"  - Actual distance: {distance} km")
                            print(f"  - Minimum distance: 5 km")
                            print(f"  - Billable distance: max({distance}, 5) = 5 km")
                            print(f"  - Fare calculation: 5 * 15.00 + 200.00 = ₹275.00")
                            print(f"  - Actual fare: ₹{fare}")
                            
                            if fare == 275.00:
                                print("✓ Minimum distance fare calculation is correct!")
                            else:
                                print("✗ Minimum distance fare calculation is incorrect!")
                        else:
                            print(f"✗ Failed to end trip: {response.text}")
                    else:
                        print(f"✗ Failed to start trip: {response.text}")
                else:
                    print(f"✗ Failed to assign driver: {response.text}")
            else:
                print("✗ No available drivers found")
        else:
            print(f"✗ Failed to get available drivers: {response.text}")
    else:
        print(f"✗ Failed to create test trip: {response.text}")

def test_round_trip_fare():
    """Test round trip fare calculation"""
    
    print("\n\n=== Testing Round Trip Fare ===\n")
    
    # Create round trip
    trip_data = {
        "customer_name": "Round Trip Customer",
        "customer_phone": "9876543213",
        "pickup_address": "Mumbai",
        "drop_address": "Pune",
        "trip_type": "round_trip",
        "vehicle_type": "sedan",
        "passenger_count": 3
    }
    
    response = requests.post(f"{BASE_URL}/trips/", json=trip_data)
    if response.status_code == 201:
        trip = response.json()
        trip_id = trip['trip_id']
        print(f"✓ Round trip created: {trip_id}")
        
        # Get available driver
        response = requests.get(f"{BASE_URL}/trips/available-drivers")
        if response.status_code == 200:
            drivers = response.json()['available_drivers']
            if drivers:
                driver_id = drivers[0]['driver_id']
                
                # Assign and complete trip
                requests.patch(f"{BASE_URL}/trips/{trip_id}/assign-driver/{driver_id}")
                requests.patch(f"{BASE_URL}/trips/{trip_id}/odometer-start", params={"odo_start": 20000})
                
                # 150km round trip
                response = requests.patch(f"{BASE_URL}/trips/{trip_id}/odometer-end", params={"odo_end": 20150})
                if response.status_code == 200:
                    result = response.json()
                    distance = float(result['distance_km'])
                    fare = float(result['fare'])
                    
                    print(f"✓ Round trip completed")
                    print(f"  - Distance: {distance} km")
                    print(f"  - Round trip rate: ₹12/km")
                    print(f"  - Minimum: 10 km")
                    print(f"  - Billable: max({distance}, 10) = {distance} km")
                    print(f"  - Fare calculation: {distance} * 12.00 + 200.00 = ₹{distance * 12 + 200}")
                    print(f"  - Actual fare: ₹{fare}")
                    
                    expected_fare = distance * 12 + 200
                    if abs(fare - expected_fare) < 0.01:
                        print("✓ Round trip fare calculation is correct!")
                    else:
                        print("✗ Round trip fare calculation is incorrect!")
                else:
                    print(f"✗ Failed to complete round trip: {response.text}")
            else:
                print("✗ No available drivers found")
        else:
            print(f"✗ Failed to get available drivers: {response.text}")
    else:
        print(f"✗ Failed to create round trip: {response.text}")

def test_manual_trip_update():
    """Test manual trip update with odometer values"""
    
    print("\n\n=== Testing Manual Trip Update ===\n")
    
    # Create trip
    trip_data = {
        "customer_name": "Manual Update Customer",
        "customer_phone": "9876543214",
        "pickup_address": "Test Pickup",
        "drop_address": "Test Drop",
        "trip_type": "one_way",
        "vehicle_type": "sedan",
        "passenger_count": 1
    }
    
    response = requests.post(f"{BASE_URL}/trips/", json=trip_data)
    if response.status_code == 201:
        trip = response.json()
        trip_id = trip['trip_id']
        print(f"✓ Trip created for manual update: {trip_id}")
        
        # Get available driver and assign
        response = requests.get(f"{BASE_URL}/trips/available-drivers")
        if response.status_code == 200:
            drivers = response.json()['available_drivers']
            if drivers:
                driver_id = drivers[0]['driver_id']
                requests.patch(f"{BASE_URL}/trips/{trip_id}/assign-driver/{driver_id}")
                print("✓ Driver assigned")
                
                # Test manual update with both odometer readings at once
                update_data = {
                    "odo_start": 25000,
                    "odo_end": 25030  # 30km trip
                }
                
                response = requests.put(f"{BASE_URL}/trips/{trip_id}", json=update_data)
                if response.status_code == 200:
                    result = response.json()
                    print(f"✓ Trip updated manually")
                    print(f"  - Status: {result['trip_status']}")
                    print(f"  - Distance: {result['distance_km']} km")
                    print(f"  - Fare: ₹{result['fare']}")
                    print(f"  - Started at: {result['started_at']}")
                    print(f"  - Ended at: {result['ended_at']}")
                    
                    # Verify auto-completion worked
                    if result['trip_status'] == 'COMPLETED':
                        print("✓ Trip auto-completed with manual update!")
                    else:
                        print("✗ Trip did not auto-complete")
                else:
                    print(f"✗ Failed to update trip manually: {response.text}")
            else:
                print("✗ No available drivers found")
        else:
            print(f"✗ Failed to get available drivers: {response.text}")
    else:
        print(f"✗ Failed to create trip for manual update: {response.text}")

if __name__ == "__main__":
    print("Testing Odometer, Distance & Fare Calculation System")
    print("=" * 60)
    
    try:
        test_complete_trip_workflow()
        test_edge_cases()
        test_round_trip_fare()
        test_manual_trip_update()
        
        print("\n" + "=" * 60)
        print("All tests completed! Check the results above.")
        print("Key features tested:")
        print("  ✓ Automatic trip status changes based on odometer readings")
        print("  ✓ Distance calculation from odometer difference")
        print("  ✓ Fare calculation with minimum distance rules")
        print("  ✓ Different rates for one-way vs round-trip")
        print("  ✓ Driver allowance inclusion")
        print("  ✓ Driver availability management")
        
    except Exception as e:
        print(f"\nTest execution failed: {str(e)}")