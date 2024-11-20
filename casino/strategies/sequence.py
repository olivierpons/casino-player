import json
import os
from typing import List, Dict

from .base import Strategy, PlacedBet


class SequenceStrategy(Strategy):
    """
    Strategy following a predefined sequence of bets loaded from a file
    """

    def __init__(self, sequence_file: str, base_bet: int = 100):
        super().__init__(base_bet)
        self.current_position = 0
        self.sequence = self._load_sequence(sequence_file)

    @staticmethod
    def _load_sequence(filename: str) -> List[Dict]:
        """Load bet sequence from JSON file"""
        if not os.path.exists(filename):
            # Default sequence if file not found
            return [
                {"bet_type": "black", "multiplier": 1},
                {"bet_type": "red", "multiplier": 2},
                {"bet_type": "black", "multiplier": 1},
                {"bet_type": "first_dozen", "multiplier": 2},
                {"bet_type": "straight_0", "multiplier": 1},
            ]

        with open(filename, "r") as f:
            return json.load(f)

    def calculate_bets(self) -> List[PlacedBet]:
        """Get next bet from sequence"""
        # Get current sequence entry
        sequence_entry = self.sequence[self.current_position]

        # Calculate bet amount using multiplier
        current_bet = int(self.base_bet * sequence_entry["multiplier"])

        return [PlacedBet(bet_type=sequence_entry["bet_type"], amount=current_bet)]

    def update_after_spin(self, *, won: bool, number: int):
        """Move to next position in sequence"""
        self.current_position = (self.current_position + 1) % len(self.sequence)
        super().update_after_spin(won=won, number=number)

    @staticmethod
    def create_sequence_file(filename: str, sequence: List[Dict]):
        """
        Create a sequence file with the specified bets
        Example sequence:
        [
            {"bet_type": "black", "multiplier": 1},
            {"bet_type": "red", "multiplier": 2},
            {"bet_type": "straight_0", "multiplier": 1}
        ]
        """
        with open(filename, "w") as f:
            json.dump(sequence, f, indent=2)
