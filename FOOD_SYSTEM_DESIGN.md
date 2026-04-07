# Agent Monster 食物系统设计文档

## 1. 食物系统概述

食物系统允许 Agent Monster 用户在自己的 GitHub 仓库中"种植"食物，其他玩家的宠物可以"来访"并"进食"。食物具有以下特性：

- **生长周期**: 被吃掉后会慢慢恢复
- **营养价值**: 不同食物提供不同的营养和效果
- **多样性**: 多种食物类型，鼓励多样化种植
- **社交性**: 跨仓库访问，促进玩家互动
- **防作弊**: Judge Server 验证所有食物交易

---

## 2. 食物类型定义

### 2.1 食物格式

在代码注释中使用标准格式定义食物：

```python
# 🍪 agent_monster food type:cookie regeneration:24h quantity:3 seed:0x1234abcd
# 🍩 agent_monster food type:donut regeneration:48h quantity:2 seed:0xabcd1234
# 🍎 agent_monster food type:apple regeneration:12h quantity:5 seed:0x5678ef00
# 🧬 agent_monster food type:gene regeneration:72h quantity:1 seed:0xfeedbeef
```

**格式说明:**
- `🍪🍩🍎🧬` - 食物表情符号（视觉识别）
- `type` - 食物类型（cookie/donut/apple/gene）
- `regeneration` - 恢复时间（12h/24h/48h/72h）
- `quantity` - 初始数量（可用份数）
- `seed` - 随机种子（用于验证）

### 2.2 食物类型详情

| 食物 | 表情 | 恢复时间 | 营养值 | 效果 | 描述 |
|------|------|--------|-------|------|------|
| Cookie | 🍪 | 24h | +10 EXP | 基础食物 | 最常见，快速恢复 |
| Donut | 🍩 | 48h | +50 EN | 高能量 | 中等稀有，能量回复 |
| Apple | 🍎 | 12h | +5 All Stats | 全能补给 | 快速恢复，全面提升 |
| Gene | 🧬 | 72h | Gene Mutation | 基因强化 | 最稀有，改变宠物基因 |

---

## 3. 食物种植系统

### 3.1 定义食物农场

用户可以在仓库中创建 `.monster/farm.yaml` 文件定义食物：

```yaml
# .monster/farm.yaml
farm:
  owner: "player_name"
  planted_at: "2026-04-07T00:00:00Z"
  foods:
    - id: "cookie_001"
      type: "cookie"
      emoji: "🍪"
      quantity: 3           # 初始数量
      max_quantity: 3       # 最大容量
      regeneration_hours: 24
      last_eaten_at: null   # 尚未被吃过
      seed: "0x1234abcd"
      
    - id: "gene_001"
      type: "gene"
      emoji: "🧬"
      quantity: 1
      max_quantity: 1
      regeneration_hours: 72
      last_eaten_at: null
      seed: "0xfeedbeef"
```

### 3.2 食物仓库模型

```json
{
  "farm": {
    "owner": "username",
    "repository": "repo_name",
    "url": "https://github.com/username/repo_name",
    "planted_at": "2026-04-07T00:00:00Z",
    "foods": [
      {
        "id": "unique_food_id",
        "type": "cookie",           // cookie, donut, apple, gene
        "emoji": "🍪",
        "quantity": 3,              // 当前数量
        "max_quantity": 3,          // 最大容量
        "regeneration_hours": 24,   // 恢复周期
        "last_eaten_at": null,      // 最后被吃的时间
        "eating_history": [],       // 历史记录
        "seed": "0x1234abcd"        // 用于验证
      }
    ]
  }
}
```

---

## 4. 食物进食系统

### 4.1 进食流程

```
1. 玩家发现其他仓库 (/monster explore)
   ↓
2. 检查该仓库的食物农场 (GET farm.yaml/json)
   ↓
3. 选择要吃的食物并验证可用性
   ↓
4. 发送进食请求到 Judge Server
   ↓
5. Judge Server 验证：
   - 食物确实存在
   - 食物还未被吃过或已恢复
   - 进食者没有超过日限额
   - 防止重复进食同一食物
   ↓
6. 如果验证通过：
   - 标记食物为已吃 (quantity -= 1)
   - 记录进食者信息
   - 给宠物增加营养
   - 返回成功响应
```

### 4.2 进食 API

```
POST /api/food/eat
{
  "id": "eat_0x1234",
  "eater_id": "player_eater",
  "eater_pet_id": "pikachu_001",
  "farm_owner": "player_farmer",
  "farm_repo": "agent-monster-pet",
  "food_id": "cookie_001",
  "eat_time": "2026-04-07T12:00:00Z",
  "signature": "..." // 验证签名
}

Response:
{
  "is_valid": true,
  "success": true,
  "nutrition_gained": {
    "exp": 10,
    "energy": 0,
    "stats": {}
  },
  "next_regeneration": "2026-04-08T12:00:00Z",
  "remaining_quantity": 2
}
```

---

## 5. 食物恢复机制

### 5.1 恢复规则

- **恢复时间**: 每种食物有固定的恢复周期（12h/24h/48h/72h）
- **恢复数量**: 每次恢复 +1 份食物（直到达到最大容量）
- **恢复检查**: Judge Server 在处理进食请求时自动计算恢复

### 5.2 恢复算法

```python
def calculate_food_status(food, current_time):
    """计算食物当前状态"""
    if food.quantity >= food.max_quantity:
        return "ready"  # 已满
    
    if food.last_eaten_at is None:
        return "ready"  # 从未被吃过
    
    # 计算距离上次被吃的时间
    time_elapsed = current_time - food.last_eaten_at
    regeneration_period = timedelta(hours=food.regeneration_hours)
    
    # 计算应该恢复的数量
    cycles_completed = int(time_elapsed / regeneration_period)
    
    if cycles_completed > 0:
        # 恢复食物
        food.quantity = min(
            food.quantity + cycles_completed,
            food.max_quantity
        )
        food.last_eaten_at += cycles_completed * regeneration_period
        return "ready"
    else:
        # 还未恢复
        time_to_regeneration = regeneration_period - time_elapsed
        return f"regenerating_{time_to_regeneration}"
```

---

## 6. 跨仓库探索系统

### 6.1 发现 Agent Monster 用户

```
方式 1: GitHub 搜索
- 搜索含有 ".monster/farm.yaml" 的仓库
- 搜索含有特定 topic 的仓库 ("agent-monster-farm")

方式 2: 中央注册表
- 在中央仓库维护用户列表
- 每个用户自己注册或被自动发现

方式 3: 邀请链接
- 直接输入仓库 URL
- 使用 GitHub @mentions
```

### 6.2 探索 API

```
GET /explore/discover
- 发现新的 Agent Monster 仓库

GET /farm/list?owner=username
- 列出某个用户的所有食物

GET /farm/{owner}/{repo}/foods
- 获取特定仓库的食物列表
```

---

## 7. Judge Server 防作弊验证

### 7.1 需要验证的方面

1. **食物存在性** - 验证食物确实在那个仓库
2. **恢复状态** - 验证食物已恢复或未被吃过
3. **日限额** - 每个玩家每天最多吃 N 顿饭
4. **仓库限额** - 同一仓库每天最多被访问 M 次
5. **重复检查** - 防止同一食物被吃两次
6. **时间戳验证** - 验证时间戳的合理性

### 7.2 防作弊规则

```
规则 1: 日进食限制
- 每个宠物每天最多进食 5 次
- 防止刷屏和农号

规则 2: 仓库访问限制
- 同一仓库每天最多被访问 10 次
- 防止特定用户过度利用单个农场

规则 3: 食物冷却时间
- 同一食物最多 24 小时内只能被吃一次（在恢复前）
- 防止重复操作

规则 4: 地理分散
- 鼓励访问多个不同用户的仓库
- 防止固定对象农场

规则 5: 签名验证
- 所有进食请求必须被 Owner 签名
- 防止未授权操作
```

### 7.3 Judge Server API

```
POST /api/food/validate
{
  "eater_id": "player",
  "eater_pet_id": "pet_001",
  "farm_owner": "farmer",
  "farm_repo": "repo",
  "food_id": "food_001",
  "timestamp": "2026-04-07T12:00:00Z"
}

Response:
{
  "is_valid": true,
  "can_eat": true,  // 是否允许吃
  "reasons": [],
  "daily_eat_count": 3,      // 今天已吃几次
  "daily_eat_limit": 5,
  "repo_visit_count": 2,     // 该仓库今天被访问几次
  "repo_visit_limit": 10,
  "next_available_eat": "2026-04-07T13:00:00Z",  // 下一次可以吃的时间
  "regeneration_ready": true,  // 食物是否已恢复
  "food_status": {
    "quantity": 2,
    "last_eaten_at": "2026-04-06T12:00:00Z",
    "next_ready_at": "2026-04-07T12:00:00Z"
  }
}
```

---

## 8. 用户指南

### 8.1 种植食物

1. 在仓库中创建 `.monster/farm.yaml`
2. 定义食物列表
3. 提交到 GitHub
4. 等待其他玩家来访

### 8.2 探索和进食

```bash
# 发现新的农场
/monster explore

# 查看农场食物
/monster farm list <owner>/<repo>

# 吃食物
/monster feed <owner>/<repo> <food_id>

# 查看进食历史
/monster feed history
```

### 8.3 指标和排行榜

- **农场主排行** - 谁的农场被访问最多
- **美食家排行** - 谁吃了最多食物
- **营养榜** - 谁的宠物营养最高
- **社交榜** - 谁访问了最多不同的农场

---

## 9. 数据存储

### 9.1 数据位置

**食物定义** (由农场主维护)
- 位置: `.monster/farm.yaml` (在用户仓库)
- 格式: YAML
- 访问: 通过 GitHub API 读取

**进食历史** (由 Judge Server 维护)
- 位置: PostgreSQL 数据库
- 表: `food_transactions`
- 内容: 谁吃了什么，什么时候，获得了什么

**用户排行** (由 Judge Server 生成)
- 位置: GitHub Issues (每日更新)
- 或者: 中央仓库的 leaderboard.json

---

## 10. 实现时间表

### Phase 1: 食物系统核心 (1-2 天)
- [ ] 食物数据模型
- [ ] Farm YAML 解析
- [ ] 基础进食 API

### Phase 2: 探索系统 (1-2 天)
- [ ] GitHub 仓库搜索
- [ ] 用户发现机制
- [ ] 农场列表 API

### Phase 3: 防作弊验证 (1-2 天)
- [ ] Judge Server 验证逻辑
- [ ] 限流规则
- [ ] 签名验证

### Phase 4: 用户界面 (1 天)
- [ ] MCP 命令
- [ ] CLI 工具
- [ ] 排行榜显示

### Phase 5: 测试和文档 (1 天)
- [ ] 完整测试
- [ ] 用户文档
- [ ] 示例农场

---

## 11. 未来扩展

1. **食物市场** - 玩家可以交易食物
2. **特殊农场活动** - 限时食物、双倍营养周
3. **农场合作** - 多人联合运营农场
4. **食物链** - 食物可以被其他食物"吃掉"演化
5. **季节变化** - 不同季节不同食物可用

---

## 12. 示例场景

### 场景 1: Alice 种植 Cookie

```yaml
# Alice 的 .monster/farm.yaml
farm:
  owner: "alice"
  foods:
    - id: "cookie_alice_001"
      type: "cookie"
      quantity: 3
      max_quantity: 3
      regeneration_hours: 24
      seed: "0xaabbccdd"
```

Alice 的 Pikachu 获得 3 个 Cookie 供其他玩家食用。

### 场景 2: Bob 访问并进食

1. Bob 使用 `/monster explore` 发现 Alice 的农场
2. Bob 看到 Alice 有 3 个 Cookie
3. Bob 执行 `/monster feed alice/repo cookie_alice_001`
4. Judge Server 验证：
   - Cookie 确实存在 ✓
   - Bob 今天还没吃超过 5 次 ✓
   - Alice 的农场今天还没被访问超过 10 次 ✓
5. Cookie 被消费，Bob 的宠物获得 +10 EXP
6. Alice 的 Cookie 数量变为 2 (需要等 24h 恢复到 3)

### 场景 3: Cookie 恢复

24 小时后，Alice 的 Cookie 自动恢复到 3 个。Bob 可以再次进食。

---

## 13. 数据示例

### 进食请求数据结构

```json
{
  "transaction_id": "txn_0x1234",
  "timestamp": "2026-04-07T12:00:00Z",
  "eater": {
    "user_id": "bob",
    "pet_id": "pikachu_bob_001",
    "pet_name": "Pikachu"
  },
  "farm": {
    "owner": "alice",
    "repo": "alice/agent-monster-pet",
    "repo_url": "https://github.com/alice/agent-monster-pet"
  },
  "food": {
    "food_id": "cookie_alice_001",
    "type": "cookie",
    "nutrition": {
      "exp": 10,
      "energy": 0,
      "hp": 0
    }
  },
  "validation": {
    "is_valid": true,
    "daily_eat_count": 3,
    "repo_visit_count": 2,
    "passed_all_checks": true
  }
}
```

---

