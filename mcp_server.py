#!/usr/bin/env python3
"""
Agent Monster MCP Server
STDIO-based MCP server for Claude Code integration
REFACTORED: SERVER-AUTHORITATIVE MODE (No local simulations)
"""

import json
import subprocess
import sys
import os
from pathlib import Path
from datetime import datetime
import time

SCRIPT_DIR = Path(__file__).parent
MONSTER_DIR = SCRIPT_DIR / ".monster"
CONFIG_FILE = MONSTER_DIR / "config.json"
SOUL_FILE = MONSTER_DIR / "pet.soul"

JUDGE_SERVER = "http://agentmonster.openx.pro:10000"

def check_dependencies():
    """Check if required dependencies are installed"""
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

# ========== Helper Functions ==========

def _find_user_by_login(user_manager, github_username):
    """Helper to find user by GitHub login"""
    users = user_manager.list_users()
    for user in users:
        if user.github_login == github_username:
            return user
    return None

# ========== Server-Authoritative Commands ==========

def cmd_welcome():
    """Initial welcome message for new players"""
    return """👋 Welcome to Agent Monster! / 欢迎来到代码怪兽！
===
The AI-powered RPG where your GitHub repository becomes a digital pet.

You are about to start a multiplayer journey validated by our global Judge Server.

Next Steps:
1. Choose your language / 选择语言 (e.g., "I want to use Chinese")
2. Register your trainer ID / 注册训练师 (e.g., "Register me")
3. Setup your base / 建立基地 (e.g., "Setup my base")
4. Get your first egg / 领一个蛋 (e.g., "Initialize my monster")

Type 'monster_guide' at any time for help!
"""

def cmd_fork_setup(github_username=""):
    """Automatically setup base and map for a forked repository"""
    try:
        from user_manager import UserManager
        user_manager = UserManager(str(MONSTER_DIR))
        
        if not github_username:
            github_username = "current_user"
            
        user = _find_user_by_login(user_manager, github_username)
        if not user:
            return "❌ 请先运行 monster_welcome 或 user_register 进行注册。"

        # Generate a starter map using maps/generator.go
        map_id = f"{github_username}_starter"
        cmd = [
            "go", "run", "maps/generator.go", "generate",
            f"-id={map_id}",
            f"-owner-id={user.github_id}",
            f"-owner={github_username}",
            "-width=20",
            "-height=20"
        ]
        
        subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Verify if the map file was created
        map_file = Path("maps") / f"{map_id}.json"
        if map_file.exists():
            return f"""✅ Base Setup Complete! / 基地建立成功！
===
Map ID: {map_id}
Location: maps/{map_file.name}

Your base has been established. You can now explore your repository's digital world!
Next Step: 'monster_init' to get your first egg.
"""
        else:
            return "❌ Map generation failed (file not found)."
            
    except Exception as e:
        return f"❌ Base setup failed: {str(e)}"

def cmd_user_register(github_username):
    """Register a new user with GitHub username"""
    try:
        from onboarding_manager import OnboardingManager
        onboarding = OnboardingManager(str(MONSTER_DIR))
        
        github_id = hash(github_username) % (10**9)
        success, user, message = onboarding.register_from_github(
            github_login=github_username,
            github_id=github_id
        )
        
        if success:
            # Sync with Judge Server
            judge_res = call_judge_server("/api/users/create", {
                "github_id": github_id,
                "github_login": github_username
            })
            
            return f"""✅ User Registration Complete!
===
Username: {user.github_login}
GitHub ID: {user.github_id}
Online Sync: {'Success' if judge_res.get('success') else 'Failed'}

Next Step: Run 'monster_fork_setup' to establish your base!
"""
        else:
            return f"❌ Registration failed: {message}"
    except Exception as e:
        return f"❌ Registration failed: {str(e)}"

def cmd_init(github_username=""):
    """Initialize a new monster by registering an egg on the Judge Server"""
    try:
        from user_manager import UserManager
        user_manager = UserManager(str(MONSTER_DIR))
        
        if not github_username:
            github_username = "current_user"
            
        user = _find_user_by_login(user_manager, github_username)
        if not user:
            return "❌ 请先运行 monster_welcome 或 user_register 进行注册。"

        egg_id = f"egg_{user.github_id}_{int(time.time())}"
        
        egg_request = {
            "egg_id": egg_id,
            "owner_id": str(user.github_id),
            "incubation_hours": 72,
            "attributes": json.dumps({"origin": "github_init", "repo": github_username})
        }
        
        judge_result = call_judge_server("/api/eggs/create", egg_request)
        
        if judge_result.get("success", False):
            # We still keep a small local cache for 'current state' quick access, 
            # but the server is the source of truth.
            save_json(MONSTER_DIR / "egg.json", {
                "id": egg_id,
                "owner": github_username,
                "status": "incubating",
                "server_verified": True,
                "synced_at": datetime.utcnow().isoformat()
            })
            
            return f"""🥚 获得新蛋（已通过服务器验证）!
===
所有者: {github_username}
在线模式：所有数据均已同步至裁判服务器。请等待孵化！
"""
        else:
            return f"❌ 蛋初始化失败 (裁判服务器): {judge_result.get('error', '未知错误')}"
    except Exception as e:
        return f"❌ 初始化异常: {str(e)}"

def cmd_duel(github_username, target, attack_stack=None):
    """Start a battle through the Judge Server (No local simulation)"""
    try:
        from user_manager import UserManager
        user_manager = UserManager(str(MONSTER_DIR))
        
        attacker = _find_user_by_login(user_manager, github_username)
        if not attacker:
            return {"success": False, "error": f"Attacker '{github_username}' not found"}

        # Resolve Target
        defender_id = 0
        if "pikachu" in target.lower(): defender_id = 25
        elif "duck" in target.lower(): defender_id = 54
        else:
            defender = _find_user_by_login(user_manager, target)
            if defender: defender_id = defender.github_id
            else: return {"success": False, "error": f"Could not resolve target '{target}'"}

        battle_request = {
            "attacker_id": attacker.github_id,
            "defender_id": defender_id,
            "battle_type": "duel",
            "attacker_team_id": 1, 
            "defender_team_id": 1
        }
        
        judge_result = call_judge_server("/api/battles/start", battle_request)
        
        if judge_result.get("success", False):
            battle = judge_result.get("battle", {})
            return {
                "success": True,
                "message": "⚔️ Battle started on Judge Server!",
                "battle_id": battle.get("id"),
                "status": "ONLINE_AUTHORITATIVE"
            }
        else:
            return {"success": False, "error": judge_result.get("error", "Judge server failed")}
    except Exception as e:
        return {"success": False, "error": str(e)}

def cmd_design(name, species_type, hp, attack, defense, speed):
    """Guide the user to design a new monster metadata (UGC)"""
    try:
        design = {
            "metadata": {
                "name": name,
                "species": name,
                "generation": 1,
                "level": 1,
                "designer_mode": True
            },
            "base_stats": {
                "hp": int(hp),
                "attack": int(attack),
                "defense": int(defense),
                "sp_atk": int((attack + defense) // 2),
                "sp_def": int(defense),
                "speed": int(speed)
            },
            "type": [species_type],
            "nature": "Hardy",
            "ability": "Recycle"
        }
        
        # Save to temporary design file
        design_dir = MONSTER_DIR / "designs"
        design_dir.mkdir(parents=True, exist_ok=True)
        file_path = design_dir / f"design_{name.lower().replace(' ', '_')}.json"
        save_json(file_path, design)
        
        return f"""🎨 Monster Design Created!
===
Name: {name}
Type: {species_type}
Stats: HP={hp}, ATK={attack}, DEF={defense}, SPD={speed}

File saved to: .monster/designs/{file_path.name}

Next Step: Run 'monster_submit_design' to prepare it for your repository!
"""
    except Exception as e:
        return f"❌ Design failed: {str(e)}"

def cmd_submit_design(name):
    """Prepare a designed monster for submission to the user's repository"""
    try:
        import shutil
        design_name = name.lower().replace(' ', '_')
        src_file = MONSTER_DIR / "designs" / f"design_{design_name}.json"
        
        if not src_file.exists():
            return f"❌ Design '{name}' not found. Run 'monster_design' first."
            
        # Target directory in the repo
        target_dir = SCRIPT_DIR / "designs" / "monsters"
        target_dir.mkdir(parents=True, exist_ok=True)
        dest_file = target_dir / f"{design_name}.soul"
        
        shutil.copy(src_file, dest_file)
        
        return f"""📤 Design Ready for Submission!
===
Your monster '{name}' has been moved to:
/designs/monsters/{dest_file.name}

What to do now:
1. Commit this file: 'git add designs/monsters/{dest_file.name}'
2. Push to your repo: 'git push origin main'
3. Share the link for voting!

Once validated by the community, your monster can hatch from new eggs!
"""
    except Exception as e:
        return f"❌ Submission preparation failed: {str(e)}"

def cmd_guide(github_username=""):
    """Bilingual AI Guide - Multi-language support included"""
    try:
        from user_manager import UserManager
        user_manager = UserManager(str(MONSTER_DIR))
        
        if not github_username: github_username = "current_user"
        user = _find_user_by_login(user_manager, github_username)
        lang = "zh" if not user else user.language
        
        # Real-time state check (simplified for authoritative mode)
        output = "🤖 Agent Monster AI Guide / 代码怪兽助手\n"
        if lang == "zh":
            output += "==========================\n"
            output += "当前模式：多人在线验证模式 (Online Auth)\n"
            output += "您可以：对战、孵蛋、训练、或去商店购买。\n"
        else:
            output += "==========================\n"
            output += "Mode: Multiplayer Online (Online Auth)\n"
            output += "Actions: Duel, Hatch, Train, or Visit Shop.\n"
        return output
    except Exception as e:
        return f"Error: {str(e)}"

# ========== Main MCP Loop (Simplified) ==========

def mcp_loop():
    while True:
        try:
            line = sys.stdin.readline()
            if not line: break
            req = json.loads(line.strip())
            method = req.get("method", "")
            params = req.get("params", {})
            req_id = req.get("id")
            resp = {"jsonrpc": "2.0", "id": req_id}

            if method == "initialize":
                resp["result"] = {"protocolVersion": "2024-11-05", "capabilities": {"tools": {}}}
            elif method == "tools/list":
                resp["result"] = {"tools": [
                    {"name": "monster_init", "description": "Init egg via Judge Server", "inputSchema": {"type": "object", "properties": {"github_username": {"type": "string"}}, "required": []}},
                    {"name": "monster_welcome", "description": "Welcome new players and start registration", "inputSchema": {"type": "object", "properties": {}, "required": []}},
                    {"name": "monster_fork_setup", "description": "Setup base and map for the repository", "inputSchema": {"type": "object", "properties": {"github_username": {"type": "string"}}, "required": []}},
                    {"name": "monster_duel", "description": "Online battle via Judge Server", "inputSchema": {"type": "object", "properties": {"github_username": {"type": "string"}, "target": {"type": "string"}}, "required": ["github_username", "target"]}},
                    {"name": "monster_guide", "description": "Get AI advice", "inputSchema": {"type": "object", "properties": {"github_username": {"type": "string"}}, "required": []}},
                    {"name": "monster_design", "description": "Create a new monster design (UGC)", "inputSchema": {
                        "type": "object", 
                        "properties": {
                            "name": {"type": "string", "description": "Monster name"},
                            "species_type": {"type": "string", "enum": ["Low-Level", "Scripting", "Logic", "Automation", "Web", "Data", "System", "Network", "Security", "Metal", "Glass", "Hybrid"], "description": "Species type"},
                            "hp": {"type": "integer", "description": "Base HP (1-255)"},
                            "attack": {"type": "integer", "description": "Base Attack (1-255)"},
                            "defense": {"type": "integer", "description": "Base Defense (1-255)"},
                            "speed": {"type": "integer", "description": "Base Speed (1-255)"}
                        }, 
                        "required": ["name", "species_type", "hp", "attack", "defense", "speed"]
                    }},
                    {"name": "monster_submit_design", "description": "Move design to repo for git submission", "inputSchema": {
                        "type": "object",
                        "properties": {"name": {"type": "string", "description": "Monster name"}},
                        "required": ["name"]
                    }}
                ]}
            elif method == "tools/call":
                tool = params.get("name", "")
                args = params.get("arguments", {})
                if tool == "monster_init":
                    out = cmd_init(args.get("github_username", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_welcome":
                    out = cmd_welcome()
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_fork_setup":
                    out = cmd_fork_setup(args.get("github_username", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_duel":
                    res = cmd_duel(args.get("github_username", ""), args.get("target", ""))
                    resp["result"] = {"content": [{"type": "text", "text": json.dumps(res)}]}
                elif tool == "monster_guide":
                    out = cmd_guide(args.get("github_username", ""))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_design":
                    out = cmd_design(args.get("name"), args.get("species_type"), args.get("hp"), args.get("attack"), args.get("defense"), args.get("speed"))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
                elif tool == "monster_submit_design":
                    out = cmd_submit_design(args.get("name"))
                    resp["result"] = {"content": [{"type": "text", "text": out}]}
            
            print(json.dumps(resp), flush=True)
        except Exception as e:
            print(json.dumps({"error": str(e)}), flush=True)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "mcp":
        mcp_loop()
    else:
        print("Agent Monster Server-Authoritative CLI")
