#!/usr/bin/env python3
"""
MCP Server Data Manager Integration
Provides decorators and utilities for integrating data manager with MCP commands
"""

from functools import wraps
from typing import Callable, Any
from pathlib import Path
from unified_data_manager import UnifiedDataManager

# Global data manager instance
_data_manager = None

def init_data_manager(data_dir: str = ".monster", enable_sync: bool = True):
    """Initialize the global data manager"""
    global _data_manager
    _data_manager = UnifiedDataManager(data_dir, enable_sync)
    return _data_manager

def get_data_manager() -> UnifiedDataManager:
    """Get the global data manager"""
    global _data_manager
    if not _data_manager:
        _data_manager = UnifiedDataManager()
    return _data_manager

def with_data_manager(func: Callable) -> Callable:
    """
    Decorator to inject data manager into MCP commands
    Usage:
        @with_data_manager
        def cmd_user_info(dm: UnifiedDataManager, username: str):
            profile = dm.get_user_profile(username)
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        dm = get_data_manager()
        # Inject data manager as first positional argument
        return func(dm, *args, **kwargs)
    return wrapper

def find_user(github_login: str) -> Any:
    """Find user by GitHub login"""
    dm = get_data_manager()
    return dm.find_user_by_login(github_login)

def get_account(user_id: str) -> Any:
    """Get user account"""
    dm = get_data_manager()
    return dm.get_account(user_id)

def get_balance(user_id: str) -> float:
    """Get user balance"""
    dm = get_data_manager()
    return dm.get_balance(user_id)

def get_user_profile(github_login: str) -> dict:
    """Get full user profile"""
    dm = get_data_manager()
    return dm.get_user_profile(github_login)

def list_users():
    """List all users"""
    dm = get_data_manager()
    return dm.list_users()

# Example usage in MCP commands:
"""
from mcp_data_manager import with_data_manager, get_data_manager

def cmd_user_info(github_username):
    dm = get_data_manager()
    user = dm.find_user_by_login(github_username)
    if not user:
        return f"❌ User not found"
    
    profile = dm.get_user_profile(github_username)
    return f"✓ User: {profile['github_login']}, Balance: {profile['balance']}"
"""
