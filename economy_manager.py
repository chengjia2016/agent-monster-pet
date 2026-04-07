#!/usr/bin/env python3
"""
Economy System
Manages user balance, transactions, and economic interactions
"""

import json
import uuid
from pathlib import Path
from typing import Dict, Optional, Any, List
from datetime import datetime
from enum import Enum


class TransactionType(Enum):
    """Types of economic transactions"""
    INITIAL_GRANT = "initial_grant"
    PURCHASE = "purchase"
    FOOD_SALE = "food_sale"
    FOOD_PURCHASE = "food_purchase"
    BATTLE_REWARD = "battle_reward"
    BATTLE_PENALTY = "battle_penalty"
    PET_SALE = "pet_sale"
    AUCTION_SALE = "auction_sale"
    SHOP_COMMISSION = "shop_commission"


class Transaction:
    """Single transaction record"""
    
    def __init__(
        self,
        transaction_id: str,
        user_id: str,
        amount: float,
        trans_type: TransactionType,
        description: str,
        metadata: Dict[str, Any] = None,
        created_at: str = None
    ):
        self.transaction_id = transaction_id
        self.user_id = user_id
        self.amount = amount
        self.trans_type = trans_type
        self.description = description
        self.metadata = metadata or {}
        self.created_at = created_at or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "transaction_id": self.transaction_id,
            "user_id": self.user_id,
            "amount": self.amount,
            "trans_type": self.trans_type.value,
            "description": self.description,
            "metadata": self.metadata,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Transaction":
        """Create from dictionary"""
        data_copy = data.copy()
        data_copy["trans_type"] = TransactionType(data_copy["trans_type"])
        return cls(**data_copy)


class UserAccount:
    """User account with balance and transaction history"""
    
    def __init__(
        self,
        user_id: str,
        balance: float = 100.0,  # 初始100精灵币
        transactions: List[Transaction] = None,
        created_at: str = None
    ):
        self.user_id = user_id
        self.balance = balance
        self.transactions = transactions or []
        self.created_at = created_at or datetime.utcnow().isoformat()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "user_id": self.user_id,
            "balance": self.balance,
            "transactions": [t.to_dict() for t in self.transactions],
            "created_at": self.created_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "UserAccount":
        """Create from dictionary"""
        transactions = [
            Transaction.from_dict(t) for t in data.get("transactions", [])
        ]
        return cls(
            user_id=data["user_id"],
            balance=data["balance"],
            transactions=transactions,
            created_at=data.get("created_at")
        )
    
    def add_transaction(
        self,
        amount: float,
        trans_type: TransactionType,
        description: str,
        metadata: Dict[str, Any] = None
    ) -> Transaction:
        """Add a transaction and update balance"""
        transaction = Transaction(
            transaction_id=str(uuid.uuid4())[:8],
            user_id=self.user_id,
            amount=amount,
            trans_type=trans_type,
            description=description,
            metadata=metadata
        )
        
        self.balance += amount
        self.transactions.append(transaction)
        return transaction
    
    def get_balance(self) -> float:
        """Get current balance"""
        return self.balance
    
    def has_sufficient_balance(self, amount: float) -> bool:
        """Check if user has enough balance"""
        return self.balance >= amount
    
    def get_recent_transactions(self, limit: int = 10) -> List[Transaction]:
        """Get recent transactions"""
        return self.transactions[-limit:]


class EconomyManager:
    """Manage all economic interactions"""
    
    # Commission rates (手续费)
    FOOD_TRANSACTION_COMMISSION = 0.05  # 5% commission on food sales
    AUCTION_COMMISSION = 0.10  # 10% commission on auction sales
    
    def __init__(self, data_dir: str = ".monster"):
        self.data_dir = Path(data_dir)
        self.accounts_dir = self.data_dir / "accounts"
        self.accounts_dir.mkdir(parents=True, exist_ok=True)
        self.transactions_log = self.data_dir / "transactions.jsonl"
    
    def create_account(self, user_id: str, initial_balance: float = 100.0) -> UserAccount:
        """Create a new user account"""
        account = UserAccount(user_id=user_id, balance=0.0)  # Start with 0
        
        # 添加初始赠送记录
        account.add_transaction(
            amount=initial_balance,
            trans_type=TransactionType.INITIAL_GRANT,
            description="Initial grant for new user"
        )
        
        self._save_account(account)
        return account
    
    def get_account(self, user_id: str) -> Optional[UserAccount]:
        """Get user account"""
        account_file = self.accounts_dir / f"{user_id}.json"
        if account_file.exists():
            try:
                with open(account_file, "r", encoding="utf-8") as f:
                    return UserAccount.from_dict(json.load(f))
            except:
                return None
        return None
    
    def _save_account(self, account: UserAccount):
        """Save account to disk"""
        account_file = self.accounts_dir / f"{account.user_id}.json"
        with open(account_file, "w", encoding="utf-8") as f:
            json.dump(account.to_dict(), f, indent=2, ensure_ascii=False)
        
        # Also log transaction
        self._log_transactions(account.transactions[-1:])
    
    def _log_transactions(self, transactions: List[Transaction]):
        """Log transactions to file"""
        with open(self.transactions_log, "a", encoding="utf-8") as f:
            for t in transactions:
                f.write(json.dumps(t.to_dict(), ensure_ascii=False) + "\n")
    
    def purchase_item(
        self,
        user_id: str,
        item_name: str,
        item_price: float,
        item_id: str = ""
    ) -> bool:
        """Purchase an item from shop"""
        account = self.get_account(user_id)
        if not account:
            return False
        
        if not account.has_sufficient_balance(item_price):
            return False
        
        # 扣款
        account.add_transaction(
            amount=-item_price,
            trans_type=TransactionType.PURCHASE,
            description=f"Purchase {item_name}",
            metadata={"item_name": item_name, "item_id": item_id}
        )
        
        self._save_account(account)
        return True
    
    def process_food_transaction(
        self,
        buyer_id: str,
        seller_id: str,
        food_id: str,
        food_name: str,
        base_price: float
    ) -> tuple[bool, float, float]:
        """
        Process food transaction with commission
        Returns: (success, buyer_paid, seller_received)
        """
        buyer_account = self.get_account(buyer_id)
        seller_account = self.get_account(seller_id)
        
        if not buyer_account or not seller_account:
            return (False, 0.0, 0.0)
        
        # Calculate amounts
        buyer_paid = base_price
        commission = base_price * self.FOOD_TRANSACTION_COMMISSION
        seller_received = base_price - commission
        
        if not buyer_account.has_sufficient_balance(buyer_paid):
            return (False, 0.0, 0.0)
        
        # 买家付款
        buyer_account.add_transaction(
            amount=-buyer_paid,
            trans_type=TransactionType.FOOD_PURCHASE,
            description=f"Purchase food: {food_name}",
            metadata={"food_id": food_id, "seller_id": seller_id, "commission": commission}
        )
        
        # 卖家收款（已经扣去手续费）
        seller_account.add_transaction(
            amount=seller_received,
            trans_type=TransactionType.FOOD_SALE,
            description=f"Sold food: {food_name} (after {self.FOOD_TRANSACTION_COMMISSION*100}% commission)",
            metadata={"food_id": food_id, "buyer_id": buyer_id, "gross_price": base_price, "commission": commission}
        )
        
        self._save_account(buyer_account)
        self._save_account(seller_account)
        
        return (True, buyer_paid, seller_received)
    
    def process_battle_reward(
        self,
        winner_id: str,
        loser_id: str,
        base_reward: float = 50.0
    ) -> bool:
        """
        Process battle reward
        Winner gets money, loser loses money
        """
        winner_account = self.get_account(winner_id)
        loser_account = self.get_account(loser_id)
        
        if not winner_account or not loser_account:
            return False
        
        # Check if loser has enough balance
        if not loser_account.has_sufficient_balance(base_reward):
            # Partial penalty only
            penalty = loser_account.balance * 0.5
        else:
            penalty = base_reward
        
        # Winner gets reward
        winner_account.add_transaction(
            amount=penalty,
            trans_type=TransactionType.BATTLE_REWARD,
            description="Battle victory reward",
            metadata={"defeated_opponent": loser_id}
        )
        
        # Loser loses money
        loser_account.add_transaction(
            amount=-penalty,
            trans_type=TransactionType.BATTLE_PENALTY,
            description="Battle defeat penalty",
            metadata={"defeated_by": winner_id}
        )
        
        self._save_account(winner_account)
        self._save_account(loser_account)
        
        return True
    
    def sell_pet(
        self,
        seller_id: str,
        pet_name: str,
        sale_price: float
    ) -> bool:
        """Sell a pet to the shop"""
        account = self.get_account(seller_id)
        if not account:
            return False
        
        account.add_transaction(
            amount=sale_price,
            trans_type=TransactionType.PET_SALE,
            description=f"Sold pet: {pet_name}",
            metadata={"pet_name": pet_name}
        )
        
        self._save_account(account)
        return True
    
    def auction_pet(
        self,
        seller_id: str,
        pet_name: str,
        auction_final_price: float
    ) -> bool:
        """Auction a pet and transfer earnings"""
        account = self.get_account(seller_id)
        if not account:
            return False
        
        # Calculate after commission
        commission = auction_final_price * self.AUCTION_COMMISSION
        seller_receives = auction_final_price - commission
        
        account.add_transaction(
            amount=seller_receives,
            trans_type=TransactionType.AUCTION_SALE,
            description=f"Auctioned pet: {pet_name}",
            metadata={"pet_name": pet_name, "final_price": auction_final_price, "commission": commission}
        )
        
        self._save_account(account)
        return True
    
    def get_user_statistics(self, user_id: str) -> Dict[str, Any]:
        """Get user economic statistics"""
        account = self.get_account(user_id)
        if not account:
            return {}
        
        transactions = account.transactions
        
        stats = {
            "current_balance": account.balance,
            "total_transactions": len(transactions),
            "total_spent": sum(t.amount for t in transactions if t.amount < 0),
            "total_earned": sum(t.amount for t in transactions if t.amount > 0),
            "transaction_breakdown": {}
        }
        
        # Breakdown by type
        for trans_type in TransactionType:
            matching = [t for t in transactions if t.trans_type == trans_type]
            if matching:
                stats["transaction_breakdown"][trans_type.value] = {
                    "count": len(matching),
                    "total_amount": sum(t.amount for t in matching)
                }
        
        return stats
