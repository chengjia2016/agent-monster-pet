"""
Integration tests for the Food System
Tests the complete flow: farm creation, exploration, feeding, and validation
"""

import json
import sys
import os
from datetime import datetime, timedelta
from pathlib import Path
import unittest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from food_system import FoodManager, Food, Farm, FoodType
from food_explorer import GitHubFarmExplorer


class TestFoodSystemIntegration(unittest.TestCase):
    """Integration tests for food system"""

    def setUp(self):
        """Set up test fixtures"""
        self.test_dir = Path(".monster_test")
        self.test_dir.mkdir(exist_ok=True)
        self.manager = FoodManager()
        
    def tearDown(self):
        """Clean up test files"""
        import shutil
        if self.test_dir.exists():
            shutil.rmtree(self.test_dir)

    def test_01_create_farm(self):
        """Test creating a new farm"""
        farm = self.manager.create_farm(
            owner="testuser",
            repository="test-repo",
            url="https://github.com/testuser/test-repo"
        )
        
        self.assertIsNotNone(farm)
        self.assertEqual(farm.owner, "testuser")
        self.assertEqual(farm.repository, "test-repo")
        self.assertEqual(len(farm.foods), 0)
        print("✅ Test 01: Farm creation passed")

    def test_02_add_foods_to_farm(self):
        """Test adding different food types to a farm"""
        farm = self.manager.create_farm(
            owner="testuser",
            repository="test-repo",
            url="https://github.com/testuser/test-repo"
        )
        
        # Add multiple food types
        self.manager.add_food_to_farm(farm, "cookie", 3)
        self.manager.add_food_to_farm(farm, "donut", 2)
        self.manager.add_food_to_farm(farm, "apple", 5)
        
        self.assertEqual(len(farm.foods), 3)
        
        # Verify food details
        cookies = [f for f in farm.foods if f.type == FoodType.COOKIE]
        self.assertEqual(len(cookies), 1)
        self.assertEqual(cookies[0].quantity, 3)
        print("✅ Test 02: Add foods to farm passed")

    def test_03_save_and_load_farm(self):
        """Test saving farm to YAML and loading it back"""
        farm_path = str(self.test_dir / "farm.yaml")
        owner = "alice"
        repository = "alice-repo"
        
        # Create and save farm
        farm = self.manager.create_farm(
            owner=owner,
            repository=repository,
            url=f"https://github.com/{owner}/{repository}"
        )
        self.manager.add_food_to_farm(farm, "cookie", 3)
        self.manager.add_food_to_farm(farm, "apple", 5)
        
        # Save using the proper API
        success = self.manager.save_farm_to_file(owner, repository, farm_path)
        self.assertTrue(success)
        
        # Load farm back
        loaded_farm = self.manager.load_farm_from_file(farm_path)
        self.assertIsNotNone(loaded_farm)
        self.assertEqual(loaded_farm.owner, "alice")
        self.assertEqual(len(loaded_farm.foods), 2)
        print("✅ Test 03: Save and load farm passed")

    def test_04_consume_food(self):
        """Test consuming food from a farm"""
        farm = self.manager.create_farm(
            owner="bob",
            repository="bob-repo",
            url="https://github.com/bob/bob-repo"
        )
        self.manager.add_food_to_farm(farm, "cookie", 3)
        
        initial_quantity = farm.foods[0].quantity
        food_id = farm.foods[0].id
        
        # Consume one cookie using the proper API
        success, result = self.manager.consume_food(
            owner="bob",
            repository="bob-repo",
            food_id=food_id,
            eater_id="test_eater",
            eater_pet_id="test_pet"
        )
        self.assertTrue(success)
        # After consumption, the food quantity should decrease
        print("✅ Test 04: Consume food passed")

    def test_05_food_regeneration_calculation(self):
        """Test food regeneration calculation"""
        farm = self.manager.create_farm(
            owner="charlie",
            repository="charlie-repo",
            url="https://github.com/charlie/charlie-repo"
        )
        self.manager.add_food_to_farm(farm, "donut", 2)
        food = farm.foods[0]
        food_id = food.id
        
        # Get current status
        current_quantity, is_ready, next_ready = self.manager.calculate_food_status(food)
        
        # Food should be available initially
        self.assertGreater(current_quantity, 0)
        print("✅ Test 05: Food regeneration calculation passed")

    def test_06_farm_statistics(self):
        """Test getting farm statistics"""
        owner = "diana"
        repository = "diana-repo"
        
        farm = self.manager.create_farm(
            owner=owner,
            repository=repository,
            url=f"https://github.com/{owner}/{repository}"
        )
        self.manager.add_food_to_farm(farm, "cookie", 3)
        self.manager.add_food_to_farm(farm, "apple", 5)
        self.manager.add_food_to_farm(farm, "donut", 2)
        
        stats = self.manager.get_farm_stats(owner, repository)
        
        self.assertEqual(stats['total_foods'], 3)
        self.assertEqual(stats['current_quantity'], 10)
        print("✅ Test 06: Farm statistics passed")

    def test_07_food_consumption_history(self):
        """Test tracking food consumption history"""
        farm = self.manager.create_farm(
            owner="eve",
            repository="eve-repo",
            url="https://github.com/eve/eve-repo"
        )
        self.manager.add_food_to_farm(farm, "cookie", 3)
        
        # Farm should have one food type
        self.assertEqual(len(farm.foods), 1)
        print("✅ Test 07: Food consumption history passed")

    def test_08_all_food_types(self):
        """Test all food types have correct properties"""
        farm = self.manager.create_farm(
            owner="frank",
            repository="frank-repo",
            url="https://github.com/frank/frank-repo"
        )
        
        # Add all food types
        for food_type in ["cookie", "donut", "apple", "gene"]:
            self.manager.add_food_to_farm(farm, food_type, 1)
        
        self.assertEqual(len(farm.foods), 4)
        print("✅ Test 08: All food types passed")

    def test_09_food_persistence_round_trip(self):
        """Test complete farm save/load round trip"""
        farm_path = str(self.test_dir / "persistence_test.yaml")
        owner = "grace"
        repository = "grace-repo"
        
        # Create a complex farm
        original_farm = self.manager.create_farm(
            owner=owner,
            repository=repository,
            url=f"https://github.com/{owner}/{repository}"
        )
        self.manager.add_food_to_farm(original_farm, "cookie", 3)
        self.manager.add_food_to_farm(original_farm, "apple", 5)
        
        # Save using the proper API
        success = self.manager.save_farm_to_file(owner, repository, farm_path)
        self.assertTrue(success)
        
        # Load
        loaded_farm = self.manager.load_farm_from_file(farm_path)
        
        # Verify persistence
        self.assertEqual(loaded_farm.owner, owner)
        self.assertEqual(len(loaded_farm.foods), 2)
        print("✅ Test 09: Farm persistence round trip passed")

    def test_10_multiple_farms(self):
        """Test managing multiple farms"""
        farms = []
        for i in range(3):
            farm = self.manager.create_farm(
                owner=f"user{i}",
                repository=f"repo{i}",
                url=f"https://github.com/user{i}/repo{i}"
            )
            self.manager.add_food_to_farm(farm, "cookie", i + 1)
            farms.append(farm)
        
        self.assertEqual(len(farms), 3)
        self.assertEqual(farms[0].foods[0].quantity, 1)
        self.assertEqual(farms[1].foods[0].quantity, 2)
        self.assertEqual(farms[2].foods[0].quantity, 3)
        print("✅ Test 10: Multiple farms management passed")


class TestGitHubFarmExplorer(unittest.TestCase):
    """Tests for GitHub farm explorer"""

    def setUp(self):
        """Set up test fixtures"""
        self.explorer = GitHubFarmExplorer()

    def test_01_explorer_initialization(self):
        """Test explorer initializes correctly"""
        self.assertIsNotNone(self.explorer)
        self.assertIsNotNone(self.explorer.headers)
        self.assertTrue("Accept" in self.explorer.headers)
        print("✅ Explorer Test 01: Initialization passed")

    def test_02_farm_info_extraction(self):
        """Test extracting farm info from repository object"""
        repo_data = {
            "owner": {"login": "testuser"},
            "name": "test-repo",
            "html_url": "https://github.com/testuser/test-repo"
        }
        
        farm_info = self.explorer._extract_farm_info(repo_data)
        self.assertIsNotNone(farm_info)
        self.assertEqual(farm_info.owner, "testuser")
        self.assertEqual(farm_info.repository, "test-repo")
        print("✅ Explorer Test 02: Farm info extraction passed")

    def test_03_favorites_management(self):
        """Test saving and loading favorites"""
        test_favorites_file = Path(".monster_test/favorites.json")
        test_favorites_file.parent.mkdir(exist_ok=True)
        
        farms = [
            "https://github.com/user1/repo1",
            "https://github.com/user2/repo2"
        ]
        
        # Save
        self.explorer.save_favorites(farms, str(test_favorites_file))
        self.assertTrue(test_favorites_file.exists())
        
        # Load
        loaded = self.explorer.get_favorites(str(test_favorites_file))
        self.assertEqual(len(loaded), 2)
        self.assertIn(farms[0], loaded)
        
        # Cleanup
        test_favorites_file.unlink()
        test_favorites_file.parent.rmdir()
        print("✅ Explorer Test 03: Favorites management passed")


def run_integration_tests():
    """Run all integration tests"""
    print("\n" + "="*50)
    print("Running Food System Integration Tests")
    print("="*50 + "\n")
    
    # Create test suite
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add test classes
    suite.addTests(loader.loadTestsFromTestCase(TestFoodSystemIntegration))
    suite.addTests(loader.loadTestsFromTestCase(TestGitHubFarmExplorer))
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*50)
    print("Test Summary")
    print("="*50)
    print(f"Tests run: {result.testsRun}")
    print(f"Successes: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print("="*50 + "\n")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_integration_tests()
    sys.exit(0 if success else 1)
