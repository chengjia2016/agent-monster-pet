#!/usr/bin/env python3
"""
Test script for Judge Server integration
Tests the fallback mechanism and hybrid data management
"""

import sys
import json
from pathlib import Path
from hybrid_user_data_manager import HybridUserDataManager
from judge_server_user_manager import JudgeServerUserManager
from user_manager import UserManager
from economy_manager import EconomyManager

def test_judge_server_connectivity():
    """Test if Judge Server is reachable"""
    print("\n" + "="*60)
    print("TEST 1: Judge Server Connectivity")
    print("="*60)
    
    manager = JudgeServerUserManager()
    
    # Test health endpoint
    try:
        import urllib.request
        response = urllib.request.urlopen(
            f"{manager.server_url}/health",
            timeout=5
        )
        print(f"✓ Judge Server is reachable")
        print(f"  Status: {response.status}")
        return True
    except Exception as e:
        print(f"✗ Judge Server is NOT reachable")
        print(f"  Error: {e}")
        return False

def test_hybrid_data_manager_local_fallback():
    """Test that hybrid manager falls back to local cache when server is unavailable"""
    print("\n" + "="*60)
    print("TEST 2: Hybrid Manager Local Fallback")
    print("="*60)
    
    # Create temporary cache directory
    cache_dir = Path(".monster/test_cache")
    cache_dir.mkdir(parents=True, exist_ok=True)
    
    # Create hybrid manager WITHOUT judge server (simulating server unavailability)
    hybrid = HybridUserDataManager(
        local_cache_dir=cache_dir,
        judge_server_manager=None  # No server connection
    )
    
    # Save data locally
    test_user_data = {
        "github_id": 12345,
        "github_login": "test_user",
        "balance": 100.0,
        "pokemons": [{"name": "Pikachu", "level": 5}],
        "items": [{"id": "ball_1", "name": "Poke Ball", "quantity": 5}]
    }
    
    print("1. Saving user data to local cache...")
    hybrid.save_user_data(12345, test_user_data, sync_to_server=False)
    print("   ✓ Data saved locally")
    
    print("2. Retrieving data from cache...")
    retrieved = hybrid.get_user_data(12345, use_server=False)
    
    if retrieved and retrieved["balance"] == 100.0:
        print("   ✓ Data retrieved successfully from cache")
        print(f"   Balance: {retrieved['balance']}")
        return True
    else:
        print("   ✗ Failed to retrieve data from cache")
        return False

def test_existing_user_data():
    """Test reading existing user data from local system"""
    print("\n" + "="*60)
    print("TEST 3: Existing User Data")
    print("="*60)
    
    data_dir = ".monster"
    user_manager = UserManager(data_dir)
    economy_manager = EconomyManager(data_dir)
    
    users = user_manager.list_users()
    print(f"Found {len(users)} existing users")
    
    if users:
        user = users[0]
        account = economy_manager.get_account(user.user_id)
        print(f"\n✓ Sample User:")
        print(f"  GitHub Login: {user.github_login}")
        print(f"  GitHub ID: {user.github_id}")
        print(f"  User ID: {user.user_id}")
        print(f"  Balance: {account.balance if account else 'N/A'}")
        return True
    else:
        print("ℹ No existing users found (this is normal for fresh installation)")
        return True

def test_hybrid_manager_with_local_data():
    """Test hybrid manager with existing local user data"""
    print("\n" + "="*60)
    print("TEST 4: Hybrid Manager With Existing Local Data")
    print("="*60)
    
    data_dir = Path(".monster")
    user_manager = UserManager(str(data_dir))
    economy_manager = EconomyManager(str(data_dir))
    
    # Create hybrid manager
    hybrid = HybridUserDataManager(
        local_cache_dir=data_dir,
        judge_server_manager=None
    )
    
    users = user_manager.list_users()
    if not users:
        print("ℹ No users to test with")
        return True
    
    user = users[0]
    account = economy_manager.get_account(user.user_id)
    
    # Simulate caching the user data
    user_data = {
        "github_id": user.github_id,
        "github_login": user.github_login,
        "balance": account.balance if account else 0,
        "user_id": user.user_id
    }
    
    print(f"1. Caching data for user: {user.github_login} (ID: {user.github_id})")
    hybrid.save_user_data(user.github_id, user_data, sync_to_server=False)
    print("   ✓ Data cached")
    
    print(f"2. Retrieving cached data...")
    retrieved = hybrid.get_user_data(user.github_id, use_server=False)
    
    if retrieved and retrieved["github_id"] == user.github_id:
        print("   ✓ Data retrieved from cache")
        print(f"   GitHub ID: {retrieved['github_id']}")
        print(f"   Login: {retrieved['github_login']}")
        return True
    else:
        print("   ✗ Failed to retrieve cached data")
        return False

def test_judge_server_user_manager_api():
    """Test JudgeServerUserManager API methods"""
    print("\n" + "="*60)
    print("TEST 5: JudgeServerUserManager API")
    print("="*60)
    
    manager = JudgeServerUserManager()
    
    # Test creating a test user
    print("1. Testing user creation API (will fail if server endpoints not implemented)...")
    try:
        result = manager._make_request(
            "/api/users/test_create",
            method="POST",
            data={"github_id": 999999, "github_login": "test"}
        )
        if result and result.get("success"):
            print("   ✓ User creation API responded")
        else:
            print(f"   ℹ API not implemented yet (expected)")
            print(f"   Response: {result}")
    except Exception as e:
        print(f"   ℹ API endpoint not available (expected during development)")
        print(f"   Error: {type(e).__name__}")
    
    print("2. API structure validation...")
    # Check that manager has expected methods
    methods = [
        "create_user",
        "get_user",
        "update_balance",
        "add_pokemon",
        "get_pokemons",
        "add_item",
        "get_items",
        "sync_local_to_server"
    ]
    
    missing = [m for m in methods if not hasattr(manager, m)]
    if not missing:
        print(f"   ✓ All {len(methods)} API methods are defined")
        return True
    else:
        print(f"   ✗ Missing methods: {missing}")
        return False

def main():
    """Run all integration tests"""
    print("\n" + "="*60)
    print("JUDGE SERVER INTEGRATION TESTS")
    print("="*60)
    
    results = {}
    
    # Test 1: Connectivity
    results["connectivity"] = test_judge_server_connectivity()
    
    # Test 2: Hybrid fallback
    results["hybrid_fallback"] = test_hybrid_data_manager_local_fallback()
    
    # Test 3: Existing data
    results["existing_data"] = test_existing_user_data()
    
    # Test 4: Hybrid with existing data
    results["hybrid_existing"] = test_hybrid_manager_with_local_data()
    
    # Test 5: API structure
    results["api_structure"] = test_judge_server_user_manager_api()
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✓ All integration tests passed!")
        return 0
    else:
        print(f"\n✗ {total - passed} tests failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
