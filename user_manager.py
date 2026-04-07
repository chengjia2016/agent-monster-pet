#!/usr/bin/env python3
"""
User Management System
Handles user authentication, registration, and profile management
Integrates with GitHub OAuth for login
"""

import json
import hashlib
import time
import uuid
from pathlib import Path
from typing import Dict, Optional, Any
from datetime import datetime, timedelta


class User:
    """User profile and account information"""
    
    def __init__(
        self,
        user_id: str,
        github_login: str,
        github_id: int,
        email: str = "",
        avatar_url: str = "",
        registered_at: str = None,
        last_login: str = None
    ):
        self.user_id = user_id
        self.github_login = github_login
        self.github_id = github_id
        self.email = email
        self.avatar_url = avatar_url
        self.registered_at = registered_at or datetime.utcnow().isoformat()
        self.last_login = last_login
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "github_login": self.github_login,
            "github_id": self.github_id,
            "email": self.email,
            "avatar_url": self.avatar_url,
            "registered_at": self.registered_at,
            "last_login": self.last_login
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create from dictionary"""
        return cls(**data)


class UserManager:
    """Manage user accounts and authentication"""
    
    def __init__(self, data_dir: str = ".monster"):
        self.data_dir = Path(data_dir)
        self.users_dir = self.data_dir / "users"
        self.users_dir.mkdir(parents=True, exist_ok=True)
        self.sessions_file = self.data_dir / "sessions.json"
        self.sessions = self._load_sessions()
    
    def _load_sessions(self) -> Dict[str, Dict]:
        """Load active sessions"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return {}
        return {}
    
    def _save_sessions(self):
        """Save sessions to disk"""
        with open(self.sessions_file, "w", encoding="utf-8") as f:
            json.dump(self.sessions, f, indent=2, ensure_ascii=False)
    
    def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID"""
        user_file = self.users_dir / f"{user_id}.json"
        if user_file.exists():
            try:
                with open(user_file, "r", encoding="utf-8") as f:
                    return User.from_dict(json.load(f))
            except:
                return None
        return None
    
    def get_user_by_github_id(self, github_id: int) -> Optional[User]:
        """Get user by GitHub ID"""
        for user_file in self.users_dir.glob("*.json"):
            try:
                with open(user_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if data.get("github_id") == github_id:
                        return User.from_dict(data)
            except:
                continue
        return None
    
    def register_user(
        self,
        github_login: str,
        github_id: int,
        email: str = "",
        avatar_url: str = ""
    ) -> User:
        """Register a new user from GitHub OAuth"""
        # Check if user already exists
        existing = self.get_user_by_github_id(github_id)
        if existing:
            return existing
        
        # Create new user
        user_id = str(uuid.uuid4())[:8]
        user = User(
            user_id=user_id,
            github_login=github_login,
            github_id=github_id,
            email=email,
            avatar_url=avatar_url
        )
        
        # Save user
        user_file = self.users_dir / f"{user_id}.json"
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(user.to_dict(), f, indent=2, ensure_ascii=False)
        
        return user
    
    def create_session(self, user: User, duration_hours: int = 24) -> str:
        """Create a session token"""
        session_token = hashlib.sha256(
            f"{user.user_id}_{time.time()}_{uuid.uuid4()}".encode()
        ).hexdigest()
        
        self.sessions[session_token] = {
            "user_id": user.user_id,
            "created_at": datetime.utcnow().isoformat(),
            "expires_at": (datetime.utcnow() + timedelta(hours=duration_hours)).isoformat()
        }
        self._save_sessions()
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[str]:
        """Validate session and return user_id if valid"""
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        expires_at = datetime.fromisoformat(session["expires_at"])
        
        if datetime.utcnow() > expires_at:
            del self.sessions[session_token]
            self._save_sessions()
            return None
        
        return session["user_id"]
    
    def update_last_login(self, user: User):
        """Update user's last login timestamp"""
        user.last_login = datetime.utcnow().isoformat()
        user_file = self.users_dir / f"{user.user_id}.json"
        with open(user_file, "w", encoding="utf-8") as f:
            json.dump(user.to_dict(), f, indent=2, ensure_ascii=False)
    
    def list_users(self) -> list[User]:
        """List all registered users"""
        users = []
        for user_file in self.users_dir.glob("*.json"):
            try:
                with open(user_file, "r", encoding="utf-8") as f:
                    users.append(User.from_dict(json.load(f)))
            except:
                continue
        return users
