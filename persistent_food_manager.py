#!/usr/bin/env python3
"""
Persistent Food Manager
增强的食物系统管理器，支持本地持久化和 Judge Server 同步

特性：
- 本地 JSON 持久化（解决数据丢失问题）
- 应用重启后自动恢复农场数据
- 支持 Judge Server 迁移（离线备用）
- 并发安全的农场操作
"""

import json
import yaml
import time
import threading
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict, field
from pathlib import Path
import hashlib

from food_system import (
    FoodType,
    FOOD_PROPERTIES,
    Food,
    Farm,
    FoodManager,
    EatingRecord,
)


class PersistentFoodManager(FoodManager):
    """
    食物系统管理器 - 支持持久化
    
    数据存储架构：
    .monster/farms/
    ├── alice/
    │   └── agent-monster-pet.json       # Alice 的农场数据
    ├── bob/
    │   └── some-repo.json               # Bob 的农场数据
    └── ...
    
    每个农场文件包含完整的农场状态，可以独立加载和保存。
    """
    
    def __init__(self, cache_dir: Path = None, judge_server_client=None, auto_load: bool = True):
        """
        初始化持久化食物管理器
        
        Args:
            cache_dir: 缓存目录路径（默认 .monster）
            judge_server_client: Judge Server 客户端实例（可选）
            auto_load: 是否在初始化时自动加载本地农场数据
        """
        super().__init__()
        
        # 设置存储目录
        if cache_dir is None:
            cache_dir = Path(".monster")
        self.cache_dir = Path(cache_dir)
        self.farms_dir = self.cache_dir / "farms"
        self.farms_dir.mkdir(parents=True, exist_ok=True)
        
        # Judge Server 客户端
        self.judge_server_client = judge_server_client
        
        # 线程锁 - 保证并发操作安全
        self.lock = threading.RLock()
        
        # 同步状态跟踪
        self.sync_cache: Dict[str, datetime] = {}  # 记录最后同步时间
        self.pending_syncs: List[str] = []  # 待同步的农场
        
        # 自动加载本地数据
        if auto_load:
            self._load_all_farms()
    
    def _get_farm_file(self, owner: str, repository: str) -> Path:
        """获取农场文件路径"""
        owner_dir = self.farms_dir / owner
        owner_dir.mkdir(parents=True, exist_ok=True)
        return owner_dir / f"{repository}.json"
    
    def _load_all_farms(self) -> int:
        """
        从本地加载所有农场数据
        
        Returns:
            加载的农场数量
        """
        count = 0
        try:
            for owner_dir in self.farms_dir.iterdir():
                if not owner_dir.is_dir():
                    continue
                    
                for farm_file in owner_dir.glob("*.json"):
                    try:
                        with open(farm_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        farm = Farm.from_dict(data)
                        self.farms[f"{farm.owner}/{farm.repository}"] = farm
                        count += 1
                        
                    except Exception as e:
                        print(f"⚠️  加载农场数据失败: {farm_file} - {e}")
        except Exception as e:
            print(f"⚠️  遍历农场目录失败: {e}")
        
        if count > 0:
            print(f"✓ 从本地加载了 {count} 个农场")
        
        return count
    
    def _save_farm_sync(self, farm: Farm) -> bool:
        """
        同步保存农场到本地文件（线程安全）
        
        Args:
            farm: 农场对象
            
        Returns:
            是否保存成功
        """
        with self.lock:
            farm_file = self._get_farm_file(farm.owner, farm.repository)
            
            try:
                with open(farm_file, 'w', encoding='utf-8') as f:
                    json.dump(farm.to_dict(), f, indent=2, ensure_ascii=False)
                
                # 标记同步时间
                self.sync_cache[f"{farm.owner}/{farm.repository}"] = datetime.utcnow()
                
                return True
            except Exception as e:
                print(f"❌ 保存农场失败: {e}")
                return False
    
    def _sync_to_judge_server_async(self, farm: Farm) -> None:
        """
        异步同步农场到 Judge Server（如果可用）
        此方法不阻塞主线程
        
        Args:
            farm: 农场对象
        """
        if not self.judge_server_client:
            return
        
        # TODO: 实现异步同步逻辑
        # 当 Judge Server 添加农场 API 时启用此功能
        pass
    
    def create_farm(self, owner: str, repository: str, url: str) -> Farm:
        """
        创建新农场（自动持久化）
        
        Args:
            owner: 仓库所有者
            repository: 仓库名称
            url: 仓库 URL
            
        Returns:
            创建的农场对象
        """
        with self.lock:
            farm = super().create_farm(owner, repository, url)
            
            # 立即保存到本地
            self._save_farm_sync(farm)
            
            return farm
    
    def add_food_to_farm(
        self,
        owner,
        repository=None,
        food_type=None,
        quantity: int = 1,
    ) -> Food:
        """
        向农场添加食物（自动持久化）
        
        Args:
            owner: 农场所有者或 Farm 对象
            repository: 仓库名称（或 food_type 如果 owner 是 Farm）
            food_type: 食物类型（或 quantity 如果 owner 是 Farm）
            quantity: 数量
            
        Returns:
            创建的食物对象
        """
        with self.lock:
            food = super().add_food_to_farm(owner, repository, food_type, quantity)
            
            # 获取农场对象
            if isinstance(owner, Farm):
                farm = owner
            else:
                farm_key = f"{owner}/{repository}"
                farm = self.farms.get(farm_key)
            
            if farm:
                # 立即保存到本地
                self._save_farm_sync(farm)
            
            return food
    
    def consume_food(
        self,
        owner: str,
        repository: str,
        food_id: str,
        eater_id: str,
        eater_pet_id: str,
    ) -> Tuple[bool, Dict]:
        """
        消费食物（自动持久化）
        
        Args:
            owner: 农场所有者
            repository: 仓库名称
            food_id: 食物 ID
            eater_id: 进食者 ID
            eater_pet_id: 进食者宠物 ID
            
        Returns:
            (是否成功, 响应数据)
        """
        with self.lock:
            success, response = super().consume_food(owner, repository, food_id, eater_id, eater_pet_id)
            
            if success:
                # 消费成功，保存农场状态
                farm = self.get_farm(owner, repository)
                if farm:
                    self._save_farm_sync(farm)
            
            return success, response
    
    def delete_food(self, owner: str, repository: str, food_id: str) -> bool:
        """
        删除食物
        
        Args:
            owner: 农场所有者
            repository: 仓库名称
            food_id: 食物 ID
            
        Returns:
            是否成功
        """
        with self.lock:
            farm = self.get_farm(owner, repository)
            if not farm:
                return False
            
            farm.foods = [f for f in farm.foods if f.id != food_id]
            self._save_farm_sync(farm)
            
            return True
    
    def delete_farm(self, owner: str, repository: str) -> bool:
        """
        删除整个农场
        
        Args:
            owner: 农场所有者
            repository: 仓库名称
            
        Returns:
            是否成功
        """
        with self.lock:
            farm_key = f"{owner}/{repository}"
            
            if farm_key in self.farms:
                del self.farms[farm_key]
            
            farm_file = self._get_farm_file(owner, repository)
            if farm_file.exists():
                try:
                    farm_file.unlink()
                    return True
                except Exception as e:
                    print(f"❌ 删除农场文件失败: {e}")
                    return False
            
            return True
    
    def search_farms_by_owner(self, owner: str) -> List[Farm]:
        """
        查询某个所有者的所有农场
        
        Args:
            owner: 所有者名称
            
        Returns:
            农场列表
        """
        with self.lock:
            return [farm for farm in self.farms.values() if farm.owner == owner]
    
    def get_all_farms_statistics(self) -> Dict:
        """
        获取所有农场的统计数据
        
        Returns:
            统计字典
        """
        with self.lock:
            total_farms = len(self.farms)
            total_foods = sum(len(f.foods) for f in self.farms.values())
            total_eaten = sum(
                len(f.eating_history)
                for farm in self.farms.values()
                for f in farm.foods
            )
            
            return {
                "total_farms": total_farms,
                "total_foods": total_foods,
                "total_eaten": total_eaten,
                "farms": [
                    {
                        "owner": farm.owner,
                        "repository": farm.repository,
                        "foods_count": len(farm.foods),
                        "url": farm.url,
                    }
                    for farm in sorted(
                        self.farms.values(),
                        key=lambda f: (f.owner, f.repository)
                    )
                ]
            }
    
    def export_farm_to_yaml(self, owner: str, repository: str, filepath: str) -> bool:
        """
        导出农场为 YAML 格式（备份用）
        
        Args:
            owner: 农场所有者
            repository: 仓库名称
            filepath: 输出文件路径
            
        Returns:
            是否成功
        """
        farm = self.get_farm(owner, repository)
        if not farm:
            return False
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                yaml.dump(farm.to_dict(), f, default_flow_style=False, allow_unicode=True)
            return True
        except Exception as e:
            print(f"❌ 导出农场失败: {e}")
            return False
    
    def import_farm_from_yaml(self, filepath: str) -> Optional[Farm]:
        """
        从 YAML 文件导入农场
        
        Args:
            filepath: YAML 文件路径
            
        Returns:
            导入的农场对象，如果失败返回 None
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            farm = Farm.from_dict(data)
            self.farms[f"{farm.owner}/{farm.repository}"] = farm
            
            # 保存到本地
            self._save_farm_sync(farm)
            
            return farm
        except Exception as e:
            print(f"❌ 导入农场失败: {e}")
            return None
    
    def get_farm_sync_status(self) -> Dict[str, Any]:
        """
        获取农场同步状态
        
        Returns:
            同步状态字典
        """
        with self.lock:
            return {
                "total_farms": len(self.farms),
                "synced_farms": len(self.sync_cache),
                "pending_syncs": len(self.pending_syncs),
                "cache_location": str(self.farms_dir),
                "judge_server_available": bool(self.judge_server_client),
            }


def migrate_from_memory_to_persistent() -> Tuple[FoodManager, PersistentFoodManager]:
    """
    从内存 FoodManager 迁移到 PersistentFoodManager
    
    Returns:
        (原始 FoodManager, 新的 PersistentFoodManager)
    """
    # 创建内存管理器和持久化管理器
    memory_manager = FoodManager()
    persistent_manager = PersistentFoodManager()
    
    # 将内存中的所有农场迁移到持久化管理器
    print("\n🔄 迁移农场数据...")
    migrated = 0
    
    for farm_key, farm in memory_manager.farms.items():
        try:
            persistent_manager.farms[farm_key] = farm
            persistent_manager._save_farm_sync(farm)
            migrated += 1
        except Exception as e:
            print(f"❌ 迁移农场失败: {farm_key} - {e}")
    
    print(f"✓ 成功迁移 {migrated} 个农场")
    
    return memory_manager, persistent_manager


# ============================================================================
# 示例和测试
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print(" 🌾 持久化食物管理系统演示")
    print("=" * 70)
    print()
    
    from pathlib import Path
    
    # 创建管理器
    manager = PersistentFoodManager(cache_dir=Path(".monster"))
    
    # 演示 1: 创建农场
    print("1️⃣  创建 Alice 的农场")
    print("-" * 70)
    alice_farm = manager.create_farm(
        "alice",
        "agent-monster-pet",
        "https://github.com/alice/agent-monster-pet"
    )
    print(f"✓ 农场已创建并保存: {alice_farm.owner}/{alice_farm.repository}")
    print()
    
    # 演示 2: 添加食物
    print("2️⃣  向农场添加食物")
    print("-" * 70)
    cookie = manager.add_food_to_farm("alice", "agent-monster-pet", FoodType.COOKIE, 3)
    print(f"✓ 添加 Cookie: {cookie.id}")
    
    gene = manager.add_food_to_farm("alice", "agent-monster-pet", FoodType.GENE, 1)
    print(f"✓ 添加 Gene: {gene.id}")
    print()
    
    # 演示 3: 检查存储
    print("3️⃣  检查本地存储")
    print("-" * 70)
    farm_file = manager._get_farm_file("alice", "agent-monster-pet")
    print(f"✓ 农场文件: {farm_file}")
    if farm_file.exists():
        print(f"✓ 文件大小: {farm_file.stat().st_size} 字节")
        with open(farm_file, 'r') as f:
            data = json.load(f)
            print(f"✓ 包含 {len(data['farm']['foods'])} 件食物")
    print()
    
    # 演示 4: 消费食物
    print("4️⃣  消费食物")
    print("-" * 70)
    success, response = manager.consume_food(
        "alice", "agent-monster-pet", cookie.id, "bob", "pikachu_bob_001"
    )
    print(f"✓ 消费结果: {'成功' if success else '失败'}")
    print(f"  营养值: {response.get('nutrition')}")
    print(f"  剩余数量: {response.get('remaining_quantity')}/{response.get('max_quantity')}")
    print()
    
    # 演示 5: 统计数据
    print("5️⃣  查看统计数据")
    print("-" * 70)
    stats = manager.get_all_farms_statistics()
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print()
    
    # 演示 6: 重启后加载数据
    print("6️⃣  模拟应用重启 - 从本地加载数据")
    print("-" * 70)
    # 创建新实例（模拟重启）
    manager2 = PersistentFoodManager(cache_dir=Path(".monster"), auto_load=True)
    print(f"✓ 新实例加载了 {len(manager2.farms)} 个农场")
    alice_farm_loaded = manager2.get_farm("alice", "agent-monster-pet")
    if alice_farm_loaded:
        print(f"✓ Alice 的农场包含 {len(alice_farm_loaded.foods)} 件食物")
        print(f"✓ Cookie 剩余数量: {alice_farm_loaded.foods[0].quantity}/3")
    print()
    
    print("=" * 70)
    print("✓ 演示完成!")
    print("=" * 70)
