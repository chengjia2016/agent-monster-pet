# 🎮 Agent Monster 交互式菜单系统指南

## 概述

交互式菜单系统是一个为 OpenCode 和 Claude Code 设计的完整的 CLI 菜单界面。它使玩家可以通过简单的数字输入来操作游戏，而不需要记住复杂的命令。

## 系统架构

### 核心组件

```
MenuManager
├── MenuSession (菜单会话)
│   ├── user_id
│   ├── github_login
│   ├── current_menu
│   ├── last_action
│   └── history
├── UserManager (用户管理)
├── EconomyManager (经济管理)
├── Shop (商店管理)
└── OnboardingManager (新用户初始化)
```

### 菜单类型

| 菜单类型 | 说明 | 功能 |
|---------|------|------|
| MAIN | 主菜单 | 游戏主界面，选择各个模块 |
| ACCOUNT | 账户菜单 | 查看用户资料和账户统计 |
| SHOP | 商店菜单 | 浏览和购买物品 |
| INVENTORY | 背包菜单 | 查看拥有的物品 |
| BATTLE | 对战菜单 | 与其他玩家对战 (开发中) |
| SETTINGS | 设置菜单 | 游戏设置 (开发中) |
| HELP | 帮助菜单 | 游戏指南和帮助信息 |

## 使用方法

### 1. 启动菜单系统

**MCP 命令:**
```
menu_start
参数: github_username (你的GitHub用户名)
```

**示例:**
```
在 Claude Code 或 OpenCode 中调用:
/monster menu_start username:alice
```

**响应:**
显示主菜单，包含所有可用选项的列表。

### 2. 在菜单中选择操作

**MCP 命令:**
```
menu_action
参数: 
  - github_username: 你的GitHub用户名
  - action: 选择的编号 (0-9)
```

**示例:**
```
选择选项1 (账户信息):
/monster menu_action username:alice action:1

选择选项2 (商店):
/monster menu_action username:alice action:2

返回主菜单:
/monster menu_action username:alice action:0
```

## 主菜单选项

### 主菜单 (MenuType.MAIN)

```
🎮 Agent Monster 主菜单
═════════════════════════
1. 👤 账户信息 - 查看个人资料和统计
2. 🏪 商店 - 购买物品
3. 📦 背包 - 查看物品清单
4. ⚔️ 对战 - 与其他玩家对战
5. 🎰 精灵 - 管理你的精灵
6. ⚙️ 设置 - 游戏设置
7. ❓ 帮助 - 查看帮助信息
0. 🚪 退出 - 保存并退出游戏
```

### 账户菜单 (MenuType.ACCOUNT)

显示内容:
- 用户名
- GitHub ID
- 加入时间
- 当前余额
- 总收入和支出
- 最近5笔交易

### 商店菜单 (MenuType.SHOP)

显示所有可购买物品:
- 精灵球 (Poké Ball)
- 超级球 (Ultra Ball)
- 草种子 (Grass Seed)
- 水种子 (Water Seed)
- 小药剂 (Small Potion)
- 复活液 (Revive)
- 增强剂 (Boost)

### 背包菜单 (MenuType.INVENTORY)

显示用户拥有的所有物品及数量。

### 帮助菜单 (MenuType.HELP)

包含:
1. 新用户注册指南
2. 经济系统说明
3. 物品种类介绍
4. 对战系统说明
5. 背包管理指南
6. 游戏小贴士

## 会话管理

### 会话存储

会话存储在 `.monster/menu_sessions.json` 文件中:

```json
{
  "alice": {
    "user_id": "a1b2c3d4",
    "github_login": "alice",
    "current_menu": "main",
    "last_action": "1",
    "history": ["main", "account", "main"]
  },
  "bob": {
    "user_id": "b2c3d4e5",
    "github_login": "bob",
    "current_menu": "shop",
    "last_action": "2",
    "history": []
  }
}
```

### 多用户支持

系统支持多个用户同时玩耍，每个用户有独立的菜单状态:

```python
# 用户1导航到商店
menu_manager.handle_action("alice", "2")

# 用户2导航到账户
menu_manager.handle_action("bob", "1")

# 各自保持独立的菜单状态
session_alice = menu_manager.get_session("alice")  # 商店菜单
session_bob = menu_manager.get_session("bob")      # 账户菜单
```

## 完整游戏流程示例

### 1. 新用户加入

```
用户: alice
1️⃣ 调用 /monster menu_start username:alice
   → 系统自动注册新用户
   → 分配 100 精灵币
   → 分配启动物品和精灵
   → 显示主菜单

2️⃣ 查看账户信息
   调用 /monster menu_action username:alice action:1
   → 显示账户菜单
   → 看到 100 精灵币的初始余额

3️⃣ 进入商店
   调用 /monster menu_action username:alice action:0
   (返回主菜单)
   调用 /monster menu_action username:alice action:2
   → 显示商店菜单
   → 看到所有可购买物品

4️⃣ 查看背包
   调用 /monster menu_action username:alice action:0
   调用 /monster menu_action username:alice action:3
   → 显示背包菜单
   → 看到初始物品 (3 精灵球, 2 种子, 1 药剂)

5️⃣ 获取帮助
   调用 /monster menu_action username:alice action:7
   → 显示帮助菜单
   → 了解游戏规则

6️⃣ 退出游戏
   调用 /monster menu_action username:alice action:0
   → 游戏自动保存
   → 会话数据持久化到磁盘
```

### 2. 返回游戏

```
用户: alice (再次登入)
1️⃣ 调用 /monster menu_start username:alice
   → 系统检查到用户已存在
   → 加载之前的会话状态
   → 显示主菜单

2️⃣ 继续游戏
   → 账户余额得以保留
   → 物品清单得以保留
   → 交易历史得以保留
```

## 代码示例

### Python 集成

```python
from menu_system import MenuManager

# 初始化菜单系统
menu_manager = MenuManager(".monster")

# 启动用户会话
session = menu_manager.start_session("alice")

# 显示主菜单
menu_text, options = menu_manager.get_menu_display("alice")
print(menu_text)

# 处理用户操作
continue_menu, message = menu_manager.handle_action("alice", "2")
print(message)

# 获取新菜单
menu_text, options = menu_manager.get_menu_display("alice")
print(menu_text)
```

### MCP 集成

菜单系统已内置于 MCP 服务器中，可通过以下工具调用:

```json
{
  "name": "menu_start",
  "description": "启动交互式游戏菜单系统",
  "inputSchema": {
    "type": "object",
    "properties": {
      "github_username": {"type": "string"}
    },
    "required": ["github_username"]
  }
}

{
  "name": "menu_action",
  "description": "在菜单中执行操作",
  "inputSchema": {
    "type": "object",
    "properties": {
      "github_username": {"type": "string"},
      "action": {"type": "string"}
    },
    "required": ["github_username", "action"]
  }
}
```

## 特性列表

- ✅ **交互式菜单**: 使用数字选择操作
- ✅ **菜单导航**: 轻松在不同菜单间切换
- ✅ **会话管理**: 自动保存和恢复用户状态
- ✅ **多用户支持**: 支持多个用户同时游戏
- ✅ **漂亮的UI**: 使用 Unicode 符号和格式化文本
- ✅ **帮助系统**: 内置游戏指南
- ✅ **数据持久化**: 所有会话状态保存到磁盘

## 未来功能

- 🚧 **购买确认**: 菜单中直接购买物品
- 🚧 **对战菜单**: 在菜单中选择对手并对战
- 🚧 **精灵管理**: 查看和管理你的精灵
- 🚧 **交易系统**: 在菜单中进行交易
- 🚧 **排行榜**: 查看全局排行榜
- 🚧 **成就系统**: 查看已解锁的成就

## 常见问题

### Q: 如何重新开始游戏?
A: 使用不同的 GitHub 用户名调用 menu_start，系统会为新账户初始化。

### Q: 我的游戏数据会保存吗?
A: 是的，所有数据都自动保存到 `.monster/menu_sessions.json` 和其他数据文件。

### Q: 可以同时玩多个账户吗?
A: 可以，系统支持无限数量的并发用户。

### Q: 如何导出我的游戏数据?
A: 游戏数据存储在 `.monster/` 目录中的 JSON 文件中，可以直接访问和导出。

## 故障排除

### 菜单无响应
- 检查网络连接
- 验证 MCP 服务器是否正在运行
- 检查 GitHub 用户名是否正确

### 会话丢失
- 检查 `.monster/menu_sessions.json` 文件是否存在
- 确认磁盘空间足够
- 尝试重新启动菜单系统

### 菜单显示错误
- 清理缓存: 删除 `.monster/menu_sessions.json`
- 重新启动游戏
- 报告问题到项目 GitHub issues

## 性能指标

| 指标 | 值 |
|-----|-----|
| 菜单加载时间 | < 100ms |
| 会话切换时间 | < 50ms |
| 支持的并发用户 | 无限制* |
| 会话数据大小 | ~200 bytes/user |

*受系统内存限制

## 文件结构

```
.monster/
├── menu_sessions.json       # 菜单会话数据
├── users/                   # 用户数据
│   ├── user_id.json
│   └── ...
├── accounts/                # 账户数据
│   ├── user_id.json
│   └── ...
├── inventory/               # 物品清单
│   ├── user_id.json
│   └── ...
└── shop.json               # 商店数据
```

## 开发指南

### 添加新菜单

```python
class MenuType(Enum):
    CUSTOM = "custom"  # 添加新菜单类型

def render_custom_menu(self, github_login: str) -> Tuple[str, List]:
    """渲染自定义菜单"""
    menu_text = "..."
    options = [...]
    return menu_text, options
```

### 处理新操作

```python
def handle_action(self, github_login: str, action: str):
    # ...
    elif current_menu == MenuType.CUSTOM:
        if action == "1":
            # 处理操作
            return True, "消息"
```

## 许可证

此系统是 Agent Monster 项目的一部分。

## 联系方式

如有问题或建议，请提交 issue 或联系开发者。
