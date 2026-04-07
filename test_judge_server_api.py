#!/usr/bin/env python3
"""
Comprehensive Judge Server API testing script - Fixed parameters
"""

import requests
import json
import sys
from datetime import datetime
import random

JUDGE_SERVER_URL = "http://localhost:10000"

# Test results
results = {
    "passed": [],
    "failed": [],
    "total": 0,
    "errors": []
}

def test_endpoint(method, endpoint, data=None, name=None, expected_status=200, headers=None):
    """Test a single endpoint"""
    global results
    results["total"] += 1
    
    url = JUDGE_SERVER_URL + endpoint
    test_name = name or f"{method} {endpoint}"
    
    try:
        if method == "GET":
            response = requests.get(url, timeout=5, headers=headers or {})
        elif method == "POST":
            response = requests.post(url, json=data, timeout=5, headers=headers or {})
        else:
            results["failed"].append(f"{test_name} - Unknown method")
            results["errors"].append({"test": test_name, "error": "Unknown method"})
            return False, None
        
        success = response.status_code == expected_status
        
        if success:
            results["passed"].append(test_name)
            print(f"✓ {test_name} ({response.status_code})")
            try:
                return True, response.json()
            except:
                return True, response.text
        else:
            results["failed"].append(f"{test_name} - Expected {expected_status}, got {response.status_code}")
            print(f"✗ {test_name} - Expected {expected_status}, got {response.status_code}")
            if response.text:
                error_msg = response.text[:300]
                print(f"  Response: {error_msg}")
                results["errors"].append({"test": test_name, "error": error_msg})
            return False, None
    except Exception as e:
        error = str(e)
        results["failed"].append(f"{test_name} - {error}")
        results["errors"].append({"test": test_name, "error": error})
        print(f"✗ {test_name} - {error}")
        return False, None

def main():
    print("=" * 70)
    print("Judge Server API Test Suite - Fixed Parameters")
    print("=" * 70)
    print()
    
    # 1. Health check
    print("1. Health Check")
    print("-" * 70)
    success, _ = test_endpoint("GET", "/health", name="Health Check", expected_status=200)
    if not success:
        print("ERROR: Judge Server is not responding. Please check if it's running.")
        return 1
    print()
    
    # 2. User Account Management
    print("2. User Account Management")
    print("-" * 70)
    test_user_id = random.randint(100000, 999999)
    success, _ = test_endpoint("POST", "/api/users/create",
                 {"github_username": f"testuser{random.randint(1000, 9999)}", "github_id": test_user_id},
                 "Create User Account (with int github_id)", 200)
    print()
    
    # 3. Farm Management
    print("3. Farm Management APIs")
    print("-" * 70)
    success, farm_data = test_endpoint("POST", "/api/farms/create",
                 {"owner_id": "testuser", "repository_name": f"testrepo_{random.randint(1000, 9999)}", "farm_name": "Test Farm"},
                 "Create Farm", 200)
    test_endpoint("GET", "/api/farms/search?owner=testuser", name="Search Farms", expected_status=200)
    print()
    
    # 4. Cookie Management
    print("4. Cookie Management APIs")
    print("-" * 70)
    test_endpoint("POST", "/api/cookies/register",
                 {"github_username": "testuser"},
                 "Register Cookie", 200)
    test_endpoint("GET", "/api/cookies/statistics", name="Cookie Statistics", expected_status=200)
    test_endpoint("GET", "/api/cookies/scan", name="Scan Cookies", expected_status=200)
    print()
    
    # 5. Egg Management
    print("5. Egg Management APIs")
    print("-" * 70)
    # Use unique identifier to avoid duplicate key errors
    test_endpoint("POST", "/api/eggs/create",
                 {"github_username": f"testuser_{random.randint(1000000, 9999999)}", "pet_species": "Pikachu"},
                 "Create Egg", 200)
    test_endpoint("GET", "/api/eggs/statistics", name="Egg Statistics", expected_status=200)
    print()
    
    # 6. Shop Management
    print("6. Shop Management APIs")
    print("-" * 70)
    test_endpoint("GET", "/api/shop/items", name="List Shop Items", expected_status=200)
    test_endpoint("GET", "/api/shop/statistics", name="Shop Statistics", expected_status=200)
    # Transaction history requires player_id parameter
    test_endpoint("GET", "/api/shop/transactions?player_id=testuser", name="Transaction History (with player_id)", expected_status=200)
    print()
    
    # 7. Validation Endpoints
    print("7. Validation Endpoints")
    print("-" * 70)
    test_endpoint("POST", "/api/pet/validate",
                 {"pet_id": "test_pet", "owner": "testuser"},
                 "Validate Pet", 200)
    test_endpoint("POST", "/api/battle/validate",
                 {"pet1": "pet1", "pet2": "pet2", "result": "pet1"},
                 "Validate Battle", 200)
    test_endpoint("POST", "/api/food/validate",
                 {"food_id": "food_001", "owner": "testuser"},
                 "Validate Food", 200)
    test_endpoint("POST", "/api/food/record",
                 {"owner": "testuser", "pet_id": "pet1", "food_value": 10},
                 "Record Food", 200)
    test_endpoint("POST", "/api/growth/record",
                 {"owner": "testuser", "pet_id": "pet1", "growth_value": 5},
                 "Record Growth", 200)
    print()
    
    # Print results
    print()
    print("=" * 70)
    print("Test Results Summary")
    print("=" * 70)
    print(f"Total Tests: {results['total']}")
    print(f"Passed: {len(results['passed'])} ✓")
    print(f"Failed: {len(results['failed'])} ✗")
    print(f"Success Rate: {len(results['passed'])/results['total']*100:.1f}%")
    print()
    
    if results['failed']:
        print("Failed Tests:")
        for i, test in enumerate(results['failed'], 1):
            print(f"  {i}. {test}")
    
    if results['errors']:
        print()
        print("Error Details:")
        for err_detail in results['errors']:
            print(f"  • {err_detail['test']}")
            print(f"    Error: {err_detail['error']}")
    
    return 0 if len(results['failed']) == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
