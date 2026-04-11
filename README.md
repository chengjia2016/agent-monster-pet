# Agent Monster (代码怪兽) 👾

> **The AI-Powered RPG where your GitHub repository becomes a digital pet.**
> **基于 GitHub 生态的 AI 驱动 RPG 游戏：让你的仓库进化成数字宠物。**

---

## 🌟 Introduction / 简介

**Agent Monster** has evolved. We've moved beyond traditional menus to a **Natural Language First** gameplay experience. Powered by AI agents (Gemini CLI, Claude Code, OpenCode) and a high-performance **Go-based Judge Server**, you can now play the game just by talking to your terminal.

**代码怪兽** 已经完成了全面进化。我们告别了传统的繁琐菜单，转而采用**自然语言优先**的游戏体验。在 AI 助手（如 Gemini CLI, Claude Code, OpenCode）和高性能 **Go 编写的裁判服务器**的支持下，你现在只需在终端通过对话即可进行游戏。

---

## 🚀 Quick Start for Forkers / Fork 用户快速开始

If you just forked this repository, setting up your base is as easy as one sentence:
如果你刚刚 Fork 了本仓库，建立基地只需一句话：

> **"I just forked this repo, setup my base and map for me."**
> **"我刚刚 Fork 了这个仓库，帮我建立基地和地图。"**

The AI will automatically:
AI 将会自动执行：
1. **Register** your trainer ID / **注册**训练师身份。
2. **Initialize** your monster from your commit history / **初始化**宠物（基于你的代码提交记录）。
3. **Establish** your Farm (Base) / **建立**你的个人基地。
4. **Generate** your first adventure map / **生成**第一张冒险地图。

---

## 🎮 How to Play / 玩法介绍

### 1. Natural Language Interface / 自然语言交互
You don't need to remember complex CLI arguments. Just tell the AI what you want to do:
你不需要记住复杂的命令行参数，直接告诉 AI 你的意图：

- *"Show my monster status"* / *"查看我的宠物状态"*
- *"Analyze my recent code activity to train my pet"* / *"分析我最近的代码记录来训练宠物"*
- *"I want to buy two Poké Balls from the shop"* / *"我想去商店买两个精灵球"*
- *"Hatch my egg"* / *"帮我孵蛋"*
- *"Challenge Pikachu to a duel!"* / *"向皮卡丘发起挑战！"*
- *"What should I do next?"* / *"我下一步该做什么？"*
- *"I want to design a new monster"* / *"我想设计一个新的怪兽"*

### 2. Multi-Language Support / 多语言支持
...
---

## 🎨 Community & UGC / 社区与玩家创作

You can now design your own monsters and contribute to the global game world!
您现在可以设计自己的怪兽，并为全球游戏世界做出贡献！

1. **Design**: Use `monster_design` to create your monster's soul metadata.
2. **Submit**: Use `monster_submit_design` to move it to your repository.
3. **Vote**: Share your repository! Once the community votes for your design, it will be added to the global **Egg Pool** for everyone to hatch.

See the [UGC Guide](docs/UGC_GUIDE.md) for details.

---
The game remembers your preference. Start by saying:
游戏会记住你的语言偏好。你可以从这句话开始：
- *"I want to use English"* 或 *"我想用中文"*

### 3. AI Guidance / AI 智能引导
Feeling lost? The `monster_guide` tool analyzes your balance, inventory, and pet status to give you strategic advice.
感到迷茫？AI 助手会实时分析你的余额、背包和宠物状态，为你提供最佳行动建议。

---

## 🌐 Online Architecture / 在线架构

Agent Monster is a **strictly server-authoritative multiplayer game**. 
代码怪兽是一款**严格由服务器授权的多人在线游戏**。

- **The Judge Server (Go)** is the sole authority for battles, items, and stats.
- **裁判服务器 (Go)** 是对战、物品和属性的唯一权威。
- **No Local Simulation**: All game logic is executed and validated online to ensure fairness.
- **无本地模拟**: 所有游戏逻辑均在云端执行和验证，确保公平性。
- **Local Maps**: You can still design maps locally and share them by committing to your repository!
- **本地地图**: 你仍然可以在本地设计地图，并通过提交到你的仓库来分享它们！

---

- **AI Agents**: Deeply integrated via **MCP (Model Context Protocol)**. Supports Gemini CLI, Claude Code, and OpenCode.
- **Judge Server**: A robust backend written in **Go**, ensuring all transactions and battles are fair and validated.
- **Soul Data**: Your pet's DNA is derived from your real-world coding behavior.

- **AI 助手**: 通过 **MCP 协议** 深度集成。支持 Gemini CLI, Claude Code 和 OpenCode。
- **裁判服务器**: 使用 **Go 语言** 编写的高性能后端，确保所有交易和对战公平有效。
- **灵魂数据**: 宠物的基因和属性完全源自你真实的编程行为。

---

## 🔧 Installation & Setup / 安装与配置

### 0. Prerequisites / 必要前提
Since Agent Monster is built on the GitHub ecosystem, the **GitHub CLI (gh)** is required for authentication and repository interactions.
由于代码怪兽基于 GitHub 生态构建，**GitHub CLI (gh)** 是身份验证和仓库交互的必要工具。

1. **Install GitHub CLI**: [Follow official guide](https://cli.github.com/) / **安装 gh**: [参考官方指南](https://cli.github.com/)。
2. **Login**: Run `gh auth login` in your terminal / **登录**: 在终端运行 `gh auth login`。

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Configure MCP & Skills

#### For Claude Code / OpenCode
Add this to your `~/.claude/settings.json`:
```json
{
  "mcpServers": {
    "agent-monster": {
      "command": "python3",
      "args": ["mcp_server.py", "mcp"],
      "cwd": "/absolute/path/to/agent-monster"
    }
  }
}
```

#### For Gemini CLI (Recommended)
Gemini CLI provides the deepest integration via specialized **Skills**. 
Gemini CLI 通过专门的 **Skills** 提供最深度的集成。

1. **Automatic Skill Loading**: Gemini CLI will automatically detect `GEMINI.md` and `MONSTER_SKILL.md` in the workspace.
2. **Setup Command**: Just tell Gemini:
   > *"I want to play Agent Monster, setup the project for me."*
   > *"我想玩代码怪兽，帮我配置项目。"*

Gemini will automatically configure the MCP server, initialize your soul data, and prepare your digital pet environment.
Gemini 会自动配置 MCP 服务、初始化灵魂数据，并准备好数字宠物环境。

### 3. Start the Adventure
Just type `monster_welcome` or talk to the AI to begin!
直接输入 `monster_welcome` 或开始与 AI 对话即可开启冒险！

---

## 📝 License
MIT License

**Start your code-driven adventure today!** ⚔️🦊
