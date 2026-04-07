#!/usr/bin/env python3
"""
Test cases for the interactive menu system
"""

import pytest
import json
from pathlib import Path
from menu_system import MenuManager, MenuType, MenuSession


class TestMenuSystem:
    """Test the interactive menu system"""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test environment"""
        self.test_dir = str(tmp_path)
        self.menu_manager = MenuManager(self.test_dir)
    
    def test_menu_session_creation(self):
        """Test creating a new menu session"""
        session = self.menu_manager.start_session("test_user")
        
        assert session is not None
        assert session.github_login == "test_user"
        assert session.current_menu == MenuType.MAIN
    
    def test_session_persistence(self):
        """Test that sessions persist to disk"""
        self.menu_manager.start_session("persistent_user")
        
        # Create a new manager instance to load from disk
        manager2 = MenuManager(self.test_dir)
        session = manager2.get_session("persistent_user")
        
        assert session is not None
        assert session.github_login == "persistent_user"
    
    def test_menu_navigation(self):
        """Test navigating between menus"""
        self.menu_manager.start_session("nav_user")
        
        # Navigate to account menu
        self.menu_manager.update_menu("nav_user", MenuType.ACCOUNT)
        session = self.menu_manager.get_session("nav_user")
        assert session.current_menu == MenuType.ACCOUNT
        
        # Navigate to shop menu
        self.menu_manager.update_menu("nav_user", MenuType.SHOP)
        session = self.menu_manager.get_session("nav_user")
        assert session.current_menu == MenuType.SHOP
    
    def test_main_menu_render(self):
        """Test rendering the main menu"""
        self.menu_manager.start_session("menu_user")
        menu_text, options = self.menu_manager.render_main_menu("menu_user")
        
        assert "🎮 Agent Monster 主菜单" in menu_text
        assert len(options) == 8
        assert options[0][0] == "1"
        assert "账户信息" in options[0][1]
    
    def test_account_menu_render(self):
        """Test rendering the account menu"""
        self.menu_manager.start_session("account_user")
        menu_text, options = self.menu_manager.render_account_menu("account_user")
        
        assert "👤 账户信息" in menu_text
        assert "account_user" in menu_text
        assert len(options) >= 2
    
    def test_shop_menu_render(self):
        """Test rendering the shop menu"""
        self.menu_manager.start_session("shop_user")
        menu_text, options = self.menu_manager.render_shop_menu("shop_user")
        
        assert "🏪 精灵商店" in menu_text
        assert "Poké Ball" in menu_text
        assert len(options) > 1
    
    def test_inventory_menu_render(self):
        """Test rendering the inventory menu"""
        self.menu_manager.start_session("inv_user")
        menu_text, options = self.menu_manager.render_inventory_menu("inv_user")
        
        assert "📦 我的背包" in menu_text
    
    def test_help_menu_render(self):
        """Test rendering the help menu"""
        menu_text, options = self.menu_manager.render_help_menu()
        
        assert "❓ 帮助" in menu_text
        assert "新用户注册" in menu_text
        assert "经济系统" in menu_text
    
    def test_action_handling_main_menu(self):
        """Test handling actions in main menu"""
        self.menu_manager.start_session("action_user")
        
        # Select account menu
        continue_menu, message = self.menu_manager.handle_action("action_user", "1")
        assert continue_menu is True
        session = self.menu_manager.get_session("action_user")
        assert session.current_menu == MenuType.ACCOUNT
    
    def test_action_handling_exit(self):
        """Test handling exit action"""
        self.menu_manager.start_session("exit_user")
        
        # Select exit
        continue_menu, message = self.menu_manager.handle_action("exit_user", "0")
        assert continue_menu is False
        assert "保存" in message
    
    def test_action_handling_invalid(self):
        """Test handling invalid actions"""
        self.menu_manager.start_session("invalid_user")
        
        # Select invalid option
        continue_menu, message = self.menu_manager.handle_action("invalid_user", "99")
        assert continue_menu is True
        assert "无效" in message or "暂未实现" in message
    
    def test_menu_display(self):
        """Test getting current menu display"""
        self.menu_manager.start_session("display_user")
        
        menu_text, options = self.menu_manager.get_menu_display("display_user")
        assert menu_text is not None
        assert len(options) > 0
        assert "🎮" in menu_text or "Agent" in menu_text
    
    def test_multiple_users(self):
        """Test handling multiple users simultaneously"""
        session1 = self.menu_manager.start_session("user1")
        session2 = self.menu_manager.start_session("user2")
        
        assert session1.github_login == "user1"
        assert session2.github_login == "user2"
        
        # Navigate user1 to shop
        self.menu_manager.update_menu("user1", MenuType.SHOP)
        # Keep user2 in main
        
        s1 = self.menu_manager.get_session("user1")
        s2 = self.menu_manager.get_session("user2")
        
        assert s1.current_menu == MenuType.SHOP
        assert s2.current_menu == MenuType.MAIN
    
    def test_menu_session_format(self):
        """Test MenuSession data structure"""
        session = MenuSession(
            user_id="test_id",
            github_login="test_login",
            current_menu=MenuType.ACCOUNT
        )
        
        assert session.user_id == "test_id"
        assert session.github_login == "test_login"
        assert session.current_menu == MenuType.ACCOUNT
        assert session.history == []


class TestMenuIntegration:
    """Integration tests for menu system"""
    
    @pytest.fixture(autouse=True)
    def setup(self, tmp_path):
        """Setup test environment"""
        self.test_dir = str(tmp_path)
        self.menu_manager = MenuManager(self.test_dir)
    
    def test_full_user_flow(self):
        """Test a complete user flow through the menu"""
        # 1. Start session
        session = self.menu_manager.start_session("full_user")
        assert session is not None
        
        # 2. Display main menu
        menu_text, options = self.menu_manager.get_menu_display("full_user")
        assert "Agent Monster" in menu_text
        
        # 3. Navigate to account
        self.menu_manager.handle_action("full_user", "1")
        menu_text, options = self.menu_manager.get_menu_display("full_user")
        assert "账户信息" in menu_text
        
        # 4. Return to main
        self.menu_manager.handle_action("full_user", "0")
        menu_text, options = self.menu_manager.get_menu_display("full_user")
        assert "Agent Monster" in menu_text
        
        # 5. Navigate to shop
        self.menu_manager.handle_action("full_user", "2")
        menu_text, options = self.menu_manager.get_menu_display("full_user")
        assert "商店" in menu_text
        
        # 6. Navigate to help
        self.menu_manager.handle_action("full_user", "0")
        self.menu_manager.handle_action("full_user", "7")
        menu_text, options = self.menu_manager.get_menu_display("full_user")
        assert "帮助" in menu_text
    
    def test_session_recovery(self):
        """Test that sessions can be recovered from disk"""
        # Create and save session
        self.menu_manager.start_session("recovery_user")
        self.menu_manager.update_menu("recovery_user", MenuType.SHOP)
        
        # Create new manager to simulate restart
        manager2 = MenuManager(self.test_dir)
        session = manager2.get_session("recovery_user")
        
        assert session is not None
        assert session.github_login == "recovery_user"
        assert session.current_menu == MenuType.SHOP


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
