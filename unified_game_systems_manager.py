#!/usr/bin/env python3
"""
Unified Game Systems Manager
统一的游戏系统管理器 - 整合食物、Cookie 等系统的本地和服务器存储

架构：
- 本地存储优先（立即响应）
- 异步同步到 Judge Server（后台操作）
- 离线模式支持（无网络时使用本地缓存）
- 冲突解决机制（服务器数据优先）
"""

import threading
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from datetime import datetime
import json

from persistent_food_manager import PersistentFoodManager
from persistent_cookie_manager import PersistentCookieManager
from hybrid_user_data_manager import HybridUserDataManager


class UnifiedGameSystemsManager:
    """
    统一游戏系统管理器
    
    功能：
    1. 管理所有游戏数据系统（食物、Cookie、用户、库存等）
    2. 提供统一的本地/服务器同步接口
    3. 支持离线模式和缓存回退
    4. 处理并发操作和冲突解决
    """
    
    def __init__(
        self,
        cache_dir: Path = None,
        judge_server_client=None,
        enable_auto_sync: bool = True,
    ):
        """
        初始化统一管理器
        
        Args:
            cache_dir: 缓存目录路径（默认 .monster）
            judge_server_client: Judge Server 客户端实例（可选）
            enable_auto_sync: 是否启用自动同步
        """
        if cache_dir is None:
            cache_dir = Path(".monster")
        
        self.cache_dir = Path(cache_dir)
        self.judge_server_client = judge_server_client
        self.enable_auto_sync = enable_auto_sync
        
        # 初始化各个系统管理器
        self.food_manager = PersistentFoodManager(
            cache_dir=self.cache_dir,
            judge_server_client=judge_server_client,
        )
        
        self.cookie_manager = PersistentCookieManager(
            cache_dir=self.cache_dir,
            judge_server_client=judge_server_client,
        )
        
        self.user_data_manager = HybridUserDataManager(
            local_cache_dir=self.cache_dir,
            judge_server_manager=judge_server_client,
        )
        
        # 全局锁
        self.lock = threading.RLock()
        
        # 同步队列和状态
        self.sync_queue: List[Dict[str, Any]] = []
        self.is_syncing = False
        self.last_sync_time: Dict[str, datetime] = {}
        
        # 启动自动同步服务
        if enable_auto_sync:
            self._start_auto_sync_service()
        
        print("✓ 统一游戏系统管理器已初始化")
    
    def _start_auto_sync_service(self) -> None:
        """启动后台同步服务"""
        def sync_worker():
            import time
            while self.enable_auto_sync:
                try:
                    self._process_sync_queue()
                    time.sleep(30)  # 每 30 秒检查一次
                except Exception as e:
                    print(f"⚠️  同步服务错误: {e}")
        
        sync_thread = threading.Thread(daemon=True, target=sync_worker)
        sync_thread.start()
    
    def _add_to_sync_queue(self, operation: Dict[str, Any]) -> None:
        """添加操作到同步队列"""
        with self.lock:
            self.sync_queue.append({
                "timestamp": datetime.utcnow().isoformat(),
                **operation,
            })
    
    def _process_sync_queue(self) -> int:
        """处理同步队列中的操作"""
        if self.is_syncing or not self.judge_server_client:
            return 0
        
        with self.lock:
            if not self.sync_queue:
                return 0
            
            self.is_syncing = True
            processed = 0
        
        try:
            while self.sync_queue:
                operation = self.sync_queue.pop(0)
                
                # 根据操作类型执行同步
                op_type = operation.get("type")
                
                if op_type == "farm":
                    # 同步农场数据到 Judge Server
                    # TODO: 实现农场 API 调用
                    pass
                elif op_type == "cookie":
                    # 同步 Cookie 数据到 Judge Server
                    # TODO: 实现 Cookie API 调用
                    pass
                elif op_type == "user":
                    # 同步用户数据到 Judge Server
                    # TODO: 实现用户 API 调用
                    pass
                
                processed += 1
        finally:
            self.is_syncing = False
        
        return processed
    
    # ========== 食物系统 API ==========
    
    def create_farm(self, owner: str, repository: str, url: str):
        """创建农场"""
        farm = self.food_manager.create_farm(owner, repository, url)
        
        # 添加到同步队列
        self._add_to_sync_queue({
            "type": "farm",
            "action": "create",
            "owner": owner,
            "repository": repository,
        })
        
        return farm
    
    def add_food_to_farm(
        self,
        owner,
        repository=None,
        food_type=None,
        quantity: int = 1,
    ):
        """向农场添加食物"""
        food = self.food_manager.add_food_to_farm(owner, repository, food_type, quantity)
        
        # 添加到同步队列
        if isinstance(owner, str):
            self._add_to_sync_queue({
                "type": "farm",
                "action": "add_food",
                "owner": owner,
                "repository": repository,
                "food_id": food.id,
            })
        
        return food
    
    def consume_food(
        self,
        owner: str,
        repository: str,
        food_id: str,
        eater_id: str,
        eater_pet_id: str,
    ) -> Tuple[bool, Dict]:
        """消费食物"""
        success, response = self.food_manager.consume_food(
            owner, repository, food_id, eater_id, eater_pet_id
        )
        
        if success:
            self._add_to_sync_queue({
                "type": "farm",
                "action": "consume_food",
                "owner": owner,
                "repository": repository,
                "food_id": food_id,
                "eater_id": eater_id,
            })
        
        return success, response
    
    def get_farm_statistics(self, owner: str = None) -> Dict:
        """获取农场统计"""
        if owner:
            farms = self.food_manager.search_farms_by_owner(owner)
            if not farms:
                return {"owner": owner, "farms": 0}
            
            total_foods = sum(len(f.foods) for f in farms)
            total_eaten = sum(
                len(f.eating_history)
                for f in farms
                for food in f.foods
            )
            
            return {
                "owner": owner,
                "farms": len(farms),
                "total_foods": total_foods,
                "total_eaten": total_eaten,
            }
        else:
            return self.food_manager.get_all_farms_statistics()
    
    # ========== Cookie 系统 API ==========
    
    def register_cookie(
        self,
        cookie_id: str,
        cookie_type: str = "cookie",
        source_file: str = None,
        generator_id: str = None,
    ) -> bool:
        """注册 Cookie"""
        success = self.cookie_manager.register_cookie(
            cookie_id, cookie_type, source_file, generator_id
        )
        
        if success:
            self._add_to_sync_queue({
                "type": "cookie",
                "action": "register",
                "cookie_id": cookie_id,
                "cookie_type": cookie_type,
            })
        
        return success
    
    def claim_cookie(self, cookie_id: str, player_id: str) -> Tuple[bool, Dict]:
        """玩家索赔 Cookie"""
        success, response = self.cookie_manager.claim_cookie(cookie_id, player_id)
        
        if success:
            self._add_to_sync_queue({
                "type": "cookie",
                "action": "claim",
                "cookie_id": cookie_id,
                "player_id": player_id,
                "rewards": response.get("rewards"),
            })
        
        return success, response
    
    def scan_and_register_cookies(
        self,
        directory: str,
        player_id: str,
    ) -> Tuple[int, List[str]]:
        """扫描并注册 Cookie"""
        found, new_ids = self.cookie_manager.scan_and_register_cookies(directory, player_id)
        
        if new_ids:
            self._add_to_sync_queue({
                "type": "cookie",
                "action": "scan",
                "player_id": player_id,
                "found_count": found,
                "new_count": len(new_ids),
            })
        
        return found, new_ids
    
    def get_cookie_statistics(self, player_id: str = None) -> Dict:
        """获取 Cookie 统计"""
        if player_id:
            return self.cookie_manager.get_player_statistics(player_id)
        else:
            return self.cookie_manager.get_global_statistics()
    
    # ========== 用户系统 API ==========
    
    def get_user_data(self, github_id: int, use_server: bool = True) -> Optional[Dict]:
        """获取用户数据"""
        return self.user_data_manager.get_user_data(github_id, use_server)
    
    def save_user_data(self, github_id: int, user_data: Dict, sync_to_server: bool = True) -> bool:
        """保存用户数据"""
        return self.user_data_manager.save_user_data(github_id, user_data, sync_to_server)
    
    # ========== 系统状态 API ==========
    
    def get_system_status(self) -> Dict:
        """获取系统总体状态"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "local_storage": {
                "cache_dir": str(self.cache_dir),
            },
            "food_system": {
                "farms": len(self.food_manager.farms),
                "total_foods": sum(len(f.foods) for f in self.food_manager.farms.values()),
                "sync_status": self.food_manager.get_farm_sync_status(),
            },
            "cookie_system": {
                "registered_cookies": len(self.cookie_manager.cookie_registry),
                "player_claims": len(self.cookie_manager.player_claims),
                "sync_status": {
                    "judge_server_available": bool(self.judge_server_client),
                },
            },
            "sync_service": {
                "enabled": self.enable_auto_sync,
                "is_syncing": self.is_syncing,
                "queue_size": len(self.sync_queue),
            },
        }
    
    def check_server_connectivity(self) -> bool:
        """检查 Judge Server 连接状态"""
        return self.user_data_manager.is_server_online()
    
    def export_all_data(self, export_dir: str) -> Dict:
        """导出所有数据（备份）"""
        export_path = Path(export_dir)
        export_path.mkdir(parents=True, exist_ok=True)
        
        results = {
            "timestamp": datetime.utcnow().isoformat(),
            "exports": {},
        }
        
        # 导出农场数据
        farms_export = export_path / "farms_export.json"
        try:
            all_farms = {}
            for farm_key, farm in self.food_manager.farms.items():
                all_farms[farm_key] = farm.to_dict()
            
            with open(farms_export, 'w', encoding='utf-8') as f:
                json.dump(all_farms, f, indent=2, ensure_ascii=False)
            
            results["exports"]["farms"] = str(farms_export)
        except Exception as e:
            results["exports"]["farms"] = f"Error: {e}"
        
        # 导出 Cookie 数据
        cookies_export = export_path / "cookies_export.json"
        if self.cookie_manager.export_cookies_to_json(str(cookies_export)):
            results["exports"]["cookies"] = str(cookies_export)
        else:
            results["exports"]["cookies"] = "Error"
        
        return results
    
    def get_sync_queue_status(self) -> Dict:
        """获取同步队列状态"""
        with self.lock:
            return {
                "queue_size": len(self.sync_queue),
                "is_syncing": self.is_syncing,
                "recent_operations": self.sync_queue[-10:],  # 最后 10 个操作
            }


# ============================================================================
# 集成示例
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print(" 🎮 统一游戏系统管理器演示")
    print("=" * 70)
    print()
    
    from pathlib import Path
    
    # 创建管理器
    manager = UnifiedGameSystemsManager(
        cache_dir=Path(".monster"),
        enable_auto_sync=True,
    )
    
    # 演示 1: 食物系统
    print("1️⃣  食物系统操作")
    print("-" * 70)
    farm = manager.create_farm("alice", "repo", "https://github.com/alice/repo")
    print(f"✓ 创建农场")
    
    food = manager.add_food_to_farm("alice", "repo", "cookie", 3)
    print(f"✓ 添加食物")
    
    success, response = manager.consume_food("alice", "repo", food.id, "bob", "pikachu")
    print(f"✓ 消费食物: {response.get('remaining_quantity')}/{response.get('max_quantity')}")
    print()
    
    # 演示 2: Cookie 系统
    print("2️⃣  Cookie 系统操作")
    print("-" * 70)
    manager.register_cookie("0xcookie123", "cookie", "main.py", "alice")
    print(f"✓ 注册 Cookie")
    
    success, response = manager.claim_cookie("0xcookie123", "bob")
    print(f"✓ 索赔 Cookie: 获得 {response.get('rewards')} 奖励")
    print()
    
    # 演示 3: 系统状态
    print("3️⃣  系统状态")
    print("-" * 70)
    status = manager.get_system_status()
    print(json.dumps(status, indent=2, ensure_ascii=False))
    print()
    
    # 演示 4: 同步队列
    print("4️⃣  同步队列状态")
    print("-" * 70)
    queue_status = manager.get_sync_queue_status()
    print(f"队列大小: {queue_status['queue_size']}")
    print(f"正在同步: {queue_status['is_syncing']}")
    print()
    
    print("=" * 70)
    print("✓ 演示完成!")
    print("=" * 70)
