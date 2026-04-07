# 🌐 Judge Server 用户数据集中管理系统

## 架构设计

本系统实现了**混合数据存储架构**:

```
┌─────────────────────────────────────────────────────────────┐
│                        客户端 (OpenCode)                      │
│  - 游戏菜单  - 精灵管理  - 背包  - 对战                       │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌─────────────────┐      ┌──────────────────┐
│   本地缓存       │      │  MCP/CLI命令    │
│ (离线访问)      │      │                  │
└─────────────────┘      └────────┬─────────┘
        ▲                         │
        └────────────┬────────────┘
                     ▼
        ┌────────────────────────┐
        │  混合数据管理器         │
        │ Hybrid Data Manager    │
        └────────────┬───────────┘
                     │ (数据同步)
                     ▼
        ┌────────────────────────┐
        │   裁判服务器数据库     │
        │  Judge Server DB       │
        │ (数据源、权限验证)     │
        └────────────────────────┘
```

---

## 数据模型

### 用户账户 (UserAccount)
```python
{
  "github_id": 24448747,           # GitHub 数字 ID (主键)
  "github_login": "chengjia2016",  # GitHub 用户名
  "balance": 150.50,               # 精灵币余额
  "pokemons": [                    # 拥有的精灵
    {
      "id": "pkmn_001",
      "name": "Pikachu",
      "level": 5,
      "hp": 25,
      "max_hp": 25
    }
  ],
  "items": [                       # 背包物品
    {"item_id": "ball_red", "quantity": 10},
    {"item_id": "potion_small", "quantity": 3}
  ],
  "transactions": [],              # 交易历史
  "battles_won": 3,                # 胜利场数
  "battles_lost": 1,               # 失败场数
  "created_at": "2026-04-07T...",  # 创建时间
  "last_login": "2026-04-07T...",  # 最后登录
}
```

### 精灵数据 (Pokemon)
```python
{
  "id": "pkmn_001",
  "name": "Pikachu",
  "species": "Pikachu",
  "level": 5,
  "exp": 100,
  "hp": 25,
  "max_hp": 25,
  "attack": 12,
  "defense": 10,
  "sp_attack": 15,
  "sp_defense": 10,
  "speed": 18,
  "moves": ["Thunder Shock", "Tail Whip"],
  "caught_at": "2026-04-07T..."
}
```

### 背包物品 (Item)
```python
{
  "item_id": "ball_red",
  "name": "Poké Ball",
  "quantity": 10,
  "rarity": "common",
  "added_at": "2026-04-07T..."
}
```

---

## API 端点设计

### 用户管理

#### 创建用户
```
POST /api/users/create
Request: { "github_id": 24448747, "github_login": "chengjia2016", "initial_balance": 100 }
Response: { "success": true, "user": {...} }
```

#### 获取用户
```
GET /api/users/{github_id}
Response: { "success": true, "user": {...} }
```

#### 更新余额
```
PUT /api/users/{github_id}/balance
Request: { "amount": 50, "transaction_type": "PURCHASE" }
Response: { "success": true, "new_balance": 150 }
```

### 精灵管理

#### 添加精灵
```
POST /api/users/{github_id}/pokemons
Request: { "pokemon": {...} }
Response: { "success": true, "pokemon_id": "pkmn_001" }
```

#### 获取精灵列表
```
GET /api/users/{github_id}/pokemons
Response: { "success": true, "pokemons": [...] }
```

#### 更新精灵
```
PUT /api/users/{github_id}/pokemons/{pokemon_id}
Request: { "hp": 20, "level": 6 }
Response: { "success": true, "pokemon": {...} }
```

### 背包管理

#### 添加物品
```
POST /api/users/{github_id}/items
Request: { "item_id": "ball_red", "quantity": 5 }
Response: { "success": true, "item": {...} }
```

#### 获取物品列表
```
GET /api/users/{github_id}/items
Response: { "success": true, "items": [...] }
```

#### 使用物品
```
PUT /api/users/{github_id}/items/{item_id}
Request: { "action": "use", "quantity": 1 }
Response: { "success": true, "remaining": 4 }
```

### 统计数据

#### 获取用户统计
```
GET /api/users/{github_id}/stats
Response: {
  "success": true,
  "stats": {
    "balance": 150.50,
    "pokemons_count": 5,
    "items_count": 15,
    "battles_won": 3,
    "battles_lost": 1
  }
}
```

### 同步

#### 全量同步
```
PUT /api/users/{github_id}/sync
Request: { 全部用户数据 }
Response: { "success": true }
```

---

## 实现步骤

### 1️⃣ 部署裁判服务器数据库

在 `agentmonster.openx.pro:10000` 上创建数据表:

```sql
-- 用户表
CREATE TABLE users (
  github_id INT PRIMARY KEY,
  github_login VARCHAR(255) UNIQUE,
  balance FLOAT DEFAULT 100.0,
  total_income FLOAT DEFAULT 0.0,
  total_expense FLOAT DEFAULT 0.0,
  battles_won INT DEFAULT 0,
  battles_lost INT DEFAULT 0,
  pokemons_caught INT DEFAULT 0,
  created_at TIMESTAMP,
  last_login TIMESTAMP,
  last_updated TIMESTAMP
);

-- 精灵表
CREATE TABLE pokemons (
  id VARCHAR(255) PRIMARY KEY,
  github_id INT REFERENCES users(github_id),
  name VARCHAR(255),
  species VARCHAR(255),
  level INT,
  exp INT,
  hp INT,
  max_hp INT,
  attack INT,
  defense INT,
  sp_attack INT,
  sp_defense INT,
  speed INT,
  moves JSON,
  caught_at TIMESTAMP
);

-- 背包表
CREATE TABLE inventory (
  id VARCHAR(255) PRIMARY KEY,
  github_id INT REFERENCES users(github_id),
  item_id VARCHAR(255),
  name VARCHAR(255),
  quantity INT,
  rarity VARCHAR(50),
  added_at TIMESTAMP
);

-- 交易表
CREATE TABLE transactions (
  id VARCHAR(255) PRIMARY KEY,
  github_id INT REFERENCES users(github_id),
  amount FLOAT,
  transaction_type VARCHAR(50),
  description VARCHAR(255),
  balance_before FLOAT,
  balance_after FLOAT,
  timestamp TIMESTAMP
);

-- 对战表
CREATE TABLE battles (
  battle_id VARCHAR(255) PRIMARY KEY,
  player1_github_id INT REFERENCES users(github_id),
  player2_github_id INT REFERENCES users(github_id),
  player1_pokemon JSON,
  player2_pokemon JSON,
  winner_github_id INT REFERENCES users(github_id),
  prize_coins FLOAT,
  duration_seconds INT,
  timestamp TIMESTAMP
);
```

### 2️⃣ 更新 MCP 服务器集成

在 `mcp_server.py` 中使用新的管理器:

```python
from judge_server_user_manager import get_judge_server_manager
from hybrid_user_data_manager import HybridUserDataManager

# 初始化
judge_mgr = get_judge_server_manager()
hybrid_mgr = HybridUserDataManager(MONSTER_DIR, judge_mgr)

# 获取用户数据
user_data = hybrid_mgr.get_user_data(github_id=24448747)

# 保存用户数据
hybrid_mgr.save_user_data(github_id=24448747, user_data=user_data)
```

### 3️⃣ 迁移现有数据

运行迁移脚本将所有本地数据上传到服务器:

```python
from judge_server_user_manager import JudgeServerUserManager
import json
from pathlib import Path

manager = JudgeServerUserManager()
users_dir = Path(".monster/users")

for user_file in users_dir.glob("*.json"):
    with open(user_file) as f:
        user_data = json.load(f)
        github_id = user_data.get('github_id')
        if github_id:
            manager.create_user(
                github_id=github_id,
                github_login=user_data.get('github_login'),
                initial_balance=100.0
            )
```

### 4️⃣ 测试集成

```bash
# 测试服务器连接
python3 judge_server_user_manager.py

# 测试数据管理
python3 hybrid_user_data_manager.py

# 测试 MCP 命令
/monster menu
```

---

## 优势

✅ **数据集中化**: 所有用户数据存储在一个可靠的服务器上  
✅ **权限验证**: GitHub ID 作为唯一标识，防止欺骗  
✅ **跨平台同步**: 用户可以在任何设备上访问数据  
✅ **对战验证**: 所有交易和对战都可以在服务器上验证  
✅ **离线支持**: 本地缓存允许离线访问  
✅ **自动同步**: 后台自动同步本地更改到服务器  

---

## 迁移计划

| 阶段 | 任务 | 时间 |
|------|------|------|
| **1** | 部署数据表 | Day 1 |
| **2** | 实现 API 端点 | Day 2-3 |
| **3** | 集成 MCP | Day 4 |
| **4** | 数据迁移 | Day 5 |
| **5** | 测试和验证 | Day 6-7 |
| **6** | 上线 | Day 8 |

---

## 故障转移

如果裁判服务器离线:

1. **自动降级**: 使用本地缓存
2. **排队**: 记录所有更改
3. **重新连接**: 服务器恢复时自动同步
4. **冲突解决**: 服务器数据优先

```python
if not hybrid_manager.is_server_online():
    # Use local cache
    user_data = hybrid_manager._get_cached_user_data(github_id)
    # Queue changes for later sync
    queue_change(github_id, user_data)
```

---

## 安全性

🔐 **GitHub ID 验证**: 每个用户由 GitHub ID 唯一标识  
🔐 **Token 保护**: 所有 API 调用使用 GitHub token  
🔐 **时间戳验证**: 防止重放攻击  
🔐 **交易签名**: 所有交易都有签名和验证

---

## 下一步

1. **部署数据库**: 在裁判服务器上创建表
2. **实现 API**: 创建所有必要的端点
3. **集成测试**: 验证数据流
4. **用户迁移**: 将现有用户数据移到服务器
5. **上线**: 启用服务器存储
