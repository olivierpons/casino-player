from .base import Strategy, PlacedBet
from typing import List


class ZeroAndHalfStrategy(Strategy):
    ACCEPTABLE_OTHER_BET = ["red", "black", "even", "odd", "low", "high"]

    def __init__(self, *, base_bet: int = 200, max_progression: int = 4, other: str = '', wait_before_bet=0):
        if other not in self.ACCEPTABLE_OTHER_BET:
            raise Exception(f"{other} is not valid, acceptable values are {self.ACCEPTABLE_OTHER_BET}")
        super().__init__(base_bet, max_progression)
        self.other = other
        self.wait_before_bet = wait_before_bet
        self.is_betting: bool = False
        self.non_zero_count = 0


    def calculate_bets(self) -> List[PlacedBet]:
        if not self.is_betting:
            return []
        # 2/3 on 0, 1/30 on the other (should be 50% win like 'black' or 'red')
        straight_0 = self.validate_bet_amount(self.base_bet * 2 // 3)
        if straight_0:
            other = self.validate_bet_amount(self.base_bet - straight_0)
            if other:
                return [
                    PlacedBet(bet_type="straight_0", amount=straight_0),
                    PlacedBet(bet_type=self.other, amount=other),
                ]
        return [PlacedBet(bet_type="straight_0", amount=self.base_bet)]

    def update_after_spin(self, *, won: bool, number: int):
        super().update_after_spin(won=won, number=number)
        if number:
            self.non_zero_count += 1
            if self.non_zero_count >= self.wait_before_bet:
                self.is_betting = True
        else:
            self.non_zero_count = 0
            self.is_betting = False
