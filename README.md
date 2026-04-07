# Agent Monster

> 🐤 Turn your GitHub repository into a digital pet and battle other developers!

**Agent Monster** is a slow-paced养成 game built on the GitHub ecosystem. Your code repository is the pet's home, and code commits are the pet's food.

---

## 🚀 Quick Start

### 1. Fork the Base Repository

```bash
# Using GitHub CLI
gh repo fork agent-monster/agent-monster-pet

# Or fork manually on GitHub
```

### 2. Clone to Your Local Machine

```bash
git clone https://github.com/chengjia2016/agent-monster-pet
cd agent-monster-pet
```

### 3. Install and Claim Your Pet

```bash
# Windows
install.bat

# Linux/macOS
./install.sh
```

**Initial Rewards:**
- 🐤 **Little Yellow Duck** (Starter Pet)
- 🥚 **Pet Egg** x1 (Hatches after 72 hours)

---

## 🎮 Gameplay

### Food System (Cookie)

Hide food items in code comments across any repository:

```python
# 🍪 agent_monster cookie 0x67678328732673287
def my_function():
    pass
```

```javascript
// 🍩 agent_monster cookie 0xabcdef1234567890
const x = 1;
```

```markdown
<!-- 🍎 agent_monster cookie 0x1234567890abcdef -->
```

**Food Types:**
| Food | Effect |
|------|--------|
| 🍪 Cookie | +10 EXP |
| 🍩 Donut | +50 EN |
| 🍎 Apple | +5 All Stats |
| 🧬 Gene | Gene Mutation (during hatching) |

### Egg Incubation

The pet egg requires **72 hours** to collect behavioral genes:

| Behavior | Gene Impact |
|----------|-------------|
| Writing Code (commits) | Logic Gene |
| Writing Docs (md files) | Creative Gene |
| Writing Configs (yaml/json) | Speed Gene |
| Hiding Cookies | Lucky Gene |

### Battle System

```bash
# In Claude Code
/monster duel opponent/repo
```

---

## 📡 GitHub Actions Game Server

This project uses GitHub Actions as the game server:

| Workflow | Frequency | Purpose |
|----------|-----------|---------|
| `hourly-settlement.yml` | Hourly | Settle cookies, restore energy |
| `daily-rank.yml` | Daily | Update leaderboards |
| `battle-arena.yml` | Manual/Trigger | Battle simulation |

### Enable Actions

```bash
gh workflow enable hourly-settlement.yml
gh workflow enable daily-rank.yml
gh workflow enable battle-arena.yml
```

---

## 🎯 Command Reference

### Claude Code MCP Commands

```
/monster init       - Claim starter pet
/monster status     - View pet status
/monster analyze    - Analyze repository activity
/monster traps      - Scan code traps
/monster duel       - Start a battle challenge
```

### CLI Commands

```bash
python monster.py status     # View status
python monster.py analyze    # Analyze repository
python monster.py traps      # Scan traps
python cookie.py generate    # Generate food
python cookie.py scan        # Scan food items
```

---

## 📊 Leaderboards

### Personal Leaderboard

Each repository's `leaderboard.json`:

```json
{
  "player": "your-name",
  "pet_name": "Little Yellow Duck",
  "level": 25,
  "battles": {
    "win": 15,
    "lose": 8
  }
}
```

### Global Leaderboard

The central repository aggregates all players' `leaderboard.json` files.

---

## 📁 File Structure

```
agent-monster-pet/
├── .monster/
│   ├── pet.soul            # Pet data
│   ├── egg.yaml            # Pet egg (72h)
│   ├── food-bank.json      # Food bank
│   └── guard.yaml          # Defense config
├── .github/
│   └── workflows/
│       ├── hourly-settlement.yml
│       ├── daily-rank.yml
│       └── battle-arena.yml
├── battle-reports/         # Battle records
├── cookies/                # Food factory
├── leaderboard.json        # Personal leaderboard
├── monster.py              # Main CLI
├── cookie.py               # Food generator
├── claim_pet.py            # Claim pet
└── README.md               # Pet showcase page
```

---

## 🔧 Configure MCP Server

Add to `~/.claude/settings.json`:

```json
{
  "mcpServers": {
    "agent-monster": {
      "command": "python",
      "args": ["mcp_server.py", "mcp"],
      "cwd": "/path/to/agentmonster"
    }
  }
}
```

---

## 🏆 Game Objectives

1. **Hatch the Strongest Pet** - Collect genes over 72 hours
2. **Top the Leaderboard** - Daily/Weekly/Season rankings
3. **Win Battles** - Defeat other players' pets
4. **Collect Food** - Hide the most cookies in code

---

## 📖 Documentation

- [Game Design](GAME%20DESIGN.md)
- [Installation Guide](INSTALL.md)
- [Plugin README](PLUGIN%20README.md)
- [MCP Configuration](CLAUDE.md)
- [Quick Start](QUICKSTART.md)

---

## 🤝 Contributing

1. Fork this repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a new Pull Request

---

## 📝 License

MIT License

---

**Start Battling!** ⚔️🐤
