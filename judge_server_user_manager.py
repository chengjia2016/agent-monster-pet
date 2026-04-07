#!/usr/bin/env python3
"""
Judge Server User Data Persistence Module
Manages all user data (Pokémon, coins, items) on the judge server
"""

import json
import urllib.request
import urllib.error
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict


JUDGE_SERVER = "http://agentmonster.openx.pro:10000"


@dataclass
class JudgeServerUser:
    """User data stored on judge server"""
    github_id: int
    github_login: str
    balance: float = 0.0
    pokemons: List[Dict[str, Any]] = None
    items: List[Dict[str, Any]] = None
    created_at: str = ""
    last_updated: str = ""
    
    def __post_init__(self):
        if self.pokemons is None:
            self.pokemons = []
        if self.items is None:
            self.items = []


class JudgeServerUserManager:
    """
    Manages user data persistence on judge server
    All user data is stored centrally on the judge server
    """
    
    def __init__(self, server_url: str = JUDGE_SERVER):
        self.server_url = server_url
        self.base_endpoint = "/api/users"
    
    def _make_request(self, endpoint: str, method: str = "GET", data: Dict = None) -> Optional[Dict]:
        """
        Make HTTP request to judge server
        
        Args:
            endpoint: API endpoint (e.g., "/api/users/123")
            method: HTTP method (GET, POST, PUT, DELETE)
            data: Request body for POST/PUT
            
        Returns:
            Response JSON or None if error
        """
        try:
            url = f"{self.server_url}{endpoint}"
            
            if method == "GET":
                with urllib.request.urlopen(url, timeout=10) as response:
                    return json.loads(response.read().decode("utf-8"))
            
            elif method in ["POST", "PUT"]:
                req_data = json.dumps(data).encode("utf-8") if data else b""
                req = urllib.request.Request(
                    url,
                    data=req_data,
                    headers={"Content-Type": "application/json"},
                    method=method
                )
                with urllib.request.urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode("utf-8"))
            
            elif method == "DELETE":
                req = urllib.request.Request(url, method="DELETE")
                with urllib.request.urlopen(req, timeout=10) as response:
                    return json.loads(response.read().decode("utf-8"))
        
        except urllib.error.HTTPError as e:
            print(f"HTTP Error {e.code}: {e.reason}")
            return None
        except Exception as e:
            print(f"Request error: {e}")
            return None
    
    def create_user(self, github_id: int, github_login: str, initial_balance: float = 100.0) -> Optional[JudgeServerUser]:
        """
        Create new user on judge server
        
        Args:
            github_id: GitHub numeric ID
            github_login: GitHub username
            initial_balance: Initial coin balance (default 100)
            
        Returns:
            Created user data or None if error
        """
        user_data = {
            "github_id": github_id,
            "github_login": github_login,
            "balance": initial_balance,
            "pokemons": [],
            "items": [],
            "created_at": self._get_timestamp()
        }
        
        response = self._make_request(
            f"{self.base_endpoint}/create",
            method="POST",
            data=user_data
        )
        
        if response and response.get("success"):
            return JudgeServerUser(**response.get("user", {}))
        return None
    
    def get_user(self, github_id: int) -> Optional[JudgeServerUser]:
        """
        Get user data from judge server
        
        Args:
            github_id: GitHub numeric ID
            
        Returns:
            User data or None if not found
        """
        response = self._make_request(f"{self.base_endpoint}/{github_id}")
        
        if response and response.get("success"):
            return JudgeServerUser(**response.get("user", {}))
        return None
    
    def update_balance(self, github_id: int, amount: float, transaction_type: str = "MANUAL") -> bool:
        """
        Update user coin balance
        
        Args:
            github_id: GitHub numeric ID
            amount: Amount to add/subtract (can be negative)
            transaction_type: Type of transaction (INITIAL_GRANT, PURCHASE, REWARD, etc.)
            
        Returns:
            True if successful
        """
        data = {
            "amount": amount,
            "transaction_type": transaction_type,
            "timestamp": self._get_timestamp()
        }
        
        response = self._make_request(
            f"{self.base_endpoint}/{github_id}/balance",
            method="PUT",
            data=data
        )
        
        return response and response.get("success", False)
    
    def add_pokemon(self, github_id: int, pokemon_data: Dict) -> bool:
        """
        Add Pokémon to user's collection
        
        Args:
            github_id: GitHub numeric ID
            pokemon_data: Pokémon details (name, level, hp, etc.)
            
        Returns:
            True if successful
        """
        data = {
            "pokemon": pokemon_data,
            "timestamp": self._get_timestamp()
        }
        
        response = self._make_request(
            f"{self.base_endpoint}/{github_id}/pokemons",
            method="POST",
            data=data
        )
        
        return response and response.get("success", False)
    
    def get_pokemons(self, github_id: int) -> List[Dict]:
        """
        Get user's Pokémon collection
        
        Args:
            github_id: GitHub numeric ID
            
        Returns:
            List of Pokémon data
        """
        response = self._make_request(f"{self.base_endpoint}/{github_id}/pokemons")
        
        if response and response.get("success"):
            return response.get("pokemons", [])
        return []
    
    def add_item(self, github_id: int, item_id: str, quantity: int = 1) -> bool:
        """
        Add item to user's inventory
        
        Args:
            github_id: GitHub numeric ID
            item_id: Item identifier (e.g., "ball_red", "potion_small")
            quantity: Quantity to add
            
        Returns:
            True if successful
        """
        data = {
            "item_id": item_id,
            "quantity": quantity,
            "timestamp": self._get_timestamp()
        }
        
        response = self._make_request(
            f"{self.base_endpoint}/{github_id}/items",
            method="POST",
            data=data
        )
        
        return response and response.get("success", False)
    
    def get_items(self, github_id: int) -> List[Dict]:
        """
        Get user's inventory
        
        Args:
            github_id: GitHub numeric ID
            
        Returns:
            List of items
        """
        response = self._make_request(f"{self.base_endpoint}/{github_id}/items")
        
        if response and response.get("success"):
            return response.get("items", [])
        return []
    
    def get_stats(self, github_id: int) -> Dict:
        """
        Get comprehensive user stats
        
        Args:
            github_id: GitHub numeric ID
            
        Returns:
            User statistics dictionary
        """
        response = self._make_request(f"{self.base_endpoint}/{github_id}/stats")
        
        if response and response.get("success"):
            return response.get("stats", {})
        return {}
    
    def sync_local_to_server(self, github_id: int, local_user_data: Dict) -> bool:
        """
        Sync local user data to judge server
        
        Args:
            github_id: GitHub numeric ID
            local_user_data: User data from local storage
            
        Returns:
            True if successful
        """
        response = self._make_request(
            f"{self.base_endpoint}/{github_id}/sync",
            method="PUT",
            data=local_user_data
        )
        
        return response and response.get("success", False)
    
    @staticmethod
    def _get_timestamp() -> str:
        """Get current timestamp in ISO format"""
        from datetime import datetime
        return datetime.utcnow().isoformat()


# Global instance
_judge_server_manager = None


def get_judge_server_manager() -> JudgeServerUserManager:
    """Get or create global judge server manager instance"""
    global _judge_server_manager
    if _judge_server_manager is None:
        _judge_server_manager = JudgeServerUserManager()
    return _judge_server_manager


if __name__ == "__main__":
    manager = JudgeServerUserManager()
    
    print("=" * 70)
    print(" 🔌 Judge Server User Data Manager")
    print("=" * 70)
    print()
    
    # Test connection
    print("1️⃣  Testing server connection...")
    try:
        import urllib.request
        urllib.request.urlopen(f"{JUDGE_SERVER}/api/health", timeout=5)
        print("   ✓ Server is online")
    except:
        print("   ✗ Server is offline or unreachable")
        print(f"   Server URL: {JUDGE_SERVER}")
