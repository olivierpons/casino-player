from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List


@dataclass
class PlacedBet:
    bet_type: str
    amount: int  # Amount in cents


class Strategy(ABC):
    """Abstract base class for all roulette strategies"""

    @staticmethod
    def validate_bet_amount(amount: int) -> int:
        """Round bet amount to nearest 50 or 100 cents"""
        if amount <= 0:
            return 100  # Minimum bet of 1€
        remainder = amount % 100
        if remainder == 0:
            return amount
        return amount + (100 - remainder) if remainder >= 50 else amount - remainder

    def __init__(self, base_bet: int = 100, max_progression: int = 4):
        self.base_bet = self.validate_bet_amount(base_bet)
        self.max_progression = max_progression
        self.consecutive_losses = 0

    @abstractmethod
    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets for the next round"""
        pass

    def update_after_spin(self, *, won: bool, number: int):
        """Update strategy state after a spin"""
        if won:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses += 1
