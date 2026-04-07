# MCP Server 数据同步集成方案

## 现状分析

### Judge Server
- ✅ 已存在，由Go实现 (不上传GitHub)
- ✅ 端点：宠物验证、对战验证、排行榜、食物、蛋孵化、捕获
- ❌ 不包含用户账户管理功能

### MCP Server (Python)
- ✅ 用户管理系统（本地存储）
- ✅ 经济系统（精灵币、交易）
- ✅ 库存系统（物品管理）
- 🔄 待集成：混合存储 (本地 + Judge Server)

## 实现方案

### Phase 1: 启用MCP Server混合存储（当前）
**目标**：为所有MCP Server操作启用本地缓存 + 数据同步

```
MCP Server
    ↓
UnifiedDataManager (NEW)
    ├─ 本地存储 (Primary)
    │  └─ .monster/
    │     ├── users/
    │     ├── accounts/
    │     ├── inventory/
    │     └── user_cache/ ← 混合存储缓存
    │
    └─ Judge Server (未来扩展)
       └─ 待实现的用户API
```

### Phase 2: 数据迁移（可选）
**目标**：准备数据以供将来上传到Judge Server用户管理系统

```bash
# 将本地用户数据缓存到混合存储格式
python3 migrate_to_judge_server.py
```

### Phase 3: 未来 - Judge Server扩展
**目标**：当Judge Server添加用户API时，启用完整的混合存储

```go
// 在judge-server/cmd/main.go中添加
http.HandleFunc("/api/users/create", h.CreateUser)
http.HandleFunc("/api/users/{github_id}", h.GetUser)
http.HandleFunc("/api/users/{github_id}/balance", h.GetBalance)
http.HandleFunc("/api/users/{github_id}/balance", h.UpdateBalance)
// ... 更多端点
```

## 当前行动计划

### ✅ 已完成
1. ✅ 修复`user.github_id` → `user.user_id` bug
2. ✅ 创建`UnifiedDataManager`
3. ✅ 创建数据迁移工具
4. ✅ 集成测试（5/5通过）
5. ✅ 文档完成

### 🔄 现在要做 (3个任务)
1. **启用MCP Server中的混合存储** 
   - 在mcp_server.py中导入UnifiedDataManager
   - 更新用户相关命令使用混合存储
   - 测试所有操作

2. **运行数据迁移脚本**
   - 执行dry-run验证
   - 执行live migration缓存所有用户
   - 验证数据完整性

3. **验证端到端流程**
   - 新用户注册测试
   - 账户操作测试
   - 离线模式测试

## 实现细节

### MCP Server 集成示例

```python
# mcp_server.py中
from mcp_data_manager import get_data_manager

def cmd_user_info(github_username):
    dm = get_data_manager()  # 使用混合存储
    profile = dm.get_user_profile(github_username)
    
    if not profile:
        return "❌ User not found"
    
    return f"""✓ User: {profile['github_login']}
Balance: {profile['balance']} coins
Status: {dm.get_sync_status()['mode']}"""

def cmd_purchase_item(github_username, item_id, quantity):
    dm = get_data_manager()
    user = dm.find_user_by_login(github_username)
    
    if not user:
        return "❌ User not found"
    
    result = dm.purchase_item(user.user_id, item_id, quantity)
    # 自动同步到混合存储
    return f"✓ Purchase successful. New balance: {result['new_balance']}"
```

### 数据同步流程

```
User Operation
    ↓
UnifiedDataManager.save_user_data()
    ├─ Save to local storage (同步)
    ├─ Cache to .monster/user_cache/ (同步)
    └─ Sync to Judge Server (异步，可选)
```

## 文件说明

| 文件 | 用途 | 状态 |
|------|------|------|
| unified_data_manager.py | 主数据管理API | ✅ 完成 |
| mcp_data_manager.py | MCP集成层 | ✅ 完成 |
| hybrid_user_data_manager.py | 混合存储实现 | ✅ 完成 |
| migrate_to_judge_server.py | 数据迁移工具 | ✅ 完成 |
| test_judge_server_integration.py | 集成测试 | ✅ 完成 (5/5pass) |

## 后续扩展（当Judge Server添加用户API时）

### 在judge-server中添加

```go
// judge-server/internal/handler/users.go (NEW)
func (h *Handler) CreateUser(w http.ResponseWriter, r *http.Request) { ... }
func (h *Handler) GetUser(w http.ResponseWriter, r *http.Request) { ... }
func (h *Handler) UpdateBalance(w http.ResponseWriter, r *http.Request) { ... }
func (h *Handler) GetBalance(w http.ResponseWriter, r *http.Request) { ... }
func (h *Handler) AddItem(w http.ResponseWriter, r *http.Request) { ... }
func (h *Handler) GetItems(w http.ResponseWriter, r *http.Request) { ... }
// ... 等等
```

### 在MCP Server中启用

```python
# mcp_server.py中
# 将enable_server_sync从False改为True
dm = get_data_manager(enable_server_sync=True)
```

## 风险评估

| 风险 | 影响 | 缓解措施 |
|------|------|---------|
| Judge Server未实现用户API | 低 | 使用本地存储，API就绪时直接启用 |
| 数据迁移失败 | 中 | Dry-run测试，完整备份，逐个用户验证 |
| 同步延迟 | 低 | 异步操作不阻塞用户，有本地缓存 |

## 验收标准

✅ 混合存储启用：
- [ ] UnifiedDataManager在所有MCP命令中使用
- [ ] 本地缓存正常工作
- [ ] 离线模式可用

✅ 数据迁移完成：
- [ ] 所有11个用户数据已缓存
- [ ] 数据完整性验证通过
- [ ] 迁移日志记录完整

✅ 端到端测试：
- [ ] 新用户注册成功
- [ ] 账户操作正常
- [ ] 离线/在线切换无缝

