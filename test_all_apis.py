"""
Comprehensive API Testing Script for Cab Booking System
Tests all endpoints and generates detailed report
"""
import requests
import json
from datetime import datetime
from typing import Dict, List, Tuple
import sys

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
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(60)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.RESET}\n")

def print_test(name: str, status: bool, details: str = ""):
    """Print test result"""
    status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if status else f"{Colors.RED}✗{Colors.RESET}"
    status_text = f"{Colors.GREEN}PASS{Colors.RESET}" if status else f"{Colors.RED}FAIL{Colors.RESET}"
    print(f"{status_icon} {name:<50} [{status_text}]")
    if details and not status:
        print(f"  {Colors.YELLOW}└─ {details}{Colors.RESET}")
    
    test_results.append({
        'name': name,
        'status': 'PASS' if status else 'FAIL',
        'details': details,
        'timestamp': datetime.now().isoformat()
    })

def test_endpoint(method: str, endpoint: str, name: str, data: Dict = None, 
                 expected_status: int = 200, save_id_key: str = None) -> Tuple[bool, any]:
    """Test a single endpoint"""
    url = f"{API_BASE}{endpoint}" if not endpoint.startswith('http') else endpoint
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
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
                if 'id' in response_data:
                    created_ids[save_id_key] = response_data['id']
                elif isinstance(response_data, dict) and len(response_data) > 0:
                    # Try to find ID in nested structure
                    for key, value in response_data.items():
                        if 'id' in str(key).lower() and isinstance(value, int):
                            created_ids[save_id_key] = value
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
    print(f"\n{Colors.BOLD}Cab Booking API - Comprehensive Test Suite{Colors.RESET}")
    print(f"Testing server at: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ========== SYSTEM ENDPOINTS ==========
    print_header("SYSTEM ENDPOINTS")
    
    test_endpoint("GET", BASE_URL, "Root Endpoint")
    test_endpoint("GET", f"{BASE_URL}/health", "Health Check")
    test_endpoint("GET", "/stats", "API Statistics")
    
    # ========== TARIFF CONFIGURATION ==========
    print_header("TARIFF CONFIGURATION API")
    
    test_endpoint("GET", "/tariff-config", "Get All Tariff Configs")
    
    tariff_data = {
        "vehicle_type": "sedan",
        "one_way_per_km": 12.00,
        "one_way_min_km": 5,
        "round_trip_per_km": 10.00,
        "round_trip_min_km": 10,
        "driver_allowance": 200.00,
        "is_active": True
    }
    test_endpoint("POST", "/tariff-config", "Create Tariff Config", 
                 tariff_data, 201, "tariff_config_id")
    
    test_endpoint("GET", "/tariff-config/active/sedan", "Get Active Tariff for Sedan")
    
    # ========== DRIVERS API ==========
    print_header("DRIVERS API")
    
    test_endpoint("GET", "/drivers", "Get All Drivers")
    
    driver_data = {
        "name": "Test Driver",
        "phone_number": "9876543210",
        "email": f"testdriver{datetime.now().timestamp()}@example.com",
        "primary_location": "Mumbai",
        "licence_number": f"MH{int(datetime.now().timestamp())}"
    }
    success, response = test_endpoint("POST", "/drivers", "Create Driver", 
                                     driver_data, 201, "driver_id")
    
    if created_ids['driver_id']:
        driver_id = created_ids['driver_id']
        
        test_endpoint("GET", f"/drivers/{driver_id}", "Get Driver by ID")
        
        update_data = {
            "name": "Updated Test Driver",
            "primary_location": "Delhi"
        }
        test_endpoint("PUT", f"/drivers/{driver_id}", "Update Driver", update_data)
        
        test_endpoint("PATCH", f"/drivers/{driver_id}/availability?is_available=true", 
                     "Update Driver Availability")
        
        test_endpoint("GET", f"/drivers/{driver_id}/wallet-balance", "Get Driver Wallet Balance")
    
    # ========== VEHICLES API ==========
    print_header("VEHICLES API")
    
    test_endpoint("GET", "/vehicles", "Get All Vehicles")
    
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
        success, response = test_endpoint("POST", "/vehicles", "Create Vehicle", 
                                         vehicle_data, 201, "vehicle_id")
        
        if created_ids['vehicle_id']:
            vehicle_id = created_ids['vehicle_id']
            
            test_endpoint("GET", f"/vehicles/{vehicle_id}", "Get Vehicle by ID")
            
            update_data = {
                "vehicle_color": "Black",
                "seating_capacity": 5
            }
            test_endpoint("PUT", f"/vehicles/{vehicle_id}", "Update Vehicle", update_data)
            
            test_endpoint("PATCH", f"/vehicles/{vehicle_id}/approve", "Approve Vehicle")
            
            test_endpoint("GET", f"/vehicles/driver/{created_ids['driver_id']}", 
                         "Get Vehicles by Driver")
    
    # ========== TRIPS API ==========
    print_header("TRIPS API")
    
    test_endpoint("GET", "/trips", "Get All Trips")
    
    trip_data = {
        "customer_name": "Test Customer",
        "customer_phone": "9876543211",
        "pickup_address": "Mumbai Airport",
        "drop_address": "Bandra West",
        "trip_type": "one_way",
        "vehicle_type": "sedan",
        "passenger_count": 2
    }
    success, response = test_endpoint("POST", "/trips", "Create Trip", 
                                     trip_data, 201, "trip_id")
    
    if created_ids['trip_id']:
        trip_id = created_ids['trip_id']
        
        test_endpoint("GET", f"/trips/{trip_id}", "Get Trip by ID")
        
        if created_ids['driver_id']:
            test_endpoint("PATCH", f"/trips/{trip_id}/assign-driver/{created_ids['driver_id']}", 
                         "Assign Driver to Trip")
            
            test_endpoint("GET", f"/trips/driver/{created_ids['driver_id']}", 
                         "Get Trips by Driver")
        
        test_endpoint("PATCH", f"/trips/{trip_id}/status?new_status=started", 
                     "Update Trip Status to Started")
        
        update_data = {
            "trip_status": "completed",
            "distance_km": 15.5
        }
        test_endpoint("PUT", f"/trips/{trip_id}", "Update Trip", update_data)
    
    # ========== PAYMENTS API ==========
    print_header("PAYMENTS API")
    
    test_endpoint("GET", "/payments", "Get All Payments")
    
    if created_ids['trip_id']:
        payment_data = {
            "trip_id": created_ids['trip_id'],
            "amount": 500.00,
            "payment_method": "card",
            "payment_status": "completed",
            "transaction_reference": f"TXN{int(datetime.now().timestamp())}"
        }
        test_endpoint("POST", "/payments", "Create Payment", 
                     payment_data, 201, "payment_id")
    
    # ========== WALLET TRANSACTIONS API ==========
    print_header("WALLET TRANSACTIONS API")
    
    test_endpoint("GET", "/wallet-transactions", "Get All Wallet Transactions")
    
    if created_ids['driver_id']:
        wallet_data = {
            "driver_id": created_ids['driver_id'],
            "transaction_type": "credit",
            "amount": 1000.00,
            "description": "Test wallet credit"
        }
        test_endpoint("POST", "/wallet-transactions", "Create Wallet Transaction", 
                     wallet_data, 201, "wallet_transaction_id")
        
        test_endpoint("GET", f"/wallet-transactions/driver/{created_ids['driver_id']}", 
                     "Get Wallet Transactions by Driver")
    
    # ========== CLEANUP (Optional - Delete Test Data) ==========
    print_header("CLEANUP (Deleting Test Data)")
    
    # Note: Uncomment these if you want to clean up test data
    # if created_ids['payment_id']:
    #     test_endpoint("DELETE", f"/payments/{created_ids['payment_id']}", 
    #                  "Delete Payment", expected_status=204)
    
    # if created_ids['trip_id']:
    #     test_endpoint("DELETE", f"/trips/{created_ids['trip_id']}", 
    #                  "Delete Trip", expected_status=204)
    
    # if created_ids['vehicle_id']:
    #     test_endpoint("DELETE", f"/vehicles/{created_ids['vehicle_id']}", 
    #                  "Delete Vehicle", expected_status=204)
    
    # if created_ids['driver_id']:
    #     test_endpoint("DELETE", f"/drivers/{created_ids['driver_id']}", 
    #                  "Delete Driver", expected_status=204)
    
    print(f"\n{Colors.YELLOW}Note: Test data was NOT deleted. Uncomment cleanup section to enable.{Colors.RESET}")

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
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
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
        sys.exit(1)
