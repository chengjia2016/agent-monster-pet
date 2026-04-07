#!/usr/bin/env python3
"""
Judge Server API Client for MCP Server
Manages user accounts, pokemons, and items via Judge Server
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from dataclasses import dataclass

JUDGE_SERVER_URL = "http://agentmonster.openx.pro:10000"

@dataclass
class UserAccount:
    github_id: int
    github_login: str
    balance: float
    email: str = ""
    avatar_url: str = ""

class JudgeServerClient:
    """Client for interacting with Judge Server user management API"""
    
    def __init__(self, server_url: str = JUDGE_SERVER_URL):
        self.server_url = server_url
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """Make HTTP request to Judge Server"""
        try:
            url = f"{self.server_url}{endpoint}"
            headers = {"Content-Type": "application/json"}
            
            if method == "GET":
                request = urllib.request.Request(url, headers=headers, method=method)
            else:
                body = json.dumps(data).encode('utf-8') if data else None
                request = urllib.request.Request(url, data=body, headers=headers, method=method)
            
            with urllib.request.urlopen(request, timeout=10) as response:
                return json.loads(response.read().decode('utf-8'))
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            return None
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    # ========== User Account Operations ==========
    
    def create_user_account(self, github_id: int, github_login: str, email: str = "", 
                           avatar_url: str = "", balance: float = 0.0) -> bool:
        """Create a new user account on Judge Server"""
        data = {
            "github_id": github_id,
            "github_login": github_login,
            "email": email,
            "avatar_url": avatar_url,
            "balance": balance
        }
        result = self._make_request("/api/users/create", method="POST", data=data)
        return result is not None and result.get("success", False)
    
    def get_user_account(self, github_id: int) -> Optional[UserAccount]:
        """Get user account from Judge Server"""
        result = self._make_request(f"/api/users/{github_id}")
        if result and "github_id" in result:
            return UserAccount(
                github_id=result["github_id"],
                github_login=result["github_login"],
                balance=float(result.get("balance", 0)),
                email=result.get("email", ""),
                avatar_url=result.get("avatar_url", "")
            )
        return None
    
    def get_user_balance(self, github_id: int) -> float:
        """Get user balance from Judge Server"""
        result = self._make_request(f"/api/user/balance/get", method="POST", 
                                    data={"github_id": github_id})
        if result:
            return float(result.get("balance", 0))
        return 0.0
    
    def update_user_balance(self, github_id: int, amount: float, description: str = "") -> bool:
        """Update user balance on Judge Server"""
        data = {
            "github_id": github_id,
            "amount": amount,
            "description": description
        }
        result = self._make_request("/api/user/balance/update", method="POST", data=data)
        return result is not None and result.get("success", False)
    
    # ========== Pokemon Operations ==========
    
    def get_user_pokemons(self, github_id: int) -> List[Dict]:
        """Get all pokemons for a user"""
        data = {"github_id": github_id}
        result = self._make_request("/api/user/pokemons/get", method="POST", data=data)
        if result:
            return result.get("pokemons", [])
        return []
    
    def add_user_pokemon(self, github_id: int, pet_id: str, pet_name: str, 
                        level: int = 1, species: str = "") -> bool:
        """Add a pokemon to user's collection"""
        data = {
            "github_id": github_id,
            "pet_id": pet_id,
            "pet_name": pet_name,
            "level": level,
            "species": species
        }
        result = self._make_request("/api/user/pokemons/add", method="POST", data=data)
        return result is not None and result.get("success", False)
    
    # ========== Inventory Operations ==========
    
    def get_user_inventory(self, github_id: int) -> List[Dict]:
        """Get user's inventory"""
        data = {"github_id": github_id}
        result = self._make_request("/api/user/inventory/get", method="POST", data=data)
        if result:
            return result.get("items", [])
        return []
    
    def add_user_item(self, github_id: int, item_id: str, item_name: str, 
                     quantity: int = 1) -> bool:
        """Add item to user's inventory"""
        data = {
            "github_id": github_id,
            "item_id": item_id,
            "item_name": item_name,
            "quantity": quantity
        }
        result = self._make_request("/api/user/inventory/add", method="POST", data=data)
        return result is not None and result.get("success", False)
    
    # ========== Transaction History ==========
    
    def get_user_transactions(self, github_id: int, limit: int = 50) -> List[Dict]:
        """Get transaction history for a user"""
        data = {"github_id": github_id, "limit": limit}
        result = self._make_request("/api/user/transactions/get", method="POST", data=data)
        if result:
            return result.get("transactions", [])
        return []
    
    # ========== Health Check ==========
    
    def health_check(self) -> bool:
        """Check if Judge Server is healthy"""
        result = self._make_request("/health")
        return result is not None and result.get("status") == "healthy"
    
    # ========== Farm Operations ==========
    
    def create_farm(self, owner_id: str, repository_name: str, repository_url: str) -> Optional[Dict]:
        """Create a new farm"""
        data = {
            "owner_id": owner_id,
            "repository_name": repository_name,
            "repository_url": repository_url
        }
        result = self._make_request("/api/farms/create", method="POST", data=data)
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def get_farm(self, farm_id: int) -> Optional[Dict]:
        """Get farm details"""
        result = self._make_request(f"/api/farms/{farm_id}")
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def search_farms(self, owner: str = "", repository: str = "") -> List[Dict]:
        """Search farms by owner or repository name"""
        endpoint = "/api/farms/search?"
        if owner:
            endpoint += f"owner={owner}&"
        if repository:
            endpoint += f"repository={repository}&"
        
        result = self._make_request(endpoint.rstrip("&"))
        if result and result.get("success"):
            return result.get("data", [])
        return []
    
    def add_food_to_farm(self, farm_id: int, food_id: str, food_type: str, 
                         quantity: int, max_quantity: int = 100, 
                         regeneration_hours: int = 24, emoji: str = "🍪") -> Optional[Dict]:
        """Add food to a farm"""
        data = {
            "food_id": food_id,
            "food_type": food_type,
            "quantity": quantity,
            "max_quantity": max_quantity,
            "regeneration_hours": regeneration_hours,
            "emoji": emoji
        }
        result = self._make_request(f"/api/farms/{farm_id}/foods", method="POST", data=data)
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def consume_food(self, farm_id: int, food_id: str, eater_id: str, eater_pet_id: str) -> bool:
        """Consume food from a farm"""
        data = {
            "food_id": food_id,
            "eater_id": eater_id,
            "eater_pet_id": eater_pet_id
        }
        result = self._make_request(f"/api/farms/{farm_id}/foods/consume", method="POST", data=data)
        return result is not None and result.get("success", False)
    
    def get_farm_statistics(self, farm_id: int) -> Optional[Dict]:
        """Get farm statistics"""
        result = self._make_request(f"/api/farms/{farm_id}/statistics")
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def delete_farm(self, farm_id: int) -> bool:
        """Delete a farm"""
        result = self._make_request(f"/api/farms/{farm_id}", method="DELETE")
        return result is not None and result.get("success", False)
    
    # ========== Cookie Operations ==========
    
    def register_cookie(self, cookie_id: str, cookie_type: str, emoji: str = "🍪",
                       source_file: str = "", generator_id: str = "") -> Optional[Dict]:
        """Register a new cookie"""
        data = {
            "cookie_id": cookie_id,
            "cookie_type": cookie_type,
            "emoji": emoji,
            "source_file": source_file,
            "generator_id": generator_id
        }
        result = self._make_request("/api/cookies/register", method="POST", data=data)
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def claim_cookie(self, cookie_id: str, player_id: str, 
                    exp_reward: int = 10, energy_reward: int = 5) -> Optional[Dict]:
        """Claim a cookie for a player"""
        data = {
            "cookie_id": cookie_id,
            "player_id": player_id,
            "exp_reward": exp_reward,
            "energy_reward": energy_reward
        }
        result = self._make_request("/api/cookies/claim", method="POST", data=data)
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def get_cookie_statistics(self) -> Optional[Dict]:
        """Get cookie statistics"""
        result = self._make_request("/api/cookies/statistics")
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def scan_cookies(self, player_id: str) -> Optional[Dict]:
        """Scan cookies for a player"""
        result = self._make_request(f"/api/cookies/scan?player_id={player_id}")
        if result and result.get("success"):
            return result.get("data")
        return None
    
    # ========== Egg Operations ==========
    
    def create_egg(self, egg_id: str, owner_id: str, incubation_hours: int = 72,
                  attributes: str = "") -> Optional[Dict]:
        """Create a new egg"""
        data = {
            "egg_id": egg_id,
            "owner_id": owner_id,
            "incubation_hours": incubation_hours,
            "attributes": attributes
        }
        result = self._make_request("/api/eggs/create", method="POST", data=data)
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def get_egg(self, egg_id: str) -> Optional[Dict]:
        """Get egg details"""
        result = self._make_request(f"/api/eggs/{egg_id}")
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def hatch_egg(self, egg_id: str, pet_id: str) -> bool:
        """Hatch an egg into a pet"""
        data = {"pet_id": pet_id}
        result = self._make_request(f"/api/eggs/{egg_id}/hatch", method="POST", data=data)
        return result is not None and result.get("success", False)
    
    def get_egg_statistics(self) -> Optional[Dict]:
        """Get egg statistics"""
        result = self._make_request("/api/eggs/statistics")
        if result and result.get("success"):
            return result.get("data")
        return None
    
    # ========== Shop Operations ==========
    
    def list_shop_items(self) -> List[Dict]:
        """Get all shop items"""
        result = self._make_request("/api/shop/items")
        if result and result.get("success"):
            return result.get("data", [])
        return []
    
    def buy_item(self, item_id: str, player_id: str, quantity: int = 1) -> Optional[Dict]:
        """Buy an item from the shop"""
        data = {
            "item_id": item_id,
            "player_id": player_id,
            "quantity": quantity
        }
        result = self._make_request("/api/shop/buy", method="POST", data=data)
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def get_shop_statistics(self) -> Optional[Dict]:
        """Get shop statistics"""
        result = self._make_request("/api/shop/statistics")
        if result and result.get("success"):
            return result.get("data")
        return None
    
    def get_transaction_history(self, player_id: str, limit: int = 50) -> List[Dict]:
        """Get transaction history for a player"""
        result = self._make_request(f"/api/shop/transactions?player_id={player_id}&limit={limit}")
        if result and result.get("success"):
            return result.get("data", [])
        return []


# Singleton instance
_client = None

def get_judge_server_client() -> JudgeServerClient:
    """Get or create the global Judge Server client"""
    global _client
    if not _client:
        _client = JudgeServerClient()
    return _client
