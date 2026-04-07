"""
Enhanced Battle System with TUI Integration
Combines battle logic with interactive terminal user interface
"""

import hashlib
import json
import os
import random
import re
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Tuple
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from rich.progress import Progress, BarColumn, TextColumn
from rich.align import Align
import time

from battle_tui import (
    BattleParticipant,
    StatusEffect,
    EffectType,
    Move,
    BattleDisplay,
    BattleAnimator,
    BattlePhase,
)


class BattleMode(Enum):
    AGGRESSIVE = "aggressive"
    TANK = "tank"
    EVASIVE = "evasive"
    BALANCED = "balanced"


class SkillType(Enum):
    """Skill classifications"""
    PHYSICAL = "physical"
    SPECIAL = "special"
    STATUS = "status"
    ULTIMATE = "ultimate"


@dataclass
class Skill:
    """Enhanced skill definition"""
    name: str
    skill_type: SkillType
    power: int
    accuracy: float
    en_cost: int
    cooldown: int = 0
    effects: List[StatusEffect] = field(default_factory=list)
    description: str = ""
    priority: int = 0  # Higher priority = goes first

    def can_use(self, current_en: int, cooldown_remaining: int = 0) -> bool:
        """Check if skill can be used"""
        return current_en >= self.en_cost and cooldown_remaining <= 0

    def get_type_emoji(self) -> str:
        """Get emoji based on skill type"""
        emojis = {
            SkillType.PHYSICAL: "💪",
            SkillType.SPECIAL: "✨",
            SkillType.STATUS: "🎯",
            SkillType.ULTIMATE: "⭐",
        }
        return emojis.get(self.skill_type, "•")


# Predefined skills for different builds
PHYSICAL_SKILLS = {
    "slash": Skill(
        name="Slash",
        skill_type=SkillType.PHYSICAL,
        power=40,
        accuracy=0.95,
        en_cost=10,
        description="Basic physical attack",
        priority=0,
    ),
    "heavy_strike": Skill(
        name="Heavy Strike",
        skill_type=SkillType.PHYSICAL,
        power=80,
        accuracy=0.70,
        en_cost=25,
        description="Powerful attack with lower accuracy",
        priority=0,
    ),
    "multi_hit": Skill(
        name="Multi-Hit",
        skill_type=SkillType.PHYSICAL,
        power=50,
        accuracy=0.80,
        en_cost=20,
        description="Attack multiple times",
        priority=1,
    ),
}

SPECIAL_SKILLS = {
    "flame_burst": Skill(
        name="Flame Burst",
        skill_type=SkillType.SPECIAL,
        power=75,
        accuracy=0.85,
        en_cost=20,
        effects=[StatusEffect(EffectType.BURN, 3, 0.5, "Burning")],
        description="Fire damage with burn effect",
        priority=0,
    ),
    "ice_beam": Skill(
        name="Ice Beam",
        skill_type=SkillType.SPECIAL,
        power=90,
        accuracy=0.75,
        en_cost=22,
        effects=[StatusEffect(EffectType.FREEZE, 2, 0.3, "Frozen")],
        description="Ice damage with freeze chance",
        priority=0,
    ),
    "electric_shock": Skill(
        name="Electric Shock",
        skill_type=SkillType.SPECIAL,
        power=85,
        accuracy=0.80,
        en_cost=21,
        effects=[StatusEffect(EffectType.PARALYZE, 3, 0.4, "Paralyzed")],
        description="Electric damage with paralysis",
        priority=0,
    ),
}

STATUS_SKILLS = {
    "shield": Skill(
        name="Shield",
        skill_type=SkillType.STATUS,
        power=0,
        accuracy=1.0,
        en_cost=15,
        effects=[StatusEffect(EffectType.SHIELD, 2, 0.5, "Protected")],
        description="Reduce incoming damage",
        priority=1,
    ),
    "poison_cloud": Skill(
        name="Poison Cloud",
        skill_type=SkillType.STATUS,
        power=0,
        accuracy=0.80,
        en_cost=18,
        effects=[StatusEffect(EffectType.POISON, 4, 0.3, "Poisoned")],
        description="Poison the opponent",
        priority=0,
    ),
    "recover": Skill(
        name="Recover",
        skill_type=SkillType.STATUS,
        power=0,
        accuracy=1.0,
        en_cost=25,
        description="Restore HP",
        priority=2,
    ),
}

ULTIMATE_SKILLS = {
    "final_attack": Skill(
        name="Final Attack",
        skill_type=SkillType.ULTIMATE,
        power=150,
        accuracy=0.60,
        en_cost=50,
        cooldown=3,
        description="Powerful finishing move",
        priority=0,
    ),
    "transcend": Skill(
        name="Transcend",
        skill_type=SkillType.ULTIMATE,
        power=200,
        accuracy=0.50,
        en_cost=60,
        cooldown=5,
        effects=[StatusEffect(EffectType.BOOST, 2, 1.0, "Transcended")],
        description="Ultimate transformation and attack",
        priority=-1,
    ),
}

ALL_SKILLS = {
    **PHYSICAL_SKILLS,
    **SPECIAL_SKILLS,
    **STATUS_SKILLS,
    **ULTIMATE_SKILLS,
}


@dataclass
class EnhancedBattleParticipant(BattleParticipant):
    """Extended battle participant with skills and advanced mechanics"""
    skills: List[str] = field(default_factory=list)
    skill_cooldowns: Dict[str, int] = field(default_factory=dict)
    experience: int = 0
    battle_mode: BattleMode = BattleMode.BALANCED

    def get_available_skills(self) -> List[Skill]:
        """Get list of usable skills"""
        available = []
        for skill_name in self.skills:
            if skill_name in ALL_SKILLS:
                skill = ALL_SKILLS[skill_name]
                cooldown = self.skill_cooldowns.get(skill_name, 0)
                if skill.can_use(self.en, cooldown):
                    available.append(skill)
        return available

    def use_skill(self, skill: Skill) -> bool:
        """Use a skill and return success"""
        if not skill.can_use(self.en, self.skill_cooldowns.get(skill.name, 0)):
            return False

        self.en -= skill.en_cost

        if skill.cooldown > 0:
            self.skill_cooldowns[skill.name] = skill.cooldown

        return True

    def reduce_cooldowns(self):
        """Reduce all skill cooldowns by 1 turn"""
        for skill_name in self.skill_cooldowns:
            self.skill_cooldowns[skill_name] = max(0, self.skill_cooldowns[skill_name] - 1)


class EnhancedBattleSimulator:
    """Improved battle simulator with TUI support"""

    def __init__(
        self,
        attacker: EnhancedBattleParticipant,
        defender: EnhancedBattleParticipant,
        console: Optional[Console] = None,
    ):
        self.attacker = attacker
        self.defender = defender
        self.console = console or Console()
        self.display = BattleDisplay(self.console)
        self.animator = BattleAnimator(self.console)
        self.battle_log: List[str] = []
        self.turn = 0
        self.seed = self._generate_seed()
        self.phase = BattlePhase.INTRO

    def _generate_seed(self) -> int:
        """Generate deterministic seed"""
        data = f"{self.attacker.name}{self.defender.name}{datetime.now().isoformat()}"
        return int(hashlib.sha256(data.encode()).hexdigest()[:8], 16)

    def _random(self) -> float:
        """Seeded random number"""
        self.seed = (self.seed * 1103515245 + 12345) & 0x7FFFFFFF
        return self.seed / 0x7FFFFFFF

    def _calculate_damage(
        self,
        attacker: EnhancedBattleParticipant,
        defender: EnhancedBattleParticipant,
        skill: Skill,
    ) -> int:
        """Calculate damage with stat modifiers"""
        stat_mult = 1.0

        if skill.skill_type == SkillType.PHYSICAL:
            attacker_stat = attacker.stats.get("attack", 50)
            defender_stat = defender.stats.get("defense", 50)
        else:  # SPECIAL
            attacker_stat = attacker.stats.get("sp_atk", 50)
            defender_stat = defender.stats.get("sp_def", 50)

        # Basic damage formula
        base_damage = max(1, int((2 * 5 / 5 + 2) * (attacker_stat * skill.power / defender_stat) / 50 + 2))

        # Randomization
        random_factor = 0.85 + (self._random() * 0.15)

        # Critical hit chance
        crit_chance = 0.0625 if self._random() < 0.0625 else 0
        crit_mult = 1.5 if crit_chance else 1.0

        # Status effects resistance
        defense_mult = 1.0
        for effect in defender.effects:
            if effect.effect_type in [EffectType.SHIELD, EffectType.BOOST]:
                defense_mult *= 0.7

        final_damage = int(base_damage * stat_mult * random_factor * crit_mult * defense_mult)
        return max(1, final_damage)

    def _apply_skill_effects(self, skill: Skill, target: EnhancedBattleParticipant):
        """Apply skill effects to target"""
        for effect in skill.effects:
            target.effects.append(effect)
            self.animator.animate_effect_applied(effect, target.name)
            self.battle_log.append(f"{target.name} is now {effect.name.lower()}!")

    def _process_status_effects(self, participant: EnhancedBattleParticipant) -> int:
        """Process damage from status effects, return damage taken"""
        damage_taken = 0

        for effect in participant.effects[:]:
            if effect.effect_type == EffectType.POISON:
                damage = int(participant.max_hp * 0.125 * effect.power)
                participant.hp = max(0, participant.hp - damage)
                damage_taken += damage
                self.battle_log.append(f"{participant.name} takes {damage} poison damage!")

            elif effect.effect_type == EffectType.BURN:
                damage = int(participant.max_hp * 0.125 * effect.power)
                participant.hp = max(0, participant.hp - damage)
                damage_taken += damage
                self.battle_log.append(f"{participant.name} takes {damage} burn damage!")

            # Reduce duration
            effect.duration -= 1
            if effect.duration <= 0:
                participant.effects.remove(effect)
                self.battle_log.append(f"{participant.name} is no longer {effect.name.lower()}!")

        return damage_taken

    def simulate_turn(self, attacker: EnhancedBattleParticipant, defender: EnhancedBattleParticipant):
        """Simulate one turn"""
        self.turn += 1
        self.phase = BattlePhase.TURN

        # Display battle state
        self.display.render_full_battle_state(
            self.attacker, self.defender, self.battle_log, self.phase
        )

        # Choose skill (AI logic for defender)
        available_skills = attacker.get_available_skills()
        if not available_skills:
            self.battle_log.append(f"{attacker.name} has no available skills!")
            return

        # Simple AI: choose skill based on situation
        if attacker.hp < attacker.max_hp * 0.3 and "recover" in attacker.skills:
            skill = ALL_SKILLS.get("recover")
        else:
            skill = available_skills[int(self._random() * len(available_skills))]

        # Execute skill
        if attacker.use_skill(skill):
            self.animator.animate_move_execution(attacker.name, Move(
                name=skill.name,
                power=skill.power,
                accuracy=skill.accuracy,
                en_cost=skill.en_cost,
                description=skill.description,
            ), defender.name)

            if skill.power > 0:
                damage = self._calculate_damage(attacker, defender, skill)
                defender.hp = max(0, defender.hp - damage)
                self.animator.animate_damage(damage, defender.name)
                self.battle_log.append(f"{attacker.name}'s {skill.name} deals {damage} damage!")

            # Apply effects
            if skill.effects:
                self._apply_skill_effects(skill, defender)

            # Handle recovery skills
            if skill.name == "recover":
                recovery = int(attacker.max_hp * 0.5)
                attacker.hp = min(attacker.max_hp, attacker.hp + recovery)
                self.battle_log.append(f"{attacker.name} recovers {recovery} HP!")

        # Process status effects
        self._process_status_effects(defender)

        # Reduce cooldowns
        attacker.reduce_cooldowns()
        defender.reduce_cooldowns()

        # Regenerate EN
        attacker.en = min(attacker.max_en, int(attacker.en + attacker.max_en * 0.1))
        defender.en = min(defender.max_en, int(defender.en + defender.max_en * 0.1))

        time.sleep(0.5)

    def run_battle(self) -> Dict:
        """Run complete battle"""
        self.animator.animate_intro(self.attacker, self.defender)

        while self.attacker.hp > 0 and self.defender.hp > 0 and self.turn < 30:
            # Attacker turn
            if self.attacker.hp > 0 and self.defender.hp > 0:
                self.simulate_turn(self.attacker, self.defender)

            # Defender turn
            if self.attacker.hp > 0 and self.defender.hp > 0:
                self.simulate_turn(self.defender, self.attacker)

        # Battle end
        winner = self.attacker if self.attacker.hp > self.defender.hp else self.defender
        loser = self.defender if winner == self.attacker else self.attacker

        self.console.print(
            Panel(
                f"[bold green]{winner.name} wins![/bold green]\n"
                f"HP: {winner.hp}/{winner.max_hp}",
                style="green",
                expand=False,
            )
        )

        # Give experience
        winner.experience += 100
        loser.experience += 50

        return {
            "winner": winner.name,
            "loser": loser.name,
            "turns": self.turn,
            "winner_hp": winner.hp,
            "loser_hp": loser.hp,
            "log": self.battle_log,
        }


def demo_enhanced_battle():
    """Demo enhanced battle system"""
    console = Console()

    # Create enhanced participants
    attacker = EnhancedBattleParticipant(
        name="PyDragon",
        hp=120,
        max_hp=120,
        en=60,
        max_en=60,
        level=10,
        stats={
            "attack": 60,
            "defense": 50,
            "sp_atk": 70,
            "sp_def": 55,
            "speed": 65,
        },
        skills=["slash", "heavy_strike", "flame_burst", "shield", "recover", "final_attack"],
        battle_mode=BattleMode.AGGRESSIVE,
    )

    defender = EnhancedBattleParticipant(
        name="GoPhoenix",
        hp=120,
        max_hp=120,
        en=60,
        max_en=60,
        level=10,
        stats={
            "attack": 65,
            "defense": 48,
            "sp_atk": 68,
            "sp_def": 60,
            "speed": 70,
        },
        skills=["multi_hit", "ice_beam", "electric_shock", "shield", "recover", "transcend"],
        battle_mode=BattleMode.BALANCED,
    )

    # Run battle
    simulator = EnhancedBattleSimulator(attacker, defender, console)
    result = simulator.run_battle()

    console.print("\n[bold yellow]Battle Summary:[/bold yellow]")
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Result", style="cyan")
    table.add_column("Value", style="green")
    table.add_row("Winner", result["winner"])
    table.add_row("Turns", str(result["turns"]))
    table.add_row("Winner HP", str(result["winner_hp"]))
    table.add_row("Loser HP", str(result["loser_hp"]))
    console.print(table)


if __name__ == "__main__":
    demo_enhanced_battle()
