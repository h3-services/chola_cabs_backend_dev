"""Test the error handling endpoint locally to see the actual error"""
import requests

BASE_URL = "http://localhost:8000/api/v1"

print("Testing GET /api/v1/errors/")
print("="*60)

try:
    response = requests.get(f"{BASE_URL}/errors/", timeout=5)
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ SUCCESS: {len(data)} errors retrieved")
        if data:
            print("\nFirst error:")
            print(data[0])
    else:
        print(f"❌ ERROR Response:")
        print(response.text)
        
except requests.exceptions.ConnectionError:
    print("❌ Cannot connect to local server")
    print("Please start the server first with: python -m uvicorn app.main:app --reload")
except Exception as e:
    print(f"❌ Exception: {e}")
