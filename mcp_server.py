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


def cmd_init():
    result = subprocess.run(
        [sys.executable, "egg_incubator.py"],
        capture_output=True,
        cwd=SCRIPT_DIR,
        env={**os.environ, "PYTHONIOENCODING": "utf-8"}
    )
    if result.returncode != 0:
        return f"Error: {result.stderr.decode('utf-8', errors='replace')}"
    return result.stdout.decode('utf-8', errors='replace')


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
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


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
