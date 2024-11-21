from typing import List

from .base import Strategy, PlacedBet


class MartingaleStrategy(Strategy):
    """
    Classic Martingale strategy betting on black.
    Double the bet after each loss, reset to base after win.
    """

    def __init__(
        self, base_bet: int = 100, max_progression: int = 6, color: str = "black"
    ):
        super().__init__(base_bet, max_progression)
        self.color = color  # 'red' or 'black'

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate next bet based on Martingale progression"""
        # Calculate bet amount: base_bet * 2^losses, but limit the progression
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        current_bet = int(self.base_bet * multiplier)
        return [PlacedBet(bet_type=self.color, amount=current_bet)]
