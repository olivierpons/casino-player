from .base import Strategy, PlacedBet
from typing import List


class ZeroAlwaysStrategy(Strategy):

    def __init__(self, base_bet: int = 200, max_progression: int = 4):
        super().__init__(base_bet, max_progression)

    def calculate_bets(self) -> List[PlacedBet]:
        return [PlacedBet(bet_type="straight_0", amount=self.base_bet)]
