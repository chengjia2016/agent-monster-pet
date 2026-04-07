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


# Singleton instance
_client = None

def get_judge_server_client() -> JudgeServerClient:
    """Get or create the global Judge Server client"""
    global _client
    if not _client:
        _client = JudgeServerClient()
    return _client
