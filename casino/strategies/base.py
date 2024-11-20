# strategies/__init__.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class PlacedBet:
    bet_type: str
    amount: int  # Amount in cents


class Strategy(ABC):
    """Abstract base class for all roulette strategies"""

    def __init__(self, base_bet: int = 100, max_progression: int = 4):
        self.base_bet = base_bet
        self.max_progression = max_progression
        self.consecutive_losses = 0

    @abstractmethod
    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets for the next round"""
        pass

    def update_after_spin(self, won: bool):
        """Update strategy state after a spin"""
        if won:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
