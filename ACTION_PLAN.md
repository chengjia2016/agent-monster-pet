# 🎯 Agent Monster 优先级行动计划

## 立即行动项（今天）

### ✅ 已完成
- [x] 修复 cookie.py `import os` bug
- [x] 完成全面审计（1,484 行文档）
- [x] 识别所有临界问题和阻塞项

---

## 🔴 第一阶段：临界修复（第 1 周）

### 1. 创建 Judge Server Schema（3 小时）- **TODAY START**
**优先级**: ⭐⭐⭐⭐⭐ 最高

需要为以下数据创建 Go 模型和数据库表：

#### Egg（蛋系统）
- ID, OwnerGithubID, Name
- IncubationTime (剩余秒数)
- HatchTime, CreatedAt

#### Farm（农场系统）
- ID, OwnerGithubID, Repository
- URL, Foods (列表), PlantedAt

#### Food（食物系统）
- ID, FarmID, Type (cookie/donut/apple/gene)
- Quantity, MaxQuantity, RegenerationHours
- LastEatenAt, EatingHistory, CreatedAt

#### CookieFragment（Cookie 碎片）
- ID, Hash (0xABC...), Type
- File (源文件), ClaimedBy, ClaimedAt

**实现位置**:
- `judge-server/internal/model/egg.go`
- `judge-server/internal/model/farm.go`
- `judge-server/internal/model/food.go`
- `judge-server/internal/model/cookie.go`

---

### 2. 创建 API 端点（5 小时）

#### Egg API
```
POST   /api/eggs/create
GET    /api/eggs/{github_id}
PUT    /api/eggs/{egg_id}/hatch
DELETE /api/eggs/{egg_id}
```

#### Farm API
```
POST   /api/farms/create
GET    /api/farms/{owner}/{repo}
GET    /api/farms/search?query=...
PUT    /api/farms/{farm_id}
DELETE /api/farms/{farm_id}
```

#### Food API
```
POST   /api/foods/add
GET    /api/foods/farm/{farm_id}
GET    /api/foods/search?type=cookie
POST   /api/foods/{food_id}/consume
PUT    /api/foods/{food_id}/regenerate
```

#### Cookie API
```
GET    /api/cookies/search?hash=0x...
POST   /api/cookies/claim
GET    /api/cookies/claimed/{github_id}
GET    /api/cookies/statistics
```

**实现位置**: `judge-server/internal/handler/`

---

### 3. 修复食物系统持久化（8 小时）

**问题**: food_system.py 中的农场数据只在内存中存储，应用重启后丢失。

**文件**: `food_system.py`

**需要做**:
1. 创建 `JudgeServerFoodManager` 包装器
2. 转发所有操作到 Judge Server API
3. 实现本地缓存（离线备用）
4. 实现自动同步机制

**示例架构**:
```python
class FoodManager:
    def __init__(self, use_server=True):
        self.judge_server = JudgeServerClient()
        self.local_cache = {}  # 离线备用
    
    def create_farm(self, owner, repo):
        try:
            return self.judge_server.post('/api/farms/create', ...)
        except:
            # 离线模式
            farm = Farm(owner=owner, repo=repo)
            self.local_cache[farm.id] = farm
            return farm
```

---

### 4. 修复 Cookie 持久化（6 小时）

**问题**: Cookie 可以生成和扫描，但无处存储、无法索赔。

**文件**: `cookie.py`

**需要实现**:

1. **Cookie 索赔机制**:
```python
def claim_cookie(hash: str, github_id: int) -> bool:
    # 验证 cookie 是否存在且未被索赔
    # 调用 /api/cookies/claim
    # 返回成功/失败
```

2. **Cookie 验证**:
```python
def verify_cookie(hash: str) -> bool:
    # 检查过期时间
    # 验证数字签名
    # 返回有效性
```

3. **Cookie 查询**:
```python
def get_user_cookies(github_id: int):
    # 从 Judge Server 获取用户索赔的 cookies
    # 返回 Cookie 列表
```

---

## 🟡 第二阶段：集成（第 2 周）

- [ ] 集成 Hybrid Manager (2h)
  - 更新 `onboarding_manager.py` 使用 HybridUserDataManager
  - 实现自动同步
  
- [ ] 更新蛋孵化系统 (3h)
  - 迁移 egg_incubator.py 到 Judge Server
  
- [ ] 更新 onboarding 流程 (2h)
  - 确保新用户数据同步到 Judge Server
  
- [ ] 数据迁移测试 (3h)
  - 测试本地数据到 Judge Server 的迁移

## 🟢 第三阶段：验证（第 3 周）

- [ ] 离线模式测试 (4h)
  - 验证当 Judge Server 不可用时系统继续工作
  
- [ ] 负载测试 (3h)
  - 测试同时处理多个用户操作
  
- [ ] 文档更新 (1h)

---

## 📊 时间表

```
Week 1  ████████████ 20h (Schemas + Endpoints + Food/Cookie)
Week 2  ████████     10h (Integration + Migration)
Week 3  ███████      7h  (Testing + Verification)
        ─────────────────
Total   ██████████████ 37h
```

---

## 📈 成功指标

| 指标 | 目标 | 现状 |
|-----|------|------|
| 食物系统持久化 | ✅ Judge Server | ❌ 内存 |
| Cookie 存储 | ✅ Judge Server + 索赔 | ❌ 无存储 |
| Schema 完整性 | ✅ 100% | ❌ 60% |
| 离线模式 | ✅ 支持 | ⚠️ 部分 |
| 同步延迟 | < 5s | ⏳ 未测量 |
| 数据丢失率 | 0% | ❌ 食物系统 |

---

## 📚 参考文档

- `AUDIT_QUICK_REFERENCE.md` - 5 分钟快速概览
- `CODEBASE_AUDIT_REPORT.md` - 完整技术分析（492 行）
- `MIGRATION_DATA_FLOW_DIAGRAM.md` - 架构可视化（425 行）
- `AUDIT_INDEX.md` - 导航指南（200 行）

---

**生成日期**: 2026-04-07  
**状态**: 🟢 准备就绪 → 🟡 实现中  
**预期完成**: 1 周内
