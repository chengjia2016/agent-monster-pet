#!/usr/bin/env python3
"""
MCP Server Account Management Commands
Uses Judge Server for centralized user account, pokemon, and item management
"""

from judge_server_client import get_judge_server_client
from user_manager import UserManager

def cmd_account_info(github_username: str) -> str:
    """Get user account info from Judge Server"""
    try:
        client = get_judge_server_client()
        user_manager = UserManager()
        
        # Find user locally to get github_id
        user = None
        for u in user_manager.list_users():
            if u.github_login == github_username:
                user = u
                break
        
        if not user:
            return f"❌ User '{github_username}' not found"
        
        # Get account from Judge Server
        account = client.get_user_account(user.github_id)
        if not account:
            return f"❌ Account not found on Judge Server"
        
        transactions = client.get_user_transactions(user.github_id, limit=5)
        
        trans_text = "最近交易:\n"
        for tx in transactions:
            trans_text += f"  • {tx['type']}: {tx['amount']:+.0f} 精灵币 - {tx['description']}\n"
        
        return f"""👤 账户信息
===
用户名: {account.github_login}
GitHub ID: {account.github_id}

💰 账户余额: {account.balance:.1f} 精灵币
邮箱: {account.email or '未设置'}

{trans_text}"""
    except Exception as e:
        return f"❌ Error: {str(e)}"


def cmd_add_balance(github_username: str, amount: float, reason: str = "") -> str:
    """Add balance to user account on Judge Server"""
    try:
        client = get_judge_server_client()
        user_manager = UserManager()
        
        # Find user locally
        user = None
        for u in user_manager.list_users():
            if u.github_login == github_username:
                user = u
                break
        
        if not user:
            return f"❌ User '{github_username}' not found"
        
        # Update balance on Judge Server
        success = client.update_user_balance(user.github_id, amount, reason or "手动调整")
        if not success:
            return f"❌ Failed to update balance on Judge Server"
        
        # Get new balance
        new_balance = client.get_user_balance(user.github_id)
        
        return f"""✅ 余额已更新
===
用户: {github_username}
变化: {amount:+.1f} 精灵币
原因: {reason or '手动调整'}
新余额: {new_balance:.1f} 精灵币"""
    except Exception as e:
        return f"❌ Error: {str(e)}"


def cmd_list_pokemons(github_username: str) -> str:
    """List user's pokemons from Judge Server"""
    try:
        client = get_judge_server_client()
        user_manager = UserManager()
        
        # Find user locally
        user = None
        for u in user_manager.list_users():
            if u.github_login == github_username:
                user = u
                break
        
        if not user:
            return f"❌ User '{github_username}' not found"
        
        # Get pokemons from Judge Server
        pokemons = client.get_user_pokemons(user.github_id)
        
        if not pokemons:
            return f"📦 {github_username} 还没有精灵"
        
        pokemon_list = "🎮 我的精灵:\n"
        for i, pokemon in enumerate(pokemons, 1):
            pokemon_list += f"  {i}. {pokemon['pet_name']} ({pokemon['species']}) - Lv.{pokemon['level']}\n"
        
        return f"""✅ 精灵列表
===
用户: {github_username}
总数: {len(pokemons)}

{pokemon_list}"""
    except Exception as e:
        return f"❌ Error: {str(e)}"


def cmd_add_pokemon(github_username: str, pet_id: str, pet_name: str, 
                   level: int = 1, species: str = "") -> str:
    """Add a pokemon to user's collection on Judge Server"""
    try:
        client = get_judge_server_client()
        user_manager = UserManager()
        
        # Find user locally
        user = None
        for u in user_manager.list_users():
            if u.github_login == github_username:
                user = u
                break
        
        if not user:
            return f"❌ User '{github_username}' not found"
        
        # Add pokemon to Judge Server
        success = client.add_user_pokemon(user.github_id, pet_id, pet_name, level, species)
        if not success:
            return f"❌ Failed to add pokemon to Judge Server"
        
        return f"""✅ 精灵已添加
===
用户: {github_username}
精灵: {pet_name}
物种: {species or '未知'}
等级: {level}"""
    except Exception as e:
        return f"❌ Error: {str(e)}"


def cmd_list_inventory(github_username: str) -> str:
    """List user's inventory from Judge Server"""
    try:
        client = get_judge_server_client()
        user_manager = UserManager()
        
        # Find user locally
        user = None
        for u in user_manager.list_users():
            if u.github_login == github_username:
                user = u
                break
        
        if not user:
            return f"❌ User '{github_username}' not found"
        
        # Get inventory from Judge Server
        items = client.get_user_inventory(user.github_id)
        
        if not items:
            return f"📦 {github_username} 的背包是空的"
        
        items_list = "📦 我的物品:\n"
        total_value = 0
        for i, item in enumerate(items, 1):
            quantity = item.get('quantity', 0)
            items_list += f"  {i}. {item['item_name']} × {quantity}\n"
        
        return f"""✅ 物品清单
===
用户: {github_username}
总数: {len(items)}

{items_list}"""
    except Exception as e:
        return f"❌ Error: {str(e)}"


def cmd_add_item(github_username: str, item_id: str, item_name: str, 
                quantity: int = 1) -> str:
    """Add item to user's inventory on Judge Server"""
    try:
        client = get_judge_server_client()
        user_manager = UserManager()
        
        # Find user locally
        user = None
        for u in user_manager.list_users():
            if u.github_login == github_username:
                user = u
                break
        
        if not user:
            return f"❌ User '{github_username}' not found"
        
        # Add item to Judge Server
        success = client.add_user_item(user.github_id, item_id, item_name, quantity)
        if not success:
            return f"❌ Failed to add item to Judge Server"
        
        return f"""✅ 物品已添加
===
用户: {github_username}
物品: {item_name}
数量: {quantity}"""
    except Exception as e:
        return f"❌ Error: {str(e)}"


def cmd_judge_server_status() -> str:
    """Check Judge Server health status"""
    try:
        client = get_judge_server_client()
        healthy = client.health_check()
        
        if healthy:
            return "✅ Judge Server 状态: 正常运行 ✓"
        else:
            return "⚠️ Judge Server 状态: 离线或不可用"
    except Exception as e:
        return f"⚠️ Judge Server 连接失败: {str(e)}"
