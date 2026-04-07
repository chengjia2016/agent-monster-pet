#!/usr/bin/env python3
"""
Persistent Cookie Manager
增强的 Cookie 系统，支持本地持久化、索赔机制和统计

特性：
- Cookie 生成、扫描和索赔机制
- 本地 JSON 持久化（解决 Cookie 数据丢失问题）
- Cookie 验证和防重复索赔
- 玩家 Cookie 统计和历史记录
- 支持 Judge Server 迁移（离线备用）
"""

import json
import hashlib
import os
import random
import string
import threading
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import re

# 导入现有的 cookie 模块
from cookie import (
    COOKIE_TEMPLATES,
    COMMENT_FORMATS,
    generate_cookie_id,
    generate_cookie,
    scan_file_for_cookies,
    scan_directory_for_cookies,
)


class PersistentCookieManager:
    """
    Cookie 系统管理器 - 支持持久化和索赔机制
    
    数据存储架构：
    .monster/cookies/
    ├── cookie_registry.json         # 所有 Cookie 注册表（cookie_id -> metadata）
    ├── player_cookies/
    │   ├── player1.json             # 玩家 1 的 Cookie 索赔记录
    │   ├── player2.json             # 玩家 2 的 Cookie 索赔记录
    │   └── ...
    └── cookie_history.jsonl         # Cookie 事件历史（按行存储，每行一条记录）
    """
    
    def __init__(self, cache_dir: Path = None, judge_server_client=None):
        """
        初始化持久化 Cookie 管理器
        
        Args:
            cache_dir: 缓存目录路径（默认 .monster）
            judge_server_client: Judge Server 客户端实例（可选）
        """
        if cache_dir is None:
            cache_dir = Path(".monster")
        
        self.cache_dir = Path(cache_dir)
        self.cookies_dir = self.cache_dir / "cookies"
        self.cookies_dir.mkdir(parents=True, exist_ok=True)
        
        self.registry_file = self.cookies_dir / "cookie_registry.json"
        self.player_cookies_dir = self.cookies_dir / "player_cookies"
        self.player_cookies_dir.mkdir(parents=True, exist_ok=True)
        self.history_file = self.cookies_dir / "cookie_history.jsonl"
        
        # Judge Server 客户端
        self.judge_server_client = judge_server_client
        
        # 线程锁
        self.lock = threading.RLock()
        
        # 内存缓存
        self.cookie_registry: Dict[str, Dict] = {}  # cookie_id -> metadata
        self.player_claims: Dict[str, List[str]] = {}  # player_id -> [claimed_cookie_ids]
        
        # 加载现有数据
        self._load_registry()
        self._load_all_player_claims()
    
    def _load_registry(self) -> int:
        """
        从本地加载 Cookie 注册表
        
        Returns:
            加载的 Cookie 数量
        """
        count = 0
        try:
            if self.registry_file.exists():
                with open(self.registry_file, 'r', encoding='utf-8') as f:
                    self.cookie_registry = json.load(f)
                count = len(self.cookie_registry)
                print(f"✓ 从注册表加载了 {count} 个 Cookie")
        except Exception as e:
            print(f"⚠️  加载 Cookie 注册表失败: {e}")
            self.cookie_registry = {}
        
        return count
    
    def _load_all_player_claims(self) -> int:
        """
        从本地加载所有玩家的 Cookie 索赔记录
        
        Returns:
            加载的玩家数量
        """
        count = 0
        try:
            for claim_file in self.player_cookies_dir.glob("*.json"):
                try:
                    with open(claim_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    player_id = data.get("player_id")
                    if player_id:
                        self.player_claims[player_id] = data.get("claimed_cookies", [])
                        count += 1
                except Exception as e:
                    print(f"⚠️  加载玩家索赔记录失败: {claim_file} - {e}")
        except Exception as e:
            print(f"⚠️  遍历玩家目录失败: {e}")
        
        if count > 0:
            print(f"✓ 从本地加载了 {count} 个玩家的 Cookie 记录")
        
        return count
    
    def _save_registry(self) -> bool:
        """保存 Cookie 注册表到本地"""
        with self.lock:
            try:
                with open(self.registry_file, 'w', encoding='utf-8') as f:
                    json.dump(self.cookie_registry, f, indent=2, ensure_ascii=False)
                return True
            except Exception as e:
                print(f"❌ 保存 Cookie 注册表失败: {e}")
                return False
    
    def _save_player_claims(self, player_id: str) -> bool:
        """保存玩家的 Cookie 索赔记录"""
        with self.lock:
            try:
                player_file = self.player_cookies_dir / f"{player_id}.json"
                claimed = self.player_claims.get(player_id, [])
                
                data = {
                    "player_id": player_id,
                    "last_updated": datetime.utcnow().isoformat(),
                    "claimed_cookies": claimed,
                    "total_claimed": len(claimed),
                }
                
                with open(player_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                
                return True
            except Exception as e:
                print(f"❌ 保存玩家索赔记录失败: {e}")
                return False
    
    def _add_history_record(self, event: str, player_id: str, cookie_id: str, details: Dict = None) -> bool:
        """
        添加 Cookie 事件到历史记录（JSONL 格式）
        
        Args:
            event: 事件类型 (generated, scanned, claimed, validated, etc.)
            player_id: 玩家 ID
            cookie_id: Cookie ID
            details: 额外详情
            
        Returns:
            是否成功
        """
        try:
            record = {
                "timestamp": datetime.utcnow().isoformat(),
                "event": event,
                "player_id": player_id,
                "cookie_id": cookie_id,
                **(details or {}),
            }
            
            with open(self.history_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(record, ensure_ascii=False) + '\n')
            
            return True
        except Exception as e:
            print(f"❌ 添加历史记录失败: {e}")
            return False
    
    def register_cookie(
        self,
        cookie_id: str,
        cookie_type: str = "cookie",
        source_file: str = None,
        generator_id: str = None,
    ) -> bool:
        """
        注册一个新 Cookie
        
        Args:
            cookie_id: Cookie ID
            cookie_type: Cookie 类型
            source_file: 来源文件（如果从代码扫描）
            generator_id: 生成者 ID
            
        Returns:
            是否成功
        """
        with self.lock:
            # 检查重复
            if cookie_id in self.cookie_registry:
                return False
            
            self.cookie_registry[cookie_id] = {
                "id": cookie_id,
                "type": cookie_type,
                "emoji": COOKIE_TEMPLATES.get(cookie_type, {}).get("emoji", "🍪"),
                "source_file": source_file,
                "generator_id": generator_id,
                "created_at": datetime.utcnow().isoformat(),
                "claimed_by": None,
                "claimed_at": None,
                "claimed_times": 0,
            }
            
            self._save_registry()
            self._add_history_record("generated", generator_id or "system", cookie_id)
            
            return True
    
    def claim_cookie(self, cookie_id: str, player_id: str) -> Tuple[bool, Dict]:
        """
        玩家索赔 Cookie（领取经验和能量）
        
        Args:
            cookie_id: Cookie ID
            player_id: 玩家 ID
            
        Returns:
            (是否成功, 响应数据)
        """
        with self.lock:
            # 检查 Cookie 是否存在
            if cookie_id not in self.cookie_registry:
                return False, {"error": "Cookie not found"}
            
            # 检查是否已索赔
            if player_id in self.player_claims and cookie_id in self.player_claims[player_id]:
                return False, {
                    "error": "Cookie already claimed by this player",
                    "claimed_at": self.cookie_registry[cookie_id].get("claimed_at"),
                }
            
            # 获取 Cookie 信息
            cookie = self.cookie_registry[cookie_id]
            cookie_type = cookie["type"]
            cookie_info = COOKIE_TEMPLATES.get(cookie_type, COOKIE_TEMPLATES["cookie"])
            
            # 更新 Cookie 为已索赔
            cookie["claimed_by"] = player_id
            cookie["claimed_at"] = datetime.utcnow().isoformat()
            cookie["claimed_times"] += 1
            
            # 记录玩家的索赔
            if player_id not in self.player_claims:
                self.player_claims[player_id] = []
            self.player_claims[player_id].append(cookie_id)
            
            # 持久化
            self._save_registry()
            self._save_player_claims(player_id)
            self._add_history_record("claimed", player_id, cookie_id)
            
            return True, {
                "success": True,
                "cookie_id": cookie_id,
                "cookie_type": cookie_type,
                "emoji": cookie_info["emoji"],
                "rewards": {
                    "exp": cookie_info["exp_bonus"],
                    "energy": cookie_info["en_bonus"],
                },
                "claimed_at": cookie["claimed_at"],
            }
    
    def validate_cookie(self, cookie_id: str) -> Tuple[bool, Dict]:
        """
        验证 Cookie 的有效性
        
        Args:
            cookie_id: Cookie ID
            
        Returns:
            (是否有效, 验证信息)
        """
        if cookie_id not in self.cookie_registry:
            return False, {"error": "Cookie not found"}
        
        cookie = self.cookie_registry[cookie_id]
        
        is_valid = True
        message = "Cookie is valid"
        
        if cookie.get("claimed_by"):
            is_valid = False
            message = f"Cookie already claimed by {cookie['claimed_by']}"
        
        return is_valid, {
            "valid": is_valid,
            "message": message,
            "cookie": cookie,
        }
    
    def scan_and_register_cookies(
        self,
        directory: str,
        player_id: str,
    ) -> Tuple[int, List[str]]:
        """
        扫描目录并注册所有 Cookie
        
        Args:
            directory: 扫描目录
            player_id: 扫描者 ID
            
        Returns:
            (发现的 Cookie 数量, [新 Cookie IDs])
        """
        cookies = scan_directory_for_cookies(directory)
        new_cookie_ids = []
        
        with self.lock:
            for cookie in cookies:
                cookie_id = cookie["cookie_id"]
                
                # 只注册新 Cookie
                if cookie_id not in self.cookie_registry:
                    self.register_cookie(
                        cookie_id,
                        cookie_type=cookie.get("type", "cookie"),
                        source_file=cookie.get("file"),
                        generator_id=player_id,
                    )
                    new_cookie_ids.append(cookie_id)
        
        if new_cookie_ids:
            print(f"✓ 扫描到 {len(new_cookie_ids)} 个新 Cookie")
        
        return len(cookies), new_cookie_ids
    
    def get_player_statistics(self, player_id: str) -> Dict:
        """
        获取玩家的 Cookie 统计信息
        
        Args:
            player_id: 玩家 ID
            
        Returns:
            统计字典
        """
        with self.lock:
            claimed_cookies = self.player_claims.get(player_id, [])
            
            # 统计类型和奖励
            stats = {
                "player_id": player_id,
                "total_claimed": len(claimed_cookies),
                "by_type": {},
                "total_rewards": {"exp": 0, "energy": 0},
                "claimed_cookies": [],
            }
            
            for cookie_id in claimed_cookies:
                if cookie_id in self.cookie_registry:
                    cookie = self.cookie_registry[cookie_id]
                    cookie_type = cookie["type"]
                    cookie_info = COOKIE_TEMPLATES.get(cookie_type, {})
                    
                    # 统计类型
                    if cookie_type not in stats["by_type"]:
                        stats["by_type"][cookie_type] = 0
                    stats["by_type"][cookie_type] += 1
                    
                    # 累计奖励
                    stats["total_rewards"]["exp"] += cookie_info.get("exp_bonus", 0)
                    stats["total_rewards"]["energy"] += cookie_info.get("en_bonus", 0)
                    
                    # 添加到列表
                    stats["claimed_cookies"].append({
                        "cookie_id": cookie_id,
                        "type": cookie_type,
                        "emoji": cookie["emoji"],
                        "claimed_at": cookie["claimed_at"],
                        "source_file": cookie.get("source_file"),
                    })
            
            return stats
    
    def get_global_statistics(self) -> Dict:
        """
        获取全局 Cookie 统计
        
        Returns:
            统计字典
        """
        with self.lock:
            total_registered = len(self.cookie_registry)
            total_claimed = sum(len(v) for v in self.player_claims.values())
            
            stats = {
                "total_cookies": total_registered,
                "total_claimed": total_claimed,
                "unclaimed": total_registered - total_claimed,
                "by_type": {},
                "top_players": [],
            }
            
            # 按类型统计
            for cookie in self.cookie_registry.values():
                cookie_type = cookie["type"]
                if cookie_type not in stats["by_type"]:
                    stats["by_type"][cookie_type] = {"total": 0, "claimed": 0}
                
                stats["by_type"][cookie_type]["total"] += 1
                if cookie.get("claimed_by"):
                    stats["by_type"][cookie_type]["claimed"] += 1
            
            # 排名前玩家
            player_rankings = [
                (pid, len(cookies))
                for pid, cookies in self.player_claims.items()
            ]
            player_rankings.sort(key=lambda x: x[1], reverse=True)
            stats["top_players"] = [
                {"player_id": pid, "claimed_count": count}
                for pid, count in player_rankings[:10]
            ]
            
            return stats
    
    def export_cookies_to_json(self, filepath: str) -> bool:
        """
        导出所有 Cookie 数据为 JSON（备份用）
        
        Args:
            filepath: 输出文件路径
            
        Returns:
            是否成功
        """
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump({
                    "registry": self.cookie_registry,
                    "player_claims": self.player_claims,
                    "exported_at": datetime.utcnow().isoformat(),
                }, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ 导出 Cookie 失败: {e}")
            return False
    
    def get_history_events(self, player_id: str = None, limit: int = 100) -> List[Dict]:
        """
        获取历史事件
        
        Args:
            player_id: 玩家 ID（可选，用于过滤）
            limit: 返回最多的记录数
            
        Returns:
            事件列表
        """
        events = []
        try:
            if self.history_file.exists():
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        if line.strip():
                            event = json.loads(line)
                            if player_id is None or event.get("player_id") == player_id:
                                events.append(event)
        except Exception as e:
            print(f"⚠️  读取历史记录失败: {e}")
        
        # 返回最后 limit 条记录
        return events[-limit:]


# ============================================================================
# 示例和测试
# ============================================================================

if __name__ == "__main__":
    print("=" * 70)
    print(" 🍪 持久化 Cookie 管理系统演示")
    print("=" * 70)
    print()
    
    from pathlib import Path
    
    # 创建管理器
    manager = PersistentCookieManager(cache_dir=Path(".monster"))
    
    # 演示 1: 注册 Cookie
    print("1️⃣  注册新 Cookie")
    print("-" * 70)
    cookies_to_register = [
        ("0x1234567890abcdef", "cookie", "src/main.py"),
        ("0xfedcba0987654321", "gene", "src/utils.py"),
        ("0xabcdef1234567890", "donut", "README.md"),
    ]
    
    for cookie_id, cookie_type, source_file in cookies_to_register:
        success = manager.register_cookie(cookie_id, cookie_type, source_file, "alice")
        print(f"{'✓' if success else '✗'} 注册 {cookie_id} ({cookie_type})")
    print()
    
    # 演示 2: 玩家索赔 Cookie
    print("2️⃣  玩家索赔 Cookie")
    print("-" * 70)
    success, response = manager.claim_cookie("0x1234567890abcdef", "bob")
    print(f"✓ 索赔结果: {'成功' if success else '失败'}")
    if success:
        print(f"  奖励: {response['rewards']}")
        print(f"  时间: {response['claimed_at']}")
    print()
    
    # 演示 3: 验证 Cookie
    print("3️⃣  验证 Cookie")
    print("-" * 70)
    valid, result = manager.validate_cookie("0xfedcba0987654321")
    print(f"✓ 有效性: {result['valid']}")
    print(f"  信息: {result['message']}")
    print()
    
    # 演示 4: 玩家统计
    print("4️⃣  玩家 Cookie 统计")
    print("-" * 70)
    stats = manager.get_player_statistics("bob")
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print()
    
    # 演示 5: 全局统计
    print("5️⃣  全局 Cookie 统计")
    print("-" * 70)
    global_stats = manager.get_global_statistics()
    print(json.dumps(global_stats, indent=2, ensure_ascii=False))
    print()
    
    # 演示 6: 重启后加载数据
    print("6️⃣  模拟应用重启 - 从本地加载数据")
    print("-" * 70)
    manager2 = PersistentCookieManager(cache_dir=Path(".monster"))
    print(f"✓ 新实例加载了 {len(manager2.cookie_registry)} 个 Cookie")
    print(f"✓ 加载了 {len(manager2.player_claims)} 个玩家的记录")
    print()
    
    print("=" * 70)
    print("✓ 演示完成!")
    print("=" * 70)
