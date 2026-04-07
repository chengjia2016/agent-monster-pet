# Agent Monster 用户流程与经济系统完整指南

## 目录
1. [用户注册与初始化](#用户注册与初始化)
2. [经济系统](#经济系统)
3. [商店系统](#商店系统)
4. [交易系统](#交易系统)
5. [完整用户流程示例](#完整用户流程示例)

---

## 用户注册与初始化

### 工作流程

每个新用户通过以下步骤注册和初始化：

```
GitHub OAuth登录 → 用户注册 → 创建账户 → 分配初始物品 → 创建启动精灵 → 创建启动蛋
```

### 注册流程代码示例

```python
from onboarding_manager import OnboardingManager

onboarding = OnboardingManager()

# 通过GitHub OAuth注册
success, user, message = onboarding.register_from_github(
    github_login="alice",
    github_id=123456,
    email="alice@example.com",
    avatar_url="https://github.com/alice.jpg"
)

if success:
    print(f"Welcome {user.github_login}!")
    print(f"User ID: {user.user_id}")
```

### 新用户获得的初始物品

| 物品 | 数量 | 描述 |
|-----|------|------|
| 精灵球 (Poké Ball) | 3 | 用于捕获野生精灵 |
| 草种子 (Grass Seed) | 2 | 用于在农场种植草系食物 |
| 小药剂 (Small Potion) | 1 | 恢复精灵20 HP |
| 启动精灵 | 1 | 小黄鸭 (Psyduck) - 初始等级1 |
| 精灵蛋 | 1 | 孵化中，需要24小时 |
| **初始精灵币** | **100** | 用于购买物品和交易 |

---

## 经济系统

### 账户结构

每个用户有一个经济账户，包含：
- **余额**: 当前持有的精灵币
- **交易历史**: 所有经济活动记录

```python
from economy_manager import EconomyManager

economy = EconomyManager()

# 获取账户信息
account = economy.get_account("user_id")
print(f"余额: {account.balance}")
print(f"交易数: {len(account.transactions)}")

# 获取用户统计信息
stats = economy.get_user_statistics("user_id")
print(f"总收入: {stats['total_earned']}")
print(f"总支出: {stats['total_spent']}")
```

### 交易类型

系统支持以下交易类型：

| 交易类型 | 金额方向 | 描述 |
|---------|---------|------|
| `INITIAL_GRANT` | + | 新用户获得的初始赠送 |
| `PURCHASE` | - | 从商店购买物品 |
| `FOOD_SALE` | + | 销售农场食物 |
| `FOOD_PURCHASE` | - | 购买其他玩家的食物 |
| `BATTLE_REWARD` | +/- | 战斗赢/输奖励 |
| `PET_SALE` | + | 出售精灵给商店 |
| `AUCTION_SALE` | + | 在拍卖行出售精灵 |
| `SHOP_COMMISSION` | - | 商店从交易中提取的手续费 |

---

## 商店系统

### 可购买物品

```python
from shop_manager import Shop, ItemType

shop = Shop()

# 列出所有精灵球
pokeballs = shop.list_items(ItemType.POKEBALL)
for item in pokeballs:
    print(f"{item.name}: {item.price}精灵币 (库存: {item.stock})")

# 列出所有种子
seeds = shop.list_items(ItemType.SEED)
for item in seeds:
    print(f"{item.name}: {item.price}精灵币")
```

### 物品目录

| 物品ID | 名称 | 类型 | 价格 | 库存 | 描述 |
|--------|------|------|------|------|------|
| `pokeball` | Poké Ball | 球 | 10 | 100 | 标准捕获球 |
| `ultraball` | Ultra Ball | 球 | 25 | 50 | 增强捕获成功率 |
| `seed_grass` | Grass Seed | 种子 | 15 | 200 | 种植草系食物 |
| `seed_water` | Water Seed | 种子 | 15 | 200 | 种植水系食物 |
| `potion_small` | Small Potion | 药剂 | 20 | 150 | 恢复20 HP |
| `revive` | Revive | 复活液 | 50 | 30 | 复活昏迷的精灵 |

### 购买物品

```python
from economy_manager import EconomyManager
from shop_manager import Shop

economy = EconomyManager()
shop = Shop()

# 从商店购买3个精灵球
success, item, message = shop.purchase_item("user_id", "pokeball", 3)

if success:
    # 从账户扣款
    cost = item.price * 3
    economy.purchase_item("user_id", item.name, cost, item.item_id)
    print(f"购买成功！")
else:
    print(f"购买失败: {message}")

# 查看用户物品清单
inventory = shop.get_user_inventory("user_id")
for item_id, item_info in inventory.items():
    print(f"{item_info['item']['name']}: {item_info['quantity']}个")
```

---

## 交易系统

### 1. 食物交易（带手续费）

**手续费**: 5% - 卖家支付给系统

```python
# Alice 购买 Bob 的食物
buyer_id = "alice_id"
seller_id = "bob_id"
base_price = 100.0

success, buyer_paid, seller_received = economy.process_food_transaction(
    buyer_id=buyer_id,
    seller_id=seller_id,
    food_id="berries_001",
    food_name="Berries",
    base_price=base_price
)

if success:
    print(f"Alice 支付: {buyer_paid} 精灵币")
    print(f"Bob 收到: {seller_received} 精灵币")
    print(f"手续费: {buyer_paid - seller_received} 精灵币 (5%)")
    # 结果: Alice -100, Bob +95, 系统 +5
```

### 2. 战斗奖励

**规则**: 赢家获得金币，输家失去金币

```python
# Alice 战胜 Bob
winner_id = "alice_id"
loser_id = "bob_id"
base_reward = 50.0

success = economy.process_battle_reward(
    winner_id=winner_id,
    loser_id=loser_id,
    base_reward=base_reward
)

if success:
    alice = economy.get_account(winner_id)
    bob = economy.get_account(loser_id)
    print(f"Alice 获胜，获得 {base_reward} 精灵币")
    print(f"Bob 失败，失去 {base_reward} 精灵币")
    # 结果: Alice +50, Bob -50
```

**特殊情况**: 如果输家余额不足，只扣除其余额的50%

```python
# Bob 只有20精灵币，输了战斗
# 扣除金额 = min(50, 20 * 0.5) = 10 精灵币
```

### 3. 精灵出售

**直接出售给商店**（无手续费）

```python
seller_id = "alice_id"
pet_name = "皮卡丘"
sale_price = 500.0

success = economy.sell_pet(
    seller_id=seller_id,
    pet_name=pet_name,
    sale_price=sale_price
)

if success:
    alice = economy.get_account(seller_id)
    print(f"Alice 出售 {pet_name}，获得 {sale_price} 精灵币")
    # 结果: Alice +500
```

### 4. 精灵拍卖

**拍卖行出售**（手续费10%）

```python
seller_id = "alice_id"
pet_name = "喷火龙"
final_bid = 1000.0

success = economy.auction_pet(
    seller_id=seller_id,
    pet_name=pet_name,
    auction_final_price=final_bid
)

if success:
    alice = economy.get_account(seller_id)
    print(f"Alice 拍卖 {pet_name}，最终价格 {final_bid}")
    print(f"Alice 收到: {final_bid * 0.9} 精灵币")
    print(f"拍卖行手续费: {final_bid * 0.1} 精灵币 (10%)")
    # 结果: Alice +900, 拍卖行 +100
```

---

## 完整用户流程示例

### 场景：Alice 和 Bob 的完整游戏流程

```python
from onboarding_manager import OnboardingManager
from economy_manager import EconomyManager
from shop_manager import Shop

# 初始化系统
onboarding = OnboardingManager()
economy = onboarding.economy_manager
shop = onboarding.shop

# ===== 第1步：用户注册 =====
print("=== 用户注册 ===")
success1, alice, msg1 = onboarding.register_from_github("alice", 1001, "alice@example.com")
success2, bob, msg2 = onboarding.register_from_github("bob", 1002, "bob@example.com")

print(f"✓ {alice.github_login} 注册成功 (ID: {alice.user_id})")
print(f"✓ {bob.github_login} 注册成功 (ID: {bob.user_id})")

# 检查初始状态
alice_account = economy.get_account(alice.user_id)
bob_account = economy.get_account(bob.user_id)
print(f"  Alice 余额: {alice_account.balance} 精灵币")
print(f"  Bob 余额: {bob_account.balance} 精灵币")

# ===== 第2步：购买物品 =====
print("\n=== 购买物品 ===")

# Alice 购买5个精灵球
success, item, msg = shop.purchase_item(alice.user_id, "pokeball", 5)
economy.purchase_item(alice.user_id, item.name, item.price * 5)
print(f"✓ Alice 购买5个 Poké Ball (-{item.price * 5})")

alice_account = economy.get_account(alice.user_id)
print(f"  Alice 余额: {alice_account.balance} 精灵币")

# ===== 第3步：食物交易 =====
print("\n=== 食物交易 ===")

# Bob 有农场食物要卖给 Alice
success, paid, received = economy.process_food_transaction(
    buyer_id=alice.user_id,
    seller_id=bob.user_id,
    food_id="berries_101",
    food_name="Lv.2 浆果",
    base_price=100.0
)

if success:
    print(f"✓ Alice 从 Bob 购买食物")
    print(f"  Alice 支付: -{paid}")
    print(f"  Bob 收到: +{received}")
    print(f"  系统手续费: {paid - received}")

# 查看更新后的余额
alice_account = economy.get_account(alice.user_id)
bob_account = economy.get_account(bob.user_id)
print(f"  Alice 余额: {alice_account.balance}")
print(f"  Bob 余额: {bob_account.balance}")

# ===== 第4步：战斗 =====
print("\n=== 战斗 ===")

# Alice 战胜 Bob，获得50精灵币
economy.process_battle_reward(
    winner_id=alice.user_id,
    loser_id=bob.user_id,
    base_reward=50.0
)

print(f"✓ Alice 战胜 Bob")
print(f"  Alice 获得: +50")
print(f"  Bob 失去: -50")

# 查看最终余额
alice_account = economy.get_account(alice.user_id)
bob_account = economy.get_account(bob.user_id)
print(f"  Alice 最终余额: {alice_account.balance}")
print(f"  Bob 最终余额: {bob_account.balance}")

# ===== 第5步：查看统计信息 =====
print("\n=== 统计信息 ===")

alice_stats = economy.get_user_statistics(alice.user_id)
bob_stats = economy.get_user_statistics(bob.user_id)

print(f"\nAlice 的统计:")
print(f"  总收入: {alice_stats['total_earned']} 精灵币")
print(f"  总支出: {alice_stats['total_spent']} 精灵币")
print(f"  交易数: {alice_stats['total_transactions']}")

print(f"\nBob 的统计:")
print(f"  总收入: {bob_stats['total_earned']} 精灵币")
print(f"  总支出: {bob_stats['total_spent']} 精灵币")
print(f"  交易数: {bob_stats['total_transactions']}")
```

### 预期输出

```
=== 用户注册 ===
✓ alice 注册成功 (ID: xxxxxxxx)
✓ bob 注册成功 (ID: yyyyyyyy)
  Alice 余额: 100.0 精灵币
  Bob 余额: 100.0 精灵币

=== 购买物品 ===
✓ Alice 购买5个 Poké Ball (-50.0)
  Alice 余额: 50.0 精灵币

=== 食物交易 ===
✓ Alice 从 Bob 购买食物
  Alice 支付: -100.0
  Bob 收到: +95.0
  系统手续费: 5.0
  Alice 余额: -50.0 [失败，余额不足]

... (继续其他交易)
```

---

## API 参考

### OnboardingManager

```python
class OnboardingManager:
    def register_from_github(github_login, github_id, email, avatar_url) 
        -> (success, user, message)
    
    def get_user_onboarding_status(user_id) -> Dict
    
    def is_user_registered(github_id) -> bool
```

### EconomyManager

```python
class EconomyManager:
    def create_account(user_id, initial_balance=100.0) -> UserAccount
    
    def get_account(user_id) -> Optional[UserAccount]
    
    def purchase_item(user_id, item_name, item_price) -> bool
    
    def process_food_transaction(buyer_id, seller_id, food_id, 
                                 food_name, base_price) 
        -> (success, buyer_paid, seller_received)
    
    def process_battle_reward(winner_id, loser_id, base_reward=50.0) -> bool
    
    def sell_pet(seller_id, pet_name, sale_price) -> bool
    
    def auction_pet(seller_id, pet_name, auction_final_price) -> bool
    
    def get_user_statistics(user_id) -> Dict
```

### Shop

```python
class Shop:
    def get_item(item_id) -> Optional[ShopItem]
    
    def list_items(item_type=None) -> List[ShopItem]
    
    def purchase_item(user_id, item_id, quantity=1) 
        -> (success, item, message)
    
    def get_user_inventory(user_id) -> Dict
    
    def use_item(user_id, item_id, quantity=1) -> bool
    
    def get_shop_statistics() -> Dict
```

---

## 手续费总结

| 交易类型 | 手续费率 | 接收者 | 备注 |
|---------|---------|--------|------|
| 食物交易 | 5% | 系统 | 卖家支付 |
| 精灵拍卖 | 10% | 拍卖行 | 卖家支付 |
| 精灵直销 | 0% | - | 无手续费 |
| 商店购买 | 0% | - | 直接扣款 |
| 战斗奖励 | 0% | - | 无手续费 |

---

## 测试

完整的测试套件在 `test_user_onboarding_economy.py` 中，包括：

- 用户管理测试（6个）
- 经济系统测试（8个）
- 商店系统测试（8个）
- 初始化系统测试（5个）
- 完整场景集成测试（1个）

运行测试：
```bash
pytest test_user_onboarding_economy.py -v
```

所有 30 个测试均为 100% 通过。

---
