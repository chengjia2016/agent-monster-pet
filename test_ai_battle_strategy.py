"""
AI Battle Strategy System Tests
Comprehensive tests for AI decision making and predictions
"""

import pytest
import json
from unittest.mock import Mock, patch

from ai_battle_strategy import (
    AIPersonality,
    BattleStateAnalyzer,
    SkillEvaluator,
    AIDecisionMaker,
    BattlePredictorAnalyzer,
    StrategyPhase,
    SkillMetrics,
)
from enhanced_battle import (
    EnhancedBattleParticipant,
    BattleMode,
    ALL_SKILLS,
)


class TestBattleStateAnalyzer:
    """Test battle state analysis"""

    def test_determine_early_game(self):
        """Test early game phase detection"""
        analyzer = BattleStateAnalyzer()
        phase = analyzer._determine_phase(1)
        assert phase == StrategyPhase.EARLY_GAME

        phase = analyzer._determine_phase(3)
        assert phase == StrategyPhase.EARLY_GAME

    def test_determine_mid_game(self):
        """Test mid game phase detection"""
        analyzer = BattleStateAnalyzer()
        phase = analyzer._determine_phase(5)
        assert phase == StrategyPhase.MID_GAME

        phase = analyzer._determine_phase(10)
        assert phase == StrategyPhase.MID_GAME

    def test_determine_late_game(self):
        """Test late game phase detection"""
        analyzer = BattleStateAnalyzer()
        phase = analyzer._determine_phase(11)
        assert phase == StrategyPhase.LATE_GAME

        phase = analyzer._determine_phase(25)
        assert phase == StrategyPhase.LATE_GAME

    def test_analyze_current_state(self):
        """Test current state analysis"""
        analyzer = BattleStateAnalyzer()

        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 60, "defense": 50, "sp_atk": 70, "sp_def": 55, "speed": 65},
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=80, max_hp=100,
            en=30, max_en=60,
            level=10,
            stats={"attack": 65, "defense": 48, "sp_atk": 68, "sp_def": 60, "speed": 70},
        )

        state = analyzer.analyze_current_state(p1, p2, 5)

        assert state.turn_number == 5
        assert state.phase == StrategyPhase.MID_GAME
        assert state.my_hp_pct == 100.0
        assert state.opponent_hp_pct == 80.0
        assert state.my_en_pct == 100.0
        assert state.opponent_en_pct == 50.0
        assert state.my_speed_advantage is False
        assert state.ai_confidence > 0

    def test_calculate_confidence(self):
        """Test confidence calculation"""
        analyzer = BattleStateAnalyzer()

        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 70, "defense": 60, "sp_atk": 80, "sp_def": 65, "speed": 75},
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=50, max_hp=100,
            en=20, max_en=60,
            level=10,
            stats={"attack": 50, "defense": 40, "sp_atk": 50, "sp_def": 45, "speed": 50},
        )

        confidence = analyzer._calculate_confidence(p1, p2)
        assert 0 <= confidence <= 1
        assert confidence > 0.5  # Should be confident


class TestSkillEvaluator:
    """Test skill evaluation"""

    def test_evaluate_skill(self):
        """Test skill evaluation"""
        evaluator = SkillEvaluator()

        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 60, "defense": 50, "sp_atk": 70, "sp_def": 55, "speed": 65},
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 65, "defense": 48, "sp_atk": 68, "sp_def": 60, "speed": 70},
        )

        state = BattleStateAnalyzer().analyze_current_state(p1, p2, 1)
        skill = ALL_SKILLS["slash"]

        metrics = evaluator.evaluate_skill(skill, p1, p2, state)

        assert metrics.expected_damage > 0
        assert 0 <= metrics.accuracy_adjusted <= 100
        assert metrics.en_efficiency > 0
        assert metrics.risk_level >= 0
        assert metrics.get_score() > 0

    def test_recover_skill_high_value_when_low_hp(self):
        """Test recover skill has high value when low HP"""
        evaluator = SkillEvaluator()

        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=20, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={},
            skills=["recover"],
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={},
        )

        state = BattleStateAnalyzer().analyze_current_state(p1, p2, 1)
        skill = ALL_SKILLS["recover"]

        metrics = evaluator.evaluate_skill(skill, p1, p2, state)
        assert metrics.strategic_value > 0  # High value for recovery when low HP

    def test_shield_skill_value(self):
        """Test shield skill evaluation"""
        evaluator = SkillEvaluator()

        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={},
            skills=["shield"],
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={},
        )

        state = BattleStateAnalyzer().analyze_current_state(p1, p2, 1)
        skill = ALL_SKILLS["shield"]

        metrics = evaluator.evaluate_skill(skill, p1, p2, state)
        assert metrics.strategic_value > 0


class TestAIDecisionMaker:
    """Test AI decision making"""

    def test_aggressive_personality(self):
        """Test aggressive personality prefers high damage"""
        ai = AIDecisionMaker(AIPersonality.AGGRESSIVE)

        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 60, "defense": 50, "sp_atk": 70, "sp_def": 55, "speed": 65},
            skills=["slash", "heavy_strike", "flame_burst"],
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 65, "defense": 48, "sp_atk": 68, "sp_def": 60, "speed": 70},
        )

        decision = ai.decide_next_move(p1, p2, 1)
        assert decision is not None
        assert decision.power >= 70  # Should prefer high-power skills

    def test_defensive_personality(self):
        """Test defensive personality prioritizes healing"""
        ai = AIDecisionMaker(AIPersonality.DEFENSIVE)

        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=30, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={},
            skills=["slash", "recover", "shield"],
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={},
        )

        decision = ai.decide_next_move(p1, p2, 1)
        assert decision is not None
        assert decision.name in ["Recover", "Shield"]  # Should prioritize defense

    def test_balanced_personality(self):
        """Test balanced personality makes reasonable decisions"""
        ai = AIDecisionMaker(AIPersonality.BALANCED)

        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 60, "defense": 50, "sp_atk": 70, "sp_def": 55, "speed": 65},
            skills=["slash", "flame_burst", "shield", "recover"],
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 65, "defense": 48, "sp_atk": 68, "sp_def": 60, "speed": 70},
        )

        decision = ai.decide_next_move(p1, p2, 1)
        assert decision is not None

    def test_tactical_personality(self):
        """Test tactical personality uses status effects"""
        ai = AIDecisionMaker(AIPersonality.TACTICAL)

        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={},
            skills=["slash", "ice_beam", "electric_shock"],
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={},
        )

        decision = ai.decide_next_move(p1, p2, 1)
        assert decision is not None


class TestBattlePredictor:
    """Test battle predictions"""

    def test_predict_win_probability(self):
        """Test win probability prediction"""
        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 70, "defense": 60, "sp_atk": 80, "sp_def": 65, "speed": 75},
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 50, "defense": 40, "sp_atk": 50, "sp_def": 45, "speed": 50},
        )

        probability = BattlePredictorAnalyzer.predict_win_probability(p1, p2)

        assert 0 <= probability <= 1
        assert probability > 0.5  # Player should have advantage

    def test_recommend_strategy_dominant(self):
        """Test strategy recommendation for dominant position"""
        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=150, max_hp=150,
            en=80, max_en=80,
            level=15,
            stats={"attack": 80, "defense": 70, "sp_atk": 90, "sp_def": 75, "speed": 85},
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=50, max_hp=50,
            en=30, max_en=30,
            level=5,
            stats={"attack": 30, "defense": 25, "sp_atk": 30, "sp_def": 25, "speed": 30},
        )

        personality, recommendation = BattlePredictorAnalyzer.recommend_strategy(p1, p2)

        assert personality == AIPersonality.AGGRESSIVE
        assert "aggressive" in recommendation.lower()

    def test_recommend_strategy_disadvantage(self):
        """Test strategy recommendation for disadvantage"""
        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=50, max_hp=50,
            en=30, max_en=30,
            level=5,
            stats={"attack": 30, "defense": 25, "sp_atk": 30, "sp_def": 25, "speed": 30},
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=150, max_hp=150,
            en=80, max_en=80,
            level=15,
            stats={"attack": 80, "defense": 70, "sp_atk": 90, "sp_def": 75, "speed": 85},
        )

        personality, recommendation = BattlePredictorAnalyzer.recommend_strategy(p1, p2)

        assert personality == AIPersonality.DEFENSIVE
        assert "defensive" in recommendation.lower()

    def test_analyze_skill_effectiveness(self):
        """Test skill effectiveness analysis"""
        p1 = EnhancedBattleParticipant(
            name="Pet1",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 60, "defense": 50, "sp_atk": 70, "sp_def": 55, "speed": 65},
            skills=["slash", "heavy_strike", "flame_burst", "shield"],
        )

        p2 = EnhancedBattleParticipant(
            name="Pet2",
            hp=100, max_hp=100,
            en=60, max_en=60,
            level=10,
            stats={"attack": 65, "defense": 48, "sp_atk": 68, "sp_def": 60, "speed": 70},
        )

        effectiveness = BattlePredictorAnalyzer.analyze_skill_effectiveness(p1, p2)

        assert len(effectiveness) > 0
        assert all(isinstance(v, float) for v in effectiveness.values())
        assert all(v > 0 for v in effectiveness.values())


class TestSkillMetrics:
    """Test skill metrics calculation"""

    def test_skill_metrics_score(self):
        """Test skill metrics score calculation"""
        metrics = SkillMetrics(
            skill_name="Test Skill",
            expected_damage=50,
            accuracy_adjusted=95,
            en_efficiency=2.5,
            strategic_value=30,
            risk_level=0.2,
            synergy_bonus=0.15,
        )

        score = metrics.get_score()
        assert score > 0
        assert isinstance(score, float)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
