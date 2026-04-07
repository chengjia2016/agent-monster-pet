#!/usr/bin/env python3
"""
Onboarding System
Handles new user registration, GitHub OAuth, and initial setup
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any, Tuple
from user_manager import UserManager, User
from economy_manager import EconomyManager
from shop_manager import Shop, ItemType


class OnboardingManager:
    """Manage new user onboarding and initial setup"""
    
    # Initial items every user gets
    INITIAL_ITEMS = {
        "pokeball": 3,        # 3 精灵球
        "seed_grass": 2,      # 2个草种子
        "potion_small": 1,    # 1个小药剂
    }
    
    def __init__(self, data_dir: str = ".monster"):
        self.data_dir = Path(data_dir)
        self.user_manager = UserManager(data_dir)
        self.economy_manager = EconomyManager(data_dir)
        self.shop = Shop(data_dir)
        
        self.onboarding_file = Path(data_dir) / "onboarding.json"
    
    def register_from_github(
        self,
        github_login: str,
        github_id: int,
        email: str = "",
        avatar_url: str = ""
    ) -> Tuple[bool, User, str]:
        """
        Register a new user from GitHub OAuth
        Returns: (success, user, message)
        """
        try:
            # Register user
            user = self.user_manager.register_user(
                github_login=github_login,
                github_id=github_id,
                email=email,
                avatar_url=avatar_url
            )
            
            # Create economy account (100 initial coins)
            account = self.economy_manager.create_account(
                user_id=user.user_id,
                initial_balance=100.0
            )
            
            # Add initial items to inventory
            self._grant_initial_items(user.user_id)
            
            # Create starter pet (小黄鸭)
            self._create_starter_pet(user.user_id)
            
            # Create egg
            self._create_starter_egg(user.user_id)
            
            # Record onboarding
            self._record_onboarding(user)
            
            return (
                True,
                user,
                f"Welcome to Agent Monster! Your account is ready. You've been granted 100 Pokécoins and starter items."
            )
        
        except Exception as e:
            return (False, None, f"Registration failed: {str(e)}")
    
    def _grant_initial_items(self, user_id: str):
        """Grant initial items to new user"""
        for item_id, quantity in self.INITIAL_ITEMS.items():
            shop_item = self.shop.get_item(item_id)
            if shop_item:
                # Just add to inventory directly (don't deduct from shop stock)
                inventory_file = self.shop.inventory_dir / f"{user_id}.json"
                
                if inventory_file.exists():
                    with open(inventory_file, "r", encoding="utf-8") as f:
                        inventory = json.load(f)
                else:
                    inventory = {}
                
                inventory[item_id] = inventory.get(item_id, 0) + quantity
                
                with open(inventory_file, "w", encoding="utf-8") as f:
                    json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    def _create_starter_pet(self, user_id: str):
        """Create starter Pokémon (小黄鸭 - Psyduck)"""
        starter_pet = {
            "pet_id": f"{user_id}_starter",
            "name": "小黄鸭",
            "species": "Psyduck",
            "level": 1,
            "experience": 0,
            "health": 35,
            "max_health": 35,
            "stats": {
                "attack": 52,
                "defense": 48,
                "speed": 55,
                "special_attack": 65,
                "special_defense": 50
            },
            "obtained_at": __import__('datetime').datetime.utcnow().isoformat(),
            "is_starter": True
        }
        
        pet_file = Path(self.data_dir) / f"{user_id}_starter_pet.json"
        with open(pet_file, "w", encoding="utf-8") as f:
            json.dump(starter_pet, f, indent=2, ensure_ascii=False)
    
    def _create_starter_egg(self, user_id: str):
        """Create starter egg for new user"""
        starter_egg = {
            "egg_id": f"{user_id}_egg_1",
            "status": "incubating",
            "created_at": __import__('datetime').datetime.utcnow().isoformat(),
            "incubation_time_required": 86400,  # 24 hours
            "remaining_time": 86400
        }
        
        egg_file = Path(self.data_dir) / f"{user_id}_egg.json"
        with open(egg_file, "w", encoding="utf-8") as f:
            json.dump(starter_egg, f, indent=2, ensure_ascii=False)
    
    def _record_onboarding(self, user: User):
        """Record onboarding event"""
        onboarding_data = []
        
        if self.onboarding_file.exists():
            with open(self.onboarding_file, "r", encoding="utf-8") as f:
                onboarding_data = json.load(f)
        
        onboarding_data.append({
            "user_id": user.user_id,
            "github_login": user.github_login,
            "registered_at": user.registered_at,
            "initial_items_granted": list(self.INITIAL_ITEMS.keys()),
            "starter_pet": "Psyduck (小黄鸭)",
            "starter_egg": "1"
        })
        
        with open(self.onboarding_file, "w", encoding="utf-8") as f:
            json.dump(onboarding_data, f, indent=2, ensure_ascii=False)
    
    def get_user_onboarding_status(self, user_id: str) -> Dict[str, Any]:
        """Get user's onboarding status"""
        user = self.user_manager.get_user(user_id)
        if not user:
            return {"status": "not_found"}
        
        account = self.economy_manager.get_account(user_id)
        inventory = self.shop.get_user_inventory(user_id)
        
        return {
            "status": "completed",
            "user": user.to_dict(),
            "balance": account.balance if account else 0.0,
            "inventory": inventory,
            "initial_rewards": {
                "coins": 100.0,
                "items": self.INITIAL_ITEMS,
                "starter_pet": "Psyduck (小黄鸭)",
                "starter_egg": 1
            }
        }
    
    def is_user_registered(self, github_id: int) -> bool:
        """Check if user is already registered"""
        user = self.user_manager.get_user_by_github_id(github_id)
        return user is not None
