"""
Comprehensive Battle System Tests
Tests for enhanced battle system, TUI, and replay functionality
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch

from battle_tui import (
    BattleParticipant,
    StatusEffect,
    EffectType,
    Move,
    BattleDisplay,
    BattleAnimator,
    BattlePhase,
)
from enhanced_battle import (
    EnhancedBattleParticipant,
    EnhancedBattleSimulator,
    BattleMode,
    Skill,
    SkillType,
    ALL_SKILLS,
)
from battle_replay import (
    BattleReplay,
    BattleReplayManager,
    BattleResult,
)


class TestBattleParticipant:
    """Test basic battle participant"""

    def test_create_participant(self):
        """Test creating a battle participant"""
        p = BattleParticipant(
            name="TestPet",
            hp=100,
            max_hp=100,
            en=50,
            max_en=50,
            level=5,
            stats={"attack": 50, "defense": 50, "speed": 50}
        )
        assert p.name == "TestPet"
        assert p.hp == 100
        assert p.level == 5

    def test_hp_percentage(self):
        """Test HP percentage calculation"""
        p = BattleParticipant(
            name="TestPet",
            hp=50,
            max_hp=100,
            en=25,
            max_en=50,
            level=5,
            stats={}
        )
        assert p.get_hp_percentage() == 50.0
        assert p.get_en_percentage() == 50.0

    def test_en_percentage_zero_max(self):
        """Test EN percentage with zero max"""
        p = BattleParticipant(
            name="TestPet",
            hp=0,
            max_hp=0,
            en=0,
            max_en=0,
            level=5,
            stats={}
        )
        assert p.get_hp_percentage() == 0.0


class TestStatusEffect:
    """Test status effects"""

    def test_create_status_effect(self):
        """Test creating a status effect"""
        effect = StatusEffect(
            effect_type=EffectType.BURN,
            duration=3,
            power=0.5,
            name="Burning"
        )
        assert effect.effect_type == EffectType.BURN
        assert effect.duration == 3
        assert effect.power == 0.5

    def test_effect_emoji(self):
        """Test effect emoji mapping"""
        effect = StatusEffect(
            effect_type=EffectType.POISON,
            duration=1,
            power=0.3,
            name="Poisoned"
        )
        assert effect.get_emoji() == "☠️"

    def test_effect_color(self):
        """Test effect color mapping"""
        effects = [
            (EffectType.POISON, "magenta"),
            (EffectType.BURN, "red"),
            (EffectType.FREEZE, "cyan"),
        ]
        for effect_type, expected_color in effects:
            effect = StatusEffect(
                effect_type=effect_type,
                duration=1,
                power=0.1,
                name="Test"
            )
            assert effect.get_color() == expected_color


class TestEnhancedBattleParticipant:
    """Test enhanced battle participant with skills"""

    def test_create_enhanced_participant(self):
        """Test creating enhanced participant"""
        p = EnhancedBattleParticipant(
            name="SkillPet",
            hp=100,
            max_hp=100,
            en=60,
            max_en=60,
            level=10,
            stats={"attack": 60, "defense": 50, "sp_atk": 70, "sp_def": 55, "speed": 65},
            skills=["slash", "flame_burst", "shield"],
            battle_mode=BattleMode.AGGRESSIVE,
        )
        assert p.name == "SkillPet"
        assert len(p.skills) == 3
        assert p.battle_mode == BattleMode.AGGRESSIVE

    def test_get_available_skills(self):
        """Test getting available skills"""
        p = EnhancedBattleParticipant(
            name="SkillPet",
            hp=100,
            max_hp=100,
            en=60,
            max_en=60,
            level=10,
            stats={},
            skills=["slash", "heavy_strike", "final_attack"],
        )
        available = p.get_available_skills()
        assert len(available) > 0
        assert all(skill.name in ["Slash", "Heavy Strike", "Final Attack"] for skill in available)

    def test_use_skill_success(self):
        """Test using a skill successfully"""
        p = EnhancedBattleParticipant(
            name="SkillPet",
            hp=100,
            max_hp=100,
            en=60,
            max_en=60,
            level=10,
            stats={},
            skills=["slash"],
        )
        initial_en = p.en
        skill = ALL_SKILLS["slash"]
        success = p.use_skill(skill)
        assert success is True
        assert p.en < initial_en

    def test_use_skill_insufficient_en(self):
        """Test using skill with insufficient EN"""
        p = EnhancedBattleParticipant(
            name="SkillPet",
            hp=100,
            max_hp=100,
            en=5,
            max_en=60,
            level=10,
            stats={},
            skills=["final_attack"],
        )
        skill = ALL_SKILLS["final_attack"]  # Costs 50 EN
        success = p.use_skill(skill)
        assert success is False
        assert p.en == 5

    def test_skill_cooldown(self):
        """Test skill cooldown"""
        p = EnhancedBattleParticipant(
            name="SkillPet",
            hp=100,
            max_hp=100,
            en=100,
            max_en=100,
            level=10,
            stats={},
            skills=["final_attack"],
        )
        skill = ALL_SKILLS["final_attack"]
        p.use_skill(skill)
        assert p.skill_cooldowns.get("Final Attack", 0) > 0

        # Try to use immediately
        success = p.use_skill(skill)
        assert success is False

    def test_reduce_cooldowns(self):
        """Test cooldown reduction"""
        p = EnhancedBattleParticipant(
            name="SkillPet",
            hp=100,
            max_hp=100,
            en=100,
            max_en=100,
            level=10,
            stats={},
            skills=["final_attack"],
        )
        p.skill_cooldowns["test_skill"] = 3
        p.reduce_cooldowns()
        assert p.skill_cooldowns["test_skill"] == 2


class TestEnhancedBattleSimulator:
    """Test enhanced battle simulator"""

    def test_create_simulator(self):
        """Test creating battle simulator"""
        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100,
            max_hp=100,
            en=60,
            max_en=60,
            level=10,
            stats={"attack": 60, "defense": 50, "sp_atk": 70, "sp_def": 55, "speed": 65},
        )
        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=100,
            max_hp=100,
            en=60,
            max_en=60,
            level=10,
            stats={"attack": 65, "defense": 48, "sp_atk": 68, "sp_def": 60, "speed": 70},
        )
        simulator = EnhancedBattleSimulator(p1, p2)
        assert simulator.attacker.name == "Pet1"
        assert simulator.defender.name == "Pet2"

    def test_calculate_damage(self):
        """Test damage calculation"""
        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100,
            max_hp=100,
            en=60,
            max_en=60,
            level=10,
            stats={"attack": 60, "defense": 50, "sp_atk": 70, "sp_def": 55, "speed": 65},
            skills=["slash"],
        )
        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=100,
            max_hp=100,
            en=60,
            max_en=60,
            level=10,
            stats={"attack": 65, "defense": 48, "sp_atk": 68, "sp_def": 60, "speed": 70},
        )
        simulator = EnhancedBattleSimulator(p1, p2)
        skill = ALL_SKILLS["slash"]

        damage = simulator._calculate_damage(p1, p2, skill)
        assert damage > 0
        assert isinstance(damage, int)

    def test_process_status_effects(self):
        """Test status effect processing"""
        p = EnhancedBattleParticipant(
            name="Pet",
            hp=100,
            max_hp=100,
            en=60,
            max_en=60,
            level=10,
            stats={},
        )

        # Add poison effect
        poison = StatusEffect(EffectType.POISON, 2, 0.5, "Poisoned")
        p.effects.append(poison)

        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100,
            max_hp=100,
            en=60,
            max_en=60,
            level=10,
            stats={},
        )
        simulator = EnhancedBattleSimulator(p1, p)

        initial_hp = p.hp
        damage = simulator._process_status_effects(p)

        assert damage > 0
        assert p.hp < initial_hp
        assert poison.duration == 1  # Duration reduced


class TestBattleReplay:
    """Test battle replay functionality"""

    def test_create_replay(self):
        """Test creating a replay"""
        replay = BattleReplay(
            id="battle_test_001",
            timestamp="2024-01-01T10:00:00",
            attacker_name="PyDragon",
            attacker_level=10,
            defender_name="GoPhoenix",
            defender_level=10,
            winner="PyDragon",
            turns=15,
            attacker_hp_final=50,
            defender_hp_final=0,
            log=["Turn 1: ...", "Turn 2: ..."],
            attacker_stats={"attack": 60},
            defender_stats={"attack": 65},
            result="win",
        )
        assert replay.id == "battle_test_001"
        assert replay.winner == "PyDragon"

    def test_replay_to_dict(self):
        """Test replay serialization"""
        replay = BattleReplay(
            id="battle_test_001",
            timestamp="2024-01-01T10:00:00",
            attacker_name="PyDragon",
            attacker_level=10,
            defender_name="GoPhoenix",
            defender_level=10,
            winner="PyDragon",
            turns=15,
            attacker_hp_final=50,
            defender_hp_final=0,
            log=[],
            attacker_stats={},
            defender_stats={},
            result="win",
        )
        data = replay.to_dict()
        assert data["id"] == "battle_test_001"
        assert data["winner"] == "PyDragon"

    def test_replay_from_dict(self):
        """Test replay deserialization"""
        data = {
            "id": "battle_test_001",
            "timestamp": "2024-01-01T10:00:00",
            "attacker_name": "PyDragon",
            "attacker_level": 10,
            "defender_name": "GoPhoenix",
            "defender_level": 10,
            "winner": "PyDragon",
            "turns": 15,
            "attacker_hp_final": 50,
            "defender_hp_final": 0,
            "log": [],
            "attacker_stats": {},
            "defender_stats": {},
            "result": "win",
        }
        replay = BattleReplay.from_dict(data)
        assert replay.id == "battle_test_001"
        assert replay.attacker_name == "PyDragon"


class TestBattleReplayManager:
    """Test replay manager"""

    def test_save_and_load_replay(self):
        """Test saving and loading replay"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BattleReplayManager(tmpdir)

            replay = manager.save_battle(
                attacker_name="PyDragon",
                attacker_level=10,
                defender_name="GoPhoenix",
                defender_level=10,
                winner="PyDragon",
                turns=15,
                attacker_hp_final=50,
                defender_hp_final=0,
                battle_log=["Turn 1: ..."],
                attacker_stats={"attack": 60},
                defender_stats={"attack": 65},
            )

            assert replay.id in manager.replays
            retrieved = manager.get_replay(replay.id)
            assert retrieved is not None
            assert retrieved.winner == "PyDragon"

    def test_get_player_replays(self):
        """Test getting replays by player"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BattleReplayManager(tmpdir)

            manager.save_battle(
                attacker_name="PyDragon",
                attacker_level=10,
                defender_name="GoPhoenix",
                defender_level=10,
                winner="PyDragon",
                turns=15,
                attacker_hp_final=50,
                defender_hp_final=0,
                battle_log=[],
                attacker_stats={},
                defender_stats={},
            )

            replays = manager.get_replays_by_player("PyDragon")
            assert len(replays) == 1
            assert replays[0].attacker_name == "PyDragon"

    def test_win_rate_calculation(self):
        """Test win rate calculation"""
        import time
        
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BattleReplayManager(tmpdir)

            # Win (PyDragon as attacker)
            manager.save_battle(
                attacker_name="PyDragon",
                attacker_level=10,
                defender_name="GoPhoenix",
                defender_level=10,
                winner="PyDragon",
                turns=10,
                attacker_hp_final=50,
                defender_hp_final=0,
                battle_log=[],
                attacker_stats={},
                defender_stats={},
            )

            time.sleep(1)  # Ensure different timestamp

            # Loss (PyDragon as attacker, loses)
            manager.save_battle(
                attacker_name="PyDragon",
                attacker_level=10,
                defender_name="GoPhoenix",
                defender_level=10,
                winner="GoPhoenix",
                turns=10,
                attacker_hp_final=0,
                defender_hp_final=50,
                battle_log=[],
                attacker_stats={},
                defender_stats={},
            )

            # Reload to ensure both are loaded
            manager._load_replays()
            
            win_rate = manager.get_win_rate("PyDragon")
            assert win_rate == 50.0

    def test_get_statistics(self):
        """Test statistics calculation"""
        with tempfile.TemporaryDirectory() as tmpdir:
            manager = BattleReplayManager(tmpdir)

            manager.save_battle(
                attacker_name="PyDragon",
                attacker_level=10,
                defender_name="GoPhoenix",
                defender_level=10,
                winner="PyDragon",
                turns=10,
                attacker_hp_final=50,
                defender_hp_final=0,
                battle_log=[],
                attacker_stats={},
                defender_stats={},
            )

            stats = manager.get_statistics("PyDragon")
            assert stats["total_battles"] == 1
            assert stats["wins"] == 1
            assert stats["win_rate"] == 100.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
