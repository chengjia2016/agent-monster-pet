# Agent Monster - Gameplay Skill & Entry Point

Welcome to **Agent Monster**, an AI-powered RPG where your GitHub repository becomes a digital pet. This guide serves as the entry point for players and the operational manual for AI agents (Claude, OpenCode, Gemini).

---

## 🚀 Entry Point: Getting Started

As an AI agent, your first task is to ensure the environment is ready for the player.

### 1. Check GitHub Authentication
Before starting, verify if the player is logged into GitHub:
```bash
gh auth status
```
*If not logged in, suggest: `gh auth login`.*

### 2. Check Judge Server Status
Verify that the Judge Server (Source of Truth) is running:
```bash
curl -s http://agentmonster.openx.pro:10000/health
```
*If the server is down, the game is in 'Local-Only' mode (limited functionality).*

### 3. Welcome the Player
If this is the first time, call:
```bash
python3 mcp_server.py welcome
```
(Or use the `monster_welcome` tool). This will guide the player through language selection and registration.

---

## 🛠️ Onboarding Workflow (Step-by-Step)

For a perfect new player experience (e.g., "I just forked this repo"), follow this sequence strictly:

1.  **Welcome & Claim Starter Pack**: Use `monster_welcome` then `user_register`.
    -   *Reward*: You automatically receive **100 Coins**, **Starter Items**, a **Starter Pet (小黄鸭)**, and your first **Egg**!
2.  **Test a Battle (Training)**: Before building your home, test your pet's strength!
    -   Use `monster_duel` against a low-level target like `"pikachu"` or `"duck"`.
3.  **Establish Your Base**: Create your own space in the digital world.
    -   Use `monster_fork_setup`. You can provide a **Base Name** (e.g., `"TitanTower"`).
    -   *Result*: This creates a `/base` directory in your repo with a `map.json` and `config.json`.
4.  **Play & Submit**: 
    -   You can now "live" and test gameplay inside your own `./base`.
    -   If the base is perfect, **Commit and Push** the `base/` folder to your GitHub repository to share it with the world!

---

## 🏗️ Architecture: Server-Authoritative vs. Local Creative
Agent Monster follows a strict **Server-Authoritative** principle to ensure a fair multiplayer experience.

### 1. Server-Stored Data (Source of Truth)
Most game data is stored in the **Judge Server's Database**. You should **NOT** write or rely on local files for these:
- **Player Profiles & Stats**: Level, EXP, Coins, and Items.
- **Pet Status**: Egg incubation progress and pet health/stats.
- **Battle Results**: All combat outcomes and rewards.
- **Inventory**: Items bought or found.
*Interaction is done via API calls (e.g., `POST /api/eggs/create`).*

### 2. Local-Stored Data (UGC & Creative)
Only **User-Generated Content (UGC)** should be stored locally in your repository before submission:
- **Your Base**: The `./base` directory (Map and Config).
- **Custom Monsters**: Monster design files (e.g., `designs/monsters/my_pet.soul`).
- **Submission Process**:
  1. Design/Setup locally using `monster_fork_setup` or `monster_design`.
  2. Commit to Git: `git add base/ && git commit -m "Add my base"`.
  3. Push to GitHub: `git push origin main`.

---

## 🔐 Login & Persistence / 登录与持久化

### How to Login Next Time?
Agent Monster uses a **Dual-Layer Persistence** system:

1.  **GitHub Layer (Primary Auth):**
    - The game relies on the `gh` CLI. If you are logged into `gh`, the game automatically detects your identity.
    - Run `gh auth status` to check. If you're logged out, run `gh auth login`.
2.  **Local Session Layer (Game State):**
    - Once identified via GitHub, a local session is created in `.monster/sessions.json`.
    - User profiles (language settings, stats) are stored in `.monster/users/<user_id>.json`.
    - **No manual password needed.** Your GitHub identity is your key.

---

## 🎮 Gameplay Mechanics (Natural Language Interaction)

The ultimate goal is for the player to play using **Natural Language**. As an AI agent, you should map the player's intent to the following Judge Server APIs or MCP tools.

### Core Player Actions

| Intent | Action / API Endpoint | MCP Tool (Preferred) |
| :--- | :--- | :--- |
| **"Who am I?" / "Stats"** | `GET /api/cookies/scan?player_id=<gh_login>` | `monster_status` |
| **"I'm new, help!"** | `N/A` | `monster_guide` |
| **"Setup my base"** | `N/A` | `monster_fork_setup` |
| **"I want a pet"** | `POST /api/eggs/create` | `monster_init` |
| **"Battle someone!"** | `POST /api/battles/start` | `monster_duel` |
| **"Go to shop"** | `GET /api/shop/items` | `shop_list` |
| **"Design a pet"** | `N/A` | `monster_design` |

---

## 🛠️ Judge Server API Reference (Authoritative)

The Judge Server is the **Source of Truth**. You can interact with it directly via `curl` even if Python scripts are missing.

### User Management
- **Create Account**: `POST /api/users/create`
  - Body: `{"github_id": 12345, "github_login": "username"}`

### Pet & Eggs
- **Claim Egg**: `POST /api/eggs/create`
  - Body: `{"egg_id": "unique_id", "owner_id": "gh_id", "incubation_hours": 72}`
- **Hatch Egg**: `POST /api/pet/validate` (Validates hatch outcome)

### Battle System
- **Start Battle**: `POST /api/battles/start`
  - Body: `{"attacker_id": 1, "defender_id": 2, "battle_type": "duel"}`
- **Record Result**: `POST /api/battle/validate`

---

## 🧠 AI Agent Mandates (from GEMINI.md)

1. **Natural Language First**: Always prioritize a narrative, RPG-like response over raw data.
2. **Server is Truth**: Never simulate a battle outcome locally; always call the Judge Server.
3. **Proactive Guidance**: If the player is idle, use `monster_guide` to suggest the next step (e.g., "Your egg is ready to hatch!" or "A rival is challenging you!").
4. **Multilingual**: Respect the user's language preference (default: Chinese).

---

*“Your code is alive. Train it well.”*
