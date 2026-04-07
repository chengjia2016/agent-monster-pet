# 🎮 Agent Monster 快速开始指南

## 最简单的启动方式

### 第一步：安装 GitHub CLI
```bash
# macOS
brew install gh

# Linux
sudo apt install gh  # Ubuntu/Debian
sudo dnf install gh  # Fedora

# Windows
choco install gh
```

### 第二步：登录 GitHub
```bash
gh auth login
```

按照提示完成登录（选择 HTTPS，然后粘贴 token）

### 第三步：启动游戏

在 OpenCode/Claude Code 中简单地输入：

```
/monster
```

或使用 MCP 工具：
```
monster_simple_start
```

就这么简单！🎉

---

## 如何工作

1. **自动检测**: `/monster` 命令自动从你的 GitHub CLI 获取用户名
2. **快速启动**: 系统自动创建用户账户（如果不存在）
3. **菜单系统**: 显示交互式菜单供你选择

---

## 其他实用命令

| 命令 | 说明 |
|------|------|
| `/monster` | 快速启动（推荐）|
| `/monster help` | 查看所有可用命令 |
| `/monster menu username:你的github用户名` | 传统方式启动菜单 |
| `/monster shop list` | 列出商店商品 |
| `/monster balance username:你的github用户名` | 查看账户余额 |

---

## 故障排除

### 问题：提示 "未认证"

**解决方案**：运行 `gh auth login` 完成登录

```bash
gh auth login
# 选择: GitHub.com
# 协议: HTTPS
# 认证方式: 粘贴 token
```

### 问题：命令不工作

**检查清单**:
- [ ] 已安装 GitHub CLI (`which gh`)
- [ ] 已登录 GitHub (`gh auth status`)
- [ ] 已安装 Python 依赖 (`pip install -r requirements.txt`)
- [ ] MCP 服务器已配置 (`.claude/settings.json`)

---

## MCP 配置（一次性设置）

如果还没有配置，创建 `~/.claude/settings.json`：

**Linux/macOS:**
```json
{
  "mcpServers": {
    "agent-monster": {
      "command": "python3",
      "args": ["/root/pet/agent-monster-pet/mcp_server.py", "mcp"]
    }
  }
}
```

**Windows:**
```json
{
  "mcpServers": {
    "agent-monster": {
      "command": "python",
      "args": ["C:/path/to/agent-monster-pet/mcp_server.py", "mcp"]
    }
  }
}
```

---

## 现在可以开始游戏了！

输入 `/monster` 开始你的冒险吧！ 🎮

有问题？输入 `/monster help` 查看完整文档。
