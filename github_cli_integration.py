#!/usr/bin/env python3
"""
GitHub CLI Integration Module
Automatically detects GitHub user from 'gh' CLI and simplifies login flow
"""

import subprocess
import json
import os
from typing import Optional, Tuple


class GitHubCLIIntegration:
    """集成 GitHub CLI 的自动登录系统"""
    
    def __init__(self):
        self.cached_user = None
    
    def get_current_user(self) -> Optional[str]:
        """
        从 GitHub CLI 获取当前登录的用户名
        
        Returns:
            str: GitHub 用户名，如果未登录则返回 None
        """
        if self.cached_user:
            return self.cached_user
        
        try:
            # 使用 gh auth status 获取用户信息
            result = subprocess.run(
                ["gh", "auth", "status", "--show-token"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # 从输出中提取用户名
                # 格式: "Logged in to github.com as username (keyring)"
                output = result.stderr or result.stdout
                for line in output.split('\n'):
                    if 'as' in line and 'github.com' in line:
                        # 提取用户名
                        parts = line.split('as ')
                        if len(parts) > 1:
                            username = parts[1].split()[0].strip('()[]')
                            self.cached_user = username
                            return username
        except FileNotFoundError:
            return None
        except Exception as e:
            return None
        
        return None
    
    def get_user_info(self) -> Optional[dict]:
        """
        获取 GitHub 用户的详细信息
        
        Returns:
            dict: 包含用户信息的字典，格式:
                {
                    "username": "...",
                    "name": "...",
                    "bio": "...",
                    "company": "..."
                }
        """
        username = self.get_current_user()
        if not username:
            return None
        
        try:
            # 使用 gh api 获取用户信息
            result = subprocess.run(
                ["gh", "api", "user"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                data = json.loads(result.stdout)
                return {
                    "username": data.get("login"),
                    "name": data.get("name"),
                    "bio": data.get("bio"),
                    "company": data.get("company"),
                    "avatar_url": data.get("avatar_url"),
                    "public_repos": data.get("public_repos")
                }
        except Exception as e:
            pass
        
        return None
    
    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self.get_current_user() is not None
    
    def open_login_flow(self) -> bool:
        """
        打开 GitHub 登录流程
        
        Returns:
            bool: 登录是否成功
        """
        try:
            result = subprocess.run(
                ["gh", "auth", "login"],
                timeout=300  # 给用户 5 分钟时间完成登录
            )
            
            if result.returncode == 0:
                # 清除缓存以获取新的用户信息
                self.cached_user = None
                return self.is_authenticated()
        except Exception as e:
            pass
        
        return False
    
    def format_welcome_message(self) -> str:
        """格式化欢迎消息"""
        username = self.get_current_user()
        user_info = self.get_user_info()
        
        if not username:
            return ""
        
        msg = f"\n🎉 欢迎回来，{username}!\n"
        
        if user_info:
            if user_info.get("name"):
                msg += f"👤 {user_info['name']}\n"
            if user_info.get("company"):
                msg += f"🏢 {user_info['company']}\n"
            if user_info.get("public_repos"):
                msg += f"📦 Public repos: {user_info['public_repos']}\n"
        
        return msg


def get_github_cli() -> GitHubCLIIntegration:
    """获取全局 GitHub CLI 集成实例"""
    if not hasattr(get_github_cli, '_instance'):
        get_github_cli._instance = GitHubCLIIntegration()
    return get_github_cli._instance


if __name__ == "__main__":
    gh = GitHubCLIIntegration()
    
    print("GitHub CLI 集成测试")
    print("=" * 50)
    
    # 检查是否认证
    if gh.is_authenticated():
        print(f"✓ 已认证: {gh.get_current_user()}")
        
        # 获取用户信息
        user_info = gh.get_user_info()
        if user_info:
            print(f"👤 用户名: {user_info['username']}")
            print(f"📝 名字: {user_info.get('name', 'N/A')}")
            print(f"🏢 公司: {user_info.get('company', 'N/A')}")
    else:
        print("✗ 未认证")
        print("\n请使用以下命令登录:")
        print("  gh auth login")
