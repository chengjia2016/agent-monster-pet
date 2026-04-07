"""
Battle Replay System
Saves, replays, and analyzes battle history
"""

import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text
from enum import Enum


class BattleResult(Enum):
    """Battle outcome"""
    WIN = "win"
    LOSS = "loss"
    DRAW = "draw"


@dataclass
class BattleReplay:
    """Battle replay data"""
    id: str
    timestamp: str
    attacker_name: str
    attacker_level: int
    defender_name: str
    defender_level: int
    winner: str
    turns: int
    attacker_hp_final: int
    defender_hp_final: int
    log: List[str]
    attacker_stats: Dict
    defender_stats: Dict
    result: str  # win, loss, draw

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "BattleReplay":
        """Create from dictionary"""
        return cls(**data)


class BattleReplayManager:
    """Manage battle replays and history"""

    def __init__(self, storage_dir: str = ".monster/battles"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.console = Console()
        self.replays: Dict[str, BattleReplay] = {}
        self._load_replays()

    def _load_replays(self):
        """Load all replays from storage"""
        for file in self.storage_dir.glob("*.json"):
            try:
                with open(file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    replay = BattleReplay.from_dict(data)
                    self.replays[replay.id] = replay
            except Exception as e:
                self.console.print(f"[red]Error loading replay {file}: {e}[/red]")

    def save_battle(
        self,
        attacker_name: str,
        attacker_level: int,
        defender_name: str,
        defender_level: int,
        winner: str,
        turns: int,
        attacker_hp_final: int,
        defender_hp_final: int,
        battle_log: List[str],
        attacker_stats: Dict,
        defender_stats: Dict,
    ) -> BattleReplay:
        """Save a battle replay"""
        battle_id = f"battle_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

        # Determine result
        if attacker_hp_final > 0 and defender_hp_final <= 0:
            result = BattleResult.WIN.value
        elif defender_hp_final > 0 and attacker_hp_final <= 0:
            result = BattleResult.LOSS.value
        else:
            result = BattleResult.DRAW.value

        replay = BattleReplay(
            id=battle_id,
            timestamp=datetime.now().isoformat(),
            attacker_name=attacker_name,
            attacker_level=attacker_level,
            defender_name=defender_name,
            defender_level=defender_level,
            winner=winner,
            turns=turns,
            attacker_hp_final=attacker_hp_final,
            defender_hp_final=defender_hp_final,
            log=battle_log,
            attacker_stats=attacker_stats,
            defender_stats=defender_stats,
            result=result,
        )

        self.replays[battle_id] = replay
        self._persist_replay(replay)

        return replay

    def _persist_replay(self, replay: BattleReplay):
        """Save replay to disk"""
        file_path = self.storage_dir / f"{replay.id}.json"
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(replay.to_dict(), f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.console.print(f"[red]Error saving replay: {e}[/red]")

    def get_replay(self, replay_id: str) -> Optional[BattleReplay]:
        """Get a specific replay"""
        return self.replays.get(replay_id)

    def get_recent_replays(self, count: int = 10) -> List[BattleReplay]:
        """Get most recent replays"""
        replays = sorted(
            self.replays.values(),
            key=lambda r: r.timestamp,
            reverse=True,
        )
        return replays[:count]

    def get_replays_by_player(self, player_name: str) -> List[BattleReplay]:
        """Get replays for a specific player"""
        return [
            r for r in self.replays.values()
            if r.attacker_name == player_name or r.defender_name == player_name
        ]

    def get_win_rate(self, player_name: str) -> float:
        """Calculate win rate for a player"""
        replays = self.get_replays_by_player(player_name)
        if not replays:
            return 0.0

        wins = sum(1 for r in replays if r.winner == player_name)
        return (wins / len(replays)) * 100

    def display_replay_list(self, replays: List[BattleReplay] = None):
        """Display list of replays"""
        if replays is None:
            replays = self.get_recent_replays(20)

        if not replays:
            self.console.print("[yellow]No battle replays found.[/yellow]")
            return

        table = Table(title="Battle History", show_header=True, header_style="bold magenta")
        table.add_column("ID", style="cyan")
        table.add_column("Attacker", style="green")
        table.add_column("Defender", style="red")
        table.add_column("Winner", style="yellow")
        table.add_column("Turns", style="blue")
        table.add_column("Result", style="magenta")
        table.add_column("Time", style="white")

        for replay in replays:
            result_color = "green" if replay.result == "win" else "red" if replay.result == "loss" else "yellow"
            table.add_row(
                replay.id[:12],
                replay.attacker_name,
                replay.defender_name,
                replay.winner,
                str(replay.turns),
                f"[{result_color}]{replay.result.upper()}[/{result_color}]",
                replay.timestamp[-8:],
            )

        self.console.print(table)

    def display_replay_details(self, replay: BattleReplay):
        """Display detailed replay information"""
        self.console.clear()

        # Title
        title = Text(f"Battle Replay: {replay.id}", style="bold cyan", justify="center")
        self.console.print(Panel(title, style="cyan"))

        # Match info
        match_info = Text()
        match_info.append(f"Time: {replay.timestamp}\n", style="white")
        match_info.append(
            f"{replay.attacker_name} (Lv. {replay.attacker_level}) vs "
            f"{replay.defender_name} (Lv. {replay.defender_level})\n",
            style="cyan bold"
        )
        match_info.append(
            f"Winner: {replay.winner} | Turns: {replay.turns}",
            style="green bold"
        )
        self.console.print(Panel(match_info, title="[cyan]Match Info[/cyan]", expand=False))

        # Stats comparison
        stats_table = Table(title="Stats Comparison", show_header=True, header_style="bold magenta")
        stats_table.add_column("Stat", style="yellow")
        stats_table.add_column(replay.attacker_name, style="green")
        stats_table.add_column(replay.defender_name, style="red")

        for stat in ["attack", "defense", "sp_atk", "sp_def", "speed"]:
            att_val = replay.attacker_stats.get(stat, 0)
            def_val = replay.defender_stats.get(stat, 0)
            stats_table.add_row(stat.capitalize(), str(att_val), str(def_val))

        self.console.print(stats_table)

        # Final HP
        hp_table = Table(title="Final HP", show_header=True, header_style="bold magenta")
        hp_table.add_column("Participant", style="cyan")
        hp_table.add_column("Final HP", style="yellow")
        hp_table.add_row(replay.attacker_name, f"{replay.attacker_hp_final} HP")
        hp_table.add_row(replay.defender_name, f"{replay.defender_hp_final} HP")
        self.console.print(hp_table)

        # Battle log
        log_panel = Panel(
            "\n".join(replay.log[-10:]),  # Show last 10 entries
            title="[cyan]Battle Log (Last 10 Turns)[/cyan]",
            expand=True,
        )
        self.console.print(log_panel)

    def get_statistics(self, player_name: str) -> Dict:
        """Get player statistics"""
        replays = self.get_replays_by_player(player_name)

        if not replays:
            return {
                "player": player_name,
                "total_battles": 0,
                "wins": 0,
                "losses": 0,
                "draws": 0,
                "win_rate": 0.0,
                "avg_turns": 0,
            }

        wins = sum(1 for r in replays if r.winner == player_name)
        losses = len(replays) - wins
        avg_turns = sum(r.turns for r in replays) / len(replays)

        return {
            "player": player_name,
            "total_battles": len(replays),
            "wins": wins,
            "losses": losses,
            "draws": sum(1 for r in replays if r.result == BattleResult.DRAW.value),
            "win_rate": (wins / len(replays)) * 100,
            "avg_turns": avg_turns,
        }

    def display_statistics(self, player_name: str):
        """Display player statistics"""
        stats = self.get_statistics(player_name)

        if stats["total_battles"] == 0:
            self.console.print(f"[yellow]No battle history for {player_name}[/yellow]")
            return

        panel = Panel(
            f"Total Battles: {stats['total_battles']}\n"
            f"Wins: [green]{stats['wins']}[/green] | "
            f"Losses: [red]{stats['losses']}[/red] | "
            f"Draws: [yellow]{stats['draws']}[/yellow]\n"
            f"Win Rate: [bold]{stats['win_rate']:.1f}%[/bold]\n"
            f"Avg Turns: {stats['avg_turns']:.1f}",
            title=f"[cyan]{player_name} Statistics[/cyan]",
            style="cyan",
        )
        self.console.print(panel)


def demo_replay_manager():
    """Demo replay manager"""
    console = Console()
    manager = BattleReplayManager()

    # Create a demo replay
    replay = manager.save_battle(
        attacker_name="PyDragon",
        attacker_level=10,
        defender_name="GoPhoenix",
        defender_level=10,
        winner="PyDragon",
        turns=15,
        attacker_hp_final=42,
        defender_hp_final=0,
        battle_log=[
            "Turn 1: PyDragon uses Slash!",
            "Turn 1: GoPhoenix takes 25 damage!",
            "Turn 2: GoPhoenix uses Ice Beam!",
            "Turn 2: PyDragon takes 30 damage!",
            # ... more turns
        ],
        attacker_stats={"attack": 60, "defense": 50, "sp_atk": 70, "sp_def": 55, "speed": 65},
        defender_stats={"attack": 65, "defense": 48, "sp_atk": 68, "sp_def": 60, "speed": 70},
    )

    console.print(f"[green]Replay saved: {replay.id}[/green]")

    # Display replays
    manager.display_replay_list()

    # Show details
    console.print("\n")
    manager.display_replay_details(replay)

    # Show stats
    console.print("\n")
    manager.display_statistics("PyDragon")


if __name__ == "__main__":
    demo_replay_manager()
