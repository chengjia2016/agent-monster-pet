#!/usr/bin/env python3
"""
Test script for egg hatching and capture systems
Tests the judge server's /api/egg/incubate and /api/capture/validate endpoints
"""

import json
import requests
import time
from datetime import datetime, timedelta
import sys

BASE_URL = "http://localhost:10000"

def test_egg_hatching():
    """Test egg incubation and hatching"""
    print("\n" + "="*60)
    print("TEST 1: EGG HATCHING SYSTEM")
    print("="*60)
    
    test_cases = [
        {
            "name": "Quick hatch (1 minute incubation)",
            "incubation_minutes": 1,
            "description": "Short incubation for Common Pokemon"
        },
        {
            "name": "Medium hatch (30 minutes incubation)",
            "incubation_minutes": 30,
            "description": "Moderate incubation for Uncommon Pokemon"
        },
        {
            "name": "Long hatch (2 hours incubation)",
            "incubation_minutes": 120,
            "description": "Long incubation for Rare Pokemon"
        },
        {
            "name": "Epic hatch (12 hours incubation)",
            "incubation_minutes": 720,
            "description": "Very long incubation for Epic/Legendary Pokemon"
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[Test 1.{i}] {test_case['name']}")
        print(f"Description: {test_case['description']}")
        
        # Calculate start time based on incubation duration
        start_time = datetime.utcnow() - timedelta(minutes=test_case["incubation_minutes"])
        
        egg_data = {
            "id": f"egg_{i}_{int(time.time())}",
            "owner": f"player_{i}",
            "start_time": start_time.isoformat() + "Z",
            "hatch_time": datetime.utcnow().isoformat() + "Z",
            "status": "incubating",
            "incubation_duration_seconds": 0,
            "energy_absorbed": 0,
            "gene_changes": []
        }
        
        print(f"Request: POST {BASE_URL}/api/egg/incubate")
        print(f"Payload: {json.dumps(egg_data, indent=2)}")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/egg/incubate",
                json=egg_data,
                timeout=5
            )
            
            print(f"Status: {response.status_code}")
            result = response.json()
            print(f"Response: {json.dumps(result, indent=2)}")
            
            if response.status_code == 200:
                if result.get("is_valid"):
                    print("✓ PASS - Egg validation successful")
                    if result.get("hatch_result"):
                        hatch = result["hatch_result"]
                        print(f"  - Hatched: {hatch['pokemon_name']} (ID: {hatch['pokemon_id']})")
                        print(f"  - Rarity: {hatch['rarity']}")
                        print(f"  - Energy Absorbed: {hatch['total_energy']}")
                        print(f"  - Gene Modifiers: {len(hatch['gene_modifiers'])} changes")
                else:
                    print(f"✗ FAIL - Validation failed: {result.get('errors', [])}")
            else:
                print(f"✗ FAIL - HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ ERROR: {e}")
        
        time.sleep(1)

def test_capture_system():
    """Test capture ball mechanics"""
    print("\n" + "="*60)
    print("TEST 2: CAPTURE BALL SYSTEM")
    print("="*60)
    
    test_cases = [
        {
            "name": "Capture weak Pokemon (10% HP)",
            "target_hp": 10,
            "max_hp": 100,
            "expected": "High success rate",
            "hp_percent": 0.1
        },
        {
            "name": "Capture low Pokemon (25% HP)",
            "target_hp": 25,
            "max_hp": 100,
            "expected": "Good success rate",
            "hp_percent": 0.25
        },
        {
            "name": "Capture medium Pokemon (50% HP)",
            "target_hp": 50,
            "max_hp": 100,
            "expected": "Lower success rate",
            "hp_percent": 0.5
        },
        {
            "name": "Capture strong Pokemon (80% HP)",
            "target_hp": 80,
            "max_hp": 100,
            "expected": "Very low success rate",
            "hp_percent": 0.8
        },
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n[Test 2.{i}] {test_case['name']}")
        print(f"Expected: {test_case['expected']}")
        
        capture_data = {
            "id": f"capture_{i}_{int(time.time())}",
            "capture_id": f"cap_{i}_{int(time.time())}",
            "battle_id": f"battle_{i}_{int(time.time())}",
            "attacker_id": f"player_attacker_{i}",
            "target_id": f"pokemon_target_{i}",
            "target_hp": test_case["target_hp"],
            "max_hp": test_case["max_hp"],
            "capture_rate": 0.0,
            "success": False,
            "throw_time": datetime.utcnow().isoformat() + "Z"
        }
        
        print(f"Request: POST {BASE_URL}/api/capture/validate")
        print(f"Target HP: {test_case['target_hp']}/{test_case['max_hp']} ({test_case['hp_percent']*100:.0f}%)")
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/capture/validate",
                json=capture_data,
                timeout=5
            )
            
            print(f"Status: {response.status_code}")
            result = response.json()
            
            if response.status_code == 200:
                if result.get("is_valid"):
                    print(f"✓ Capture Rate: {result.get('capture_rate', 0)*100:.1f}%")
                    if result.get("success") and result.get("captured_pet"):
                        pet = result['captured_pet']
                        print(f"✓ CAPTURED! Pet ID: {pet.get('id', 'unknown')}")
                    else:
                        print("✗ Capture failed (Pokemon escaped)")
                else:
                    errors = result.get("errors", [])
                    print(f"✗ FAIL - {', '.join(errors)}")
            else:
                print(f"✗ FAIL - HTTP {response.status_code}")
        except Exception as e:
            print(f"✗ ERROR: {e}")
        
        time.sleep(1)

def run_stress_test():
    """Run multiple captures to check success rate distribution"""
    print("\n" + "="*60)
    print("TEST 3: CAPTURE SUCCESS RATE STRESS TEST")
    print("="*60)
    
    print("\nTesting 50 captures at 20% HP to check success rate distribution...")
    successes = 0
    total = 50
    
    for i in range(total):
        capture_data = {
            "id": f"stress_capture_{i}_{int(time.time())}",
            "capture_id": f"stress_cap_{i}_{int(time.time())}",
            "battle_id": f"stress_battle_{i}_{int(time.time())}",
            "attacker_id": "stress_tester",
            "target_id": f"stress_target_{i}",
            "target_hp": 20,
            "max_hp": 100,
            "capture_rate": 0.0,
            "success": False,
            "throw_time": datetime.utcnow().isoformat() + "Z"
        }
        
        try:
            response = requests.post(
                f"{BASE_URL}/api/capture/validate",
                json=capture_data,
                timeout=5
            )
            
            if response.status_code == 200:
                result = response.json()
                if result.get("success"):
                    successes += 1
                    print(".", end="", flush=True)
                else:
                    print("x", end="", flush=True)
        except Exception as e:
            print("E", end="", flush=True)
    
    print(f"\n\nResults: {successes}/{total} captures successful ({successes/total*100:.1f}%)")
    print("Expected: ~50-70% success rate at 20% HP")

def main():
    print("\n" + "="*60)
    print("AGENT MONSTER - EGG & CAPTURE SYSTEM TEST")
    print("="*60)
    print(f"Judge Server URL: {BASE_URL}")
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✓ Judge server is running")
        else:
            print("✗ Judge server not responding correctly")
            sys.exit(1)
    except Exception as e:
        print(f"✗ Cannot connect to judge server: {e}")
        sys.exit(1)
    
    # Run tests
    test_egg_hatching()
    test_capture_system()
    run_stress_test()
    
    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60 + "\n")

if __name__ == "__main__":
    main()
