#!/usr/bin/env python3
"""
Data Manager Adapter
Provides unified access to user data using hybrid (local + server) storage
"""

from pathlib import Path
from typing import Optional, Dict, Any
from hybrid_user_data_manager import HybridUserDataManager
from judge_server_user_manager import JudgeServerUserManager
from user_manager import UserManager
from economy_manager import EconomyManager
from shop_manager import Shop


class UnifiedDataManager:
    """
    Unified interface for accessing user data
    Transparently handles hybrid storage (local + server)
    """
    
    def __init__(self, data_dir: str = ".monster", enable_server_sync: bool = True):
        """
        Initialize unified data manager
        
        Args:
            data_dir: Directory for local storage
            enable_server_sync: Enable server sync (False for offline mode)
        """
        self.data_dir = Path(data_dir)
        self.enable_server_sync = enable_server_sync
        
        # Initialize local managers
        self.user_manager = UserManager(str(self.data_dir))
        self.economy_manager = EconomyManager(str(self.data_dir))
        self.shop_manager = Shop(str(self.data_dir))
        
        # Initialize server manager (only if sync enabled)
        self.judge_server = None
        if enable_server_sync:
            try:
                self.judge_server = JudgeServerUserManager()
            except Exception as e:
                print(f"Warning: Could not initialize Judge Server manager: {e}")
        
        # Initialize hybrid manager
        self.hybrid_manager = HybridUserDataManager(
            self.data_dir,
            judge_server_manager=self.judge_server if enable_server_sync else None
        )
    
    # ========== User Profile Management ==========
    
    def get_user_profile(self, github_login: str) -> Optional[Dict]:
        """Get user profile with all related data"""
        user = self._find_user_by_login(github_login)
        if not user:
            return None
        
        account = self.economy_manager.get_account(user.user_id)
        inventory = self.shop_manager.get_user_inventory(user.user_id)
        
        return {
            "user_id": user.user_id,
            "github_id": user.github_id,
            "github_login": user.github_login,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "registered_at": user.registered_at,
            "last_login": user.last_login,
            "balance": account.balance if account else 0.0,
            "inventory": inventory or {},
            "transactions": account.transactions if account else [],
        }
    
    def sync_user_to_server(self, github_id: int, user_data: Dict) -> bool:
        """
        Sync user data to server
        
        Args:
            github_id: GitHub numeric ID
            user_data: User data dictionary
            
        Returns:
            True if sync successful
        """
        if not self.enable_server_sync:
            return True  # Offline mode, just cache
        
        return self.hybrid_manager.save_user_data(
            github_id=github_id,
            user_data=user_data,
            sync_to_server=True
        )
    
    # ========== Account Management ==========
    
    def get_account(self, user_id: str) -> Optional[Any]:
        """Get user account"""
        return self.economy_manager.get_account(user_id)
    
    def update_balance(self, user_id: str, amount: float, reason: str = ""):
        """Update user balance"""
        return self.economy_manager.update_balance(user_id, amount, reason)
    
    def get_balance(self, user_id: str) -> float:
        """Get current user balance"""
        account = self.economy_manager.get_account(user_id)
        return account.balance if account else 0.0
    
    # ========== Inventory Management ==========
    
    def get_inventory(self, user_id: str) -> Dict:
        """Get user inventory"""
        return self.shop_manager.get_user_inventory(user_id) or {}
    
    def add_item(self, user_id: str, item_id: str, quantity: int = 1) -> bool:
        """Add item to inventory"""
        return self.shop_manager.add_item(user_id, item_id, quantity)
    
    def remove_item(self, user_id: str, item_id: str, quantity: int = 1) -> bool:
        """Remove item from inventory"""
        return self.shop_manager.remove_item(user_id, item_id, quantity)
    
    # ========== Shopping/Economy ==========
    
    def purchase_item(self, user_id: str, item_id: str, quantity: int = 1) -> Dict:
        """Purchase item"""
        return self.economy_manager.purchase_item(user_id, item_id, quantity)
    
    # ========== User Discovery ==========
    
    def find_user_by_login(self, github_login: str) -> Optional[Any]:
        """Find user by GitHub login"""
        return self._find_user_by_login(github_login)
    
    def list_users(self):
        """List all users"""
        return self.user_manager.list_users()
    
    def get_user_by_id(self, user_id: str) -> Optional[Any]:
        """Get user by user_id"""
        return self.user_manager.get_user(user_id)
    
    # ========== Helper Methods ==========
    
    def _find_user_by_login(self, github_login: str) -> Optional[Any]:
        """Find user by GitHub login"""
        users = self.user_manager.list_users()
        for user in users:
            if user.github_login == github_login:
                return user
        return None
    
    def enable_server_mode(self, enabled: bool = True):
        """Enable/disable server sync"""
        self.enable_server_sync = enabled
        if not enabled:
            self.judge_server = None
            self.hybrid_manager.judge_manager = None
    
    def get_sync_status(self) -> Dict:
        """Get current sync status"""
        return {
            "server_sync_enabled": self.enable_server_sync,
            "server_available": self._is_server_available(),
            "mode": "hybrid" if self.enable_server_sync else "offline"
        }
    
    def _is_server_available(self) -> bool:
        """Check if Judge Server is available"""
        if not self.judge_server:
            return False
        
        try:
            import urllib.request
            response = urllib.request.urlopen(
                f"{self.judge_server.server_url}/health",
                timeout=5
            )
            return response.status == 200
        except:
            return False


# Global instance (optional, for easy access)
_manager_instance = None

def get_unified_manager(data_dir: str = ".monster", enable_sync: bool = True) -> UnifiedDataManager:
    """Get or create unified data manager"""
    global _manager_instance
    if not _manager_instance:
        _manager_instance = UnifiedDataManager(data_dir, enable_sync)
    return _manager_instance
