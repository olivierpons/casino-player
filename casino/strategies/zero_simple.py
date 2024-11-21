from .base import Strategy, PlacedBet
from typing import List


class ZeroSimpleStrategy(Strategy):
    """
    Strategy focusing on zero
    """

    def __init__(
        self, base_bet: int = 200, max_progression: int = 4, zero_threshold: int = 5
    ):
        super().__init__(base_bet, max_progression)
        self.zero_threshold = zero_threshold
        self.non_zero_count = 0
        self.is_betting = False

    def calculate_bets(self) -> List[PlacedBet]:
        if self.is_betting:
            return [PlacedBet(bet_type="straight_0", amount=self.base_bet)]
        return []

    def update_after_spin(self, *, won: bool, number: int):
        super().update_after_spin(won=won, number=number)
        if number is not None:
            if number:
                self.non_zero_count += 1
                if self.non_zero_count >= self.zero_threshold:
                    self.is_betting = True
            else:
                self.non_zero_count = 0
                self.is_betting = False
