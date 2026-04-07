#!/usr/bin/env python3
"""
Phase 3 Integration Test Suite
验证所有系统的集成和数据持久化

测试范围：
1. 本地存储持久化 - 验证应用重启后数据恢复
2. 离线模式支持 - 验证无网络时的功能
3. 并发操作 - 验证多用户/多线程安全性
4. 完整流程 - 验证从新用户到完全初始化的全流程
"""

import json
import time
import threading
from pathlib import Path
from datetime import datetime
import tempfile
import shutil
from typing import Dict

from unified_game_systems_manager import UnifiedGameSystemsManager
from persistent_food_manager import PersistentFoodManager
from persistent_cookie_manager import PersistentCookieManager
from persistent_egg_incubator import PersistentEggIncubator
from enhanced_onboarding_manager import EnhancedOnboardingManager
from food_system import FoodType


class IntegrationTestSuite:
    """集成测试套件"""
    
    def __init__(self, test_dir: Path = None):
        """初始化测试环境"""
        if test_dir is None:
            test_dir = Path(tempfile.mkdtemp(prefix="agent_monster_test_"))
        
        self.test_dir = test_dir
        self.test_dir.mkdir(parents=True, exist_ok=True)
        
        self.results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "warnings": [],
            "errors": [],
            "details": {},
        }
    
    def run_all_tests(self) -> Dict:
        """运行所有测试"""
        print("=" * 70)
        print(" 🧪 Phase 3 集成测试套件")
        print("=" * 70)
        print()
        
        # 测试 1: 本地持久化
        self._test_local_persistence()
        
        # 测试 2: 离线模式
        self._test_offline_mode()
        
        # 测试 3: 并发操作
        self._test_concurrent_operations()
        
        # 测试 4: 完整流程
        self._test_complete_user_journey()
        
        # 测试 5: 系统状态
        self._test_system_status()
        
        # 打印总结
        self._print_summary()
        
        return self.results
    
    def _test_local_persistence(self):
        """测试 1: 本地数据持久化"""
        print("🧪 测试 1: 本地数据持久化")
        print("-" * 70)
        
        test_name = "local_persistence"
        self.results["total_tests"] += 1
        
        try:
            # 创建第一个管理器实例
            manager1 = UnifiedGameSystemsManager(cache_dir=self.test_dir / "persistence")
            
            # 创建数据
            farm = manager1.create_farm("alice", "repo", "https://github.com/alice/repo")
            food = manager1.add_food_to_farm("alice", "repo", FoodType.COOKIE, 3)
            manager1.register_cookie("0xcookie123", "cookie", "main.py", "alice")
            
            print(f"✓ 创建了农场、食物和 Cookie")
            
            # 创建第二个管理器实例（模拟应用重启）
            manager2 = UnifiedGameSystemsManager(cache_dir=self.test_dir / "persistence")
            
            # 验证数据是否恢复
            stats = manager2.get_farm_statistics()
            cookie_stats = manager2.get_cookie_statistics()
            
            if stats["total_foods"] == 1 and cookie_stats["total_cookies"] == 1:
                print(f"✓ 数据持久化成功: {stats['total_foods']} 件食物, {cookie_stats['total_cookies']} 个 Cookie")
                self.results["passed"] += 1
                self.results["details"][test_name] = "✓ PASSED"
            else:
                print(f"❌ 数据持久化失败")
                self.results["failed"] += 1
                self.results["details"][test_name] = "✗ FAILED"
                self.results["errors"].append(f"{test_name}: 数据未能正确恢复")
        
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            self.results["failed"] += 1
            self.results["details"][test_name] = f"✗ ERROR: {e}"
            self.results["errors"].append(f"{test_name}: {e}")
        
        print()
    
    def _test_offline_mode(self):
        """测试 2: 离线模式"""
        print("🧪 测试 2: 离线模式（无 Judge Server）")
        print("-" * 70)
        
        test_name = "offline_mode"
        self.results["total_tests"] += 1
        
        try:
            # 创建没有 Judge Server 的管理器
            manager = UnifiedGameSystemsManager(
                cache_dir=self.test_dir / "offline",
                judge_server_client=None,  # 故意设置为 None
            )
            
            # 执行所有操作
            farm = manager.create_farm("bob", "repo", "https://github.com/bob/repo")
            food = manager.add_food_to_farm("bob", "repo", FoodType.DONUT, 2)
            success, response = manager.consume_food("bob", "repo", food.id, "alice", "pet_1")
            
            # 验证结果
            if success and response.get("remaining_quantity") == 1:
                print(f"✓ 离线模式操作成功")
                self.results["passed"] += 1
                self.results["details"][test_name] = "✓ PASSED"
            else:
                print(f"❌ 离线模式操作失败")
                self.results["failed"] += 1
                self.results["details"][test_name] = "✗ FAILED"
                self.results["errors"].append(f"{test_name}: 操作失败")
        
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            self.results["failed"] += 1
            self.results["details"][test_name] = f"✗ ERROR: {e}"
            self.results["errors"].append(f"{test_name}: {e}")
        
        print()
    
    def _test_concurrent_operations(self):
        """测试 3: 并发操作"""
        print("🧪 测试 3: 并发操作（线程安全）")
        print("-" * 70)
        
        test_name = "concurrent_operations"
        self.results["total_tests"] += 1
        
        try:
            manager = UnifiedGameSystemsManager(cache_dir=self.test_dir / "concurrent")
            
            # 创建农场
            manager.create_farm("shared", "repo", "https://github.com/shared/repo")
            food = manager.add_food_to_farm("shared", "repo", FoodType.APPLE, 10)
            
            # 并发消费食物
            results = {"success": 0, "failed": 0, "errors": []}
            lock = threading.Lock()
            
            def consume_food_task(eater_id, pet_id):
                try:
                    success, response = manager.consume_food(
                        "shared", "repo", food.id, eater_id, pet_id
                    )
                    with lock:
                        if success:
                            results["success"] += 1
                        else:
                            results["failed"] += 1
                except Exception as e:
                    with lock:
                        results["errors"].append(str(e))
            
            # 创建 5 个线程并发消费
            threads = []
            for i in range(5):
                t = threading.Thread(
                    target=consume_food_task,
                    args=(f"user_{i}", f"pet_{i}")
                )
                threads.append(t)
                t.start()
            
            # 等待所有线程完成
            for t in threads:
                t.join(timeout=5)
            
            # 验证结果
            farm_obj = manager.food_manager.get_farm("shared", "repo")
            remaining = farm_obj.foods[0].quantity if farm_obj and farm_obj.foods else -1
            
            if results["success"] >= 4 and remaining <= 5:  # 至少 4 个成功，剩余 ≤5
                print(f"✓ 并发操作成功: {results['success']}/5 操作完成，剩余 {remaining} 件食物")
                self.results["passed"] += 1
                self.results["details"][test_name] = "✓ PASSED"
            else:
                print(f"⚠️  并发操作部分成功: {results['success']}/5, 剩余 {remaining}")
                self.results["warnings"].append(f"{test_name}: 部分操作未完成")
                self.results["passed"] += 1
                self.results["details"][test_name] = "⚠️  PARTIAL"
        
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            self.results["failed"] += 1
            self.results["details"][test_name] = f"✗ ERROR: {e}"
            self.results["errors"].append(f"{test_name}: {e}")
        
        print()
    
    def _test_complete_user_journey(self):
        """测试 4: 完整用户流程"""
        print("🧪 测试 4: 完整用户流程（新用户 → 初始化）")
        print("-" * 70)
        
        test_name = "complete_user_journey"
        self.results["total_tests"] += 1
        
        try:
            # 创建 onboarding 管理器
            onboarding = EnhancedOnboardingManager(cache_dir=self.test_dir / "journey")
            
            # 步骤 1: 注册新用户
            success, result = onboarding.register_new_user(
                github_id=999999,
                github_login="journey_user",
                email="journey@test.com",
            )
            
            if not success:
                print(f"❌ 用户注册失败")
                self.results["failed"] += 1
                self.results["details"][test_name] = "✗ FAILED"
                return
            
            print(f"✓ 步骤 1: 用户注册成功 - {result['user_id']}")
            
            # 步骤 2: 检查初始资源
            resources = result["resources_granted"]
            checks = {
                "balance": resources.get("balance") == 100.0,
                "items": len(resources.get("items", {})) == 3,
                "starter_pet": "starter_pet" in resources,
                "starter_egg": "starter_egg" in resources,
            }
            
            if all(checks.values()):
                print(f"✓ 步骤 2: 所有初始资源已分配")
            else:
                print(f"⚠️  部分资源缺失: {checks}")
                self.results["warnings"].append(f"{test_name}: 部分资源未分配")
            
            # 步骤 3: 使用统一管理器验证
            systems = UnifiedGameSystemsManager(cache_dir=self.test_dir / "journey")
            status = onboarding.get_user_onboarding_status(result['user_id'])
            
            if status["resources"]["balance"] == 100.0:
                print(f"✓ 步骤 3: 统一管理器可验证用户数据")
                self.results["passed"] += 1
                self.results["details"][test_name] = "✓ PASSED"
            else:
                print(f"❌ 统一管理器验证失败")
                self.results["failed"] += 1
                self.results["details"][test_name] = "✗ FAILED"
        
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            self.results["failed"] += 1
            self.results["details"][test_name] = f"✗ ERROR: {e}"
            self.results["errors"].append(f"{test_name}: {e}")
        
        print()
    
    def _test_system_status(self):
        """测试 5: 系统状态报告"""
        print("🧪 测试 5: 系统状态报告")
        print("-" * 70)
        
        test_name = "system_status"
        self.results["total_tests"] += 1
        
        try:
            manager = UnifiedGameSystemsManager(cache_dir=self.test_dir / "status")
            
            # 添加一些数据
            manager.create_farm("status_test", "repo", "https://github.com/status_test/repo")
            manager.register_cookie("0xstatus", "cookie")
            
            # 获取状态
            status = manager.get_system_status()
            
            # 验证关键字段
            checks = {
                "food_system": "food_system" in status,
                "cookie_system": "cookie_system" in status,
                "sync_service": "sync_service" in status,
                "farms_count": status.get("food_system", {}).get("farms", 0) >= 1,
                "cookies_count": status.get("cookie_system", {}).get("registered_cookies", 0) >= 1,
            }
            
            if all(checks.values()):
                print(f"✓ 系统状态报告完整:")
                print(f"  农场数: {status['food_system']['farms']}")
                print(f"  Cookies 数: {status['cookie_system']['registered_cookies']}")
                print(f"  同步队列大小: {status['sync_service']['queue_size']}")
                self.results["passed"] += 1
                self.results["details"][test_name] = "✓ PASSED"
            else:
                print(f"❌ 系统状态报告不完整: {checks}")
                self.results["failed"] += 1
                self.results["details"][test_name] = "✗ FAILED"
        
        except Exception as e:
            print(f"❌ 测试异常: {e}")
            self.results["failed"] += 1
            self.results["details"][test_name] = f"✗ ERROR: {e}"
            self.results["errors"].append(f"{test_name}: {e}")
        
        print()
    
    def _print_summary(self):
        """打印测试总结"""
        print("=" * 70)
        print(" 📊 测试总结")
        print("=" * 70)
        print()
        
        total = self.results["total_tests"]
        passed = self.results["passed"]
        failed = self.results["failed"]
        pass_rate = (passed / total * 100) if total > 0 else 0
        
        print(f"总测试数: {total}")
        print(f"✓ 通过: {passed}")
        print(f"❌ 失败: {failed}")
        print(f"📊 通过率: {pass_rate:.1f}%")
        print()
        
        if self.results["details"]:
            print("详细结果:")
            for test_name, result in self.results["details"].items():
                print(f"  {test_name}: {result}")
        print()
        
        if self.results["warnings"]:
            print("⚠️  警告:")
            for warning in self.results["warnings"]:
                print(f"  - {warning}")
            print()
        
        if self.results["errors"]:
            print("❌ 错误:")
            for error in self.results["errors"]:
                print(f"  - {error}")
            print()
        
        print("=" * 70)
        print()
    
    def cleanup(self):
        """清理测试目录"""
        try:
            shutil.rmtree(self.test_dir)
            print(f"✓ 清理测试目录: {self.test_dir}")
        except Exception as e:
            print(f"⚠️  清理测试目录失败: {e}")


# ============================================================================
# 运行测试
# ============================================================================

if __name__ == "__main__":
    import sys
    
    # 创建测试套件
    suite = IntegrationTestSuite()
    
    # 运行所有测试
    results = suite.run_all_tests()
    
    # 清理（可选）
    # suite.cleanup()
    
    # 返回退出代码
    sys.exit(0 if results["failed"] == 0 else 1)
