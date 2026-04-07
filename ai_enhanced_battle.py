"""
AI-Enhanced Interactive Battle System
Combines AI decision making with interactive battle simulation
"""

import json
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from enum import Enum
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, BarColumn, TextColumn
import time

from enhanced_battle import (
    EnhancedBattleParticipant,
    EnhancedBattleSimulator,
    Skill,
    SkillType,
    ALL_SKILLS,
    BattleMode as OrigBattleMode,
)
from ai_battle_strategy import (
    AIDecisionMaker,
    AIPersonality,
    BattleStateAnalyzer,
    BattlePredictorAnalyzer,
    SkillEvaluator,
)
from battle_tui import BattleDisplay, BattleAnimator, BattlePhase
from battle_replay import BattleReplayManager, BattleReplay


class BattleMode(Enum):
    """Battle modes"""
    PVE = "pve"              # Player vs AI Enemy
    PVP_AI = "pvp_ai"        # Player vs AI with AI assistance
    AI_VS_AI = "ai_vs_ai"    # AI vs AI (auto-battle)
    INTERACTIVE = "interactive"  # Player chooses moves


@dataclass
class BattleConfig:
    """Battle configuration"""
    mode: BattleMode
    player_ai_personality: Optional[AIPersonality] = None
    opponent_ai_personality: AIPersonality = AIPersonality.BALANCED
    show_ai_reasoning: bool = True
    auto_play_speed: float = 1.0  # Multiplier for animation speed


class AIEnhancedBattle:
    """AI-enhanced battle system with decision support"""

    def __init__(
        self,
        player: EnhancedBattleParticipant,
        opponent: EnhancedBattleParticipant,
        config: BattleConfig,
        console: Optional[Console] = None,
    ):
        self.player = player
        self.opponent = opponent
        self.config = config
        self.console = console or Console()
        self.display = BattleDisplay(self.console)
        self.animator = BattleAnimator(self.console)
        self.replay_manager = BattleReplayManager()

        # AI systems
        self.player_ai = AIDecisionMaker(config.player_ai_personality) if config.player_ai_personality else None
        self.opponent_ai = AIDecisionMaker(config.opponent_ai_personality)
        self.state_analyzer = BattleStateAnalyzer()
        self.evaluator = SkillEvaluator()
        self.predictor = BattlePredictorAnalyzer()

        # Battle state
        self.battle_log: List[str] = []
        self.turn = 0
        self.decisions_history: List[Dict] = []

    def show_pre_battle_analysis(self):
        """Show analysis before battle starts"""
        self.console.clear()

        # Predict win probability
        win_prob = self.predictor.predict_win_probability(self.player, self.opponent)
        personality, recommendation = self.predictor.recommend_strategy(self.player, self.opponent)

        analysis_panel = Panel(
            f"[cyan]{self.player.name}[/cyan] vs [magenta]{self.opponent.name}[/magenta]\n"
            f"\n[yellow]Win Probability:[/yellow] {win_prob:.1%}\n"
            f"[yellow]Recommended Strategy:[/yellow] {personality.value}\n"
            f"\n[green]{recommendation}[/green]",
            title="[bold cyan]Pre-Battle Analysis[/bold cyan]",
            style="cyan",
            expand=True,
        )
        self.console.print(analysis_panel)

        time.sleep(1)

        # Show opponent AI personality
        opponent_panel = Panel(
            f"[magenta]Opponent Strategy:[/magenta] {self.config.opponent_ai_personality.value}\n"
            f"\n[dim]The opponent will play {self.config.opponent_ai_personality.value}ly, "
            f"adapting to the battle situation.[/dim]",
            title="[bold magenta]AI Opponent[/bold magenta]",
            style="magenta",
        )
        self.console.print(opponent_panel)

        time.sleep(1)

    def get_player_skill_recommendations(self) -> Dict[str, float]:
        """Get AI recommendations for best skills"""
        available_skills = self.player.get_available_skills()
        state = self.state_analyzer.analyze_current_state(self.player, self.opponent, self.turn)

        recommendations = {}
        for skill in available_skills:
            metrics = self.evaluator.evaluate_skill(skill, self.player, self.opponent, state)
            recommendations[skill.name] = metrics.get_score()

        return recommendations

    def show_decision_reasoning(self, actor: str, decision: Skill, recommendations: Optional[Dict[str, float]] = None):
        """Show AI reasoning for decision"""
        if not self.config.show_ai_reasoning:
            return

        reasoning_text = f"[bold]{actor}[/bold] chooses [magenta]{decision.name}[/magenta]\n"

        if recommendations:
            top_skills = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:3]
            reasoning_text += f"\n[dim]Top considerations:[/dim]\n"
            for skill_name, score in top_skills:
                indicator = "→" if skill_name == decision.name else "•"
                reasoning_text += f"  {indicator} {skill_name}: {score:.2f}\n"

        panel = Panel(reasoning_text, style="blue", expand=False)
        self.console.print(panel)

    def player_turn_interactive(self):
        """Player chooses move interactively"""
        available_skills = self.player.get_available_skills()

        if not available_skills:
            self.console.print("[red]No available skills![/red]")
            return None

        # Show recommendations
        recommendations = self.get_player_skill_recommendations()

        self.console.print("\n[bold yellow]Available Moves:[/bold yellow]")
        table = Table(show_header=True, header_style="bold magenta")
        table.add_column("No.", style="cyan")
        table.add_column("Skill", style="green")
        table.add_column("Power", style="yellow")
        table.add_column("Cost", style="blue")
        table.add_column("Score", style="magenta")

        for i, skill in enumerate(available_skills, 1):
            score = recommendations.get(skill.name, 0)
            color = "green" if score > 50 else "yellow" if score > 30 else "red"
            table.add_row(
                str(i),
                skill.name,
                str(skill.power),
                f"{skill.en_cost} EN",
                f"[{color}]{score:.1f}[/{color}]",
            )

        self.console.print(table)

        while True:
            try:
                choice_str = self.console.input("\n[bold cyan]Choose skill (1-{}): [/bold cyan]".format(len(available_skills)))
                choice = int(choice_str) - 1

                if 0 <= choice < len(available_skills):
                    return available_skills[choice]

                self.console.print("[red]Invalid choice![/red]")
            except ValueError:
                self.console.print("[red]Please enter a number![/red]")

    def execute_turn(self, actor: EnhancedBattleParticipant, target: EnhancedBattleParticipant, actor_name: str):
        """Execute a turn"""
        # Decide move
        if actor == self.player and self.config.mode == BattleMode.INTERACTIVE:
            skill = self.player_turn_interactive()
        elif actor == self.player and self.player_ai:
            skill = self.player_ai.decide_next_move(actor, target, self.turn)
        else:
            skill = self.opponent_ai.decide_next_move(actor, target, self.turn)

        if not skill or not actor.use_skill(skill):
            self.battle_log.append(f"{actor_name} has no moves available!")
            return

        # Show decision reasoning
        if actor == self.opponent or (actor == self.player and self.player_ai):
            recommendations = self.get_player_skill_recommendations() if actor == self.player else None
            self.show_decision_reasoning(actor_name, skill, recommendations)

        # Execute skill
        self.animator.animate_move_execution(actor_name, skill, target.name)

        if skill.power > 0:
            # Simulate battle system damage calculation
            simulator = EnhancedBattleSimulator(actor, target, self.console)
            damage = simulator._calculate_damage(actor, target, skill)

            target.hp = max(0, target.hp - damage)
            self.animator.animate_damage(damage, target.name, is_critical=(damage > skill.power * 1.5))
            self.battle_log.append(f"{actor_name}'s {skill.name} deals {damage} damage!")

        # Apply effects
        if skill.effects:
            for effect in skill.effects:
                target.effects.append(effect)
                self.animator.animate_effect_applied(effect, target.name)
                self.battle_log.append(f"{target.name} is now {effect.name.lower()}!")

        # Recovery skill
        if skill.name == "Recover":
            recovery = int(actor.max_hp * 0.5)
            actor.hp = min(actor.max_hp, actor.hp + recovery)
            self.battle_log.append(f"{actor_name} recovers {recovery} HP!")

        # Record decision
        self.decisions_history.append({
            "turn": self.turn,
            "actor": actor_name,
            "skill": skill.name,
            "target_hp": target.hp,
            "target_max_hp": target.max_hp,
        })

    def process_status_effects(self, participant: EnhancedBattleParticipant, name: str):
        """Process status effects"""
        simulator = EnhancedBattleSimulator(participant, participant, self.console)
        damage = simulator._process_status_effects(participant)

        if damage > 0:
            self.battle_log.append(f"{name} takes {damage} damage from status effects!")

    def run_battle(self) -> Dict:
        """Run the complete battle"""
        self.show_pre_battle_analysis()
        self.animator.animate_intro(self.player, self.opponent)

        while self.player.hp > 0 and self.opponent.hp > 0 and self.turn < 30:
            self.turn += 1

            self.console.print(f"\n[bold yellow]Turn {self.turn}[/bold yellow]")

            # Speed determines turn order
            if self.player.stats.get("speed", 50) >= self.opponent.stats.get("speed", 50):
                turn_order = [(self.player, self.opponent, "Player"), (self.opponent, self.player, "Opponent")]
            else:
                turn_order = [(self.opponent, self.player, "Opponent"), (self.player, self.opponent, "Player")]

            for actor, target, actor_name in turn_order:
                if actor.hp <= 0:
                    continue

                # Execute turn
                self.execute_turn(actor, target, actor_name)

                # Process status effects
                self.process_status_effects(target, target.name)

                # Display battle state
                self.display.render_full_battle_state(
                    self.player, self.opponent, self.battle_log, BattlePhase.TURN
                )

                time.sleep(0.5)

            # Reduce cooldowns
            self.player.reduce_cooldowns()
            self.opponent.reduce_cooldowns()

            # Regenerate EN
            self.player.en = min(self.player.max_en, int(self.player.en + self.player.max_en * 0.1))
            self.opponent.en = min(self.opponent.max_en, int(self.opponent.en + self.opponent.max_en * 0.1))

        # Battle end
        winner = self.player if self.player.hp > self.opponent.hp else self.opponent
        loser = self.opponent if winner == self.player else self.player
        winner_name = "Player" if winner == self.player else "Opponent"

        self.console.print(
            Panel(
                f"[bold green]{winner_name} wins![/bold green]\n"
                f"HP: {winner.hp}/{winner.max_hp}",
                style="green",
                expand=False,
            )
        )

        # Save replay
        replay = self.replay_manager.save_battle(
            attacker_name=self.player.name,
            attacker_level=self.player.level,
            defender_name=self.opponent.name,
            defender_level=self.opponent.level,
            winner=winner.name,
            turns=self.turn,
            attacker_hp_final=self.player.hp,
            defender_hp_final=self.opponent.hp,
            battle_log=self.battle_log,
            attacker_stats=self.player.stats,
            defender_stats=self.opponent.stats,
        )

        return {
            "winner": winner.name,
            "loser": loser.name,
            "turns": self.turn,
            "battle_log": self.battle_log,
            "decisions": self.decisions_history,
            "replay_id": replay.id,
        }


def demo_ai_interactive_battle():
    """Demonstrate interactive AI battle"""
    console = Console()

    # Create players
    player = EnhancedBattleParticipant(
        name="PlayerDragon",
        hp=120, max_hp=120,
        en=60, max_en=60,
        level=10,
        stats={"attack": 58, "defense": 52, "sp_atk": 68, "sp_def": 56, "speed": 62},
        skills=["slash", "heavy_strike", "flame_burst", "shield", "recover"],
    )

    opponent = EnhancedBattleParticipant(
        name="AIPhoenix",
        hp=120, max_hp=120,
        en=60, max_en=60,
        level=10,
        stats={"attack": 65, "defense": 48, "sp_atk": 70, "sp_def": 60, "speed": 70},
        skills=["multi_hit", "ice_beam", "electric_shock", "shield", "recover"],
    )

    # Configure battle
    config = BattleConfig(
        mode=BattleMode.PVP_AI,
        player_ai_personality=AIPersonality.BALANCED,
        opponent_ai_personality=AIPersonality.TACTICAL,
        show_ai_reasoning=True,
    )

    # Run battle
    battle = AIEnhancedBattle(player, opponent, config, console)
    result = battle.run_battle()

    console.print("\n[bold]Battle Summary:[/bold]")
    summary_table = Table(show_header=True, header_style="bold magenta")
    summary_table.add_column("Stat", style="cyan")
    summary_table.add_column("Value", style="green")
    summary_table.add_row("Winner", result["winner"])
    summary_table.add_row("Turns", str(result["turns"]))
    summary_table.add_row("Replay ID", result["replay_id"][:12])
    console.print(summary_table)


if __name__ == "__main__":
    demo_ai_interactive_battle()
