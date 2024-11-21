from collections import deque
from typing import List

from .base import Strategy, PlacedBet


class HybridMartingaleStrategy(Strategy):
    """
    Hybrid Martingale Strategy:
    Combines multiple martingale progressions with different bet types,
    each with its own independent progression. Uses a dynamic allocation
    system to distribute bets based on success rates.
    """

    def __init__(
        self, base_bet: int = 100, max_progression: int = 4, history_size: int = 50
    ):
        super().__init__(base_bet, max_progression)
        self.history = deque(maxlen=history_size)
        # Track separate progressions for each bet type
        self.progressions = {"red": 0, "first_dozen": 0, "column_1": 0}
        # Track success rates for bet types
        self.success_rates = {bet_type: 0.33 for bet_type in self.progressions}
        self.bet_results = {
            bet_type: deque(maxlen=20) for bet_type in self.progressions
        }
        self.allocation_weights = {bet_type: 1.0 for bet_type in self.progressions}

    def _update_success_rates(self):
        """Update success rates for each bet type"""
        for bet_type, results in self.bet_results.items():
            if results:
                self.success_rates[bet_type] = sum(results) / len(results)
            else:
                self.success_rates[bet_type] = 0.33  # Default rate

    def _update_allocation_weights(self):
        """Update bet allocation weights based on success rates"""
        total_rate = sum(self.success_rates.values())
        if total_rate > 0:
            for bet_type in self.allocation_weights:
                # Use square of success rate to amplify differences
                self.allocation_weights[bet_type] = self.success_rates[
                    bet_type
                ] ** 2 / sum(rate**2 for rate in self.success_rates.values())

    def calculate_bets(self) -> List[PlacedBet]:
        bets = []

        if any(self.bet_results.values()):
            self._update_success_rates()
            self._update_allocation_weights()

        for bet_type, progression in self.progressions.items():
            multiplier = min(2**progression, 2**self.max_progression)
            weighted_base = self.validate_bet_amount(
                int(self.base_bet * self.allocation_weights[bet_type])
            )
            current_bet = self.validate_bet_amount(weighted_base * multiplier)

            if current_bet >= 50:
                bets.append(PlacedBet(bet_type=bet_type, amount=current_bet))

        return bets

    @staticmethod
    def _check_win(bet_type: str, number: int) -> bool:
        """Check if a specific bet type won"""
        if number == 0:
            return False
        # fmt: off
        red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
        # fmt: on
        if bet_type == "red":
            return number in red_numbers
        elif bet_type == "first_dozen":
            return 1 <= number <= 12
        elif bet_type == "column_1":
            return number % 3 == 1

        return False

    def update_after_spin(self, *, won: bool, number: int):
        """Update individual progressions and success tracking"""
        super().update_after_spin(won=won, number=number)

        if number is not None:
            self.history.append(number)

            # Update each progression separately
            for bet_type in self.progressions:
                bet_won = self._check_win(bet_type, number)

                # Update progression
                if bet_won:
                    self.progressions[bet_type] = 0
                else:
                    self.progressions[bet_type] = min(
                        self.progressions[bet_type] + 1, self.max_progression
                    )

                # Track result
                self.bet_results[bet_type].append(bet_won)
