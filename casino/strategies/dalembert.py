from typing import List

from .base import PlacedBet, Strategy


class DAlembertStrategy(Strategy):
    def __init__(
        self, base_bet: int = 100, max_progression: int = 8, bet_type: str = "red"
    ):
        super().__init__(base_bet, max_progression)
        self.bet_type = bet_type
        self.current_level = 0

    def calculate_bets(self) -> List[PlacedBet]:
        current_bet = self.validate_bet_amount(
            self.base_bet + (self.current_level * (self.base_bet // 2))
        )
        current_bet = min(max(self.base_bet, current_bet), 2000)  # Cap at 2000 cents
        return [PlacedBet(bet_type=self.bet_type, amount=current_bet)]

    def update_after_spin(self, *, won: bool, number: int):
        if won:
            self.current_level = max(0, self.current_level - 1)
        else:
            self.current_level = min(self.max_progression, self.current_level + 1)
