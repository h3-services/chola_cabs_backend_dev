"""
Comprehensive CRUD API Testing Script for Cab Booking System
Tests all endpoints including uploads and generates detailed report
"""
import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple
import sys
import io

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Test results storage
test_results = []
created_ids = {
    'driver_id': None,
    'vehicle_id': None,
    'trip_id': None,
    'payment_id': None,
    'wallet_transaction_id': None,
    'tariff_config_id': None
}

def print_header(text: str):
    """Print formatted header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_test(name: str, status: bool, details: str = ""):
    """Print test result"""
    status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if status else f"{Colors.RED}✗{Colors.RESET}"
    status_text = f"{Colors.GREEN}PASS{Colors.RESET}" if status else f"{Colors.RED}FAIL{Colors.RESET}"
    print(f"{status_icon} {name:<55} [{status_text}]")
    if details and not status:
        print(f"  {Colors.YELLOW}└─ {details}{Colors.RESET}")
    
    test_results.append({
        'name': name,
        'status': 'PASS' if status else 'FAIL',
        'details': details,
        'timestamp': datetime.now().isoformat()
    })

def test_endpoint(method: str, endpoint: str, name: str, data: Dict = None, 
                 expected_status: int = 200, save_id_key: str = None, files: Dict = None) -> Tuple[bool, any]:
    """Test a single endpoint"""
    url = f"{API_BASE}{endpoint}" if not endpoint.startswith('http') else endpoint
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            if files:
                response = requests.post(url, files=files, timeout=10)
            else:
                response = requests.post(url, json=data, timeout=10)
        elif method == "PUT":
            response = requests.put(url, json=data, timeout=10)
        elif method == "PATCH":
            response = requests.patch(url, json=data, timeout=10)
        elif method == "DELETE":
            response = requests.delete(url, timeout=10)
        else:
            print_test(name, False, f"Invalid method: {method}")
            return False, None
        
        success = response.status_code == expected_status
        details = ""
        
        if not success:
            details = f"Expected {expected_status}, got {response.status_code}"
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    details += f" - {error_data['detail']}"
            except:
                details += f" - {response.text[:100]}"
        
        # Save ID if requested
        if success and save_id_key and response.status_code in [200, 201]:
            try:
                response_data = response.json()
                # Try different ID field names
                for id_field in ['id', 'driver_id', 'vehicle_id', 'trip_id', 'payment_id', 
                                'wallet_id', 'tariff_id', 'config_id', 'transaction_id']:
                    if id_field in response_data:
                        created_ids[save_id_key] = response_data[id_field]
                        break
            except:
                pass
        
        print_test(name, success, details)
        return success, response
        
    except requests.exceptions.ConnectionError:
        print_test(name, False, "Connection refused - Is the server running?")
        return False, None
    except requests.exceptions.Timeout:
        print_test(name, False, "Request timeout")
        return False, None
    except Exception as e:
        print_test(name, False, f"Error: {str(e)}")
        return False, None

def run_all_tests():
    """Run all API tests"""
    print(f"\n{Colors.BOLD}Cab Booking API - Complete CRUD Test Suite{Colors.RESET}")
    print(f"Testing server at: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ========== SYSTEM ENDPOINTS ==========
    print_header("SYSTEM ENDPOINTS")
    
    test_endpoint("GET", BASE_URL, "Root Endpoint")
    test_endpoint("GET", f"{BASE_URL}/health", "Health Check")
    test_endpoint("GET", "/stats", "API Statistics")
    
    # ========== TARIFF CONFIGURATION - FULL CRUD ==========
    print_header("TARIFF CONFIGURATION API - CRUD")
    
    test_endpoint("GET", "/tariff-config", "GET - All Tariff Configs")
    
    tariff_data = {
        "vehicle_type": "sedan",
        "one_way_per_km": 12.00,
        "one_way_min_km": 5,
        "round_trip_per_km": 10.00,
        "round_trip_min_km": 10,
        "driver_allowance": 200.00,
        "is_active": True
    }
    success, response = test_endpoint("POST", "/tariff-config", "POST - Create Tariff Config", 
                                     tariff_data, 201, "tariff_config_id")
    
    if created_ids['tariff_config_id']:
        tariff_id = created_ids['tariff_config_id']
        test_endpoint("GET", f"/tariff-config/{tariff_id}", "GET - Tariff Config by ID")
        
        update_data = {"driver_allowance": 250.00}
        test_endpoint("PUT", f"/tariff-config/{tariff_id}", "PUT - Update Tariff Config", update_data)
    
    test_endpoint("GET", "/tariff-config/active/sedan", "GET - Active Tariff for Sedan")
    
    # ========== DRIVERS API - FULL CRUD ==========
    print_header("DRIVERS API - CRUD")
    
    test_endpoint("GET", "/drivers", "GET - All Drivers")
    
    driver_data = {
        "name": "Test Driver CRUD",
        "phone_number": f"{int(datetime.now().timestamp()) % 10000000000}",
        "email": f"testdriver{int(datetime.now().timestamp())}@example.com",
        "primary_location": "Mumbai",
        "licence_number": f"MH{int(datetime.now().timestamp()) % 1000000000}"
    }
    success, response = test_endpoint("POST", "/drivers", "POST - Create Driver", 
                                     driver_data, 201, "driver_id")
    
    if created_ids['driver_id']:
        driver_id = created_ids['driver_id']
        
        test_endpoint("GET", f"/drivers/{driver_id}", "GET - Driver by ID")
        
        update_data = {
            "name": "Updated Test Driver",
            "primary_location": "Delhi"
        }
        test_endpoint("PUT", f"/drivers/{driver_id}", "PUT - Update Driver", update_data)
        
        test_endpoint("PATCH", f"/drivers/{driver_id}/availability?is_available=true", 
                     "PATCH - Update Driver Availability")
        
        test_endpoint("GET", f"/drivers/{driver_id}/wallet-balance", "GET - Driver Wallet Balance")
    
    # ========== VEHICLES API - FULL CRUD ==========
    print_header("VEHICLES API - CRUD")
    
    test_endpoint("GET", "/vehicles", "GET - All Vehicles")
    
    if created_ids['driver_id']:
        vehicle_data = {
            "driver_id": created_ids['driver_id'],
            "vehicle_type": "sedan",
            "vehicle_brand": "Toyota",
            "vehicle_model": "Camry",
            "vehicle_number": f"MH01AB{int(datetime.now().timestamp()) % 10000}",
            "vehicle_color": "White",
            "seating_capacity": 4
        }
        success, response = test_endpoint("POST", "/vehicles", "POST - Create Vehicle", 
                                         vehicle_data, 201, "vehicle_id")
        
        if created_ids['vehicle_id']:
            vehicle_id = created_ids['vehicle_id']
            
            test_endpoint("GET", f"/vehicles/{vehicle_id}", "GET - Vehicle by ID")
            
            update_data = {
                "vehicle_color": "Black",
                "seating_capacity": 5
            }
            test_endpoint("PUT", f"/vehicles/{vehicle_id}", "PUT - Update Vehicle", update_data)
            
            test_endpoint("PATCH", f"/vehicles/{vehicle_id}/approve", "PATCH - Approve Vehicle")
            
            test_endpoint("GET", f"/vehicles/driver/{created_ids['driver_id']}", 
                         "GET - Vehicles by Driver")
    
    # ========== TRIPS API - FULL CRUD ==========
    print_header("TRIPS API - CRUD")
    
    test_endpoint("GET", "/trips", "GET - All Trips")
    
    trip_data = {
        "customer_name": "Test Customer",
        "customer_phone": "9876543211",
        "pickup_address": "Mumbai Airport",
        "drop_address": "Bandra West",
        "trip_type": "one_way",
        "vehicle_type": "sedan",
        "passenger_count": 2
    }
    success, response = test_endpoint("POST", "/trips", "POST - Create Trip", 
                                     trip_data, 201, "trip_id")
    
    if created_ids['trip_id']:
        trip_id = created_ids['trip_id']
        
        test_endpoint("GET", f"/trips/{trip_id}", "GET - Trip by ID")
        
        if created_ids['driver_id']:
            test_endpoint("PATCH", f"/trips/{trip_id}/assign-driver/{created_ids['driver_id']}", 
                         "PATCH - Assign Driver to Trip")
            
            test_endpoint("GET", f"/trips/driver/{created_ids['driver_id']}", 
                         "GET - Trips by Driver")
        
        test_endpoint("PATCH", f"/trips/{trip_id}/status?new_status=started", 
                     "PATCH - Update Trip Status to Started")
        
        update_data = {
            "trip_status": "completed",
            "distance_km": 15.5,
            "fare": 500.00
        }
        test_endpoint("PUT", f"/trips/{trip_id}", "PUT - Update Trip", update_data)
    
    # ========== PAYMENTS API - FULL CRUD ==========
    print_header("PAYMENTS API - CRUD")
    
    test_endpoint("GET", "/payments", "GET - All Payments")
    
    if created_ids['driver_id']:
        payment_data = {
            "driver_id": created_ids['driver_id'],
            "amount": 500.00,
            "transaction_type": "credit",
            "status": "completed",
            "transaction_id": f"TXN{int(datetime.now().timestamp())}"
        }
        success, response = test_endpoint("POST", "/payments", "POST - Create Payment", 
                                         payment_data, 201, "payment_id")
        
        if created_ids['payment_id']:
            payment_id = created_ids['payment_id']
            test_endpoint("GET", f"/payments/{payment_id}", "GET - Payment by ID")
            
            update_data = {"status": "completed"}
            test_endpoint("PUT", f"/payments/{payment_id}", "PUT - Update Payment", update_data)
        
        test_endpoint("GET", f"/payments/driver/{created_ids['driver_id']}", 
                     "GET - Payments by Driver")
    
    # ========== WALLET TRANSACTIONS API - FULL CRUD ==========
    print_header("WALLET TRANSACTIONS API - CRUD")
    
    test_endpoint("GET", "/wallet-transactions", "GET - All Wallet Transactions")
    
    if created_ids['driver_id']:
        wallet_data = {
            "driver_id": created_ids['driver_id'],
            "transaction_type": "credit",
            "amount": 1000.00,
            "description": "Test wallet credit"
        }
        success, response = test_endpoint("POST", "/wallet-transactions", "POST - Create Wallet Transaction", 
                                         wallet_data, 201, "wallet_transaction_id")
        
        if created_ids['wallet_transaction_id']:
            wallet_id = created_ids['wallet_transaction_id']
            test_endpoint("GET", f"/wallet-transactions/{wallet_id}", "GET - Wallet Transaction by ID")
        
        test_endpoint("GET", f"/wallet-transactions/driver/{created_ids['driver_id']}", 
                     "GET - Wallet Transactions by Driver")
    
    # ========== UPLOADS API ==========
    print_header("UPLOADS API")
    
    if created_ids['driver_id'] and created_ids['vehicle_id']:
        # Create a dummy image file for testing
        dummy_image = io.BytesIO(b"fake image content")
        dummy_image.name = "test_photo.jpg"
        
        files = {'file': ('test_photo.jpg', dummy_image, 'image/jpeg')}
        test_endpoint("POST", f"{BASE_URL}/api/v1/uploads/driver/{created_ids['driver_id']}/photo",
                     "POST - Upload Driver Photo", files=files)
        
        dummy_image.seek(0)
        files = {'file': ('test_aadhar.jpg', dummy_image, 'image/jpeg')}
        test_endpoint("POST", f"{BASE_URL}/api/v1/uploads/driver/{created_ids['driver_id']}/aadhar",
                     "POST - Upload Driver Aadhar", files=files)
        
        dummy_image.seek(0)
        files = {'file': ('test_licence.jpg', dummy_image, 'image/jpeg')}
        test_endpoint("POST", f"{BASE_URL}/api/v1/uploads/driver/{created_ids['driver_id']}/licence",
                     "POST - Upload Driver Licence", files=files)
        
        dummy_image.seek(0)
        files = {'file': ('test_rc.jpg', dummy_image, 'image/jpeg')}
        test_endpoint("POST", f"{BASE_URL}/api/v1/uploads/vehicle/{created_ids['vehicle_id']}/rc",
                     "POST - Upload Vehicle RC", files=files)
        
        dummy_image.seek(0)
        files = {'file': ('test_fc.jpg', dummy_image, 'image/jpeg')}
        test_endpoint("POST", f"{BASE_URL}/api/v1/uploads/vehicle/{created_ids['vehicle_id']}/fc",
                     "POST - Upload Vehicle FC", files=files)
        
        dummy_image.seek(0)
        files = {'file': ('test_front.jpg', dummy_image, 'image/jpeg')}
        test_endpoint("POST", f"{BASE_URL}/api/v1/uploads/vehicle/{created_ids['vehicle_id']}/photo/front",
                     "POST - Upload Vehicle Front Photo", files=files)

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total_tests = len(test_results)
    passed_tests = sum(1 for t in test_results if t['status'] == 'PASS')
    failed_tests = total_tests - passed_tests
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"Total Tests:  {total_tests}")
    print(f"{Colors.GREEN}Passed:       {passed_tests}{Colors.RESET}")
    print(f"{Colors.RED}Failed:       {failed_tests}{Colors.RESET}")
    print(f"Pass Rate:    {pass_rate:.1f}%")
    
    if failed_tests > 0:
        print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
        for test in test_results:
            if test['status'] == 'FAIL':
                print(f"  • {test['name']}")
                if test['details']:
                    print(f"    └─ {test['details']}")
    
    # Save detailed report
    report_file = f"test_report_crud_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'summary': {
                'total': total_tests,
                'passed': passed_tests,
                'failed': failed_tests,
                'pass_rate': pass_rate,
                'timestamp': datetime.now().isoformat()
            },
            'created_ids': created_ids,
            'results': test_results
        }, f, indent=2)
    
    print(f"\n{Colors.BLUE}Detailed report saved to: {report_file}{Colors.RESET}")
    print(f"\n{Colors.BOLD}Created Test Data IDs:{Colors.RESET}")
    for key, value in created_ids.items():
        if value:
            print(f"  {key}: {value}")
    
    return failed_tests == 0

if __name__ == "__main__":
    try:
        run_all_tests()
        success = print_summary()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted by user{Colors.RESET}")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal error: {str(e)}{Colors.RESET}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
