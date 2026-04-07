#!/usr/bin/env python3
"""
Agent Monster Food System
食物系统：允许玩家在仓库中种植食物，其他玩家的宠物可以来访进食
"""

import json
import yaml
import time
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import hashlib

# ============================================================================
# 数据模型
# ============================================================================

class FoodType(Enum):
    """食物类型"""
    COOKIE = "cookie"      # 🍪
    DONUT = "donut"        # 🍩
    APPLE = "apple"        # 🍎
    GENE = "gene"          # 🧬


FOOD_PROPERTIES = {
    FoodType.COOKIE: {
        "emoji": "🍪",
        "regeneration_hours": 24,
        "max_quantity": 3,
        "nutrition": {"exp": 10, "energy": 0},
    },
    FoodType.DONUT: {
        "emoji": "🍩",
        "regeneration_hours": 48,
        "max_quantity": 2,
        "nutrition": {"exp": 0, "energy": 50},
    },
    FoodType.APPLE: {
        "emoji": "🍎",
        "regeneration_hours": 12,
        "max_quantity": 5,
        "nutrition": {"exp": 5, "energy": 5},
    },
    FoodType.GENE: {
        "emoji": "🧬",
        "regeneration_hours": 72,
        "max_quantity": 1,
        "nutrition": {"exp": 100, "energy": 100},  # 基因食物特殊效果
    },
}


@dataclass
class EatingRecord:
    """进食记录"""
    eater_id: str
    eater_pet_id: str
    eat_time: datetime
    food_id: str
    food_type: str


@dataclass
class Food:
    """食物数据类"""
    id: str
    type: FoodType
    quantity: int                           # 当前数量
    max_quantity: int
    regeneration_hours: int
    last_eaten_at: Optional[datetime] = None
    eating_history: List[EatingRecord] = field(default_factory=list)
    seed: str = ""

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.type.value,
            "emoji": FOOD_PROPERTIES[self.type]["emoji"],
            "quantity": self.quantity,
            "max_quantity": self.max_quantity,
            "regeneration_hours": self.regeneration_hours,
            "last_eaten_at": self.last_eaten_at.isoformat() if self.last_eaten_at else None,
            "seed": self.seed,
        }

    @staticmethod
    def from_dict(data: dict) -> "Food":
        return Food(
            id=data["id"],
            type=FoodType(data["type"]),
            quantity=data["quantity"],
            max_quantity=data["max_quantity"],
            regeneration_hours=data["regeneration_hours"],
            last_eaten_at=datetime.fromisoformat(data["last_eaten_at"]) if data.get("last_eaten_at") else None,
            seed=data.get("seed", ""),
        )


@dataclass
class Farm:
    """食物农场"""
    owner: str
    repository: str
    url: str
    foods: List[Food] = field(default_factory=list)
    planted_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self):
        return {
            "farm": {
                "owner": self.owner,
                "repository": self.repository,
                "url": self.url,
                "planted_at": self.planted_at.isoformat(),
                "foods": [f.to_dict() for f in self.foods],
            }
        }

    @staticmethod
    def from_dict(data: dict) -> "Farm":
        farm_data = data.get("farm", {})
        foods = [Food.from_dict(f) for f in farm_data.get("foods", [])]
        return Farm(
            owner=farm_data.get("owner", ""),
            repository=farm_data.get("repository", ""),
            url=farm_data.get("url", ""),
            foods=foods,
            planted_at=datetime.fromisoformat(farm_data.get("planted_at", datetime.utcnow().isoformat())),
        )


# ============================================================================
# 食物管理器
# ============================================================================

class FoodManager:
    """食物系统管理器"""

    def __init__(self):
        self.farms: Dict[str, Farm] = {}

    def create_farm(self, owner: str, repository: str, url: str) -> Farm:
        """创建新农场"""
        farm = Farm(owner=owner, repository=repository, url=url)
        self.farms[f"{owner}/{repository}"] = farm
        return farm

    def add_food_to_farm(
        self,
        owner: str,
        repository: str,
        food_type: FoodType,
        quantity: int = 1,
    ) -> Food:
        """向农场添加食物"""
        farm_key = f"{owner}/{repository}"
        if farm_key not in self.farms:
            self.create_farm(owner, repository, f"https://github.com/{owner}/{repository}")

        farm = self.farms[farm_key]

        # 生成食物 ID
        food_id = f"{food_type.value}_{owner}_{int(time.time() * 1000)}"

        # 生成种子
        seed = self._generate_seed(food_id)

        # 获取食物属性
        props = FOOD_PROPERTIES[food_type]

        food = Food(
            id=food_id,
            type=food_type,
            quantity=quantity,
            max_quantity=props["max_quantity"],
            regeneration_hours=props["regeneration_hours"],
            seed=seed,
        )

        farm.foods.append(food)
        return food

    def get_farm(self, owner: str, repository: str) -> Optional[Farm]:
        """获取农场"""
        farm_key = f"{owner}/{repository}"
        return self.farms.get(farm_key)

    def get_food(self, owner: str, repository: str, food_id: str) -> Optional[Food]:
        """获取特定食物"""
        farm = self.get_farm(owner, repository)
        if not farm:
            return None

        for food in farm.foods:
            if food.id == food_id:
                return food

        return None

    def calculate_food_status(self, food: Food, current_time: datetime = None) -> Tuple[int, bool, Optional[datetime]]:
        """
        计算食物状态

        返回: (当前数量, 是否已准备好, 下次恢复时间)
        """
        if current_time is None:
            current_time = datetime.utcnow()

        if food.quantity >= food.max_quantity:
            return food.quantity, True, None

        if food.last_eaten_at is None:
            return food.quantity, True, None

        # 计算恢复周期
        time_elapsed = current_time - food.last_eaten_at
        regeneration_period = timedelta(hours=food.regeneration_hours)

        # 计算完成的周期数
        cycles_completed = int(time_elapsed.total_seconds() / regeneration_period.total_seconds())

        if cycles_completed > 0:
            # 恢复食物
            old_quantity = food.quantity
            food.quantity = min(food.quantity + cycles_completed, food.max_quantity)

            # 更新最后吃食物的时间
            food.last_eaten_at += cycles_completed * regeneration_period

            return food.quantity, True, None
        else:
            # 还未恢复
            time_to_regeneration = regeneration_period - time_elapsed
            next_ready = current_time + time_to_regeneration

            return food.quantity, False, next_ready

    def consume_food(
        self,
        owner: str,
        repository: str,
        food_id: str,
        eater_id: str,
        eater_pet_id: str,
    ) -> Tuple[bool, Dict]:
        """
        消费食物

        返回: (是否成功, 响应数据)
        """
        food = self.get_food(owner, repository, food_id)
        if not food:
            return False, {"error": "Food not found"}

        current_quantity, is_ready, next_ready = self.calculate_food_status(food)

        if current_quantity <= 0:
            return False, {
                "error": "Food exhausted",
                "next_ready": next_ready.isoformat() if next_ready else None,
            }

        if not is_ready and food.last_eaten_at is not None:
            return False, {
                "error": "Food not ready",
                "next_ready": next_ready.isoformat() if next_ready else None,
            }

        # 消费食物
        food.quantity -= 1
        food.last_eaten_at = datetime.utcnow()

        # 记录进食
        record = EatingRecord(
            eater_id=eater_id,
            eater_pet_id=eater_pet_id,
            eat_time=datetime.utcnow(),
            food_id=food_id,
            food_type=food.type.value,
        )
        food.eating_history.append(record)

        # 获取营养值
        nutrition = FOOD_PROPERTIES[food.type]["nutrition"]

        return True, {
            "success": True,
            "nutrition": nutrition,
            "remaining_quantity": food.quantity,
            "max_quantity": food.max_quantity,
            "next_ready": (food.last_eaten_at + timedelta(hours=food.regeneration_hours)).isoformat(),
        }

    def save_farm_to_file(self, owner: str, repository: str, filepath: str) -> bool:
        """保存农场到文件"""
        farm = self.get_farm(owner, repository)
        if not farm:
            return False

        try:
            with open(filepath, "w") as f:
                yaml.dump(farm.to_dict(), f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"Error saving farm: {e}")
            return False

    def load_farm_from_file(self, filepath: str) -> Optional[Farm]:
        """从文件加载农场"""
        try:
            with open(filepath, "r") as f:
                data = yaml.safe_load(f)
            farm = Farm.from_dict(data)
            self.farms[f"{farm.owner}/{farm.repository}"] = farm
            return farm
        except Exception as e:
            print(f"Error loading farm: {e}")
            return None

    @staticmethod
    def _generate_seed(food_id: str) -> str:
        """生成食物种子"""
        hash_obj = hashlib.sha256(f"{food_id}{time.time()}".encode())
        return "0x" + hash_obj.hexdigest()[:8]

    def list_all_farms(self) -> List[Farm]:
        """列出所有农场"""
        return list(self.farms.values())

    def get_farm_stats(self, owner: str, repository: str) -> Dict:
        """获取农场统计"""
        farm = self.get_farm(owner, repository)
        if not farm:
            return {}

        total_foods = len(farm.foods)
        total_quantity = sum(f.quantity for f in farm.foods)
        total_max = sum(f.max_quantity for f in farm.foods)
        total_eaten = sum(len(f.eating_history) for f in farm.foods)

        return {
            "owner": farm.owner,
            "repository": farm.repository,
            "total_foods": total_foods,
            "current_quantity": total_quantity,
            "max_capacity": total_max,
            "total_eaten": total_eaten,
            "foods": [
                {
                    "id": f.id,
                    "type": f.type.value,
                    "emoji": FOOD_PROPERTIES[f.type]["emoji"],
                    "quantity": f.quantity,
                    "max": f.max_quantity,
                    "eaten_count": len(f.eating_history),
                }
                for f in farm.foods
            ],
        }


# ============================================================================
# 示例和测试
# ============================================================================

def create_example_farm() -> Farm:
    """创建示例农场"""
    manager = FoodManager()

    # 创建农场
    farm = manager.create_farm("alice", "agent-monster-pet", "https://github.com/alice/agent-monster-pet")

    # 添加食物
    manager.add_food_to_farm("alice", "agent-monster-pet", FoodType.COOKIE, quantity=3)
    manager.add_food_to_farm("alice", "agent-monster-pet", FoodType.GENE, quantity=1)
    manager.add_food_to_farm("alice", "agent-monster-pet", FoodType.APPLE, quantity=5)

    return farm


if __name__ == "__main__":
    print("Agent Monster 食物系统演示\n")
    print("=" * 60)

    # 创建管理器
    manager = FoodManager()

    # 创建 Alice 的农场
    print("1. Alice 创建农场并种植食物")
    print("-" * 60)
    alice_farm = manager.create_farm("alice", "agent-monster-pet", "https://github.com/alice/agent-monster-pet")
    print(f"✓ 农场已创建: {alice_farm.owner}/{alice_farm.repository}")

    # 添加食物
    cookie = manager.add_food_to_farm("alice", "agent-monster-pet", FoodType.COOKIE, quantity=3)
    gene = manager.add_food_to_farm("alice", "agent-monster-pet", FoodType.GENE, quantity=1)
    apple = manager.add_food_to_farm("alice", "agent-monster-pet", FoodType.APPLE, quantity=5)

    print(f"✓ 添加 Cookie: {cookie.id} (数量: {cookie.quantity})")
    print(f"✓ 添加 Gene: {gene.id} (数量: {gene.quantity})")
    print(f"✓ 添加 Apple: {apple.id} (数量: {apple.quantity})")

    # 获取统计
    print("\n2. 查看农场统计")
    print("-" * 60)
    stats = manager.get_farm_stats("alice", "agent-monster-pet")
    print(json.dumps(stats, indent=2, ensure_ascii=False))

    # Bob 进食
    print("\n3. Bob 访问 Alice 的农场并进食")
    print("-" * 60)
    success, response = manager.consume_food("alice", "agent-monster-pet", cookie.id, "bob", "pikachu_bob_001")
    print(f"✓ 进食结果: {'成功' if success else '失败'}")
    print(f"  营养值: {response.get('nutrition')}")
    print(f"  剩余数量: {response.get('remaining_quantity')}/{response.get('max_quantity')}")
    print(f"  下次恢复: {response.get('next_ready')}")

    # 再次进食
    print("\n4. Bob 再次进食")
    print("-" * 60)
    success, response = manager.consume_food("alice", "agent-monster-pet", cookie.id, "bob", "pikachu_bob_001")
    print(f"✓ 进食结果: {'成功' if success else '失败'}")
    print(f"  营养值: {response.get('nutrition')}")
    print(f"  剩余数量: {response.get('remaining_quantity')}/{response.get('max_quantity')}")

    # 第三次进食
    print("\n5. Bob 第三次进食")
    print("-" * 60)
    success, response = manager.consume_food("alice", "agent-monster-pet", cookie.id, "bob", "pikachu_bob_001")
    print(f"✓ 进食结果: {'成功' if success else '失败'}")
    print(f"  营养值: {response.get('nutrition')}")
    print(f"  剩余数量: {response.get('remaining_quantity')}/{response.get('max_quantity')}")

    # 尝试进食已用尽的食物
    print("\n6. Bob 尝试进食已用尽的食物")
    print("-" * 60)
    success, response = manager.consume_food("alice", "agent-monster-pet", cookie.id, "bob", "pikachu_bob_001")
    print(f"✓ 进食结果: {'成功' if success else '失败'}")
    if not success:
        print(f"  错误: {response.get('error')}")
        print(f"  下次恢复: {response.get('next_ready')}")

    # 保存农场
    print("\n7. 保存农场到文件")
    print("-" * 60)
    success = manager.save_farm_to_file("alice", "agent-monster-pet", "/tmp/farm.yaml")
    print(f"✓ 保存结果: {'成功' if success else '失败'}")

    # 显示最后的统计
    print("\n8. 最终农场统计")
    print("-" * 60)
    final_stats = manager.get_farm_stats("alice", "agent-monster-pet")
    print(json.dumps(final_stats, indent=2, ensure_ascii=False))

    print("\n" + "=" * 60)
    print("演示完成！")
