#!/usr/bin/env python3
"""
Shop System
Manages item catalog, purchases, and inventory
"""

import json
from pathlib import Path
from typing import Dict, Optional, Any, List
from enum import Enum
from dataclasses import dataclass, asdict


class ItemType(Enum):
    """Types of shop items"""
    POKEBALL = "pokeball"          # 精灵球
    ULTRABALL = "ultraball"        # 超级球
    SEED = "seed"                  # 种子
    FOOD = "food"                  # 食物
    POTION = "potion"              # 药剂
    REVIVE = "revive"              # 复活液
    BOOST = "boost"                # 增强剂


@dataclass
class ShopItem:
    """Shop item definition"""
    item_id: str
    name: str
    description: str
    item_type: ItemType
    price: float
    stock: int
    max_stock: int
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "item_id": self.item_id,
            "name": self.name,
            "description": self.description,
            "item_type": self.item_type.value,
            "price": self.price,
            "stock": self.stock,
            "max_stock": self.max_stock
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ShopItem":
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy["item_type"] = ItemType(data_copy["item_type"])
        return cls(**data_copy)


class Shop:
    """Shop management system"""
    
    # Default shop catalog
    DEFAULT_CATALOG = {
        "pokeball": ShopItem(
            item_id="pokeball",
            name="Poké Ball",
            description="A standard Poké Ball for catching Pokémon",
            item_type=ItemType.POKEBALL,
            price=10.0,
            stock=100,
            max_stock=100
        ),
        "ultraball": ShopItem(
            item_id="ultraball",
            name="Ultra Ball",
            description="An enhanced ball with higher catch rate",
            item_type=ItemType.ULTRABALL,
            price=25.0,
            stock=50,
            max_stock=50
        ),
        "seed_grass": ShopItem(
            item_id="seed_grass",
            name="Grass Seed",
            description="Seed for planting grass-type food",
            item_type=ItemType.SEED,
            price=15.0,
            stock=200,
            max_stock=200
        ),
        "seed_water": ShopItem(
            item_id="seed_water",
            name="Water Seed",
            description="Seed for planting water-type food",
            item_type=ItemType.SEED,
            price=15.0,
            stock=200,
            max_stock=200
        ),
        "potion_small": ShopItem(
            item_id="potion_small",
            name="Small Potion",
            description="Restores 20 HP",
            item_type=ItemType.POTION,
            price=20.0,
            stock=150,
            max_stock=150
        ),
        "revive": ShopItem(
            item_id="revive",
            name="Revive",
            description="Brings a fainted Pokémon back to battle",
            item_type=ItemType.REVIVE,
            price=50.0,
            stock=30,
            max_stock=30
        ),
    }
    
    def __init__(self, data_dir: str = ".monster"):
        self.data_dir = Path(data_dir)
        self.shop_file = self.data_dir / "shop.json"
        self.inventory_dir = self.data_dir / "inventory"
        self.inventory_dir.mkdir(parents=True, exist_ok=True)
        
        self.catalog = self._load_catalog()
    
    def _load_catalog(self) -> Dict[str, ShopItem]:
        """Load shop catalog"""
        if self.shop_file.exists():
            try:
                with open(self.shop_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    return {
                        key: ShopItem.from_dict(item)
                        for key, item in data.items()
                    }
            except:
                pass
        
        # Use default catalog
        self._save_catalog(self.DEFAULT_CATALOG)
        return self.DEFAULT_CATALOG.copy()
    
    def _save_catalog(self, catalog: Dict[str, ShopItem]):
        """Save catalog to disk"""
        with open(self.shop_file, "w", encoding="utf-8") as f:
            json.dump(
                {key: item.to_dict() for key, item in catalog.items()},
                f,
                indent=2,
                ensure_ascii=False
            )
    
    def get_item(self, item_id: str) -> Optional[ShopItem]:
        """Get item from catalog"""
        return self.catalog.get(item_id)
    
    def list_items(self, item_type: Optional[ItemType] = None) -> List[ShopItem]:
        """List all items, optionally filtered by type"""
        items = list(self.catalog.values())
        if item_type:
            items = [i for i in items if i.item_type == item_type]
        return items
    
    def purchase_item(
        self,
        user_id: str,
        item_id: str,
        quantity: int = 1
    ) -> tuple[bool, Optional[ShopItem], str]:
        """
        Purchase item from shop
        Returns: (success, item, message)
        """
        item = self.get_item(item_id)
        if not item:
            return (False, None, "Item not found")
        
        if item.stock < quantity:
            return (False, None, f"Insufficient stock. Available: {item.stock}")
        
        # Deduct from shop stock
        item.stock -= quantity
        self.catalog[item_id] = item
        self._save_catalog(self.catalog)
        
        # Add to user inventory
        self._add_to_inventory(user_id, item_id, quantity)
        
        return (True, item, f"Purchased {quantity}x {item.name}")
    
    def _add_to_inventory(self, user_id: str, item_id: str, quantity: int):
        """Add item to user inventory"""
        inventory_file = self.inventory_dir / f"{user_id}.json"
        
        if inventory_file.exists():
            with open(inventory_file, "r", encoding="utf-8") as f:
                inventory = json.load(f)
        else:
            inventory = {}
        
        inventory[item_id] = inventory.get(item_id, 0) + quantity
        
        with open(inventory_file, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False)
    
    def get_user_inventory(self, user_id: str) -> Dict[str, Any]:
        """Get user's inventory"""
        inventory_file = self.inventory_dir / f"{user_id}.json"
        
        if not inventory_file.exists():
            return {}
        
        with open(inventory_file, "r", encoding="utf-8") as f:
            inventory_data = json.load(f)
        
        # Enrich with item details
        result = {}
        for item_id, quantity in inventory_data.items():
            item = self.get_item(item_id)
            if item:
                result[item_id] = {
                    "item": item.to_dict(),
                    "quantity": quantity,
                    "total_value": item.price * quantity
                }
        
        return result
    
    def use_item(
        self,
        user_id: str,
        item_id: str,
        quantity: int = 1
    ) -> bool:
        """Use item from inventory"""
        inventory_file = self.inventory_dir / f"{user_id}.json"
        
        if not inventory_file.exists():
            return False
        
        with open(inventory_file, "r", encoding="utf-8") as f:
            inventory = json.load(f)
        
        if item_id not in inventory or inventory[item_id] < quantity:
            return False
        
        inventory[item_id] -= quantity
        if inventory[item_id] <= 0:
            del inventory[item_id]
        
        with open(inventory_file, "w", encoding="utf-8") as f:
            json.dump(inventory, f, indent=2, ensure_ascii=False)
        
        return True
    
    def restock_item(self, item_id: str, quantity: int):
        """Restock item in shop (admin)"""
        item = self.get_item(item_id)
        if item:
            item.stock = min(item.stock + quantity, item.max_stock)
            self.catalog[item_id] = item
            self._save_catalog(self.catalog)
    
    def get_shop_statistics(self) -> Dict[str, Any]:
        """Get shop statistics"""
        stats = {
            "total_items": len(self.catalog),
            "total_stock_value": 0.0,
            "items_by_type": {},
            "low_stock_alerts": []
        }
        
        for item in self.catalog.values():
            stats["total_stock_value"] += item.price * item.stock
            
            item_type = item.item_type.value
            if item_type not in stats["items_by_type"]:
                stats["items_by_type"][item_type] = {"count": 0, "stock": 0}
            stats["items_by_type"][item_type]["count"] += 1
            stats["items_by_type"][item_type]["stock"] += item.stock
            
            # Alert if stock < 20% of max
            if item.stock < item.max_stock * 0.2:
                stats["low_stock_alerts"].append({
                    "item_id": item.item_id,
                    "item_name": item.name,
                    "current_stock": item.stock,
                    "max_stock": item.max_stock
                })
        
        return stats
