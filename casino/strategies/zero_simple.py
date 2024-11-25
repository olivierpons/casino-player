from .base import Strategy, PlacedBet
from typing import List


class ZeroSimpleStrategy(Strategy):
    """
    Strategy focusing on zero
    """

    def __init__(
        self, base_bet: int = 200, max_progression: int = 4, wait_before_bet: int = 5
    ):
        super().__init__(base_bet, max_progression)
        self.wait_before_bet = wait_before_bet
        self.non_zero_count = 0
        self.is_betting = False

    def calculate_bets(self) -> List[PlacedBet]:
        if self.is_betting:
            return [PlacedBet(bet_type="straight_0", amount=self.base_bet)]
        return []

    def update_after_spin(self, *, won: bool, number: int):
        super().update_after_spin(won=won, number=number)
        if number:
            self.non_zero_count += 1
            if self.non_zero_count >= self.wait_before_bet:
                self.is_betting = True
        else:
            self.non_zero_count = 0
            self.is_betting = False
