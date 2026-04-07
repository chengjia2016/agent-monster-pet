#!/usr/bin/env python3
"""
Data Migration Script
Migrates existing user data from local storage to Judge Server format
Prepares data for centralized storage while maintaining fallback capability
"""

import sys
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Dict, List, Tuple

from user_manager import UserManager
from economy_manager import EconomyManager
from shop_manager import Shop
from judge_server_user_manager import JudgeServerUserManager, JudgeServerUser
from hybrid_user_data_manager import HybridUserDataManager


class DataMigrationManager:
    """Manages migration from local to Judge Server"""
    
    def __init__(self, data_dir: str = ".monster"):
        self.data_dir = Path(data_dir)
        self.user_manager = UserManager(data_dir)
        self.economy_manager = EconomyManager(data_dir)
        self.shop_manager = Shop(data_dir)
        self.judge_server = JudgeServerUserManager()
        self.hybrid_manager = HybridUserDataManager(
            self.data_dir,
            judge_server_manager=self.judge_server
        )
        
        self.migration_log = []
    
    def export_user_data(self, user_id: str) -> Dict:
        """Export complete user data from local storage"""
        user = self.user_manager.get_user(user_id)
        if not user:
            return None
        
        account = self.economy_manager.get_account(user_id)
        inventory = self.shop_manager.get_user_inventory(user_id)
        
        # Convert inventory dict to list of items
        items_list = []
        if inventory:
            for item_id, item_data in inventory.items():
                items_list.append({
                    "id": item_id,
                    "name": item_data["item"]["name"],
                    "description": item_data["item"]["description"],
                    "quantity": item_data["quantity"],
                    "price": item_data["item"]["price"],
                    "acquired_at": item_data.get("acquired_at", datetime.now(timezone.utc).isoformat())
                })
        
        return {
            "github_id": user.github_id,
            "github_login": user.github_login,
            "user_id": user.user_id,
            "email": user.email,
            "avatar_url": user.avatar_url,
            "registered_at": user.registered_at,
            "last_login": user.last_login,
            "balance": account.balance if account else 0.0,
            "pokemons": [],  # Would come from pokemon manager
            "items": items_list,
            "transactions": [
                t.to_dict() if hasattr(t, 'to_dict') else t
                for t in (account.transactions if account else [])
            ],
            "migrated_at": datetime.now(timezone.utc).isoformat(),
            "migration_version": "1.0"
        }
    
    def cache_user_data_locally(self, user_data: Dict) -> bool:
        """Cache user data locally using hybrid manager"""
        try:
            self.hybrid_manager.save_user_data(
                github_id=user_data["github_id"],
                user_data=user_data,
                sync_to_server=False  # Don't sync yet, just cache
            )
            return True
        except Exception as e:
            print(f"  ✗ Failed to cache: {e}")
            return False
    
    def migrate_user_to_server(self, user_data: Dict) -> Tuple[bool, str]:
        """Migrate single user to Judge Server"""
        try:
            # Attempt to sync to server
            success = self.hybrid_manager.save_user_data(
                github_id=user_data["github_id"],
                user_data=user_data,
                sync_to_server=True
            )
            
            if success:
                return True, "Synced to server"
            else:
                return False, "Server sync failed, cached locally"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def generate_migration_report(self, results: List[Dict]) -> str:
        """Generate migration report"""
        total = len(results)
        synced = sum(1 for r in results if r["synced"])
        cached = sum(1 for r in results if r["cached"])
        failed = sum(1 for r in results if r["failed"])
        
        report = f"""
MIGRATION REPORT
================

Total Users: {total}
Successfully Synced to Server: {synced}
Cached Locally (Server Unavailable): {cached}
Failed: {failed}

Details:
--------
"""
        
        for result in results:
            status = "✓" if result["synced"] else ("◯" if result["cached"] else "✗")
            report += f"\n{status} {result['github_login']} (ID: {result['github_id']})"
            report += f"\n  Message: {result['message']}"
        
        return report
    
    def migrate_all_users(self, dry_run: bool = True) -> List[Dict]:
        """Migrate all users"""
        users = self.user_manager.list_users()
        results = []
        
        print(f"\nMigrating {len(users)} users...")
        print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will sync data)'}\n")
        
        for idx, user in enumerate(users, 1):
            print(f"[{idx}/{len(users)}] Migrating {user.github_login}...")
            
            try:
                # Export data
                user_data = self.export_user_data(user.user_id)
                if not user_data:
                    print(f"  ✗ Failed to export user data")
                    results.append({
                        "github_id": user.github_id,
                        "github_login": user.github_login,
                        "synced": False,
                        "cached": False,
                        "failed": True,
                        "message": "Export failed"
                    })
                    continue
                
                # Cache locally
                cached = self.cache_user_data_locally(user_data)
                print(f"  • Cached locally: {'✓' if cached else '✗'}")
                
                # Migrate to server
                if not dry_run:
                    synced, message = self.migrate_user_to_server(user_data)
                    print(f"  • Server sync: {message}")
                else:
                    synced = False
                    message = "[DRY RUN] Would sync to server"
                    print(f"  • Server sync: {message}")
                
                results.append({
                    "github_id": user.github_id,
                    "github_login": user.github_login,
                    "synced": synced,
                    "cached": cached,
                    "failed": False,
                    "message": message
                })
                
            except Exception as e:
                print(f"  ✗ Error: {e}")
                results.append({
                    "github_id": user.github_id,
                    "github_login": user.github_login,
                    "synced": False,
                    "cached": False,
                    "failed": True,
                    "message": str(e)
                })
        
        return results


def main():
    """Run migration"""
    print("\n" + "="*60)
    print("DATA MIGRATION TOOL - Judge Server Integration")
    print("="*60)
    
    migrator = DataMigrationManager()
    
    # First, run a dry run
    print("\n📋 PHASE 1: DRY RUN (analyzing what would be migrated)")
    dry_results = migrator.migrate_all_users(dry_run=True)
    
    # Show report
    report = migrator.generate_migration_report(dry_results)
    print(report)
    
    # Ask for confirmation
    print("\n" + "="*60)
    print("PHASE 2: LIVE MIGRATION")
    print("="*60)
    
    response = input("\nProceed with live migration? (yes/no): ").strip().lower()
    
    if response != "yes":
        print("\n✗ Migration cancelled")
        return 1
    
    # Run actual migration
    print("\n📤 Running live migration...")
    live_results = migrator.migrate_all_users(dry_run=False)
    
    # Final report
    report = migrator.generate_migration_report(live_results)
    print(report)
    
    # Summary
    synced = sum(1 for r in live_results if r["synced"])
    cached = sum(1 for r in live_results if r["cached"])
    
    print("\n" + "="*60)
    print("MIGRATION SUMMARY")
    print("="*60)
    print(f"✓ Synced to Judge Server: {synced}")
    print(f"◯ Cached Locally (Server Unavailable): {cached}")
    print(f"✗ Failed: {sum(1 for r in live_results if r['failed'])}")
    print(f"\nTotal Migrated: {synced + cached}")
    
    # Save migration report
    report_file = Path(".monster/migration_report.json")
    with open(report_file, "w") as f:
        json.dump(live_results, f, indent=2)
    print(f"\nMigration report saved to: {report_file}")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
