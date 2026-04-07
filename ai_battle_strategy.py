"""
AI Battle Strategy Engine for Agent Monster
Advanced decision-making system for intelligent combat opponents
"""

import json
import math
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from collections import defaultdict
import random

from enhanced_battle import (
    EnhancedBattleParticipant,
    Skill,
    SkillType,
    BattleMode,
    ALL_SKILLS,
)


class StrategyPhase(Enum):
    """Battle phase classification"""
    EARLY_GAME = "early_game"      # First 3 turns
    MID_GAME = "mid_game"          # Turns 4-10
    LATE_GAME = "late_game"        # Turns 11+


class AIPersonality(Enum):
    """AI opponent personality types"""
    AGGRESSIVE = "aggressive"      # High-risk, high-reward
    DEFENSIVE = "defensive"        # Safe, protective
    BALANCED = "balanced"          # Adaptative
    TACTICAL = "tactical"          # Strategic, predictive
    EVOLVING = "evolving"          # Learns from battle


@dataclass
class SkillMetrics:
    """Metrics for skill evaluation"""
    skill_name: str
    expected_damage: float
    accuracy_adjusted: float
    en_efficiency: float
    strategic_value: float
    risk_level: float
    synergy_bonus: float

    def get_score(self) -> float:
        """Calculate overall skill score"""
        base_score = (
            self.expected_damage * 0.4 +
            self.accuracy_adjusted * 0.2 +
            self.en_efficiency * 0.15 +
            self.strategic_value * 0.15 +
            (1 - self.risk_level) * 0.1 +
            self.synergy_bonus * 0.1
        )
        return max(0, base_score)


@dataclass
class BattleState:
    """Complete game state analysis"""
    turn_number: int
    phase: StrategyPhase
    my_hp_pct: float
    opponent_hp_pct: float
    my_en_pct: float
    opponent_en_pct: float
    my_effects: List[str]
    opponent_effects: List[str]
    my_speed_advantage: bool
    ai_confidence: float


@dataclass
class SkillUsagePattern:
    """Track skill usage patterns"""
    skill_name: str
    usage_count: int = 0
    success_rate: float = 0.0
    avg_damage: float = 0.0
    last_used_turn: int = -10


class BattleStateAnalyzer:
    """Analyzes battle state for decision making"""

    def __init__(self):
        self.turn_history: List[Dict] = []

    def analyze_current_state(
        self,
        player: EnhancedBattleParticipant,
        opponent: EnhancedBattleParticipant,
        turn: int,
    ) -> BattleState:
        """Analyze complete game state"""
        phase = self._determine_phase(turn)

        return BattleState(
            turn_number=turn,
            phase=phase,
            my_hp_pct=player.get_hp_percentage(),
            opponent_hp_pct=opponent.get_hp_percentage(),
            my_en_pct=player.get_en_percentage(),
            opponent_en_pct=opponent.get_en_percentage(),
            my_effects=[e.name for e in player.effects],
            opponent_effects=[e.name for e in opponent.effects],
            my_speed_advantage=player.stats.get("speed", 0) > opponent.stats.get("speed", 0),
            ai_confidence=self._calculate_confidence(player, opponent),
        )

    def _determine_phase(self, turn: int) -> StrategyPhase:
        """Determine current battle phase"""
        if turn <= 3:
            return StrategyPhase.EARLY_GAME
        elif turn <= 10:
            return StrategyPhase.MID_GAME
        else:
            return StrategyPhase.LATE_GAME

    def _calculate_confidence(
        self,
        player: EnhancedBattleParticipant,
        opponent: EnhancedBattleParticipant,
    ) -> float:
        """Calculate AI confidence level (0-1)"""
        hp_ratio = player.hp / max(1, opponent.hp)
        en_ratio = player.en / max(1, opponent.en)
        stat_ratio = sum(player.stats.values()) / max(1, sum(opponent.stats.values()))

        confidence = (
            (hp_ratio * 0.4) +
            (en_ratio * 0.3) +
            (stat_ratio * 0.3)
        )

        return min(1.0, max(0.0, confidence))

    def add_turn_history(self, turn_data: Dict):
        """Record turn history for learning"""
        self.turn_history.append(turn_data)


class SkillEvaluator:
    """Evaluates skills for decision making"""

    def __init__(self):
        self.skill_patterns: Dict[str, SkillUsagePattern] = defaultdict(
            lambda: SkillUsagePattern(skill_name="")
        )

    def evaluate_skill(
        self,
        skill: Skill,
        player: EnhancedBattleParticipant,
        opponent: EnhancedBattleParticipant,
        state: BattleState,
    ) -> SkillMetrics:
        """Evaluate skill value in current situation"""
        expected_damage = self._estimate_damage(skill, player, opponent)
        accuracy_adjusted = self._adjust_for_accuracy(skill, state)
        en_efficiency = self._calculate_en_efficiency(skill, expected_damage, player)
        strategic_value = self._evaluate_strategic_value(skill, state, opponent)
        risk_level = self._assess_risk(skill, state)
        synergy_bonus = self._calculate_synergy(skill, opponent)

        return SkillMetrics(
            skill_name=skill.name,
            expected_damage=expected_damage,
            accuracy_adjusted=accuracy_adjusted,
            en_efficiency=en_efficiency,
            strategic_value=strategic_value,
            risk_level=risk_level,
            synergy_bonus=synergy_bonus,
        )

    def _estimate_damage(self, skill: Skill, player: EnhancedBattleParticipant, opponent: EnhancedBattleParticipant) -> float:
        """Estimate skill damage"""
        if skill.power == 0:
            return 0

        if skill.skill_type == SkillType.PHYSICAL:
            attacker_stat = player.stats.get("attack", 50)
            defender_stat = opponent.stats.get("defense", 50)
        else:
            attacker_stat = player.stats.get("sp_atk", 50)
            defender_stat = opponent.stats.get("sp_def", 50)

        base_damage = (2 * 5 / 5 + 2) * (attacker_stat * skill.power / defender_stat) / 50 + 2
        return base_damage * skill.accuracy

    def _adjust_for_accuracy(self, skill: Skill, state: BattleState) -> float:
        """Adjust skill value based on accuracy"""
        return skill.accuracy * 100

    def _calculate_en_efficiency(self, skill: Skill, damage: float, player: EnhancedBattleParticipant) -> float:
        """Calculate damage per EN spent"""
        if skill.en_cost == 0:
            return 0
        return damage / skill.en_cost * 10

    def _evaluate_strategic_value(self, skill: Skill, state: BattleState, opponent: EnhancedBattleParticipant) -> float:
        """Evaluate non-damage benefits"""
        value = 0.0

        # Status skills have defensive value
        if skill.skill_type == SkillType.STATUS:
            if skill.name == "Shield":
                value += 30 if state.opponent_hp_pct > 0.5 else 10
            elif skill.name == "Recover":
                value += 50 if state.my_hp_pct < 0.4 else (20 if state.my_hp_pct < 0.6 else 5)
            elif skill.name == "Poison Cloud":
                value += 20 * (1 - state.opponent_hp_pct)

        # Ultimate skills have high strategic value
        if skill.skill_type == SkillType.ULTIMATE:
            value += 100 if state.phase == StrategyPhase.LATE_GAME else 50

        return value

    def _assess_risk(self, skill: Skill, state: BattleState) -> float:
        """Assess skill risk (0-1, higher = riskier)"""
        risk = 1 - skill.accuracy

        # Low EN is risky
        if state.my_en_pct < 0.2 and skill.en_cost > state.my_en_pct * 100:
            risk += 0.3

        return min(1.0, risk)

    def _calculate_synergy(self, skill: Skill, opponent: EnhancedBattleParticipant) -> float:
        """Calculate synergy with opponent's current state"""
        synergy = 0.0

        # Healing synergy when low HP
        if skill.name == "Recover":
            synergy = 0.5

        # Effect synergy based on opponent's current effects
        for effect in opponent.effects:
            if effect.name.lower() == "poisoned" and skill.name == "Poison Cloud":
                synergy += 0.2
            elif effect.name.lower() == "frozen" and skill.skill_type == SkillType.PHYSICAL:
                synergy += 0.3

        return min(1.0, synergy)

    def record_skill_usage(self, skill: Skill, damage: int, success: bool):
        """Record skill usage for learning"""
        pattern = self.skill_patterns[skill.name]
        pattern.usage_count += 1
        pattern.avg_damage = (pattern.avg_damage * (pattern.usage_count - 1) + damage) / pattern.usage_count
        pattern.success_rate = (pattern.success_rate * (pattern.usage_count - 1) + (1 if success else 0)) / pattern.usage_count


class AIDecisionMaker:
    """Makes intelligent battle decisions"""

    def __init__(self, personality: AIPersonality = AIPersonality.BALANCED):
        self.personality = personality
        self.analyzer = BattleStateAnalyzer()
        self.evaluator = SkillEvaluator()
        self.memory: Dict[str, any] = {}

    def decide_next_move(
        self,
        player: EnhancedBattleParticipant,
        opponent: EnhancedBattleParticipant,
        turn: int,
    ) -> Skill:
        """Decide next skill to use"""
        # Analyze current battle state
        state = self.analyzer.analyze_current_state(player, opponent, turn)

        # Get available skills
        available_skills = player.get_available_skills()
        if not available_skills:
            # Default to first usable skill
            return available_skills[0] if available_skills else ALL_SKILLS["slash"]

        # Evaluate all skills
        skill_scores = {}
        for skill in available_skills:
            metrics = self.evaluator.evaluate_skill(skill, player, opponent, state)
            skill_scores[skill.name] = metrics.get_score()

        # Apply personality modifier
        selected_skill = self._apply_personality_logic(
            player, opponent, state, available_skills, skill_scores
        )

        return selected_skill

    def _apply_personality_logic(
        self,
        player: EnhancedBattleParticipant,
        opponent: EnhancedBattleParticipant,
        state: BattleState,
        available_skills: List[Skill],
        skill_scores: Dict[str, float],
    ) -> Skill:
        """Apply personality-specific decision logic"""

        if self.personality == AIPersonality.AGGRESSIVE:
            return self._aggressive_strategy(available_skills, skill_scores, state)
        elif self.personality == AIPersonality.DEFENSIVE:
            return self._defensive_strategy(available_skills, skill_scores, state, player)
        elif self.personality == AIPersonality.TACTICAL:
            return self._tactical_strategy(available_skills, skill_scores, state, opponent)
        elif self.personality == AIPersonality.EVOLVING:
            return self._evolving_strategy(available_skills, skill_scores, state, player, opponent)
        else:  # BALANCED
            return self._balanced_strategy(available_skills, skill_scores, state)

    def _aggressive_strategy(
        self,
        available_skills: List[Skill],
        skill_scores: Dict[str, float],
        state: BattleState,
    ) -> Skill:
        """High-risk, high-reward strategy"""
        # Prefer high-damage skills
        damage_skills = [s for s in available_skills if s.power > 70]
        if damage_skills:
            return max(damage_skills, key=lambda s: skill_scores.get(s.name, 0))

        return max(available_skills, key=lambda s: skill_scores.get(s.name, 0))

    def _defensive_strategy(
        self,
        available_skills: List[Skill],
        skill_scores: Dict[str, float],
        state: BattleState,
        player: EnhancedBattleParticipant,
    ) -> Skill:
        """Safe, protective strategy"""
        # Prioritize healing when hurt
        if state.my_hp_pct < 0.4:
            heal_skills = [s for s in available_skills if s.name == "Recover"]
            if heal_skills:
                return heal_skills[0]

        # Prioritize shield
        shield_skills = [s for s in available_skills if s.name == "Shield"]
        if shield_skills and state.my_hp_pct < 0.7:
            return shield_skills[0]

        # Otherwise use low-risk skills
        low_risk = [s for s in available_skills if s.power <= 50]
        if low_risk:
            return max(low_risk, key=lambda s: skill_scores.get(s.name, 0))

        return max(available_skills, key=lambda s: skill_scores.get(s.name, 0))

    def _tactical_strategy(
        self,
        available_skills: List[Skill],
        skill_scores: Dict[str, float],
        state: BattleState,
        opponent: EnhancedBattleParticipant,
    ) -> Skill:
        """Strategic, prediction-based strategy"""
        # Exploit opponent's weaknesses
        if len(opponent.effects) > 0:
            # Opponent is already affected, use synergistic skills
            effect_skills = [
                s for s in available_skills
                if s.effects and len(s.effects) > 0
            ]
            if effect_skills:
                return max(effect_skills, key=lambda s: skill_scores.get(s.name, 0))

        # Prepare for late game by using ultimate
        if state.phase == StrategyPhase.LATE_GAME:
            ultimate_skills = [s for s in available_skills if s.skill_type == SkillType.ULTIMATE]
            if ultimate_skills and state.opponent_hp_pct < 0.3:
                return ultimate_skills[0]

        return max(available_skills, key=lambda s: skill_scores.get(s.name, 0))

    def _evolving_strategy(
        self,
        available_skills: List[Skill],
        skill_scores: Dict[str, float],
        state: BattleState,
        player: EnhancedBattleParticipant,
        opponent: EnhancedBattleParticipant,
    ) -> Skill:
        """Learning-based strategy that adapts"""
        # Analyze what worked before
        best_performing_skill = max(
            self.evaluator.skill_patterns.values(),
            key=lambda p: p.success_rate * p.avg_damage if p.usage_count > 0 else 0,
            default=None,
        )

        if best_performing_skill and best_performing_skill.usage_count > 2:
            # Use skills that worked before
            matching_skills = [
                s for s in available_skills
                if s.name == best_performing_skill.skill_name
            ]
            if matching_skills:
                return matching_skills[0]

        # Otherwise, use balanced approach with randomization for learning
        if random.random() < 0.3:  # 30% chance to try new approach
            return random.choice(available_skills)

        return max(available_skills, key=lambda s: skill_scores.get(s.name, 0))

    def _balanced_strategy(
        self,
        available_skills: List[Skill],
        skill_scores: Dict[str, float],
        state: BattleState,
    ) -> Skill:
        """Balanced, adaptative strategy"""
        # Mix offense and defense based on situation
        if state.my_hp_pct < 0.5 and state.opponent_hp_pct > 0.6:
            # Focus on defense
            return self._defensive_strategy(available_skills, skill_scores, state, None)
        elif state.opponent_hp_pct < 0.3:
            # Go for kill
            return self._aggressive_strategy(available_skills, skill_scores, state)
        else:
            # Normal play - use best scored skill
            return max(available_skills, key=lambda s: skill_scores.get(s.name, 0))


class BattlePredictorAnalyzer:
    """Predicts battle outcomes and provides analysis"""

    @staticmethod
    def predict_win_probability(
        player: EnhancedBattleParticipant,
        opponent: EnhancedBattleParticipant,
    ) -> float:
        """Estimate win probability (0-1)"""
        # Calculate stat advantage
        player_total_stats = sum(player.stats.values())
        opponent_total_stats = sum(opponent.stats.values())
        stat_ratio = player_total_stats / max(1, opponent_total_stats)

        # Calculate level advantage
        level_ratio = player.level / max(1, opponent.level)

        # Calculate HP advantage
        hp_ratio = player.max_hp / max(1, opponent.max_hp)

        # Weighted probability
        probability = (
            (stat_ratio * 0.4) +
            (level_ratio * 0.3) +
            (hp_ratio * 0.3)
        )

        # Normalize to 0-1 range
        return min(1.0, max(0.0, probability))

    @staticmethod
    def recommend_strategy(
        player: EnhancedBattleParticipant,
        opponent: EnhancedBattleParticipant,
    ) -> Tuple[AIPersonality, str]:
        """Recommend best personality for player"""
        win_prob = BattlePredictorAnalyzer.predict_win_probability(player, opponent)

        if win_prob > 0.7:
            return AIPersonality.AGGRESSIVE, "You have a significant advantage. Play aggressively!"
        elif win_prob > 0.55:
            return AIPersonality.BALANCED, "Even matchup. Use a balanced approach."
        elif win_prob > 0.35:
            return AIPersonality.TACTICAL, "At a disadvantage. Play strategically."
        else:
            return AIPersonality.DEFENSIVE, "You're outmatched. Play defensively and look for opportunities."

    @staticmethod
    def analyze_skill_effectiveness(
        player: EnhancedBattleParticipant,
        opponent: EnhancedBattleParticipant,
    ) -> Dict[str, float]:
        """Analyze effectiveness of each available skill"""
        available_skills = player.get_available_skills()
        effectiveness = {}

        evaluator = SkillEvaluator()
        state = BattleStateAnalyzer().analyze_current_state(player, opponent, 1)

        for skill in available_skills:
            metrics = evaluator.evaluate_skill(skill, player, opponent, state)
            effectiveness[skill.name] = metrics.get_score()

        return effectiveness


def demo_ai_battle():
    """Demonstrate AI battle system"""
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel

    console = Console()

    # Create players
    player = EnhancedBattleParticipant(
        name="PlayerDragon",
        hp=120, max_hp=120,
        en=60, max_en=60,
        level=10,
        stats={"attack": 58, "defense": 52, "sp_atk": 68, "sp_def": 56, "speed": 62},
        skills=["slash", "heavy_strike", "flame_burst", "shield", "recover"],
        battle_mode=BattleMode.BALANCED,
    )

    opponent = EnhancedBattleParticipant(
        name="AIPhoenix",
        hp=120, max_hp=120,
        en=60, max_en=60,
        level=10,
        stats={"attack": 65, "defense": 48, "sp_atk": 70, "sp_def": 60, "speed": 70},
        skills=["multi_hit", "ice_beam", "electric_shock", "shield", "recover"],
        battle_mode=BattleMode.BALANCED,
    )

    # Show predictions
    predictor = BattlePredictorAnalyzer()
    win_prob = predictor.predict_win_probability(player, opponent)
    personality, recommendation = predictor.recommend_strategy(player, opponent)

    console.print(Panel(f"[bold cyan]Battle Prediction[/bold cyan]\n"
                       f"Win Probability: {win_prob:.1%}\n"
                       f"Recommended Strategy: {personality.value}\n"
                       f"{recommendation}",
                       style="cyan"))

    # Show skill analysis
    console.print("\n[bold yellow]Skill Effectiveness Analysis:[/bold yellow]")
    effectiveness = predictor.analyze_skill_effectiveness(player, opponent)
    
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Skill", style="cyan")
    table.add_column("Score", style="green")
    
    for skill_name, score in sorted(effectiveness.items(), key=lambda x: x[1], reverse=True):
        table.add_row(skill_name, f"{score:.2f}")
    
    console.print(table)

    # Demonstrate AI decision making
    console.print("\n[bold yellow]AI Decision Making (5 turns):[/bold yellow]")
    
    ai_maker = AIDecisionMaker(personality)
    
    for turn in range(1, 6):
        decision = ai_maker.decide_next_move(opponent, player, turn)
        state = BattleStateAnalyzer().analyze_current_state(opponent, player, turn)
        
        console.print(f"Turn {turn}: AI chooses [magenta]{decision.name}[/magenta] "
                     f"(HP: {opponent.hp}, EN: {opponent.en})")


if __name__ == "__main__":
    demo_ai_battle()
