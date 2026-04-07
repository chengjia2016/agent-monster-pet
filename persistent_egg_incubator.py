#!/usr/bin/env python3
"""
Persistent Egg Incubator
增强的蛋孵化系统，支持本地持久化和 Judge Server 同步

特性：
- 本地 JSON 持久化（支持蛋的恢复）
- 孵化时间追踪
- 宠物属性初始化
- Judge Server 迁移支持
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict, field
import hashlib

from egg_incubator import (
    get_commit_history,
    analyze_commit_diffs,
    calculate_ivs,
    generate_initial_soul,
)


@dataclass
class Egg:
    """蛋数据类"""
    egg_id: str
    owner_id: str
    created_at: datetime
    incubation_hours: int = 72
    stage: int = 0  # 0-3: 蛋→细节孵化→即将孵化→孵化完成
    hatched_at: Optional[datetime] = None
    hatch_pet_id: Optional[str] = None
    attributes: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "egg_id": self.egg_id,
            "owner_id": self.owner_id,
            "created_at": self.created_at.isoformat(),
            "incubation_hours": self.incubation_hours,
            "stage": self.stage,
            "hatched_at": self.hatched_at.isoformat() if self.hatched_at else None,
            "hatch_pet_id": self.hatch_pet_id,
            "attributes": self.attributes,
        }
    
    @staticmethod
    def from_dict(data: Dict) -> "Egg":
        return Egg(
            egg_id=data["egg_id"],
            owner_id=data["owner_id"],
            created_at=datetime.fromisoformat(data["created_at"]),
            incubation_hours=data.get("incubation_hours", 72),
            stage=data.get("stage", 0),
            hatched_at=datetime.fromisoformat(data["hatched_at"]) if data.get("hatched_at") else None,
            hatch_pet_id=data.get("hatch_pet_id"),
            attributes=data.get("attributes", {}),
        )


class PersistentEggIncubator:
    """
    蛋孵化系统管理器 - 支持持久化
    
    数据存储架构：
    .monster/eggs/
    ├── egg_registry.json        # 所有蛋的注册表
    ├── owner_eggs/
    │   ├── owner1.json          # owner1 的所有蛋
    │   ├── owner2.json          # owner2 的所有蛋
    │   └── ...
    └── egg_history.jsonl        # 蛋相关事件历史
    """
    
    def __init__(self, cache_dir: Path = None, judge_server_client=None):
        """
        初始化持久化蛋孵化器
        
        Args:
            cache_dir: 缓存目录路径（默认 .monster）
            judge_server_client: Judge Server 客户端实例（可选）
        """
        if cache_dir is None:
            cache_dir = Path(".monster")
        
        self.cache_dir = Path(cache_dir)
        self.eggs_dir = self.cache_dir / "eggs"
        self.eggs_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry_file = self.eggs_dir / "egg_registry.json"
        self.owner_eggs_dir = self.eggs_dir / "owner_eggs"
        self.owner_eggs_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.eggs_dir / "egg_history.jsonl"
        
        self.judge_server_client = judge_server_client
        self.lock = threading.RLock()
        
        # 内存缓存
        self.egg_registry: Dict[str, Egg] = {}  # egg_id -> Egg
        self.owner_eggs: Dict[str, List[str]] = {}  # owner_id -> [egg_ids]
        
        # 加载现有数据
        self._load_registry()
        self._load_owner_eggs()
    
    def _load_registry(self) -> int:
        """从本地加载蛋注册表"""
        count = 0
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                for egg_id, egg_data in data.items():
                    self.egg_registry[egg_id] = Egg.from_dict(egg_data)
                
                count = len(self.egg_registry)
                print(f"✓ 从注册表加载了 {count} 个蛋")
        except Exception as e:
            print(f"⚠️  加载蛋注册表失败: {e}")
            self.egg_registry = {}
        
        return count
    
    def _load_owner_eggs(self) -> int:
        """从本地加载所有所有者的蛋"""
        count = 0
        try:
            for owner_file in self.owner_eggs_dir.glob("*.json"):
                try:
                    with open(owner_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    owner_id = data.get("owner_id")
                    if owner_id:
                        self.owner_eggs[owner_id] = data.get("egg_ids", [])
                        count += 1
                except Exception as e:
                    print(f"⚠️  加载所有者蛋列表失败: {owner_file} - {e}")
        except Exception as e:
            print(f"⚠️  遍历所有者蛋目录失败: {e}")
        
        if count > 0:
            print(f"✓ 从本地加载了 {count} 个所有者的蛋记录")
        
        return count
    
    def _save_registry(self) -> bool:
        """保存蛋注册表到本地"""
        with self.lock:
            try:
                data = {}
                for egg_id, egg in self.egg_registry.items():
                    data[egg_id] = egg.to_dict()
                
                with open(self.registry_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"❌ 保存蛋注册表失败: {e}")
                return False
    
    def _save_owner_eggs(self, owner_id: str) -> bool:
        """保存所有者的蛋列表"""
        with self.lock:
            try:
                owner_file = self.owner_eggs_dir / f"{owner_id}.json"
                egg_ids = self.owner_eggs.get(owner_id, [])
                
                data = {
                    "owner_id": owner_id,
                    "last_updated": datetime.utcnow().isoformat(),
                    "egg_ids": egg_ids,
                    "total_eggs": len(egg_ids),
                }
                
                with open(owner_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                return True
            except Exception as e:
                print(f"❌ 保存所有者蛋列表失败: {e}")
                return False
    
    def _add_history_record(self, event: str, owner_id: str, egg_id: str, details: Dict = None) -> bool:
        """添加蛋事件到历史记录"""
        try:
            record = {
                "timestamp": datetime.utcnow().isoformat(),
                "event": event,
                "owner_id": owner_id,
                "egg_id": egg_id,
                **(details or {}),
            }
            
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            return True
        except Exception as e:
            print(f"❌ 添加历史记录失败: {e}")
            return False
    
    def create_egg(
        self,
        owner_id: str,
        incubation_hours: int = 72,
        attributes: Dict = None,
    ) -> Egg:
        """
        创建新蛋
        
        Args:
            owner_id: 蛋的所有者
            incubation_hours: 孵化时间（小时）
            attributes: 初始属性
            
        Returns:
            创建的蛋对象
        """
        with self.lock:
            # 生成蛋 ID
            timestamp = int(time.time() * 1000)
            seed = hashlib.md5(f"{owner_id}_{timestamp}".encode()).hexdigest()[:8]
            egg_id = f"egg_{seed}_{timestamp}"
            
            # 创建蛋
            egg = Egg(
                egg_id=egg_id,
                owner_id=owner_id,
                created_at=datetime.utcnow(),
                incubation_hours=incubation_hours,
                attributes=attributes or {},
            )
            
            # 注册蛋
            self.egg_registry[egg_id] = egg
            
            if owner_id not in self.owner_eggs:
                self.owner_eggs[owner_id] = []
            self.owner_eggs[owner_id].append(egg_id)
            
            # 持久化
            self._save_registry()
            self._save_owner_eggs(owner_id)
            self._add_history_record("created", owner_id, egg_id)
            
            print(f"✓ 创建了蛋: {egg_id}")
            
            return egg
    
    def get_egg(self, egg_id: str) -> Optional[Egg]:
        """获取蛋"""
        with self.lock:
            return self.egg_registry.get(egg_id)
    
    def get_owner_eggs(self, owner_id: str) -> List[Egg]:
        """获取所有者的所有蛋"""
        with self.lock:
            egg_ids = self.owner_eggs.get(owner_id, [])
            return [self.egg_registry[eid] for eid in egg_ids if eid in self.egg_registry]
    
    def calculate_egg_stage(self, egg: Egg) -> int:
        """
        计算蛋的孵化阶段 (0-3)
        
        0: 新蛋
        1: 孵化中 (33%)
        2: 快要孵化 (66%)
        3: 可以孵化 (100%)
        """
        if egg.hatched_at:
            return 3  # 已孵化
        
        elapsed = datetime.utcnow() - egg.created_at
        progress = elapsed.total_seconds() / (egg.incubation_hours * 3600)
        
        if progress < 0.33:
            return 0
        elif progress < 0.66:
            return 1
        elif progress < 1.0:
            return 2
        else:
            return 3
    
    def get_egg_time_remaining(self, egg: Egg) -> timedelta:
        """获取蛋孵化剩余时间"""
        if egg.hatched_at:
            return timedelta(0)
        
        incubation_end = egg.created_at + timedelta(hours=egg.incubation_hours)
        remaining = incubation_end - datetime.utcnow()
        
        return max(remaining, timedelta(0))
    
    def hatch_egg(
        self,
        egg_id: str,
        pet_id: str,
        pet_name: str,
    ) -> Tuple[bool, Dict]:
        """
        孵化蛋生成宠物
        
        Args:
            egg_id: 蛋 ID
            pet_id: 生成的宠物 ID
            pet_name: 宠物名称
            
        Returns:
            (是否成功, 响应数据)
        """
        with self.lock:
            egg = self.egg_registry.get(egg_id)
            if not egg:
                return False, {"error": "Egg not found"}
            
            # 检查是否已孵化
            if egg.hatched_at:
                return False, {
                    "error": "Egg already hatched",
                    "hatched_at": egg.hatched_at.isoformat(),
                }
            
            # 检查孵化时间
            time_remaining = self.get_egg_time_remaining(egg)
            if time_remaining.total_seconds() > 0:
                return False, {
                    "error": "Egg not ready to hatch",
                    "time_remaining_seconds": int(time_remaining.total_seconds()),
                }
            
            # 孵化蛋
            egg.hatched_at = datetime.utcnow()
            egg.hatch_pet_id = pet_id
            egg.stage = 3
            
            # 保存
            self._save_registry()
            self._add_history_record("hatched", egg.owner_id, egg_id, {
                "pet_id": pet_id,
                "pet_name": pet_name,
            })
            
            return True, {
                "success": True,
                "egg_id": egg_id,
                "pet_id": pet_id,
                "pet_name": pet_name,
                "hatched_at": egg.hatched_at.isoformat(),
                "attributes": egg.attributes,
            }
    
    def get_global_statistics(self) -> Dict:
        """获取全局蛋统计"""
        with self.lock:
            total_eggs = len(self.egg_registry)
            hatched = sum(1 for egg in self.egg_registry.values() if egg.hatched_at)
            incubating = total_eggs - hatched
            
            stages = {0: 0, 1: 0, 2: 0, 3: 0}
            for egg in self.egg_registry.values():
                stage = self.calculate_egg_stage(egg)
                stages[stage] += 1
            
            return {
                "total_eggs": total_eggs,
                "incubating": incubating,
                "hatched": hatched,
                "by_stage": stages,
                "owners": len(self.owner_eggs),
            }
    
    def export_eggs_to_json(self, filepath: str) -> bool:
        """导出所有蛋数据"""
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "eggs": {eid: egg.to_dict() for eid, egg in self.egg_registry.items()},
                    "owner_eggs": self.owner_eggs,
                    "exported_at": datetime.utcnow().isoformat(),
                }, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 导出蛋失败: {e}")
            return False


# ============================================================================
# 示例和测试
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print(" 🥚 持久化蛋孵化系统演示")
    print("=" * 70)
    print()
    
    from pathlib import Path
    import time
    
    # 创建管理器
    manager = PersistentEggIncubator(cache_dir=Path(".monster"))
    
    # 演示 1: 创建蛋
    print("1️⃣  创建新蛋")
    print("-" * 70)
    egg1 = manager.create_egg(
        "alice",
        incubation_hours=72,
        attributes={"genes": {"logic": 0.5, "creative": 0.3, "speed": 0.2}},
    )
    print(f"✓ 创建了蛋: {egg1.egg_id}")
    print()
    
    # 演示 2: 创建短时间蛋（用于演示）
    print("2️⃣  创建可立即孵化的蛋（0.01小时）")
    print("-" * 70)
    egg2 = manager.create_egg("bob", incubation_hours=0.01)
    print(f"✓ 创建了蛋: {egg2.egg_id}")
    time.sleep(2)  # 等待孵化时间过去
    print()
    
    # 演示 3: 检查蛋的阶段
    print("3️⃣  检查蛋的孵化阶段")
    print("-" * 70)
    egg1_loaded = manager.get_egg(egg1.egg_id)
    stage = manager.calculate_egg_stage(egg1_loaded)
    remaining = manager.get_egg_time_remaining(egg1_loaded)
    print(f"✓ 蛋 {egg1.egg_id[:8]}...:")
    print(f"  阶段: {stage}/3")
    print(f"  剩余时间: {remaining}")
    
    egg2_loaded = manager.get_egg(egg2.egg_id)
    stage2 = manager.calculate_egg_stage(egg2_loaded)
    print(f"✓ 蛋 {egg2.egg_id[:8]}...:")
    print(f"  阶段: {stage2}/3")
    print()
    
    # 演示 4: 孵化蛋
    print("4️⃣  孵化蛋")
    print("-" * 70)
    success, response = manager.hatch_egg(egg2.egg_id, "psyduck_bob_001", "Psyduck")
    if success:
        print(f"✓ 孵化成功!")
        print(f"  宠物 ID: {response['pet_id']}")
        print(f"  宠物名: {response['pet_name']}")
    else:
        print(f"❌ 孵化失败: {response['error']}")
    print()
    
    # 演示 5: 所有者的蛋
    print("5️⃣  获取所有者的所有蛋")
    print("-" * 70)
    alice_eggs = manager.get_owner_eggs("alice")
    print(f"✓ Alice 有 {len(alice_eggs)} 个蛋")
    print()
    
    # 演示 6: 统计信息
    print("6️⃣  全局统计")
    print("-" * 70)
    stats = manager.get_global_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print()
    
    # 演示 7: 重启后加载
    print("7️⃣  模拟应用重启")
    print("-" * 70)
    manager2 = PersistentEggIncubator(cache_dir=Path(".monster"))
    print(f"✓ 新实例加载了 {len(manager2.egg_registry)} 个蛋")
    print()
    
    print("=" * 70)
    print("✓ 演示完成!")
    print("=" * 70)
