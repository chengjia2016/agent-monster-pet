#!/usr/bin/env python3
"""
Hybrid Data Manager
Manages both local cache and judge server sync
Ensures data consistency between local storage and judge server
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class HybridUserDataManager:
    """
    Hybrid data management system
    - Primary storage: Judge Server (source of truth)
    - Secondary cache: Local filesystem (for offline access)
    """
    
    def __init__(self, local_cache_dir: Path, judge_server_manager=None):
        """
        Initialize hybrid manager
        
        Args:
            local_cache_dir: Directory for local cache
            judge_server_manager: Judge server manager instance
        """
        self.local_cache_dir = local_cache_dir / "user_cache"
        self.local_cache_dir.mkdir(parents=True, exist_ok=True)
        self.judge_manager = judge_server_manager
    
    def get_user_data(self, github_id: int, use_server: bool = True) -> Optional[Dict]:
        """
        Get user data from server or cache
        
        Args:
            github_id: GitHub numeric ID
            use_server: Try server first, fallback to cache
            
        Returns:
            User data dict or None
        """
        if use_server and self.judge_manager:
            user = self.judge_manager.get_user(github_id)
            if user:
                # Cache locally for offline access
                self._cache_user_data(github_id, user)
                return user.__dict__
        
        # Fallback to local cache
        return self._get_cached_user_data(github_id)
    
    def save_user_data(self, github_id: int, user_data: Dict, sync_to_server: bool = True) -> bool:
        """
        Save user data to cache and optionally sync to server
        
        Args:
            github_id: GitHub numeric ID
            user_data: User data dictionary
            sync_to_server: Sync to judge server
            
        Returns:
            True if successful
        """
        # Always save to local cache
        self._cache_user_data(github_id, user_data)
        
        # Try to sync to server
        if sync_to_server and self.judge_manager:
            return self.judge_manager.sync_local_to_server(github_id, user_data)
        
        return True
    
    def _cache_user_data(self, github_id: int, user_data: Any) -> None:
        """Save user data to local cache"""
        cache_file = self.local_cache_dir / f"user_{github_id}.json"
        
        # Convert to dict if it's an object
        if hasattr(user_data, '__dict__'):
            data = user_data.__dict__
        else:
            data = user_data
        
        # Add sync timestamp
        data['_last_synced'] = datetime.utcnow().isoformat()
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _get_cached_user_data(self, github_id: int) -> Optional[Dict]:
        """Get user data from local cache"""
        cache_file = self.local_cache_dir / f"user_{github_id}.json"
        
        if cache_file.exists():
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return None
        
        return None
    
    def clear_cache(self, github_id: int = None) -> None:
        """
        Clear local cache
        
        Args:
            github_id: Specific user to clear, None for all
        """
        if github_id:
            cache_file = self.local_cache_dir / f"user_{github_id}.json"
            if cache_file.exists():
                cache_file.unlink()
        else:
            # Clear all cache
            for cache_file in self.local_cache_dir.glob("*.json"):
                cache_file.unlink()
    
    def is_server_online(self) -> bool:
        """Check if judge server is online"""
        if self.judge_manager:
            try:
                import urllib.request
                from judge_server_user_manager import JUDGE_SERVER
                urllib.request.urlopen(f"{JUDGE_SERVER}/api/health", timeout=3)
                return True
            except:
                return False
        return False
    
    def sync_all_to_server(self) -> Dict[str, bool]:
        """
        Sync all cached user data to server
        
        Returns:
            Dict with sync results for each user
        """
        results = {}
        
        if not self.judge_manager:
            return results
        
        for cache_file in self.local_cache_dir.glob("user_*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    user_data = json.load(f)
                    github_id = user_data.get('github_id')
                    if github_id:
                        results[str(github_id)] = self.judge_manager.sync_local_to_server(
                            github_id,
                            user_data
                        )
            except:
                pass
        
        return results


class UserDataSyncService:
    """
    Automatic sync service for user data
    Manages periodic syncing and conflict resolution
    """
    
    def __init__(self, hybrid_manager: HybridUserDataManager):
        self.hybrid_manager = hybrid_manager
        self.sync_interval = 300  # 5 minutes
        self.last_sync_time = {}
    
    def should_sync(self, github_id: int) -> bool:
        """
        Check if user data should be synced
        
        Args:
            github_id: GitHub numeric ID
            
        Returns:
            True if sync is needed
        """
        import time
        current_time = time.time()
        last_sync = self.last_sync_time.get(github_id, 0)
        
        return (current_time - last_sync) > self.sync_interval
    
    def resolve_conflict(self, local_data: Dict, server_data: Dict) -> Dict:
        """
        Resolve conflicts between local and server data
        Server data takes precedence (source of truth)
        
        Args:
            local_data: Local cache data
            server_data: Server data
            
        Returns:
            Resolved data (server data wins)
        """
        # Server is source of truth
        resolved = server_data.copy()
        
        # Merge local changes that might not be synced
        if 'balance' in local_data:
            # If local balance is higher, keep it (user earned coins locally)
            if local_data['balance'] > server_data.get('balance', 0):
                resolved['balance'] = local_data['balance']
        
        return resolved


if __name__ == "__main__":
    print("=" * 70)
    print(" 🔄 Hybrid User Data Manager")
    print("=" * 70)
    print()
    
    from pathlib import Path
    
    # Test initialization
    cache_dir = Path(".monster")
    manager = HybridUserDataManager(cache_dir)
    
    print(f"✓ Cache directory: {manager.local_cache_dir}")
    print(f"✓ Server online: {manager.is_server_online()}")
    print()
    
    # Example sync service
    sync_service = UserDataSyncService(manager)
    print(f"✓ Sync interval: {sync_service.sync_interval} seconds")
    print(f"✓ Conflict resolution: Server data takes precedence")
