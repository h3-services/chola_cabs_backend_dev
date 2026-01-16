"""
Comprehensive GET and POST API Test
Tests all GET and POST endpoints for all resources
"""
import requests
import json
from datetime import datetime
from typing import Dict, List

BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

# Color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

# Store created IDs for dependent tests
created_ids = {}
test_results = []

def print_header(text: str):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text.center(70)}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def test_api(method: str, endpoint: str, name: str, data: Dict = None, expected_status: int = 200):
    """Test a single API endpoint"""
    url = f"{API_BASE}{endpoint}" if not endpoint.startswith('http') else endpoint
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=10)
        elif method == "POST":
            response = requests.post(url, json=data, timeout=10)
        else:
            print(f"{Colors.RED}✗{Colors.RESET} {name:<50} [INVALID METHOD]")
            return False, None
        
        success = response.status_code == expected_status
        status_icon = f"{Colors.GREEN}✓{Colors.RESET}" if success else f"{Colors.RED}✗{Colors.RESET}"
        status_text = f"{Colors.GREEN}PASS{Colors.RESET}" if success else f"{Colors.RED}FAIL{Colors.RESET}"
        
        print(f"{status_icon} {name:<50} [{status_text}] Status: {response.status_code}")
        
        if not success:
            try:
                error_data = response.json()
                if 'detail' in error_data:
                    print(f"  {Colors.YELLOW}└─ {error_data['detail']}{Colors.RESET}")
            except:
                print(f"  {Colors.YELLOW}└─ {response.text[:100]}{Colors.RESET}")
        
        # Store created IDs
        if success and method == "POST" and response.status_code in [200, 201]:
            try:
                response_data = response.json()
                # Try to extract IDs from response
                for key in ['driver_id', 'vehicle_id', 'trip_id', 'payment_id', 'wallet_id', 'tariff_id']:
                    if key in response_data:
                        created_ids[key] = response_data[key]
                        print(f"  {Colors.BLUE}└─ Created {key}: {response_data[key]}{Colors.RESET}")
            except:
                pass
        
        test_results.append({
            'method': method,
            'endpoint': endpoint,
            'name': name,
            'status': 'PASS' if success else 'FAIL',
            'status_code': response.status_code,
            'expected': expected_status
        })
        
        return success, response
        
    except requests.exceptions.ConnectionError:
        print(f"{Colors.RED}✗{Colors.RESET} {name:<50} [FAIL] Connection refused")
        test_results.append({'method': method, 'endpoint': endpoint, 'name': name, 'status': 'FAIL', 'error': 'Connection refused'})
        return False, None
    except Exception as e:
        print(f"{Colors.RED}✗{Colors.RESET} {name:<50} [FAIL] {str(e)}")
        test_results.append({'method': method, 'endpoint': endpoint, 'name': name, 'status': 'FAIL', 'error': str(e)})
        return False, None

def run_all_tests():
    """Run all GET and POST tests"""
    print(f"\n{Colors.BOLD}Comprehensive GET & POST API Test Suite{Colors.RESET}")
    print(f"Testing server at: {BASE_URL}")
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    # ========== SYSTEM ENDPOINTS ==========
    print_header("SYSTEM ENDPOINTS")
    test_api("GET", BASE_URL, "GET Root Endpoint")
    test_api("GET", f"{BASE_URL}/health", "GET Health Check")
    test_api("GET", "/stats", "GET API Statistics")
    
    # ========== TARIFF CONFIG ==========
    print_header("TARIFF CONFIGURATION APIs")
    test_api("GET", "/tariff-config", "GET All Tariff Configs")
    
    tariff_data = {
        "vehicle_type": "suv",
        "one_way_per_km": 15.00,
        "one_way_min_km": 5,
        "round_trip_per_km": 12.00,
        "round_trip_min_km": 10,
        "driver_allowance": 300.00,
        "is_active": True
    }
    test_api("POST", "/tariff-config", "POST Create Tariff Config", tariff_data, 201)
    test_api("GET", "/tariff-config/active/sedan", "GET Active Tariff for Sedan")
    
    # ========== DRIVERS ==========
    print_header("DRIVER APIs")
    test_api("GET", "/drivers", "GET All Drivers")
    
    driver_data = {
        "name": f"Test Driver {datetime.now().timestamp()}",
        "phone_number": str(int(datetime.now().timestamp()) % 10000000000),
        "email": f"driver{int(datetime.now().timestamp())}@test.com",
        "primary_location": "Mumbai",
        "licence_number": f"MH{int(datetime.now().timestamp())}"
    }
    success, response = test_api("POST", "/drivers", "POST Create Driver", driver_data, 201)
    
    if created_ids.get('driver_id'):
        test_api("GET", f"/drivers/{created_ids['driver_id']}", "GET Driver by ID")
        test_api("GET", f"/drivers/{created_ids['driver_id']}/wallet-balance", "GET Driver Wallet Balance")
    
    # ========== VEHICLES ==========
    print_header("VEHICLE APIs")
    test_api("GET", "/vehicles", "GET All Vehicles")
    
    if created_ids.get('driver_id'):
        vehicle_data = {
            "driver_id": created_ids['driver_id'],
            "vehicle_type": "sedan",
            "vehicle_brand": "Honda",
            "vehicle_model": "City",
            "vehicle_number": f"MH01XY{int(datetime.now().timestamp()) % 10000}",
            "vehicle_color": "Silver",
            "seating_capacity": 4
        }
        success, response = test_api("POST", "/vehicles", "POST Create Vehicle", vehicle_data, 201)
        
        if created_ids.get('vehicle_id'):
            test_api("GET", f"/vehicles/{created_ids['vehicle_id']}", "GET Vehicle by ID")
        
        test_api("GET", f"/vehicles/driver/{created_ids['driver_id']}", "GET Vehicles by Driver")
    
    # ========== TRIPS ==========
    print_header("TRIP APIs")
    test_api("GET", "/trips", "GET All Trips")
    
    trip_data = {
        "customer_name": "Test Customer",
        "customer_phone": "9876543210",
        "pickup_address": "Andheri West, Mumbai",
        "drop_address": "Bandra East, Mumbai",
        "trip_type": "one_way",
        "vehicle_type": "sedan",
        "passenger_count": 2
    }
    success, response = test_api("POST", "/trips", "POST Create Trip", trip_data, 201)
    
    if created_ids.get('trip_id'):
        test_api("GET", f"/trips/{created_ids['trip_id']}", "GET Trip by ID")
    
    if created_ids.get('driver_id'):
        test_api("GET", f"/trips/driver/{created_ids['driver_id']}", "GET Trips by Driver")
    
    # ========== PAYMENTS ==========
    print_header("PAYMENT APIs")
    test_api("GET", "/payments", "GET All Payments")
    
    if created_ids.get('driver_id'):
        payment_data = {
            "driver_id": created_ids['driver_id'],
            "amount": 500.00,
            "transaction_type": "credit",
            "status": "pending",
            "transaction_id": f"TXN{int(datetime.now().timestamp())}"
        }
        success, response = test_api("POST", "/payments", "POST Create Payment", payment_data, 201)
        
        test_api("GET", f"/payments/driver/{created_ids['driver_id']}", "GET Payments by Driver")
    
    # ========== WALLET TRANSACTIONS ==========
    print_header("WALLET TRANSACTION APIs")
    test_api("GET", "/wallet-transactions", "GET All Wallet Transactions")
    
    if created_ids.get('driver_id'):
        wallet_data = {
            "driver_id": created_ids['driver_id'],
            "transaction_type": "credit",
            "amount": 1000.00
        }
        success, response = test_api("POST", "/wallet-transactions", "POST Create Wallet Transaction", wallet_data, 201)
        
        test_api("GET", f"/wallet-transactions/driver/{created_ids['driver_id']}", "GET Wallet Transactions by Driver")

def print_summary():
    """Print test summary"""
    print_header("TEST SUMMARY")
    
    total = len(test_results)
    passed = sum(1 for t in test_results if t['status'] == 'PASS')
    failed = total - passed
    pass_rate = (passed / total * 100) if total > 0 else 0
    
    print(f"Total Tests:  {total}")
    print(f"{Colors.GREEN}Passed:       {passed}{Colors.RESET}")
    print(f"{Colors.RED}Failed:       {failed}{Colors.RESET}")
    print(f"Pass Rate:    {pass_rate:.1f}%")
    
    # Group by method
    get_tests = [t for t in test_results if t['method'] == 'GET']
    post_tests = [t for t in test_results if t['method'] == 'POST']
    
    get_passed = sum(1 for t in get_tests if t['status'] == 'PASS')
    post_passed = sum(1 for t in post_tests if t['status'] == 'PASS')
    
    print(f"\n{Colors.BLUE}GET Endpoints:{Colors.RESET}  {get_passed}/{len(get_tests)} passing")
    print(f"{Colors.BLUE}POST Endpoints:{Colors.RESET} {post_passed}/{len(post_tests)} passing")
    
    if failed > 0:
        print(f"\n{Colors.RED}Failed Tests:{Colors.RESET}")
        for test in test_results:
            if test['status'] == 'FAIL':
                print(f"  • {test['method']} {test['name']}")
    
    # Save report
    report_file = f"get_post_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump({
            'summary': {
                'total': total,
                'passed': passed,
                'failed': failed,
                'pass_rate': pass_rate,
                'get_tests': {'total': len(get_tests), 'passed': get_passed},
                'post_tests': {'total': len(post_tests), 'passed': post_passed},
                'timestamp': datetime.now().isoformat()
            },
            'created_ids': created_ids,
            'results': test_results
        }, f, indent=2)
    
    print(f"\n{Colors.BLUE}Report saved to: {report_file}{Colors.RESET}")
    
    return failed == 0

if __name__ == "__main__":
    try:
        run_all_tests()
        success = print_summary()
        exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Tests interrupted{Colors.RESET}")
        exit(1)
    except Exception as e:
        print(f"\n\n{Colors.RED}Fatal error: {str(e)}{Colors.RESET}")
        exit(1)
