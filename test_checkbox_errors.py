"""
Test script for checkbox-based error assignment API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1/errors"

def test_error_apis():
    """Test the new error handling APIs"""
    
    # 1. Get all predefined errors (for admin checkbox UI)
    print("1. Getting predefined errors for admin panel...")
    response = requests.get(f"{BASE_URL}/predefined-errors")
    if response.status_code == 200:
        errors = response.json()["errors"]
        print(f"Found {len(errors)} predefined errors:")
        for error in errors[:5]:  # Show first 5
            print(f"  - Code {error['error_code']}: {error['error_description']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
        return
    
    # 2. Review driver documents with checkbox selection
    print("\n2. Rejecting driver with selected error codes...")
    driver_id = "ef5f714a-b902-4251-91b9-3c3c2857e8be"  # Replace with actual driver ID
    selected_errors = [1001, 1004, 2001]  # Admin selected these checkboxes
    
    review_data = {
        "driver_id": driver_id,
        "action": "reject",
        "selected_error_codes": selected_errors
    }
    
    response = requests.post(
        f"{BASE_URL}/review-driver-documents",
        params={"driver_id": driver_id, "action": "reject"},
        json=selected_errors
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"Driver rejected with {result['errors_assigned']} errors")
        print(f"Assigned error codes: {result['assigned_error_codes']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")
    
    # 3. Get driver errors (for driver app)
    print("\n3. Getting driver errors...")
    response = requests.get(f"{BASE_URL}/driver/{driver_id}")
    if response.status_code == 200:
        driver_errors = response.json()
        print(f"Driver has {driver_errors['error_count']} errors:")
        for error in driver_errors['errors']:
            print(f"  - Code {error['error_code']}: {error['error_description']}")
    else:
        print(f"Error: {response.status_code} - {response.text}")

if __name__ == "__main__":
    test_error_apis()