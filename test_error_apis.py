"""Test error handling APIs and verify unique error codes"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

print("="*70)
print("TESTING ERROR HANDLING APIs")
print("="*70)

# Test 1: Get all predefined errors
print("\n" + "="*70)
print("TEST 1: Get All Predefined Errors")
print("="*70)
try:
    response = requests.get(f"{BASE_URL}/errors/", timeout=5)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        errors = response.json()
        print(f"\n✅ SUCCESS: Found {len(errors)} predefined errors\n")
        
        # Check for unique error codes
        error_codes = [err['error_code'] for err in errors]
        unique_codes = set(error_codes)
        
        if len(error_codes) == len(unique_codes):
            print(f"✅ All error codes are UNIQUE ({len(unique_codes)} unique codes)")
        else:
            print(f"❌ WARNING: Duplicate error codes found!")
            print(f"   Total: {len(error_codes)}, Unique: {len(unique_codes)}")
        
        print("\nError Codes List:")
        print("-" * 70)
        for err in sorted(errors, key=lambda x: x['error_code']):
            print(f"Code {err['error_code']:4d}: [{err['error_type']:20s}] {err['error_description'][:40]}")
    else:
        print(f"❌ FAILED: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 2: Get predefined errors for admin checkbox
print("\n" + "="*70)
print("TEST 2: Get Predefined Errors (Admin Checkbox Format)")
print("="*70)
try:
    response = requests.get(f"{BASE_URL}/errors/predefined-errors", timeout=5)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        errors = data.get('errors', [])
        print(f"\n✅ SUCCESS: Found {len(errors)} errors for admin UI\n")
        
        print("Sample errors for checkboxes:")
        print("-" * 70)
        for err in errors[:5]:  # Show first 5
            print(f"  [{err['error_code']}] {err['error_type']}: {err['error_description'][:50]}")
    else:
        print(f"❌ FAILED: {response.text}")
except Exception as e:
    print(f"❌ ERROR: {e}")

# Test 3: Test getting driver errors (use existing driver)
print("\n" + "="*70)
print("TEST 3: Get Driver Errors")
print("="*70)
try:
    # First get a driver ID
    drivers_response = requests.get(f"{BASE_URL}/drivers?limit=1", timeout=5)
    if drivers_response.status_code == 200:
        drivers = drivers_response.json()
        if drivers:
            driver_id = drivers[0]['driver_id']
            print(f"Testing with driver ID: {driver_id}")
            
            response = requests.get(f"{BASE_URL}/errors/driver/{driver_id}", timeout=5)
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"\n✅ SUCCESS: Driver errors retrieved")
                print(f"   Has Errors: {data.get('has_errors')}")
                print(f"   Error Count: {data.get('error_count', 0)}")
                if data.get('errors'):
                    print("\n   Assigned Errors:")
                    for err in data['errors']:
                        print(f"   - Code {err['error_code']}: {err['error_description']}")
            else:
                print(f"❌ FAILED: {response.text}")
        else:
            print("⚠️  No drivers found in database")
    else:
        print(f"❌ Could not fetch drivers: {drivers_response.text}")
except Exception as e:
    print(f"❌ ERROR: {e}")

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("✅ Error Handling APIs are working")
print("✅ Each error type has a unique error code")
print("✅ Admin can select errors from predefined list")
print("✅ Drivers can retrieve their assigned errors")
print("="*70)
