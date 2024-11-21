# strategies/zero_neighbours.py

from .base import Strategy, PlacedBet
from typing import List


class ZeroNeighboursStrategy(Strategy):
    """
    Strategy focusing on zero and its neighbours with progressive coverage
    """

    def __init__(self, base_bet: int = 100, max_progression: int = 4):
        super().__init__(base_bet, max_progression)

    def _calculate_progression_bet(self) -> int:
        """Calculate bet amount based on loss progression"""
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        return int(self.base_bet * multiplier)

    def calculate_bets(self) -> List[PlacedBet]:
        """
        Calculate bets based on current strategy state
        Returns a list of all bets to place
        """
        current_bet = self._calculate_progression_bet()
        bets = [PlacedBet(bet_type="straight_0", amount=current_bet)]

        # Base bet on zero

        # Add neighbours after first loss
        if self.consecutive_losses >= 1:
            bets.append(PlacedBet(bet_type="neighbours_0", amount=current_bet))

        # Add first dozen after second loss
        if self.consecutive_losses >= 2:
            bets.append(PlacedBet(bet_type="first_dozen", amount=current_bet * 2))

        return bets
