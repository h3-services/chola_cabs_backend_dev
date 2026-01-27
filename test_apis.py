"""
Simple API Test Script
Tests the optimized APIs to verify they're working correctly
"""
import requests
import json
from datetime import datetime

# Base URL
BASE_URL = "http://localhost:8000"

def print_result(test_name, success, message=""):
    """Print test result"""
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} - {test_name}")
    if message:
        print(f"   {message}")
    print()

def test_server_health():
    """Test if server is running"""
    try:
        response = requests.get(f"{BASE_URL}/docs")
        return response.status_code == 200
    except:
        return False

def test_drivers_endpoint():
    """Test drivers endpoint (OPTIMIZED)"""
    try:
        response = requests.get(f"{BASE_URL}/drivers")
        success = response.status_code == 200
        message = f"Returned {len(response.json())} drivers" if success else f"Status: {response.status_code}"
        return success, message
    except Exception as e:
        return False, str(e)

def test_trips_endpoint():
    """Test trips endpoint (OPTIMIZED)"""
    try:
        response = requests.get(f"{BASE_URL}/trips")
        success = response.status_code == 200
        message = f"Returned {len(response.json())} trips" if success else f"Status: {response.status_code}"
        return success, message
    except Exception as e:
        return False, str(e)

def test_available_trips():
    """Test available trips endpoint (OPTIMIZED - specialized query)"""
    try:
        response = requests.get(f"{BASE_URL}/trips/available")
        success = response.status_code == 200
        message = f"Returned {len(response.json())} available trips" if success else f"Status: {response.status_code}"
        return success, message
    except Exception as e:
        return False, str(e)

def test_trip_statistics():
    """Test trip statistics endpoint (OPTIMIZED - single query)"""
    try:
        response = requests.get(f"{BASE_URL}/trips/statistics/dashboard")
        success = response.status_code == 200
        if success:
            data = response.json()
            message = f"Total: {data.get('total')}, Completed: {data.get('completed')}, Revenue: {data.get('total_revenue')}"
        else:
            message = f"Status: {response.status_code}"
        return success, message
    except Exception as e:
        return False, str(e)

def test_vehicles_endpoint():
    """Test vehicles endpoint (OPTIMIZED)"""
    try:
        response = requests.get(f"{BASE_URL}/vehicles")
        success = response.status_code == 200
        message = f"Returned {len(response.json())} vehicles" if success else f"Status: {response.status_code}"
        return success, message
    except Exception as e:
        return False, str(e)

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 TESTING OPTIMIZED APIS")
    print("=" * 60)
    print()
    
    # Test 1: Server Health
    print("Test 1: Server Health Check")
    if test_server_health():
        print_result("Server is running", True, "Swagger UI accessible at /docs")
    else:
        print_result("Server is running", False, "Cannot connect to server. Is it running?")
        print("Please start the server with: python -m uvicorn app.main:app --reload")
        return
    
    # Test 2: Drivers Endpoint
    print("Test 2: Drivers Endpoint (OPTIMIZED)")
    success, message = test_drivers_endpoint()
    print_result("GET /drivers", success, message)
    
    # Test 3: Trips Endpoint
    print("Test 3: Trips Endpoint (OPTIMIZED)")
    success, message = test_trips_endpoint()
    print_result("GET /trips", success, message)
    
    # Test 4: Available Trips
    print("Test 4: Available Trips (OPTIMIZED - Specialized Query)")
    success, message = test_available_trips()
    print_result("GET /trips/available", success, message)
    
    # Test 5: Trip Statistics
    print("Test 5: Trip Statistics (OPTIMIZED - Single Query)")
    success, message = test_trip_statistics()
    print_result("GET /trips/statistics/dashboard", success, message)
    
    # Test 6: Vehicles Endpoint
    print("Test 6: Vehicles Endpoint (OPTIMIZED)")
    success, message = test_vehicles_endpoint()
    print_result("GET /vehicles", success, message)
    
    print("=" * 60)
    print("✅ TESTING COMPLETE!")
    print("=" * 60)
    print()
    print("📊 Performance Notes:")
    print("- All endpoints now use CRUD layer (no direct db.query())")
    print("- Eager loading eliminates N+1 queries")
    print("- Specialized methods improve query performance")
    print("- Proper error handling and logging implemented")
    print()
    print("📖 For more tests, visit: http://localhost:8000/docs")
    print()

if __name__ == "__main__":
    main()
