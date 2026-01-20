"""
Quick test to check admin API response
"""
import requests
import json

response = requests.get("http://localhost:8000/api/v1/admins/")
print("Status Code:", response.status_code)
print("\nResponse JSON:")
print(json.dumps(response.json(), indent=2))

if response.status_code == 200:
    admins = response.json()
    if admins:
        print(f"\nFirst admin admin_id: {admins[0].get('admin_id', 'NOT FOUND')}")
        print("\nAll fields in response:")
        for key in admins[0].keys():
            print(f"  - {key}: {admins[0][key]}")
