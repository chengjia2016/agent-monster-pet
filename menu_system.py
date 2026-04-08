#!/usr/bin/env python3
"""
Agent Monster Interactive Menu System
提供交互式菜单让用户可以在OpenCode/Claude Code中轻松操作游戏
"""

import json
from pathlib import Path
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, asdict
from enum import Enum
import os

from user_manager import UserManager
from economy_manager import EconomyManager
from shop_manager import Shop
from onboarding_manager import OnboardingManager


class MenuType(Enum):
    """菜单类型"""
    MAIN = "main"
    ACCOUNT = "account"
    SHOP = "shop"
    INVENTORY = "inventory"
    BATTLE = "battle"
    SETTINGS = "settings"
    HELP = "help"


@dataclass
class MenuSession:
    """菜单会话数据"""
    user_id: Optional[str] = None
    github_login: Optional[str] = None
    current_menu: MenuType = MenuType.MAIN
    last_action: Optional[str] = None
    history: List[str] = None
    
    def __post_init__(self):
        if self.history is None:
            self.history = []


class MenuManager:
    """管理交互式菜单系统"""
    
    def __init__(self, data_dir: str = ".monster"):
        self.data_dir = Path(data_dir)
        self.user_manager = UserManager(data_dir)
        self.economy_manager = EconomyManager(data_dir)
        self.shop = Shop(data_dir)
        self.onboarding = OnboardingManager(data_dir)
        
        # 菜单会话存储
        self.sessions_file = self.data_dir / "menu_sessions.json"
        self.sessions: Dict[str, MenuSession] = self._load_sessions()
        
    def _load_sessions(self) -> Dict[str, MenuSession]:
        """加载菜单会话"""
        if self.sessions_file.exists():
            try:
                with open(self.sessions_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    sessions = {}
                    for key, val in data.items():
                        # 转换current_menu字符串为MenuType
                        if isinstance(val.get("current_menu"), str):
                            try:
                                val["current_menu"] = MenuType[val["current_menu"].upper()]
                            except:
                                val["current_menu"] = MenuType.MAIN
                        
                        session = MenuSession(**val)
                        sessions[key] = session
                    return sessions
            except Exception as e:
                print(f"加载会话错误: {e}", file=__import__('sys').stderr)
        return {}
    
    def _save_sessions(self):
        """保存菜单会话"""
        self.data_dir.mkdir(parents=True, exist_ok=True)
        sessions_dict = {}
        for key, session in self.sessions.items():
            # 转换为可序列化的字典
            data = asdict(session)
            data["current_menu"] = session.current_menu.value
            sessions_dict[key] = data
        
        with open(self.sessions_file, "w", encoding="utf-8") as f:
            json.dump(sessions_dict, f, indent=2, ensure_ascii=False)
    
    def _find_user_by_login(self, github_login: str):
        """通过登录名查找用户"""
        users = self.user_manager.list_users()
        for user in users:
            if user.github_login == github_login:
                return user
        return None
    
    def start_session(self, github_login: str) -> MenuSession:
        """启动菜单会话"""
        session_key = github_login
        
        # 查找或创建用户
        user = self._find_user_by_login(github_login)
        
        if not user:
            # 创建新用户
            github_id = hash(github_login) % (10**9)
            success, user, message = self.onboarding.register_from_github(
                github_login=github_login,
                github_id=github_id
            )
            if not success:
                return None
        
        session = MenuSession(
            user_id=user.user_id,
            github_login=user.github_login,
            current_menu=MenuType.MAIN
        )
        
        self.sessions[session_key] = session
        self._save_sessions()
        return session
    
    def get_session(self, github_login: str) -> Optional[MenuSession]:
        """获取菜单会话"""
        return self.sessions.get(github_login)
    
    def update_menu(self, github_login: str, menu_type: MenuType):
        """更新菜单"""
        session = self.sessions.get(github_login)
        if session:
            session.current_menu = menu_type
            self._save_sessions()
     
    def render_main_menu(self, github_login: str) -> Tuple[str, List[Tuple[str, str]]]:
        """渲染主菜单"""
        session = self.sessions.get(github_login)
        if not session:
            return "❌ 会话已过期", []
        
        user = self._find_user_by_login(github_login)
        account = self.economy_manager.get_account(user.user_id)
        
        menu_text = f"""
╔════════════════════════════════════════╗
║     🎮 Agent Monster 主菜单             ║
║     {github_login:<30} ║
╚════════════════════════════════════════╝

💰 余额: {account.balance if account else 0} 精灵币
👤 账户等级: 新手

请选择操作:
"""
        
        options = [
            ("1", "👤 账户信息 - 查看个人资料和统计"),
            ("2", "🏪 商店 - 购买物品"),
            ("3", "📦 背包 - 查看物品清单"),
            ("4", "⚔️ 对战 - 与其他玩家对战"),
            ("5", "🎰 精灵 - 管理你的精灵"),
            ("6", "⚙️ 设置 - 游戏设置"),
            ("7", "❓ 帮助 - 查看帮助信息"),
            ("0", "🚪 退出 - 保存并退出游戏"),
        ]
        
        for code, desc in options:
            menu_text += f"  {code}. {desc}\n"
        
        return menu_text, options
     
    def render_account_menu(self, github_login: str) -> Tuple[str, List[Tuple[str, str]]]:
        """渲染账户菜单"""
        user = self._find_user_by_login(github_login)
        account = self.economy_manager.get_account(user.user_id)
        
        # 计算统计数据
        total_earned = sum(t.amount for t in (account.transactions or []) if t.trans_type.value == "income")
        total_spent = sum(t.amount for t in (account.transactions or []) if t.trans_type.value == "expense")
        
        menu_text = f"""
╔════════════════════════════════════════╗
║     👤 账户信息                         ║
╚════════════════════════════════════════╝

用户名: {user.github_login}
GitHub ID: {user.github_id}
加入时间: {user.registered_at}

💰 账户统计:
  当前余额: {account.balance if account else 0} 精灵币
  总收入: {total_earned} 精灵币
  总支出: {total_spent} 精灵币
  交易次数: {len(account.transactions) if account else 0}

📊 最近5笔交易:
"""
        
        if account and account.transactions:
            for tx in account.transactions[-5:]:
                menu_text += f"  • {tx.trans_type.value}: {tx.amount} coins - {tx.created_at}\n"
        else:
            menu_text += "  暂无交易记录\n"
        
        options = [
            ("1", "🔄 刷新 - 更新账户信息"),
            ("2", "📊 详细统计 - 查看详细的财务报表"),
            ("0", "← 返回 - 返回主菜单"),
        ]
        
        for code, desc in options:
            menu_text += f"\n  {code}. {desc}"
        
        return menu_text, options
    
    def render_shop_menu(self, github_login: str) -> Tuple[str, List[Tuple[str, str]]]:
        """渲染商店菜单"""
        items = self.shop.list_items()
        
        menu_text = """
╔════════════════════════════════════════╗
║     🏪 精灵商店                         ║
╚════════════════════════════════════════╝

可购买物品:

"""
        
        options = []
        for idx, item in enumerate(items, 1):
            menu_text += f"  {idx}. {item.name}\n"
            menu_text += f"     价格: {item.price} 精灵币 | 库存: {item.stock}\n"
            menu_text += f"     描述: {item.description}\n\n"
            options.append((str(idx), f"购买 {item.name}"))
        
        options.append(("0", "← 返回 - 返回主菜单"))
        
        menu_text += "\n请选择购买的物品编号 (输入编号数字):"
        for code, desc in options:
            menu_text += f"\n  {code}. {desc}"
        
        return menu_text, options
    
    def render_inventory_menu(self, github_login: str) -> Tuple[str, List[Tuple[str, str]]]:
        """渲染背包菜单"""
        user = self._find_user_by_login(github_login)
        inventory = self.shop.get_user_inventory(user.user_id)
        
        menu_text = """
╔════════════════════════════════════════╗
║     📦 我的背包                         ║
╚════════════════════════════════════════╝

拥有物品:

"""
        
        if not inventory:
            menu_text += "  背包为空\n"
        else:
            total_items = 0
            for item_id, item_data in inventory.items():
                # Handle both old format (int) and new format (dict)
                if isinstance(item_data, dict):
                    quantity = item_data.get("quantity", 0)
                    item_name = item_data.get("item", {}).get("name", item_id)
                else:
                    quantity = item_data
                    item = self.shop.get_item(item_id)
                    item_name = item.name if item else item_id
                
                menu_text += f"  • {item_name} x{quantity}\n"
                total_items += quantity
            menu_text += f"\n总物品数: {total_items}\n"
        
        options = [
            ("1", "🔄 刷新 - 刷新物品列表"),
            ("0", "← 返回 - 返回主菜单"),
        ]
        
        for code, desc in options:
            menu_text += f"\n  {code}. {desc}"
        
        return menu_text, options
    
    def render_help_menu(self) -> Tuple[str, List[Tuple[str, str]]]:
        """渲染帮助菜单"""
        menu_text = """
╔════════════════════════════════════════╗
║     ❓ 帮助                             ║
╚════════════════════════════════════════╝

🎮 Agent Monster 游戏指南:

1. 新用户注册:
   • 输入你的GitHub用户名即可注册
   • 初始获得100精灵币 + 启动物品
   • 获得1只小黄鸭启动精灵 + 1个孵化蛋

2. 经济系统:
   • 在商店购买各种道具
   • 食物交易需要支付5%的手续费
   • 拍卖行销售扣除10%的手续费

3. 物品种类:
   • 精灵球 (Poke Ball) - 用于捕捉精灵
   • 种子 (Seeds) - 用于种植
   • 药剂 (Potions) - 恢复精灵体力
   • 复活液 (Revive) - 复活被击败的精灵
   • 增强剂 (Boost) - 临时增强属性

4. 对战系统:
   • 挑战其他玩家的精灵
   • 胜者获得精灵币奖励
   • 败者失去部分精灵币

5. 背包管理:
   • 查看所有拥有的物品
   • 使用物品来帮助精灵
   • 物品可以交易或出售

💡 提示:
   • 定期检查商店的库存
   • 参与对战获得更多奖励
   • 收集不同类型的精灵和物品

"""
        
        options = [
            ("0", "← 返回 - 返回主菜单"),
        ]
        
        for code, desc in options:
            menu_text += f"\n  {code}. {desc}"
        
        return menu_text, options
    
    def handle_action(self, github_login: str, action: str) -> Tuple[bool, str]:
        """
        处理用户操作
        返回: (继续菜单, 返回消息)
        """
        session = self.sessions.get(github_login)
        if not session:
            return False, "❌ 会话已过期"
        
        current_menu = session.current_menu
        
        if current_menu == MenuType.MAIN:
            if action == "1":
                session.current_menu = MenuType.ACCOUNT
                return True, "切换到账户菜单"
            elif action == "2":
                session.current_menu = MenuType.SHOP
                return True, "切换到商店菜单"
            elif action == "3":
                session.current_menu = MenuType.INVENTORY
                return True, "切换到背包菜单"
            elif action == "4":
                return True, "对战功能正在开发中"
            elif action == "5":
                return True, "精灵管理功能正在开发中"
            elif action == "6":
                session.current_menu = MenuType.SETTINGS
                return True, "切换到设置菜单"
            elif action == "7":
                session.current_menu = MenuType.HELP
                return True, "切换到帮助菜单"
            elif action == "0":
                self._save_sessions()
                return False, "✅ 游戏已保存,欢迎下次游玩!"
            else:
                return True, "❌ 无效选择,请重试"
        
        elif current_menu == MenuType.ACCOUNT:
            if action == "0":
                session.current_menu = MenuType.MAIN
                return True, "返回主菜单"
            else:
                return True, "选项暂未实现"
        
        elif current_menu == MenuType.SHOP:
            if action == "0":
                session.current_menu = MenuType.MAIN
                return True, "返回主菜单"
            else:
                try:
                    choice = int(action)
                    items = list(self.shop.list_items())
                    if 1 <= choice <= len(items):
                        item = items[choice - 1]
                        # Process purchase
                        user = self.user_manager.get_user_by_github_login(github_login)
                        if user:
                            account = self.economy_manager.get_account(user.user_id)
                            if account and account.has_sufficient_balance(item.price):
                                success = self.economy_manager.purchase_item(user.user_id, item.name, item.price, item.item_id)
                                if success:
                                    new_balance = self.economy_manager.get_account(user.user_id).balance
                                    return True, f"""✅ 购买成功!
===
物品: {item.name}
价格: {item.price} 精灵币
新余额: {new_balance} 精灵币

请选择返回菜单 (0)"""
                                else:
                                    return True, "❌ 购买失败"
                            else:
                                return True, f"❌ 余额不足。需要 {item.price} 精灵币，当前余额 {account.balance if account else 0} 精灵币"
                        else:
                            return True, "❌ 用户不存在"
                    else:
                        return True, "❌ 无效选择"
                except Exception as e:
                    return True, f"❌ 购买出错: {str(e)}"
        
        elif current_menu == MenuType.HELP:
            if action == "0":
                session.current_menu = MenuType.MAIN
                return True, "返回主菜单"
            else:
                return True, "❌ 无效选择"
        
        else:
            if action == "0":
                session.current_menu = MenuType.MAIN
                return True, "返回主菜单"
            else:
                return True, "❌ 无效选择"
    
    def get_menu_display(self, github_login: str) -> Tuple[str, List[Tuple[str, str]]]:
        """获取当前菜单显示内容"""
        session = self.sessions.get(github_login)
        if not session:
            return "❌ 会话已过期", []
        
        if session.current_menu == MenuType.MAIN:
            return self.render_main_menu(github_login)
        elif session.current_menu == MenuType.ACCOUNT:
            return self.render_account_menu(github_login)
        elif session.current_menu == MenuType.SHOP:
            return self.render_shop_menu(github_login)
        elif session.current_menu == MenuType.INVENTORY:
            return self.render_inventory_menu(github_login)
        elif session.current_menu == MenuType.HELP:
            return self.render_help_menu()
        else:
            return "❌ 未知菜单", []
