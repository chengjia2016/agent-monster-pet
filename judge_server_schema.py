#!/usr/bin/env python3
"""
Judge Server Database Schema
Defines data models for storing user data on the judge server
"""

from dataclasses import dataclass, field, asdict
from typing import List, Dict, Optional
from datetime import datetime


@dataclass
class Pokemon:
    """Pokémon data model"""
    id: str  # Unique ID for this Pokémon
    name: str
    species: str  # e.g., "Pikachu", "Charizard"
    level: int = 1
    exp: int = 0
    hp: int = 100
    max_hp: int = 100
    attack: int = 10
    defense: int = 10
    sp_attack: int = 10
    sp_defense: int = 10
    speed: int = 10
    moves: List[str] = field(default_factory=list)
    caught_at: str = ""
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Item:
    """Item/Inventory data model"""
    item_id: str  # e.g., "ball_red", "potion_small"
    name: str
    quantity: int
    rarity: str = "common"  # common, uncommon, rare, legendary
    added_at: str = ""
    
    def to_dict(self):
        return asdict(self)


@dataclass
class Transaction:
    """Financial transaction record"""
    id: str
    amount: float
    transaction_type: str  # INITIAL_GRANT, PURCHASE, REWARD, BATTLE_PRIZE, etc.
    description: str
    timestamp: str
    balance_before: float
    balance_after: float
    
    def to_dict(self):
        return asdict(self)


@dataclass
class UserAccount:
    """Complete user account on judge server"""
    github_id: int  # Unique GitHub numeric ID
    github_login: str  # GitHub username
    
    # Currency
    balance: float = 100.0  # Pokémon coins
    
    # Collection
    pokemons: List[Dict] = field(default_factory=list)  # List of Pokémon
    items: List[Dict] = field(default_factory=list)  # Inventory
    
    # Transactions
    transactions: List[Dict] = field(default_factory=list)
    
    # Statistics
    total_income: float = 0.0
    total_expense: float = 0.0
    battles_won: int = 0
    battles_lost: int = 0
    pokemons_caught: int = 0
    
    # Metadata
    created_at: str = ""
    last_login: Optional[str] = None
    last_updated: str = ""
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(**data)


@dataclass
class BattleRecord:
    """Battle history record"""
    battle_id: str
    player1_github_id: int
    player2_github_id: int
    player1_pokemon: List[str]  # Pokemon IDs used
    player2_pokemon: List[str]
    winner_github_id: int  # Winner's GitHub ID
    prize_coins: float
    timestamp: str
    duration_seconds: int
    
    def to_dict(self):
        return asdict(self)


# Database schema documentation
DATABASE_SCHEMA = """
====================================================================
            Agent Monster Judge Server Database Schema
====================================================================

TABLE: users
  - github_id (INT PRIMARY KEY)
  - github_login (VARCHAR)
  - balance (FLOAT)
  - total_income (FLOAT)
  - total_expense (FLOAT)
  - battles_won (INT)
  - battles_lost (INT)
  - pokemons_caught (INT)
  - created_at (TIMESTAMP)
  - last_login (TIMESTAMP)
  - last_updated (TIMESTAMP)

TABLE: pokemons
  - id (VARCHAR PRIMARY KEY)
  - github_id (INT, FOREIGN KEY users.github_id)
  - name (VARCHAR)
  - species (VARCHAR)
  - level (INT)
  - exp (INT)
  - hp (INT)
  - max_hp (INT)
  - attack (INT)
  - defense (INT)
  - sp_attack (INT)
  - sp_defense (INT)
  - speed (INT)
  - moves (JSON ARRAY)
  - caught_at (TIMESTAMP)

TABLE: inventory
  - id (VARCHAR PRIMARY KEY)
  - github_id (INT, FOREIGN KEY users.github_id)
  - item_id (VARCHAR)
  - name (VARCHAR)
  - quantity (INT)
  - rarity (VARCHAR)
  - added_at (TIMESTAMP)

TABLE: transactions
  - id (VARCHAR PRIMARY KEY)
  - github_id (INT, FOREIGN KEY users.github_id)
  - amount (FLOAT)
  - transaction_type (VARCHAR)
  - description (VARCHAR)
  - balance_before (FLOAT)
  - balance_after (FLOAT)
  - timestamp (TIMESTAMP)

TABLE: battles
  - battle_id (VARCHAR PRIMARY KEY)
  - player1_github_id (INT, FOREIGN KEY users.github_id)
  - player2_github_id (INT, FOREIGN KEY users.github_id)
  - player1_pokemon (JSON ARRAY)
  - player2_pokemon (JSON ARRAY)
  - winner_github_id (INT, FOREIGN KEY users.github_id)
  - prize_coins (FLOAT)
  - duration_seconds (INT)
  - timestamp (TIMESTAMP)

INDEXES:
  - users(github_login)
  - pokemons(github_id)
  - inventory(github_id)
  - transactions(github_id, timestamp)
  - battles(player1_github_id, player2_github_id)
"""


if __name__ == "__main__":
    print(DATABASE_SCHEMA)
    
    # Example usage
    print("\n" + "=" * 70)
    print(" 📊 Example User Account")
    print("=" * 70 + "\n")
    
    user = UserAccount(
        github_id=24448747,
        github_login="chengjia2016",
        balance=150.5,
        pokemons=[
            {
                "id": "pkmn_001",
                "name": "Pikachu",
                "species": "Pikachu",
                "level": 5,
                "hp": 25,
                "max_hp": 25
            }
        ],
        items=[
            {"item_id": "ball_red", "name": "Poké Ball", "quantity": 10},
            {"item_id": "potion_small", "name": "Small Potion", "quantity": 3}
        ]
    )
    
    import json
    print(json.dumps(user.to_dict(), indent=2, ensure_ascii=False))
