import json
import os
from _typeshed import SupportsWrite
from pathlib import Path
from typing import List, Dict, Any

from .base import Strategy, PlacedBet


class SequenceStrategy(Strategy):
    """
    Strategy following a predefined sequence of bets loaded from a file
    """

    def __init__(self, sequence_file: str | Path, base_bet: int = 100):
        super().__init__(base_bet)
        self.current_position = 0
        self.sequence = self._load_sequence(sequence_file)

    @staticmethod
    def _load_sequence(filename: str | Path) -> List[Dict[str, Any]]:
        """Load bet sequence from JSON file"""
        default_sequence = [
            {"bet_type": "black", "multiplier": 1},
            {"bet_type": "red", "multiplier": 2},
            {"bet_type": "black", "multiplier": 1},
            {"bet_type": "first_dozen", "multiplier": 2},
            {"bet_type": "straight_0", "multiplier": 1},
        ]

        if not os.path.exists(filename):
            return default_sequence

        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            return default_sequence

    def calculate_bets(self) -> List[PlacedBet]:
        """Get next bet from sequence"""
        sequence_entry = self.sequence[self.current_position]
        current_bet = int(self.base_bet * sequence_entry["multiplier"])
        return [PlacedBet(bet_type=sequence_entry["bet_type"], amount=current_bet)]

    def update_after_spin(self, *, won: bool, number: int):
        """Move to next position in sequence"""
        self.current_position = (self.current_position + 1) % len(self.sequence)
        super().update_after_spin(won=won, number=number)

    @staticmethod
    def create_sequence_file(filename: str | Path, sequence: List[Dict]):
        """
        Create a sequence file with the specified bets
        Example sequence:
        [
            {"bet_type": "black", "multiplier": 1},
            {"bet_type": "red", "multiplier": 2},
            {"bet_type": "straight_0", "multiplier": 1}
        ]
        """
        f: SupportsWrite[str]
        file_path = Path(filename) if isinstance(filename, str) else filename
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(sequence, f, indent=2)
