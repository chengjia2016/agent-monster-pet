#!/usr/bin/env python3
"""
Agent Monster MCP Server
STDIO-based MCP server for Claude Code integration
"""

import json
import subprocess
import sys
import os
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
MONSTER_DIR = SCRIPT_DIR / ".monster"
CONFIG_FILE = MONSTER_DIR / "config.json"
SOUL_FILE = MONSTER_DIR / "pet.soul"

JUDGE_SERVER = "http://agentmonster.openx.pro:10000"

EGG_POOL = ["Bulbasaur", "Charmander", "Squirtle", "Pikachu", "Clefairy", "Vulpix", "Oddish"]


def check_dependencies():
    """Check if required dependencies are installed"""
    missing = []

    try:
        import yaml
    except ImportError:
        missing.append("pyyaml")

    if missing:
        print(f"Missing dependencies: {', '.join(missing)}", file=sys.stderr)
        print(f"Install with: pip install {' '.join(missing)}", file=sys.stderr)
        return False
    return True


def load_json(path):
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return None


def save_json(path, data):
    MONSTER_DIR.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def call_judge_server(endpoint, data):
    """Call judge server API for validation"""
    import urllib.request
    import urllib.error

    try:
        url = f"{JUDGE_SERVER}{endpoint}"
        req = urllib.request.Request(
            url,
            data=json.dumps(data).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST"
        )
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"success": False, "error": str(e), "judge": "unavailable"}


# ========== User & Economy Integration Commands ==========

def _find_user_by_login(user_manager, github_username):
    """Helper to find user by GitHub login"""
    users = user_manager.list_users()
    for user in users:
        if user.github_login == github_username:
            return user
    return None


def cmd_user_register(github_username):
    """Register a new user with GitHub username"""
    try:
        from onboarding_manager import OnboardingManager
        
        onboarding = OnboardingManager(str(MONSTER_DIR))
        
        # Register user and initialize (using github_username as both login and ID for demo)
        # In production, this would come from GitHub OAuth
        github_id = hash(github_username) % (10**9)  # Simple ID generation
        success, user, message = onboarding.register_from_github(
            github_login=github_username,
            github_id=github_id
        )
        
        if success:
            return f"""✅ User Registration Complete!
===
Username: {user.github_login}
GitHub ID: {user.github_id}
Joined: {user.registered_at}

🎁 Initial Rewards:
- 100 Elemental Coins
- 3 Poke Balls
- 2 Grass Seeds  
- 1 Healing Potion
- 1 Starter Pokemon (Little Yellow Duck)
- 1 Hatching Egg

Ready to begin your adventure!
"""
        else:
            return f"❌ Registration failed: {message}"
    except Exception as e:
        return f"❌ Registration failed: {str(e)}"


def cmd_user_info(github_username=""):
    """Get current user account information"""
    try:
        from user_manager import UserManager
        from economy_manager import EconomyManager
        
        user_manager = UserManager(str(MONSTER_DIR))
        economy_manager = EconomyManager(str(MONSTER_DIR))
        
        if not github_username:
            github_username = "current_user"
        
        user = _find_user_by_login(user_manager, github_username)
        if not user:
            return f"❌ User '{github_username}' not found"
        
        account = economy_manager.get_account(user.user_id)
        
        # Calculate totals from transactions
        total_spent = 0
        total_earned = 0
        if account:
            for transaction in account.transactions:
                if transaction.amount < 0:
                    total_spent += abs(transaction.amount)
                else:
                    total_earned += transaction.amount
        
        return f"""👤 User Profile
===
Username: {user.github_login}
GitHub ID: {user.github_id}
Joined: {user.registered_at}
Last Login: {user.last_login}

💰 Account Info:
Balance: {account.balance if account else 0} Elemental Coins
Total Spent: {total_spent} Elemental Coins
Total Earned: {total_earned} Elemental Coins
Transactions: {len(account.transactions) if account else 0}
"""
    except Exception as e:
        return f"❌ Error getting user info: {str(e)}"


def cmd_shop_list():
    """List all available items in the shop"""
    try:
        from shop_manager import Shop
        
        shop = Shop(str(MONSTER_DIR))
        items = shop.list_items()
        
        output = "🏪 Shop Inventory\n===\n"
        for item in items:
            output += f"\n{item.name}\n"
            output += f"  ID: {item.item_id}\n"
            output += f"  Price: {item.price} Coins\n"
            output += f"  Stock: {item.stock}\n"
            output += f"  Desc: {item.description}\n"
        
        return output
    except Exception as e:
        return f"❌ Error listing shop: {str(e)}"


def cmd_shop_buy(github_username, item_id, quantity=1):
    """Buy an item from the shop"""
    try:
        from user_manager import UserManager
        from economy_manager import EconomyManager
        from shop_manager import Shop
        
        user_manager = UserManager(str(MONSTER_DIR))
        economy_manager = EconomyManager(str(MONSTER_DIR))
        shop = Shop(str(MONSTER_DIR))
        
        user = _find_user_by_login(user_manager, github_username)
        if not user:
            return f"❌ User '{github_username}' not found"
        
        # Get item from shop
        item = shop.get_item(item_id)
        if not item:
            return f"❌ Item '{item_id}' not found in shop"
        
        # Calculate total cost
        total_cost = item.price * quantity
        
        # Try to purchase
        account = economy_manager.get_account(user.user_id)
        if not account:
            return "❌ Account not found"
        
        if not account.has_sufficient_balance(total_cost):
            return f"❌ Insufficient balance. Need {total_cost} coins, have {account.balance} coins"
        
        # Process purchase
        success = economy_manager.purchase_item(user.user_id, item.name, total_cost, item_id)
        
        if success:
            new_balance = economy_manager.get_account(user.user_id).balance
            return f"""✅ Purchase Successful!
===
Item: {item.name}
Quantity: {quantity}
Cost: {total_cost} Coins
New Balance: {new_balance} Coins
"""
        else:
            return "❌ Purchase failed"
    except Exception as e:
        return f"❌ Error purchasing item: {str(e)}"


def cmd_inventory_view(github_username):
    """View user's inventory"""
    try:
        from user_manager import UserManager
        from shop_manager import Shop
        
        user_manager = UserManager(str(MONSTER_DIR))
        shop = Shop(str(MONSTER_DIR))
        
        user = _find_user_by_login(user_manager, github_username)
        if not user:
            return f"❌ User '{github_username}' not found"
        
        inventory = shop.get_user_inventory(user.user_id)
        
        if not inventory:
            return "📦 Your inventory is empty"
        
        output = f"📦 Inventory for {github_username}\n===\n"
        total_items = 0
        for item_id, item_info in inventory.items():
            if isinstance(item_info, dict):
                # New format: item_info contains 'item', 'quantity', 'total_value'
                item_name = item_info.get('item', {}).get('name', item_id)
                quantity = item_info.get('quantity', 0)
                total_value = item_info.get('total_value', 0)
                output += f"\n{item_name} x{quantity}\n"
                output += f"  ID: {item_id}\n"
                output += f"  Total Value: {total_value} Coins\n"
                total_items += quantity
            else:
                # Old format: item_info is just the quantity
                item = shop.get_item(item_id)
                if item:
                    output += f"\n{item.name} x{item_info}\n"
                    output += f"  ID: {item_id}\n"
                    total_items += item_info
        
        output += f"\n\nTotal Items: {total_items}\n"
        return output
    except Exception as e:
        return f"❌ Error viewing inventory: {str(e)}"


def cmd_account_stats(github_username):
    """Get detailed account statistics"""
    try:
        from user_manager import UserManager
        from economy_manager import EconomyManager
        
        user_manager = UserManager(str(MONSTER_DIR))
        economy_manager = EconomyManager(str(MONSTER_DIR))
        
        user = _find_user_by_login(user_manager, github_username)
        if not user:
            return f"❌ User '{github_username}' not found"
        
        account = economy_manager.get_account(user.user_id)
        if not account:
            return f"❌ No account found for {github_username}"
        
        # Calculate totals from transactions
        total_earned = 0
        total_spent = 0
        for tx in account.transactions:
            if tx.amount < 0:
                total_spent += abs(tx.amount)
            else:
                total_earned += tx.amount
        
        output = f"📊 Account Statistics for {github_username}\n===\n"
        output += f"\nBalance: {account.balance} Coins\n"
        output += f"Total Income: {total_earned} Coins\n"
        output += f"Total Expenses: {total_spent} Coins\n"
        output += f"Transaction Count: {len(account.transactions)}\n"
        
        output += f"\n\nRecent Transactions (Last 5):\n"
        for tx in account.transactions[-5:]:
            output += f"\n  {tx.description}: {tx.amount} coins - {tx.created_at}\n"
        
        return output
    except Exception as e:
        return f"❌ Error getting account stats: {str(e)}"


# ========== Interactive Menu System Commands ==========

def cmd_menu_start(github_username):
    """启动交互式菜单系统"""
    try:
        from menu_system import MenuManager
        
        menu_manager = MenuManager(str(MONSTER_DIR))
        session = menu_manager.start_session(github_username)
        
        if not session:
            return f"❌ 无法创建会话"
        
        # 获取主菜单
        menu_text, options = menu_manager.get_menu_display(github_username)
        
        return menu_text
    except Exception as e:
        return f"❌ 启动菜单失败: {str(e)}"


def cmd_menu_action(github_username, action):
    """在菜单中执行操作"""
    try:
        from menu_system import MenuManager
        
        menu_manager = MenuManager(str(MONSTER_DIR))
        session = menu_manager.get_session(github_username)
        
        if not session:
            return f"❌ 会话不存在,请先调用 menu_start"
        
        # 处理动作
        continue_menu, message = menu_manager.handle_action(github_username, action)
        
        # 获取新菜单显示
        menu_text, options = menu_manager.get_menu_display(github_username)
        
        response = f"{message}\n\n{menu_text}"
        
        return response
    except Exception as e:
        import traceback
        tb_str = traceback.format_exc()
        return f"❌ 菜单操作失败: {str(e)}\n\n{tb_str}"


# ========== Slash Commands System ==========

def cmd_slash_help(command_name=""):
    """显示斜杠命令帮助"""
    try:
        from slash_commands import SlashCommandRegistry, format_command_help, format_commands_list
        
        registry = SlashCommandRegistry()
        
        if command_name:
            # 显示特定命令的帮助
            cmd = registry.get_command(command_name)
            if cmd:
                return format_command_help(cmd)
            else:
                # 搜索相似命令
                results = registry.search_commands(command_name)
                if results:
                    output = f"❌ 命令 '{command_name}' 不存在\n\n💡 你是想要以下命令吗？\n"
                    for cmd in results:
                        output += f"  • /monster {cmd.name} - {cmd.description}\n"
                    return output
                else:
                    return f"❌ 命令 '{command_name}' 不存在"
        else:
            # 显示所有命令列表
            return format_commands_list()
    except Exception as e:
        return f"❌ 获取帮助失败: {str(e)}"


def cmd_slash_list():
    """列出所有可用的斜杠命令"""
    try:
        from slash_commands import SlashCommandRegistry
        
        registry = SlashCommandRegistry()
        commands = registry.get_all_commands()
        
        output = """
╔════════════════════════════════════════════╗
║  📋 可用的 /monster 斜杠命令
╚════════════════════════════════════════════╝

"""
        
        for i, cmd in enumerate(commands, 1):
            output += f"{i:2}. /{cmd.name:<25} - {cmd.description}\n"
        
        output += f"""
💡 提示:
  • 输入 /monster help [命令名] 查看详细帮助
  • 在 OpenCode 中输入 /monster 会自动显示命令提示
  • 使用 [Tab] 键可以自动补全命令

例如:
  /monster menu username:alice      (启动菜单)
  /monster shop list                (查看商店)
  /monster balance username:alice   (查看余额)
"""
        
        return output
    except Exception as e:
        return f"❌ 获取命令列表失败: {str(e)}"


def cmd_slash_completions(prefix=""):
     """获取命令自动完成建议"""
     try:
         from slash_commands import SlashCommandRegistry
         
         registry = SlashCommandRegistry()
         completions = registry.get_command_completions(prefix)
         
         if not completions:
             return f"❌ 没有找到以 '{prefix}' 开头的命令"
         
         output = f"""
╔════════════════════════════════════════════╗
║  🔍 '/monster {prefix}' 的自动完成建议
╚════════════════════════════════════════════╝

"""
         
         for comp in completions:
             output += f"• /monster {comp['label']:<20} - {comp['detail']}\n"
         
         return output
     except Exception as e:
         return f"❌ 获取自动完成失败: {str(e)}"


# ========== GitHub CLI Integration ==========

def cmd_simple_start():
    """简化的启动命令 - 自动从 gh cli 获取用户名并启动菜单"""
    try:
        from github_cli_integration import get_github_cli
        from user_manager import UserManager
        from menu_system import MenuManager
        
        # 获取 GitHub CLI 实例
        gh = get_github_cli()
        
        # 检查是否已认证
        if not gh.is_authenticated():
            output = """
╔════════════════════════════════════════════╗
║  🔑 GitHub 登录
╚════════════════════════════════════════════╝

检测到你还未登录 GitHub CLI。

请执行以下命令进行登录:
  
  gh auth login

然后选择:
  - What is your preferred protocol? → HTTPS
  - Authenticate Git with your GitHub credentials? → Yes
  - How would you like to authenticate? → Paste an authentication token

登录完成后，请重新运行 /monster 命令！
"""
            return output
        
        # 获取用户名
        username = gh.get_current_user()
        user_info = gh.get_user_info()
        
        # 确保用户在系统中注册
        user_mgr = UserManager()
        try:
            user = user_mgr.get_user_by_github_id(username)
        except:
            # 如果用户不存在，自动注册
            user = user_mgr.register_user(username)
        
        # 启动菜单
        menu_mgr = MenuManager(str(MONSTER_DIR))
        session = menu_mgr.start_session(username)
        
        if not session:
            return f"❌ 无法创建会话"
        
        # 获取主菜单
        menu_text, options = menu_mgr.get_menu_display(username)
        
        # 构建欢迎消息
        welcome = gh.format_welcome_message()
        
        output = welcome + "\n" + menu_text
        return output
        
    except Exception as e:
        import traceback
        return f"❌ 启动游戏失败: {str(e)}\n\n错误详情:\n{traceback.format_exc()}"


def cmd_init():
    import time
    egg_id = f"egg_{int(time.time())}"
    egg_data = {
        "id": egg_id,
        "owner": "player",
        "start_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": "incubating"
    }
    save_json(MONSTER_DIR / "egg.json", egg_data)
    return f"""🥚 Egg Obtained!
===
Egg ID: {egg_id}
Start Time: {egg_data['start_time']}

The egg is incubating. Use /monster hatch to hatch it!

Longer incubation = more energy = better Pokemon!
"""

def cmd_hatch():
    import time
    egg_file = MONSTER_DIR / "egg.json"
    if not egg_file.exists():
        return "No egg found. Use /monster init first!"
    
    egg_data = load_json(egg_file)
    if egg_data.get("hatched"):
        return "Egg already hatched!"
    
    hatch_result = call_judge_server("/api/egg/incubate", egg_data)
    
    if hatch_result.get("is_valid") and hatch_result.get("hatch_result"):
        result = hatch_result["hatch_result"]
        
        egg_data["hatched"] = True
        egg_data["hatch_result"] = result
        save_json(MONSTER_DIR / "egg.json", egg_data)
        
        pet_data = {
            "metadata": {
                "name": result["pokemon_name"],
                "species": result["pokemon_name"],
                "birth_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                "owner": "player",
                "generation": 1,
                "evolution_stage": 1,
                "avatar": f"\n  {result['pokemon_name']}\n ╭───╮\n│ ◕‿◕ │\n╰─────╯\n"
            },
            "stats": {
                "hp": {"base": 50, "iv": 10, "ev": 0, "exp": 0},
                "attack": {"base": 50, "iv": 10, "ev": 0, "exp": 0},
                "defense": {"base": 50, "iv": 10, "ev": 0, "exp": 0},
                "speed": {"base": 50, "iv": 10, "ev": 0, "exp": 0},
                "armor": {"base": 50, "iv": 10, "ev": 0, "exp": 0},
                "quota": {"base": 50, "iv": 10, "ev": 0, "exp": 0}
            },
            "genes": {
                "logic": {"weight": 0.33, "source_commits": []},
                "creative": {"weight": 0.33, "source_commits": []},
                "speed": {"weight": 0.34, "source_commits": []}
            },
            "battle_history": [],
            "signature": {"algorithm": "RSA-SHA256", "value": "", "keyid": ""}
        }
        
        save_json(SOUL_FILE, pet_data)
        
        return f"""🎉 Egg Hatched!
===
Pokemon: {result['pokemon_name']}
Rarity: {result['rarity']}
Energy: {result['total_energy']}

Gene Changes:
- {result['gene_modifiers'][0]['gene_type']}: {result['gene_modifiers'][0]['old_weight']:.2f} → {result['gene_modifiers'][0]['new_weight']:.2f}
- lucky: {result['gene_modifiers'][1]['old_weight']:.2f} → {result['gene_modifiers'][1]['new_weight']:.2f}
"""
    
    return "Hatch failed: " + str(hatch_result.get("errors", ["Unknown error"]))

def cmd_capture(target_hp, max_hp):
    capture_data = {
        "id": f"capture_{int(time.time())}",
        "capture_id": f"capture_{int(time.time())}",
        "battle_id": f"battle_{int(time.time())}",
        "attacker_id": "player",
        "target_id": "wild_pokemon",
        "target_hp": target_hp,
        "max_hp": max_hp,
        "throw_time": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    
    result = call_judge_server("/api/capture/validate", capture_data)
    
    if result.get("success"):
        return f"🎯 Capture Successful! Wild Pokemon caught!"
    elif result.get("errors"):
        return f"❌ Capture Failed: {result['errors'][0]}"
    else:
        return f"❌ Capture Failed (rate: {result.get('capture_rate', 0):.1%})"


def cmd_status(json_mode=False):
    soul = load_json(SOUL_FILE)
    if not soul:
        if json_mode:
            return json.dumps({"error": "No monster found, run init first"})
        else:
            return "No monster found, run: python monster.py init"

    if json_mode:
        return json.dumps(soul, indent=2, ensure_ascii=False)

    metadata = soul.get("metadata", {})
    stats = soul.get("stats", {})
    base_stats = soul.get("base_stats", {})

    if not base_stats and stats:
        base_stats = {k: v.get("base", 0) for k, v in stats.items()}

    lines = []
    avatar = metadata.get("avatar", "") or soul.get("avatar", "")
    safe_avatar = (
        avatar.encode("ascii", "replace").decode("ascii")
        if avatar
        else "[No Avatar]"
    )

    lines.append(f"\n{safe_avatar}")
    lines.append("=" * 50)
    name = metadata.get("name", soul.get("name", "Unknown"))
    level = metadata.get("generation", soul.get("level", 1))
    lines.append(f"  {name} (Gen.{level})")
    lines.append(f"  Species: {metadata.get('species', 'N/A')}")
    lines.append(f"  Type: {'/'.join(metadata.get('species', []))}")
    lines.append(
        f"  Owner: {metadata.get('owner', 'N/A')}"
    )
    lines.append("=" * 50)

    lines.append("\n[STATS]")
    for stat, val in base_stats.items():
        bar = "#" * (val // 20) + "-" * (12 - val // 20)
        lines.append(f"  {stat.upper():8}: {val:3} [{bar}]")

    if not base_stats and stats:
        for stat, data in stats.items():
            val = data.get("base", 0)
            bar = "#" * (val // 20) + "-" * (12 - val // 20)
            lines.append(f"  {stat.upper():8}: {val:3} [{bar}]")

    battle_history = soul.get("battle_history", [])
    lines.append(
        f"\n[INFO] Battles: {len(battle_history)} | Generation: {metadata.get('generation', 1)}"
    )

    return "\n".join(lines)


def cmd_analyze(days=7):
    try:
        from github_integration import analyze_commit_history
        metrics = analyze_commit_history(days)
        return {
            "success": True,
            "data": {
                "total_commits": metrics.total_commits,
                "recent_7d": metrics.recent_commits_7d,
                "green_ratio": metrics.green_ratio,
                "tech_stack": metrics.tech_stack,
                "fix_count": metrics.fix_keywords_count,
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def cmd_traps(path="."):
    try:
        from battle_logic import LogicTrapDetector
        traps = LogicTrapDetector.scan_for_traps(path)
        return {
            "success": True,
            "data": {
                "traps": [
                    {"type": t.trap_type.value, "file": t.source_file, "power": t.power}
                    for t in traps
                ],
                "count": len(traps),
            }
        }
    except Exception as e:
        return {"success": False, "error": str(e)}


def cmd_duel(target, attack_stack=None):
    try:
        from battle_logic import BattleSimulator

        attacker = load_json(SOUL_FILE)
        if not attacker:
            return {"success": False, "error": "No monster found, run init first"}

        defender = None

        if target == "demo_duck" or target == "呆呆的小黄鸭" or "demo_duck" in target:
            demo_file = SCRIPT_DIR / "demos" / "demo_duck.soul"
            defender = load_json(demo_file)
        elif "pokemon" in target.lower() or target.startswith("00"):
            for f in (SCRIPT_DIR / "demos" / "pokemon").glob("*.soul"):
                if target in f.name or target.replace("-", "-").lower() in f.name.lower():
                    defender = load_json(f)
                    break
        elif target.endswith(".soul"):
            defender = load_json(Path(target))
        elif target:
            opponent_file = MONSTER_DIR / "opponent_pet.soul"
            defender = load_json(opponent_file)

        if not defender:
            defender = {
                "monster_id": "opponent",
                "name": "Opponent",
                "base_stats": {
                    "hp": 100,
                    "attack": 80,
                    "defense": 80,
                    "sp_atk": 80,
                    "sp_def": 80,
                    "speed": 80,
                },
            }

        simulator = BattleSimulator(attacker, defender, "seed123")
        result = simulator.run_battle(
            attack_stack or ["scan", "buffer_overflow", "refactor_storm"],
            [],
            "tank",
            5
        )
        result["success"] = True

        from datetime import datetime
        battle_data = {
            "id": f"battle_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "attacker_id": attacker.get("metadata", {}).get("name", "player"),
            "defender_id": defender.get("monster_id", "opponent"),
            "attacker_name": attacker.get("metadata", {}).get("name", "Player"),
            "defender_name": defender.get("name", "Opponent"),
            "winner": attacker.get("metadata", {}).get("name", "player") if result.get("winner") == "attacker" else defender.get("name", "Opponent"),
            "turns": result.get("turns", 0),
            "attack_stack": attack_stack or ["scan", "buffer_overflow", "refactor_storm"],
            "defense_stack": [],
            "battle_log": result.get("battle_log", [])[:10],
            "start_time": datetime.now().isoformat(),
            "end_time": datetime.now().isoformat(),
            "is_valid": True
        }

        judge_result = call_judge_server("/api/battle/validate", battle_data)
        if judge_result.get("is_valid") is False:
            result["judge_warning"] = "Battle validation failed: " + str(judge_result.get("errors", []))
        else:
            result["judge_validated"] = True

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


def cmd_farm(action="view"):
    """Manage your pet's farm"""
    try:
        from food_system import FoodManager
        
        manager = FoodManager()
        
        if action == "view":
            # Load and display current farm
            farm = manager.load_farm_from_file(MONSTER_DIR / "farm.yaml")
            if not farm:
                return "No farm found. Create one with /monster farm create"
            
            output = "🌾 Your Farm\n"
            output += "===========\n\n"
            for food in farm.foods:
                output += f"{food.emoji} {food.type.upper()}: {food.quantity}/{food.max_quantity}\n"
            return output
            
        elif action == "create":
            # Create a new farm
            farm = manager.create_farm(
                owner="player",
                repository="agent-monster",
                url="https://github.com/player/agent-monster"
            )
            manager.add_food_to_farm(farm, "cookie", 3)
            manager.add_food_to_farm(farm, "apple", 5)
            manager.save_farm_to_file("player", "agent-monster", str(MONSTER_DIR / "farm.yaml"))
            return "✅ Farm created successfully!"
        
        return "Unknown farm action"
    except Exception as e:
        return f"Error: {str(e)}"


def cmd_feed(farm_owner, farm_repo, food_id):
    """Feed your pet from another player's farm"""
    try:
        import requests
        import time
        
        # Create feed request
        feed_request = {
            "id": f"feed_{int(time.time())}",
            "eater_id": "player",
            "eater_pet_id": load_json(SOUL_FILE).get("id", "unknown"),
            "farm_owner": farm_owner,
            "farm_repo": farm_repo,
            "food_id": food_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        }
        
        # Validate with judge server
        result = call_judge_server("/api/food/validate", feed_request)
        
        if result.get("can_eat", False):
            # Record the transaction
            call_judge_server("/api/food/record", feed_request)
            return f"✅ Fed successfully! Gained {result.get('nutrition_gain', {})}"
        else:
            reasons = result.get("reasons", ["Unknown reason"])
            return f"❌ Cannot feed: {', '.join(reasons)}"
    except Exception as e:
        return f"Error: {str(e)}"


def cmd_explore(query=""):
    """Explore and discover other farms"""
    try:
        from food_explorer import GitHubFarmExplorer
        
        explorer = GitHubFarmExplorer()
        
        # Search for farms
        farms = explorer.discover_farms(limit=5)
        
        if not farms:
            return "No farms found"
        
        output = "🌍 Discovered Farms\n"
        output += "==================\n\n"
        
        for i, farm in enumerate(farms, 1):
            farm_data = explorer.explore_farm(farm.owner, farm.repository)
            if farm_data:
                output += f"{i}. {farm.owner}/{farm.repository}\n"
                output += f"   Available foods: {farm_data['total_available']}\n"
                output += f"   URL: {farm.url}\n\n"
        
        return output
    except Exception as e:
        return f"Error: {str(e)}"


def cmd_favorite(action="list", farm_url=""):
    """Manage favorite farms"""
    try:
        from food_explorer import GitHubFarmExplorer
        
        explorer = GitHubFarmExplorer()
        
        if action == "list":
            favorites = explorer.get_favorites()
            if not favorites:
                return "No favorite farms yet"
            output = "⭐ Favorite Farms\n"
            output += "================\n"
            for url in favorites:
                output += f"• {url}\n"
            return output
        
        elif action == "add":
            favorites = explorer.get_favorites()
            if farm_url not in favorites:
                favorites.append(farm_url)
                explorer.save_favorites(favorites)
                return f"✅ Added {farm_url} to favorites"
            return "Already in favorites"
        
        elif action == "remove":
            favorites = explorer.get_favorites()
            if farm_url in favorites:
                favorites.remove(farm_url)
                explorer.save_favorites(favorites)
                return f"✅ Removed {farm_url} from favorites"
            return "Not in favorites"
        
        return "Unknown action"
    except Exception as e:
        return f"Error: {str(e)}"


def cmd_battle(target, mode="INTERACTIVE", ai_personality="BALANCED", show_reasoning=True):
    """Start an AI-enhanced battle"""
    try:
        # Load player's pet
        soul_file = MONSTER_DIR / "pet.soul"
        if not soul_file.exists():
            return json.dumps({
                "success": False,
                "error": "No pet found. Initialize with /monster init first!"
            }, indent=2)
        
        player_data = load_json(soul_file)
        if not player_data:
            return json.dumps({
                "success": False,
                "error": "No pet found. Initialize with /monster init first!"
            }, indent=2)
        
        # For now, return a message about the battle
        result = {
            "success": True,
            "message": f"Battle initialized: {player_data.get('name', 'Your Monster')} vs {target}",
            "config": {
                "mode": mode,
                "ai_personality": ai_personality,
                "show_reasoning": show_reasoning
            },
            "note": "Full AI battle simulation will be executed when integrated with AIEnhancedBattle system"
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


def cmd_battle_config(mode="INTERACTIVE", ai_personality="BALANCED"):
    """Configure battle settings"""
    try:
        valid_modes = ["INTERACTIVE", "PVP_AI", "PVE", "AI_VS_AI"]
        valid_personalities = ["AGGRESSIVE", "DEFENSIVE", "BALANCED", "TACTICAL", "EVOLVING"]
        
        if mode not in valid_modes:
            return json.dumps({
                "success": False,
                "error": f"Invalid mode. Valid modes: {', '.join(valid_modes)}"
            }, indent=2)
        
        if ai_personality not in valid_personalities:
            return json.dumps({
                "success": False,
                "error": f"Invalid personality. Valid personalities: {', '.join(valid_personalities)}"
            }, indent=2)
        
        config_data = {
            "mode": mode,
            "ai_personality": ai_personality,
            "timestamp": __import__('time').strftime("%Y-%m-%d %H:%M:%SZ", __import__('time').gmtime())
        }
        
        save_json(MONSTER_DIR / "battle_config.json", config_data)
        
        return json.dumps({
            "success": True,
            "message": f"Battle config updated: mode={mode}, personality={ai_personality}",
            "config": config_data
        }, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


def cmd_predict(opponent_name="", opponent_level=1):
    """Predict battle outcome and get strategy recommendations"""
    try:
        # Load player's soul/pet data
        soul_file = MONSTER_DIR / "pet.soul"
        if not soul_file.exists():
            return json.dumps({
                "success": False,
                "error": "No pet found. Initialize with /monster init first!"
            }, indent=2)
        
        player_data = load_json(soul_file)
        if not player_data:
            return json.dumps({
                "success": False,
                "error": "No pet found. Initialize with /monster init first!"
            }, indent=2)
        
        # Simple prediction based on level and stats
        player_level = player_data.get("level", 1)
        opponent_level = opponent_level or player_level
        
        # Win probability based on level difference
        win_probability = 0.5 + (player_level - opponent_level) * 0.05
        win_probability = max(0.1, min(0.9, win_probability))  # Clamp between 0.1 and 0.9
        
        # Recommend strategy
        if win_probability > 0.7:
            recommended_strategy = "AGGRESSIVE"
            recommendation = "You have a strong advantage! Use aggressive tactics to win quickly."
        elif win_probability > 0.5:
            recommended_strategy = "BALANCED"
            recommendation = "You have a slight advantage. Use balanced tactics to maintain control."
        elif win_probability > 0.3:
            recommended_strategy = "DEFENSIVE"
            recommendation = "You're at a disadvantage. Play defensively and wait for openings."
        else:
            recommended_strategy = "TACTICAL"
            recommendation = "You're significantly outmatched. Focus on exploiting status effects and weaker defenses."
        
        result = {
            "success": True,
            "matchup": {
                "player": f"{player_data.get('name', 'Your Monster')} (Lv.{player_level})",
                "opponent": f"{opponent_name} (Lv.{opponent_level})"
            },
            "prediction": {
                "win_probability": f"{win_probability * 100:.1f}%",
                "recommended_strategy": recommended_strategy,
                "recommendation": recommendation
            }
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


def cmd_replay(replay_id=""):
    """View a specific battle replay"""
    try:
        from battle_replay import BattleReplayManager
        
        manager = BattleReplayManager()
        
        if not replay_id:
            return json.dumps({
                "success": False,
                "error": "replay_id is required"
            }, indent=2)
        
        replay = manager.get_replay(replay_id)
        if not replay:
            return json.dumps({
                "success": False,
                "error": f"Replay not found: {replay_id}"
            }, indent=2)
        
        result = {
            "success": True,
            "replay": {
                "id": replay.id,
                "timestamp": replay.timestamp,
                "attacker": replay.attacker_name,
                "winner": replay.winner,
                "turns": len(replay.turns) if isinstance(replay.turns, list) else replay.turns,
                "result": replay.result,
                "log": replay.log[:5] if replay.log else []  # Show first 5 entries
            }
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


def cmd_replays(limit=10):
    """List recent battle replays"""
    try:
        from battle_replay import BattleReplayManager
        
        manager = BattleReplayManager()
        replays = manager.get_recent_replays(count=limit)
        
        result = {
            "success": True,
            "total": len(replays),
            "replays": [
                {
                    "id": r.id,
                    "timestamp": r.timestamp,
                    "attacker": r.attacker_name,
                    "winner": r.winner,
                    "turns": len(r.turns) if isinstance(r.turns, list) else r.turns,
                    "result": r.result
                }
                for r in replays
            ]
        }
        
        return json.dumps(result, indent=2, ensure_ascii=False)
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": str(e)
        }, indent=2)


def mcp_loop():
    """Main MCP server loop - reads JSON-RPC from stdin"""
    while True:
        try:
            line = sys.stdin.readline()
            if not line:
                break

            req = json.loads(line.strip())
            method = req.get("method", "")
            params = req.get("params", {})
            req_id = req.get("id")

            resp = {"jsonrpc": "2.0", "id": req_id}

            if method == "initialize":
                resp["result"] = {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "serverInfo": {
                        "name": "agent-monster",
                        "version": "0.1.0"
                    }
                }

            elif method == "tools/list":
                resp["result"] = {
                    "tools": [
                        {
                            "name": "monster_init",
                            "description": "Initialize a new Agent Monster pet for the current repository by analyzing git commit history",
                            "inputSchema": {"type": "object", "properties": {}, "required": []},
                        },
                        {
                            "name": "monster_status",
                            "description": "Show the current status of your Agent Monster (level, stats, evolution)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "json": {"type": "boolean", "description": "Output in JSON format"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "monster_duel",
                            "description": "Challenge another repository's monster to battle",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "target": {"type": "string", "description": "Target repository URL or monster ID"},
                                    "attack_sequence": {"type": "array", "items": {"type": "string"}, "description": "Attack sequence"}
                                },
                                "required": ["target"]
                            },
                        },
                        {
                            "name": "monster_attack",
                            "description": "Attack a target (demo pet or GitHub URL) - shortcut for duel",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "target": {"type": "string", "description": "Target URL or monster ID (e.g., https://github.com/.../demo_duck)"},
                                    "attack_sequence": {"type": "array", "items": {"type": "string"}, "description": "Attack sequence"}
                                },
                                "required": ["target"]
                            },
                        },
                        {
                            "name": "monster_analyze",
                            "description": "Analyze repository activity and update monster stats",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "days": {"type": "integer", "description": "Days to analyze (default: 7)"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "monster_traps",
                            "description": "Scan code for defensive traps (@monster-trap comments)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "path": {"type": "string", "description": "Path to scan (default: current directory)"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "monster_hatch",
                            "description": "Hatch your egg to get a Pokemon",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            },
                        },
                        {
                            "name": "monster_capture",
                            "description": "Throw a capture ball to catch wild Pokemon (requires low HP)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "target_hp": {"type": "number", "description": "Target Pokemon's current HP"},
                                    "max_hp": {"type": "number", "description": "Target Pokemon's max HP"}
                                },
                                "required": ["target_hp", "max_hp"]
                            },
                        },
                        {
                            "name": "monster_farm",
                            "description": "Manage your pet's farm - view or create",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "enum": ["view", "create"], "description": "Farm action"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "monster_feed",
                            "description": "Feed your pet from another player's farm",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "farm_owner": {"type": "string", "description": "Farm owner GitHub username"},
                                    "farm_repo": {"type": "string", "description": "Farm repository name"},
                                    "food_id": {"type": "string", "description": "Food ID to eat"}
                                },
                                "required": ["farm_owner", "farm_repo", "food_id"]
                            },
                        },
                        {
                            "name": "monster_explore",
                            "description": "Explore and discover other players' farms",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "query": {"type": "string", "description": "Search query"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "monster_favorite",
                            "description": "Manage favorite farms",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "action": {"type": "string", "enum": ["list", "add", "remove"], "description": "Action"},
                                    "farm_url": {"type": "string", "description": "Farm URL"}
                                },
                                "required": ["action"]
                            },
                        },
                        {
                            "name": "monster_battle",
                            "description": "Start an AI-enhanced battle with AI assistance and reasoning",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "target": {"type": "string", "description": "Target opponent name"},
                                    "mode": {"type": "string", "enum": ["INTERACTIVE", "PVP_AI", "PVE", "AI_VS_AI"], "description": "Battle mode (default: INTERACTIVE)"},
                                    "ai_personality": {"type": "string", "enum": ["AGGRESSIVE", "DEFENSIVE", "BALANCED", "TACTICAL", "EVOLVING"], "description": "AI opponent personality"},
                                    "show_reasoning": {"type": "boolean", "description": "Show AI decision reasoning"}
                                },
                                "required": ["target"]
                            },
                        },
                        {
                            "name": "monster_battle_config",
                            "description": "Configure battle settings (mode and AI personality)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "mode": {"type": "string", "enum": ["INTERACTIVE", "PVP_AI", "PVE", "AI_VS_AI"], "description": "Battle mode"},
                                    "ai_personality": {"type": "string", "enum": ["AGGRESSIVE", "DEFENSIVE", "BALANCED", "TACTICAL", "EVOLVING"], "description": "AI personality"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "monster_predict",
                            "description": "Predict battle outcome and get strategy recommendations",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "opponent_name": {"type": "string", "description": "Opponent name"},
                                    "opponent_level": {"type": "integer", "description": "Opponent level"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "monster_replay",
                            "description": "View a specific battle replay",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "replay_id": {"type": "string", "description": "Battle replay ID"}
                                },
                                "required": ["replay_id"]
                            },
                        },
                        {
                            "name": "monster_replays",
                            "description": "List recent battle replays",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "limit": {"type": "integer", "description": "Number of replays to show (default: 10)"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "user_register",
                            "description": "Register a new user with GitHub username",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "github_username": {"type": "string", "description": "GitHub username"}
                                },
                                "required": ["github_username"]
                            },
                        },
                        {
                            "name": "user_info",
                            "description": "Get current user account information",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "github_username": {"type": "string", "description": "GitHub username (optional)"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "shop_list",
                            "description": "List all available items in the shop",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            },
                        },
                        {
                            "name": "shop_buy",
                            "description": "Buy an item from the shop",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "github_username": {"type": "string", "description": "GitHub username"},
                                    "item_id": {"type": "string", "description": "Item ID to purchase"},
                                    "quantity": {"type": "integer", "description": "Quantity (default: 1)"}
                                },
                                "required": ["github_username", "item_id"]
                            },
                        },
                        {
                            "name": "inventory_view",
                            "description": "View user's inventory of items",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "github_username": {"type": "string", "description": "GitHub username"}
                                },
                                "required": ["github_username"]
                            },
                        },
                        {
                            "name": "account_stats",
                            "description": "Get detailed account statistics and transaction history",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "github_username": {"type": "string", "description": "GitHub username"}
                                },
                                "required": ["github_username"]
                            },
                        },
                        {
                            "name": "menu_start",
                            "description": "启动交互式游戏菜单系统",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "github_username": {"type": "string", "description": "GitHub用户名"}
                                },
                                "required": ["github_username"]
                            },
                        },
                        {
                            "name": "menu_action",
                            "description": "在菜单中执行操作 (输入选择编号)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "github_username": {"type": "string", "description": "GitHub用户名"},
                                    "action": {"type": "string", "description": "用户选择的动作 (0-9)"}
                                },
                                "required": ["github_username", "action"]
                            },
                        },
                        {
                            "name": "monster_slash_help",
                            "description": "Get detailed help for slash commands",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "command_name": {"type": "string", "description": "Command name (optional)"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "monster_slash_list",
                            "description": "List all available slash commands",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            },
                        },
                        {
                            "name": "monster_slash_completions",
                            "description": "Get command completions and suggestions",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "prefix": {"type": "string", "description": "Command prefix for auto-completion"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "monster_menu",
                            "description": "Start the interactive Agent Monster menu system - the main command for /monster",
                            "inputSchema": {
                                "type": "object",
                                "properties": {
                                    "github_username": {"type": "string", "description": "Your GitHub username (optional - will use auto-detected if not provided)"}
                                },
                                "required": []
                            },
                        },
                        {
                            "name": "monster_simple_start",
                            "description": "Start Agent Monster with automatic GitHub login (simplified command)",
                            "inputSchema": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            },
                        },
                    ]
                }

            elif method == "tools/call":
                tool = params.get("name", "")
                args = params.get("arguments", {})

                if tool == "monster_init":
                    out = cmd_init()
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_status":
                    out = cmd_status(args.get("json", True))
                    resp["result"] = {"content": [{"type": "text", "text": out or ""}]}
                elif tool == "monster_duel":
                    result = cmd_duel(
                        args.get("target", ""), args.get("attack_sequence")
                    )
                    resp["result"] = {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
                elif tool == "monster_attack":
                    result = cmd_duel(
                        args.get("target", ""), args.get("attack_sequence")
                    )
                    resp["result"] = {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
                elif tool == "monster_analyze":
                    result = cmd_analyze(args.get("days", 7))
                    resp["result"] = {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
                elif tool == "monster_traps":
                    result = cmd_traps(args.get("path", "."))
                    resp["result"] = {"content": [{"type": "text", "text": json.dumps(result, indent=2, ensure_ascii=False)}]}
                elif tool == "monster_hatch":
                    out = cmd_hatch()
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_capture":
                    out = cmd_capture(args.get("target_hp", 0), args.get("max_hp", 100))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_farm":
                    out = cmd_farm(args.get("action", "view"))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_feed":
                    out = cmd_feed(
                        args.get("farm_owner", ""),
                        args.get("farm_repo", ""),
                        args.get("food_id", "")
                    )
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_explore":
                    out = cmd_explore(args.get("query", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_favorite":
                    out = cmd_favorite(
                        args.get("action", "list"),
                        args.get("farm_url", "")
                    )
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_battle":
                    out = cmd_battle(
                        args.get("target", ""),
                        args.get("mode", "INTERACTIVE"),
                        args.get("ai_personality", "BALANCED"),
                        args.get("show_reasoning", True)
                    )
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_battle_config":
                    out = cmd_battle_config(
                        args.get("mode", "INTERACTIVE"),
                        args.get("ai_personality", "BALANCED")
                    )
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_predict":
                    out = cmd_predict(
                        args.get("opponent_name", ""),
                        args.get("opponent_level", 1)
                    )
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_replay":
                    out = cmd_replay(args.get("replay_id", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_replays":
                    out = cmd_replays(args.get("limit", 10))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "user_register":
                    out = cmd_user_register(args.get("github_username", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "user_info":
                    out = cmd_user_info(args.get("github_username", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "shop_list":
                    out = cmd_shop_list()
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "shop_buy":
                    out = cmd_shop_buy(
                        args.get("github_username", ""),
                        args.get("item_id", ""),
                        args.get("quantity", 1)
                    )
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "inventory_view":
                    out = cmd_inventory_view(args.get("github_username", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "account_stats":
                    out = cmd_account_stats(args.get("github_username", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "menu_start":
                    out = cmd_menu_start(args.get("github_username", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "menu_action":
                    out = cmd_menu_action(
                        args.get("github_username", ""),
                        args.get("action", "")
                    )
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_slash_help":
                    out = cmd_slash_help(args.get("command_name", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_slash_list":
                    out = cmd_slash_list()
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_slash_completions":
                    out = cmd_slash_completions(args.get("prefix", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_menu":
                    # Main /monster command - start the menu system
                    username = args.get("github_username", "")
                    if not username:
                        out = cmd_simple_start()
                    else:
                        out = cmd_menu_start(username)
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_simple_start":
                    out = cmd_simple_start()
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                else:
                    resp["error"] = {"code": -32601, "message": f"Unknown tool: {tool}"}

            else:
                resp["error"] = {"code": -32600, "message": "Invalid Request"}

            print(json.dumps(resp), flush=True)

        except json.JSONDecodeError as e:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32700, "message": "Parse error: " + str(e)}}), flush=True)
        except Exception as e:
            print(json.dumps({"jsonrpc": "2.0", "id": None, "error": {"code": -32603, "message": "Internal error: " + str(e)}}), flush=True)


if __name__ == "__main__":
    if not check_dependencies():
        sys.exit(1)

    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        mcp_loop()
    elif len(sys.argv) > 1:
        if sys.argv[1] == "init":
            print(cmd_init())
        elif sys.argv[1] == "status":
            print(cmd_status("--json" in sys.argv))
        elif sys.argv[1] == "analyze":
            print(json.dumps(cmd_analyze(), indent=2))
        elif sys.argv[1] == "traps":
            print(json.dumps(cmd_traps(sys.argv[2] if len(sys.argv) > 2 else "."), indent=2))
        elif sys.argv[1] == "duel":
            target = sys.argv[2] if len(sys.argv) > 2 else ""
            print(json.dumps(cmd_duel(target), indent=2))
    else:
        print("Agent Monster CLI v0.1.0")
        print("Usage: monster.py <command>")
        print("Commands: init, status, analyze, traps, duel, mcp")
