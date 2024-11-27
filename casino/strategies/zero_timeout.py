from .base import Strategy, PlacedBet
from typing import List


class ZeroTimeoutStrategy(Strategy):
    def __init__(
        self,
        *,
        base_bet: int = 200,
        max_progression: int = 4,
        wait_before_bet=0,
        max_rounds_without_zero=20,
        timeout_rounds=5,
    ):
        super().__init__(base_bet, max_progression)
        self.wait_before_bet = wait_before_bet
        self.max_rounds_without_zero = max_rounds_without_zero
        self.timeout_rounds = timeout_rounds
        self.is_betting: bool = True
        self.non_zero_count = 0
        self.rounds_since_zero = 0
        self.timeout_remaining = 0

    def calculate_bets(self) -> List[PlacedBet]:
        if not self.is_betting or self.timeout_remaining > 0:
            return []

        return [PlacedBet(bet_type="straight_0", amount=self.base_bet)]

    def update_after_spin(self, *, won: bool, number: int):
        super().update_after_spin(won=won, number=number)

        if self.timeout_remaining > 0:
            self.timeout_remaining -= 1
            if self.timeout_remaining == 0:
                self.non_zero_count = 0
            return

        if number == 0:
            self.non_zero_count = 0
            self.rounds_since_zero = 0
            self.is_betting = False
        else:
            self.non_zero_count += 1
            self.rounds_since_zero += 1

            if self.rounds_since_zero >= self.max_rounds_without_zero:
                self.timeout_remaining = self.timeout_rounds
                self.rounds_since_zero = 0

            if self.non_zero_count >= self.wait_before_bet:
                self.is_betting = True
