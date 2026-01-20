"""
Test Admin API Endpoints
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

def test_create_admin():
    """Test creating a new admin"""
    print("\n1. Creating new admin...")
    data = {
        "name": "Test Admin",
        "phone_number": 9876543210,
        "role": "ADMIN"
    }
    response = requests.post(f"{BASE_URL}/admins/", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json().get("admin_id") if response.status_code == 201 else None

def test_get_all_admins():
    """Test getting all admins"""
    print("\n2. Getting all admins...")
    response = requests.get(f"{BASE_URL}/admins/")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_admin_by_id(admin_id):
    """Test getting admin by ID"""
    print(f"\n3. Getting admin by ID: {admin_id}...")
    response = requests.get(f"{BASE_URL}/admins/{admin_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_get_admin_by_phone(phone_number):
    """Test getting admin by phone"""
    print(f"\n4. Getting admin by phone: {phone_number}...")
    response = requests.get(f"{BASE_URL}/admins/phone/{phone_number}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def test_update_admin(admin_id):
    """Test updating admin"""
    print(f"\n5. Updating admin: {admin_id}...")
    data = {
        "name": "Updated Admin Name",
        "is_active": True
    }
    response = requests.patch(f"{BASE_URL}/admins/{admin_id}", json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

if __name__ == "__main__":
    print("=" * 80)
    print("ADMIN API TESTS")
    print("=" * 80)
    
    # Create admin
    admin_id = test_create_admin()
    
    if admin_id:
        # Get all admins
        test_get_all_admins()
        
        # Get by ID
        test_get_admin_by_id(admin_id)
        
        # Get by phone
        test_get_admin_by_phone(9876543210)
        
        # Update admin
        test_update_admin(admin_id)
        
        print("\n" + "=" * 80)
        print("✅ All tests completed!")
        print("=" * 80)
    else:
        print("\n❌ Failed to create admin")
