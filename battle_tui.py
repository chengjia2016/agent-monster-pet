"""
Advanced Battle TUI Module for Agent Monster
Provides rich terminal UI for battle visualization and interaction
"""

import time
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Callable
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, BarColumn, TextColumn, DownloadColumn
from rich.table import Table
from rich.text import Text
from rich.live import Live
from rich.layout import Layout
from rich.align import Align
from rich.syntax import Syntax
import threading


class BattlePhase(Enum):
    """Battle phase states"""
    INTRO = "intro"
    SETUP = "setup"
    TURN = "turn"
    EFFECT = "effect"
    END = "end"


class EffectType(Enum):
    """Effect types for status conditions"""
    POISON = "poison"  # 毒素
    BURN = "burn"  # 灼烧
    FREEZE = "freeze"  # 冻结
    PARALYZE = "paralyze"  # 麻痹
    CONFUSION = "confusion"  # 混乱
    SLEEP = "sleep"  # 睡眠
    SHIELD = "shield"  # 护盾
    BOOST = "boost"  # 增强
    DEBUFF = "debuff"  # 减弱


@dataclass
class BattleParticipant:
    """Battle participant information"""
    name: str
    hp: int
    max_hp: int
    en: int
    max_en: int
    level: int
    stats: Dict[str, int]  # attack, defense, sp_atk, sp_def, speed
    effects: List['StatusEffect'] = None

    def __post_init__(self):
        if self.effects is None:
            self.effects = []

    def get_hp_percentage(self) -> float:
        """Get HP as percentage"""
        return max(0, min(100, (self.hp / self.max_hp * 100))) if self.max_hp > 0 else 0

    def get_en_percentage(self) -> float:
        """Get EN as percentage"""
        return max(0, min(100, (self.en / self.max_en * 100))) if self.max_en > 0 else 0


@dataclass
class StatusEffect:
    """Status effect on a participant"""
    effect_type: EffectType
    duration: int
    power: float
    name: str

    def get_emoji(self) -> str:
        """Get emoji for effect type"""
        emojis = {
            EffectType.POISON: "☠️",
            EffectType.BURN: "🔥",
            EffectType.FREEZE: "❄️",
            EffectType.PARALYZE: "⚡",
            EffectType.CONFUSION: "😵",
            EffectType.SLEEP: "😴",
            EffectType.SHIELD: "🛡️",
            EffectType.BOOST: "📈",
            EffectType.DEBUFF: "📉",
        }
        return emojis.get(self.effect_type, "•")

    def get_color(self) -> str:
        """Get color for effect type"""
        colors = {
            EffectType.POISON: "magenta",
            EffectType.BURN: "red",
            EffectType.FREEZE: "cyan",
            EffectType.PARALYZE: "yellow",
            EffectType.CONFUSION: "magenta",
            EffectType.SLEEP: "blue",
            EffectType.SHIELD: "green",
            EffectType.BOOST: "green",
            EffectType.DEBUFF: "red",
        }
        return colors.get(self.effect_type, "white")


@dataclass
class Move:
    """Battle move/skill"""
    name: str
    power: int
    accuracy: float
    en_cost: int
    effect: Optional[StatusEffect] = None
    description: str = ""

    def get_emoji(self) -> str:
        """Get emoji based on power level"""
        if self.power > 100:
            return "⭐"
        elif self.power > 70:
            return "💥"
        elif self.power > 50:
            return "✨"
        else:
            return "🎯"


class BattleAnimator:
    """Handles battle animations and effects"""

    def __init__(self, console: Console):
        self.console = console
        self.animation_speed = 0.03

    def animate_damage(self, damage: int, target_name: str, is_critical: bool = False):
        """Animate damage display"""
        color = "red" if not is_critical else "bright_red"
        emoji = "💥" if is_critical else "❌"
        text = f"{emoji} {damage}" if not is_critical else f"💯 {damage}"
        self.console.print(
            f"[{color}]{text}[/{color}] damage to {target_name}",
            style=f"{color} bold"
        )
        time.sleep(self.animation_speed * 2)

    def animate_heal(self, amount: int, target_name: str):
        """Animate healing"""
        self.console.print(
            f"[green]💚 +{amount}[/green] HP to {target_name}",
            style="green bold"
        )
        time.sleep(self.animation_speed)

    def animate_effect_applied(self, effect: StatusEffect, target_name: str):
        """Animate status effect application"""
        emoji = effect.get_emoji()
        color = effect.get_color()
        self.console.print(
            f"[{color}]{emoji} {effect.name} applied to {target_name}[/{color}]",
            style=f"{color} bold"
        )
        time.sleep(self.animation_speed)

    def animate_move_execution(self, attacker: str, move: Move, target: str):
        """Animate move execution"""
        emoji = move.get_emoji()
        self.console.print(
            f"[cyan]{attacker}[/cyan] uses [bold]{emoji} {move.name}[/bold] on [cyan]{target}[/cyan]!",
            style="cyan bold"
        )
        time.sleep(self.animation_speed * 2)

    def animate_level_up(self, participant: BattleParticipant):
        """Animate level up"""
        panel = Panel(
            f"[bold yellow]⭐ {participant.name} leveled up! ⭐[/bold yellow]",
            style="yellow",
            expand=False,
        )
        self.console.print(panel)
        time.sleep(self.animation_speed * 3)

    def draw_connecting_line(self, length: int = 20) -> str:
        """Draw ASCII connecting line for battle visualization"""
        return "─" * length

    def animate_intro(self, p1: BattleParticipant, p2: BattleParticipant):
        """Animate battle intro"""
        self.console.clear()
        
        # Title
        title = Text("⚔️ BATTLE START ⚔️", style="bold red", justify="center")
        self.console.print(Panel(title, expand=False, style="red"))
        time.sleep(0.5)

        # Participants
        vs_text = Text(f"{p1.name} vs {p2.name}", style="bold", justify="center")
        self.console.print(Panel(vs_text, expand=False, style="cyan"))
        time.sleep(1)


class BattleDisplay:
    """Renders battle state and information"""

    def __init__(self, console: Console):
        self.console = console
        self.animator = BattleAnimator(console)

    def render_participant_hp(self, participant: BattleParticipant) -> Panel:
        """Render participant HP bar"""
        hp_pct = participant.get_hp_percentage()
        en_pct = participant.get_en_percentage()

        # HP bar
        hp_bar = "█" * int(hp_pct / 5) + "░" * (20 - int(hp_pct / 5))
        hp_color = "green" if hp_pct > 50 else "yellow" if hp_pct > 20 else "red"

        # EN bar
        en_bar = "▓" * int(en_pct / 5) + "░" * (20 - int(en_pct / 5))

        content = Text()
        content.append(f"{participant.name} Lv. {participant.level}\n", style="bold cyan")
        content.append(f"[{hp_color}]{hp_bar}[/{hp_color}] ", style=f"{hp_color}")
        content.append(f"{participant.hp}/{participant.max_hp} HP\n", style="white")
        content.append(f"[yellow]{en_bar}[/yellow] ", style="yellow")
        content.append(f"{participant.en}/{participant.max_en} EN\n", style="white")

        # Status effects
        if participant.effects:
            effects_text = " ".join([f.get_emoji() for f in participant.effects])
            content.append(f"\nStatus: {effects_text}", style="white")

        return Panel(content, expand=True, style="cyan", title="[cyan]PARTICIPANT[/cyan]")

    def render_battle_arena(self, p1: BattleParticipant, p2: BattleParticipant) -> str:
        """Render battle arena visualization"""
        p1_hp_bars = "█" * max(1, int(p1.get_hp_percentage() / 5))
        p2_hp_bars = "█" * max(1, int(p2.get_hp_percentage() / 5))

        arena = f"""
        {p1.name.ljust(20)} {'VS'.center(10)} {p2.name.rjust(20)}
        {p1_hp_bars.ljust(20)} {' '.center(10)} {p2_hp_bars.rjust(20)}
        """
        return arena

    def render_move_options(self, moves: List[Move]) -> Table:
        """Render available moves/skills"""
        table = Table(title="Available Moves", show_header=True, header_style="bold magenta")
        table.add_column("No.", style="cyan", width=5)
        table.add_column("Name", style="magenta")
        table.add_column("Power", style="yellow")
        table.add_column("Accuracy", style="green")
        table.add_column("Cost", style="cyan")

        for i, move in enumerate(moves, 1):
            accuracy_pct = f"{int(move.accuracy * 100)}%"
            color = "red" if move.power > 100 else "yellow"
            table.add_row(
                str(i),
                f"{move.get_emoji()} {move.name}",
                f"[{color}]{move.power}[/{color}]",
                accuracy_pct,
                f"{move.en_cost} EN"
            )

        return table

    def render_battle_log(self, log_entries: List[str], max_entries: int = 5) -> Panel:
        """Render battle log"""
        recent_logs = log_entries[-max_entries:]
        log_text = "\n".join(recent_logs) if recent_logs else "[dim]No action yet...[/dim]"
        return Panel(log_text, title="[cyan]Battle Log[/cyan]", style="cyan")

    def render_stats(self, participant: BattleParticipant) -> Table:
        """Render participant stats"""
        table = Table(title=f"{participant.name} Stats", show_header=False)
        table.add_column("Stat", style="yellow")
        table.add_column("Value", style="green")

        stats_display = [
            ("Attack", participant.stats.get("attack", 0)),
            ("Defense", participant.stats.get("defense", 0)),
            ("Sp. Atk", participant.stats.get("sp_atk", 0)),
            ("Sp. Def", participant.stats.get("sp_def", 0)),
            ("Speed", participant.stats.get("speed", 0)),
        ]

        for stat_name, stat_value in stats_display:
            table.add_row(stat_name, str(stat_value))

        return table

    def render_full_battle_state(
        self,
        p1: BattleParticipant,
        p2: BattleParticipant,
        battle_log: List[str],
        phase: BattlePhase,
    ):
        """Render complete battle state"""
        self.console.clear()

        # Create layout
        layout = Layout()
        layout.split_column(
            Layout(name="header", size=3),
            Layout(name="main"),
            Layout(name="footer", size=3),
        )

        # Header
        header = Text("⚔️ Agent Monster Battle ⚔️", style="bold red", justify="center")
        layout["header"].update(Panel(header, style="red"))

        # Main area - split into two columns
        layout["main"].split_row(
            Layout(name="left"),
            Layout(name="arena", size=30),
            Layout(name="right"),
        )

        layout["left"].update(self.render_participant_hp(p1))
        layout["right"].update(self.render_participant_hp(p2))

        # Arena center
        arena_text = Text(self.render_battle_arena(p1, p2), style="dim", justify="center")
        layout["arena"].update(Panel(arena_text, expand=False))

        # Footer
        footer_text = Text(f"Phase: {phase.value.upper()}", style="bold yellow", justify="center")
        layout["footer"].update(Panel(footer_text, style="yellow"))

        self.console.print(layout)

    def show_move_selection(self, moves: List[Move]) -> int:
        """Show move selection menu and get user choice"""
        self.console.clear()
        table = self.render_move_options(moves)
        self.console.print(table)

        while True:
            try:
                choice = int(self.console.input("\n[bold cyan]Select move (1-{}): [/bold cyan]".format(len(moves))))
                if 1 <= choice <= len(moves):
                    return choice - 1
                self.console.print("[red]Invalid choice! Please try again.[/red]")
            except ValueError:
                self.console.print("[red]Invalid input! Please enter a number.[/red]")


class InteractiveBattle:
    """Manages interactive battle experience"""

    def __init__(self, p1: BattleParticipant, p2: BattleParticipant, is_player_p1: bool = True):
        self.console = Console()
        self.display = BattleDisplay(self.console)
        self.animator = BattleAnimator(self.console)
        self.p1 = p1
        self.p2 = p2
        self.is_player_p1 = is_player_p1
        self.battle_log: List[str] = []
        self.turn = 0
        self.phase = BattlePhase.INTRO

    def run(self) -> Dict:
        """Run interactive battle"""
        self.animator.animate_intro(self.p1, self.p2)
        
        # Simple turn-based demo battle
        while self.p1.hp > 0 and self.p2.hp > 0 and self.turn < 20:
            self.turn += 1
            self.phase = BattlePhase.TURN

            # Display current state
            self.display.render_full_battle_state(
                self.p1, self.p2, self.battle_log, self.phase
            )

            # For this demo, just show a random outcome
            import random
            if random.random() > 0.5:
                damage = random.randint(10, 30)
                self.p2.hp = max(0, self.p2.hp - damage)
                self.animator.animate_damage(damage, self.p2.name)
                self.battle_log.append(f"Turn {self.turn}: {self.p1.name} deals {damage} damage!")
            else:
                damage = random.randint(10, 30)
                self.p1.hp = max(0, self.p1.hp - damage)
                self.animator.animate_damage(damage, self.p1.name)
                self.battle_log.append(f"Turn {self.turn}: {self.p2.name} deals {damage} damage!")

            time.sleep(0.5)

        # Battle end
        self.phase = BattlePhase.END
        winner = self.p1.name if self.p1.hp > self.p2.hp else self.p2.name
        self.console.print(
            Panel(
                f"[bold green]{winner} wins![/bold green]",
                style="green",
                expand=False,
            )
        )

        return {
            "winner": winner,
            "turns": self.turn,
            "log": self.battle_log,
            "p1_final_hp": self.p1.hp,
            "p2_final_hp": self.p2.hp,
        }


def demo_battle_tui():
    """Demo function to test battle TUI"""
    console = Console()

    # Create participants
    p1 = BattleParticipant(
        name="PyDragon",
        hp=100,
        max_hp=100,
        en=50,
        max_en=50,
        level=5,
        stats={
            "attack": 52,
            "defense": 43,
            "sp_atk": 60,
            "sp_def": 50,
            "speed": 65,
        }
    )

    p2 = BattleParticipant(
        name="GoPhoenix",
        hp=100,
        max_hp=100,
        en=50,
        max_en=50,
        level=5,
        stats={
            "attack": 55,
            "defense": 40,
            "sp_atk": 58,
            "sp_def": 55,
            "speed": 61,
        }
    )

    # Run battle
    battle = InteractiveBattle(p1, p2)
    result = battle.run()

    console.print("\n[bold]Battle Results:[/bold]")
    console.print(result)


if __name__ == "__main__":
    demo_battle_tui()
