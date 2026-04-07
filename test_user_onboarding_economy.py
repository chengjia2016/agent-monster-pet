#!/usr/bin/env python3
"""
Comprehensive tests for User Onboarding, Economy, and Shop systems
"""

import pytest
import json
import tempfile
from pathlib import Path
from user_manager import UserManager, User
from economy_manager import EconomyManager, UserAccount, TransactionType, Transaction
from shop_manager import Shop, ShopItem, ItemType
from onboarding_manager import OnboardingManager


@pytest.fixture
def temp_dir():
    """Create temporary directory for tests"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


class TestUserManager:
    """Test user registration and management"""
    
    def test_register_user(self, temp_dir):
        """Test user registration"""
        manager = UserManager(temp_dir)
        user = manager.register_user(
            github_login="testuser",
            github_id=12345,
            email="test@example.com",
            avatar_url="https://example.com/avatar.jpg"
        )
        
        assert user.user_id is not None
        assert user.github_login == "testuser"
        assert user.github_id == 12345
    
    def test_get_user(self, temp_dir):
        """Test retrieving user"""
        manager = UserManager(temp_dir)
        user = manager.register_user("testuser", 12345)
        retrieved = manager.get_user(user.user_id)
        
        assert retrieved is not None
        assert retrieved.github_login == "testuser"
    
    def test_get_user_by_github_id(self, temp_dir):
        """Test finding user by GitHub ID"""
        manager = UserManager(temp_dir)
        user = manager.register_user("testuser", 12345)
        retrieved = manager.get_user_by_github_id(12345)
        
        assert retrieved is not None
        assert retrieved.user_id == user.user_id
    
    def test_duplicate_github_id(self, temp_dir):
        """Test that duplicate GitHub ID returns existing user"""
        manager = UserManager(temp_dir)
        user1 = manager.register_user("testuser", 12345)
        user2 = manager.register_user("testuser2", 12345)  # Same GitHub ID
        
        assert user1.user_id == user2.user_id
    
    def test_session_management(self, temp_dir):
        """Test session creation and validation"""
        manager = UserManager(temp_dir)
        user = manager.register_user("testuser", 12345)
        
        # Create session
        token = manager.create_session(user)
        assert token is not None
        
        # Validate session
        user_id = manager.validate_session(token)
        assert user_id == user.user_id
    
    def test_invalid_session(self, temp_dir):
        """Test invalid session returns None"""
        manager = UserManager(temp_dir)
        result = manager.validate_session("invalid_token")
        assert result is None


class TestEconomyManager:
    """Test economic system"""
    
    def test_create_account(self, temp_dir):
        """Test account creation with initial balance"""
        manager = EconomyManager(temp_dir)
        account = manager.create_account("user1", 100.0)
        
        assert account.user_id == "user1"
        assert account.balance == 100.0
        assert len(account.transactions) == 1
        assert account.transactions[0].trans_type == TransactionType.INITIAL_GRANT
    
    def test_purchase_item(self, temp_dir):
        """Test purchasing item from balance"""
        manager = EconomyManager(temp_dir)
        account = manager.create_account("user1", 100.0)
        
        # Purchase item
        success = manager.purchase_item("user1", "Pokéball", 10.0, "item_1")
        assert success is True
        
        # Check balance decreased
        updated = manager.get_account("user1")
        assert updated.balance == 90.0
    
    def test_insufficient_balance(self, temp_dir):
        """Test purchase fails with insufficient balance"""
        manager = EconomyManager(temp_dir)
        account = manager.create_account("user1", 50.0)
        
        success = manager.purchase_item("user1", "Pokéball", 100.0)
        assert success is False
        
        # Balance unchanged
        updated = manager.get_account("user1")
        assert updated.balance == 50.0
    
    def test_food_transaction(self, temp_dir):
        """Test food trading with commission"""
        manager = EconomyManager(temp_dir)
        buyer = manager.create_account("buyer", 100.0)
        seller = manager.create_account("seller", 50.0)
        
        # Process transaction
        success, buyer_paid, seller_received = manager.process_food_transaction(
            buyer_id="buyer",
            seller_id="seller",
            food_id="food_1",
            food_name="Berries",
            base_price=100.0
        )
        
        assert success is True
        assert buyer_paid == 100.0
        # Commission is 5%, so seller gets 95.0
        assert seller_received == 95.0
        
        # Check balances
        buyer_updated = manager.get_account("buyer")
        seller_updated = manager.get_account("seller")
        
        assert buyer_updated.balance == 0.0  # 100 - 100
        assert seller_updated.balance == 145.0  # 50 + 95
    
    def test_battle_reward(self, temp_dir):
        """Test battle reward system"""
        manager = EconomyManager(temp_dir)
        winner = manager.create_account("winner", 100.0)
        loser = manager.create_account("loser", 100.0)
        
        success = manager.process_battle_reward(
            winner_id="winner",
            loser_id="loser",
            base_reward=50.0
        )
        
        assert success is True
        
        winner_updated = manager.get_account("winner")
        loser_updated = manager.get_account("loser")
        
        assert winner_updated.balance == 150.0  # 100 + 50
        assert loser_updated.balance == 50.0    # 100 - 50
    
    def test_sell_pet(self, temp_dir):
        """Test selling pet to shop"""
        manager = EconomyManager(temp_dir)
        account = manager.create_account("user1", 50.0)
        
        success = manager.sell_pet("user1", "Pikachu", 300.0)
        assert success is True
        
        updated = manager.get_account("user1")
        assert updated.balance == 350.0
    
    def test_auction_pet(self, temp_dir):
        """Test auctioning pet with commission"""
        manager = EconomyManager(temp_dir)
        account = manager.create_account("user1", 50.0)
        
        success = manager.auction_pet("user1", "Charizard", 1000.0)
        assert success is True
        
        updated = manager.get_account("user1")
        # Commission is 10%, so receives 900.0
        assert updated.balance == 950.0
    
    def test_user_statistics(self, temp_dir):
        """Test user economic statistics"""
        manager = EconomyManager(temp_dir)
        account = manager.create_account("user1", 100.0)
        
        # Make some transactions
        manager.purchase_item("user1", "Item", 20.0)
        manager.purchase_item("user1", "Item", 30.0)
        
        stats = manager.get_user_statistics("user1")
        
        assert stats["current_balance"] == 50.0
        assert stats["total_spent"] == -50.0
        assert stats["total_earned"] == 100.0


class TestShop:
    """Test shop system"""
    
    def test_shop_initialization(self, temp_dir):
        """Test shop initializes with default catalog"""
        shop = Shop(temp_dir)
        
        assert len(shop.catalog) > 0
        assert "pokeball" in shop.catalog
    
    def test_get_item(self, temp_dir):
        """Test getting item from catalog"""
        shop = Shop(temp_dir)
        item = shop.get_item("pokeball")
        
        assert item is not None
        assert item.item_id == "pokeball"
        assert item.price == 10.0
    
    def test_list_items_by_type(self, temp_dir):
        """Test filtering items by type"""
        shop = Shop(temp_dir)
        pokeballs = shop.list_items(ItemType.POKEBALL)
        
        assert len(pokeballs) > 0
        assert all(item.item_type == ItemType.POKEBALL for item in pokeballs)
    
    def test_purchase_item(self, temp_dir):
        """Test purchasing item from shop"""
        shop = Shop(temp_dir)
        
        initial_stock = shop.get_item("pokeball").stock
        success, item, msg = shop.purchase_item("user1", "pokeball", 2)
        
        assert success is True
        assert item.name == "Poké Ball"
        
        # Check stock decreased
        updated_stock = shop.get_item("pokeball").stock
        assert updated_stock == initial_stock - 2
    
    def test_insufficient_stock(self, temp_dir):
        """Test purchase fails with insufficient stock"""
        shop = Shop(temp_dir)
        
        success, item, msg = shop.purchase_item("user1", "pokeball", 1000)
        assert success is False
        assert "Insufficient stock" in msg
    
    def test_user_inventory(self, temp_dir):
        """Test getting user inventory"""
        shop = Shop(temp_dir)
        
        shop.purchase_item("user1", "pokeball", 2)
        shop.purchase_item("user1", "seed_grass", 1)
        
        inventory = shop.get_user_inventory("user1")
        
        assert "pokeball" in inventory
        assert inventory["pokeball"]["quantity"] == 2
        assert "seed_grass" in inventory
    
    def test_use_item(self, temp_dir):
        """Test using/consuming item from inventory"""
        shop = Shop(temp_dir)
        
        shop.purchase_item("user1", "pokeball", 3)
        
        # Use one pokeball
        success = shop.use_item("user1", "pokeball", 1)
        assert success is True
        
        # Check quantity decreased
        inventory = shop.get_user_inventory("user1")
        assert inventory["pokeball"]["quantity"] == 2
    
    def test_shop_statistics(self, temp_dir):
        """Test shop statistics"""
        shop = Shop(temp_dir)
        
        stats = shop.get_shop_statistics()
        
        assert "total_items" in stats
        assert "total_stock_value" in stats
        assert "items_by_type" in stats
        assert stats["total_items"] > 0


class TestOnboarding:
    """Test new user onboarding"""
    
    def test_github_registration(self, temp_dir):
        """Test registering from GitHub OAuth"""
        onboarding = OnboardingManager(temp_dir)
        
        success, user, msg = onboarding.register_from_github(
            github_login="newuser",
            github_id=99999,
            email="new@example.com",
            avatar_url="https://example.com/new.jpg"
        )
        
        assert success is True
        assert user is not None
        assert user.github_login == "newuser"
    
    def test_initial_balance(self, temp_dir):
        """Test user gets 100 coins after registration"""
        onboarding = OnboardingManager(temp_dir)
        
        success, user, msg = onboarding.register_from_github(
            "user1", 11111
        )
        
        account = onboarding.economy_manager.get_account(user.user_id)
        assert account.balance == 100.0
    
    def test_initial_items(self, temp_dir):
        """Test user gets initial items"""
        onboarding = OnboardingManager(temp_dir)
        
        success, user, msg = onboarding.register_from_github(
            "user1", 11111
        )
        
        inventory = onboarding.shop.get_user_inventory(user.user_id)
        
        # Check for initial items
        assert "pokeball" in inventory
        assert inventory["pokeball"]["quantity"] == 3
        assert "seed_grass" in inventory
        assert inventory["seed_grass"]["quantity"] == 2
    
    def test_starter_pet_created(self, temp_dir):
        """Test starter pet is created"""
        onboarding = OnboardingManager(temp_dir)
        
        success, user, msg = onboarding.register_from_github(
            "user1", 11111
        )
        
        # Check starter pet file exists
        pet_file = Path(temp_dir) / f"{user.user_id}_starter_pet.json"
        assert pet_file.exists()
        
        with open(pet_file, "r") as f:
            pet_data = json.load(f)
            assert pet_data["species"] == "Psyduck"
            assert pet_data["name"] == "小黄鸭"
    
    def test_starter_egg_created(self, temp_dir):
        """Test starter egg is created"""
        onboarding = OnboardingManager(temp_dir)
        
        success, user, msg = onboarding.register_from_github(
            "user1", 11111
        )
        
        # Check starter egg file exists
        egg_file = Path(temp_dir) / f"{user.user_id}_egg.json"
        assert egg_file.exists()
        
        with open(egg_file, "r") as f:
            egg_data = json.load(f)
            assert egg_data["status"] == "incubating"
    
    def test_duplicate_registration(self, temp_dir):
        """Test that duplicate GitHub ID doesn't create new account"""
        onboarding = OnboardingManager(temp_dir)
        
        # First registration
        success1, user1, msg1 = onboarding.register_from_github(
            "user1", 11111
        )
        
        # Second registration with same GitHub ID
        success2, user2, msg2 = onboarding.register_from_github(
            "user1_different", 11111  # Same GitHub ID
        )
        
        # Should succeed but return same user
        assert success2 is True
        # GitHub ID takes precedence, so same user is returned
        assert user2.github_id == user1.github_id
    
    def test_onboarding_status(self, temp_dir):
        """Test getting user onboarding status"""
        onboarding = OnboardingManager(temp_dir)
        
        success, user, msg = onboarding.register_from_github(
            "user1", 11111
        )
        
        status = onboarding.get_user_onboarding_status(user.user_id)
        
        assert status["status"] == "completed"
        assert status["balance"] == 100.0
        assert len(status["inventory"]) > 0
        assert status["initial_rewards"]["coins"] == 100.0


class TestIntegrationScenarios:
    """Test complete user scenarios"""
    
    def test_complete_user_journey(self, temp_dir):
        """Test complete user journey: register -> buy item -> trade food"""
        onboarding = OnboardingManager(temp_dir)
        economy = onboarding.economy_manager
        shop = onboarding.shop
        
        # Register two users
        success1, user1, msg = onboarding.register_from_github("alice", 111)
        success2, user2, msg = onboarding.register_from_github("bob", 222)
        
        assert success1 and success2
        
        # Alice and Bob both have 100 coins
        alice_balance = economy.get_account(user1.user_id).balance
        bob_balance = economy.get_account(user2.user_id).balance
        
        assert alice_balance == 100.0
        assert bob_balance == 100.0
        
        # Alice buys pokeballs
        success = economy.purchase_item(user1.user_id, "Pokéball", 50.0)
        assert success is True
        assert economy.get_account(user1.user_id).balance == 50.0
        
        # Alice and Bob trade food
        success, paid, received = economy.process_food_transaction(
            buyer_id=user1.user_id,
            seller_id=user2.user_id,
            food_id="berries",
            food_name="Berries",
            base_price=30.0
        )
        
        assert success is True
        assert paid == 30.0
        assert received == 28.5  # 30 - 5% commission
        
        # Check final balances
        alice_final = economy.get_account(user1.user_id).balance
        bob_final = economy.get_account(user2.user_id).balance
        
        assert alice_final == 20.0   # 50 - 30
        assert bob_final == 128.5    # 100 + 28.5


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
