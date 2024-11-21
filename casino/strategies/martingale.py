from typing import List

from .base import Strategy, PlacedBet


class MartingaleStrategy(Strategy):
    """
    Classic Martingale strategy betting on black.
    Double the bet after each loss, reset to base after win.
    Maximum bet is capped at 2000 cents (20€).
    """

    def __init__(
        self, base_bet: int = 100, max_progression: int = 4, color: str = "black"
    ):
        super().__init__(base_bet, max_progression)
        self.color = color  # 'red' or 'black'

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate next bet based on Martingale progression"""
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        current_bet = min(self.base_bet * multiplier, 2000)  # Cap at 2000 cents
        current_bet = self.validate_bet_amount(int(current_bet))
        if current_bet <= 0:
            return []
        return [PlacedBet(bet_type=self.color, amount=current_bet)]
