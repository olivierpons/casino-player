from typing import List

from .base import PlacedBet, Strategy


class JamesBondStrategy(Strategy):
    """
    James Bond 007 strategy:
    Covers 25 numbers in one bet pattern:
    - 70% on high numbers (19-36)
    - 25% on six numbers (13-18)
    - 5% on zero
    """

    def __init__(self, base_bet: int = 2000, max_progression: int = 3):
        # Base bet should be divisible by 20 for proper bet distribution
        adjusted_base = (base_bet // 20) * 20
        super().__init__(adjusted_base, max_progression)
        self.losses_before_progression = 2

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets according to James Bond pattern"""
        progression_level = self.consecutive_losses // self.losses_before_progression
        multiplier = min(2**progression_level, 2**self.max_progression)
        current_base = int(self.base_bet * multiplier)

        bets = [
            # 70% sur les numéros hauts (19-36)
            PlacedBet(bet_type="high", amount=int(current_base * 0.7)),
            # 25% sur sixline_13 (13-18)
            PlacedBet(bet_type="sixline_13", amount=int(current_base * 0.25)),
            # 5% sur le zéro
            PlacedBet(bet_type="straight_0", amount=int(current_base * 0.05)),
        ]

        return [bet for bet in bets if bet.amount > 0]

    def update_after_spin(self, *, won: bool, number: int):
        """Update progression state"""
        super().update_after_spin(won=won, number=number)
