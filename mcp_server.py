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
MONSTER_DIR = SCRIPT_DIR.parent / ".monster"
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
                repository="agent-monster-pet",
                url="https://github.com/player/agent-monster-pet"
            )
            manager.add_food_to_farm(farm, "cookie", 3)
            manager.add_food_to_farm(farm, "apple", 5)
            manager.save_farm_to_file(farm, MONSTER_DIR / "farm.yaml")
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
