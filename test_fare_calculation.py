"""
Test fare calculation for the specific trip
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_fare_calculation():
    """Test fare calculation for the specific trip"""
    
    trip_id = "3bd094d1-4fa7-411d-a3ca-58fadc52a966"
    
    print("=== FARE CALCULATION TEST ===")
    print(f"Trip ID: {trip_id}")
    
    # 1. Check tariff configuration for sedan
    print("\n1. Checking tariff configuration for sedan...")
    response = requests.get(f"{BASE_URL}/tariff-config")
    if response.status_code == 200:
        tariffs = response.json()
        sedan_tariff = None
        for tariff in tariffs:
            if tariff['vehicle_type'] == 'sedan':
                sedan_tariff = tariff
                break
        
        if sedan_tariff:
            print(f"Sedan Tariff Config:")
            print(f"  - One Way Per KM: ₹{sedan_tariff['one_way_per_km']}")
            print(f"  - One Way Min KM: {sedan_tariff['one_way_min_km']}")
            print(f"  - Round Trip Per KM: ₹{sedan_tariff['round_trip_per_km']}")
            print(f"  - Round Trip Min KM: {sedan_tariff['round_trip_min_km']}")
            print(f"  - Driver Allowance: ₹{sedan_tariff['driver_allowance']}")
        else:
            print("No sedan tariff configuration found!")
    else:
        print(f"Error getting tariff config: {response.status_code}")
    
    # 2. Get current trip details
    print("\n2. Current trip details...")
    response = requests.get(f"{BASE_URL}/trips/{trip_id}")
    if response.status_code == 200:
        trip = response.json()
        print(f"Trip Type: {trip['trip_type']}")
        print(f"Vehicle Type: {trip['vehicle_type']}")
        print(f"Odo Start: {trip['odo_start']}")
        print(f"Odo End: {trip['odo_end']}")
        print(f"Current Distance: {trip['distance_km']} km")
        print(f"Current Fare: ₹{trip['fare']}")
        print(f"Status: {trip['trip_status']}")
        
        # Calculate expected fare
        if sedan_tariff and trip['odo_start'] and trip['odo_end']:
            distance = trip['odo_end'] - trip['odo_start']
            print(f"\n3. Expected fare calculation:")
            print(f"Distance: {distance} km")
            
            if trip['trip_type'] == 'ONE_WAY':
                per_km = sedan_tariff['one_way_per_km']
                min_km = sedan_tariff['one_way_min_km']
                billable_km = max(distance, min_km)
                fare_calc = billable_km * per_km + sedan_tariff['driver_allowance']
                print(f"ONE_WAY: max({distance}, {min_km}) × ₹{per_km} + ₹{sedan_tariff['driver_allowance']} = ₹{fare_calc}")
            else:
                per_km = sedan_tariff['round_trip_per_km']
                min_km = sedan_tariff['round_trip_min_km']
                billable_km = max(distance, min_km)
                fare_calc = billable_km * per_km + sedan_tariff['driver_allowance']
                print(f"ROUND_TRIP: max({distance}, {min_km}) × ₹{per_km} + ₹{sedan_tariff['driver_allowance']} = ₹{fare_calc}")
    
    # 3. Fix the trip and verify fare calculation
    print("\n4. Fixing trip status and calculating fare...")
    response = requests.patch(f"{BASE_URL}/trips/{trip_id}/fix-status")
    if response.status_code == 200:
        result = response.json()
        print(f"Status: {result['old_status']} → {result['new_status']}")
        print(f"Distance: {result['distance_km']} km")
        print(f"Calculated Fare: ₹{result['fare']}")
        
        if result['new_status'] == 'COMPLETED' and result['fare']:
            print("✅ SUCCESS: Fare calculated automatically!")
        else:
            print("❌ FAILED: Fare not calculated")
    else:
        print(f"Error fixing trip: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_fare_calculation()