from typing import List

from .base import PlacedBet
from .zero_trend import ZeroTrendStrategy


class EnhancedZeroTrendStrategy(ZeroTrendStrategy):
    """
    Enhanced version of ZeroTrendStrategy with additional analysis and betting patterns
    """

    def __init__(
        self,
        base_bet: int = 100,
        max_progression: int = 4,
        zero_threshold: int = 5,
        history_size: int = 100,
    ):
        super().__init__(base_bet, max_progression, zero_threshold, history_size)
        self.consecutive_near_misses = 0
        # Numbers near zero on wheel:
        self.near_zero_numbers = {1, 2, 3, 26, 27, 28, 29, 32, 35}

    def is_near_miss(self, number: int) -> bool:
        """Check if number is adjacent or near zero on the wheel"""
        return number in self.near_zero_numbers

    def calculate_bets(self) -> List[PlacedBet]:
        if not self.is_betting:
            return []

        bets = []
        current_bet = self.validate_bet_amount(
            self.base_bet * (2 ** min(self.consecutive_losses, self.max_progression))
        )

        bets.append(PlacedBet(bet_type="straight_0", amount=current_bet))

        recent_spins = list(self.spins_history)[-5:]
        near_misses = sum(1 for num in recent_spins if self.is_near_miss(num))

        if near_misses >= 2:
            neighbours_bet = self.validate_bet_amount(current_bet // 2)
            if neighbours_bet >= 50:
                bets.append(PlacedBet(bet_type="neighbours_0", amount=neighbours_bet))

        if self.non_zero_count >= self.zero_threshold * 2:
            dozen_bet = self.validate_bet_amount(current_bet // 3)
            if dozen_bet >= 50:
                bets.append(PlacedBet(bet_type="first_dozen", amount=dozen_bet))

        return bets

    def update_after_spin(self, *, won: bool, number: int):
        """Enhanced update with near miss tracking"""
        super().update_after_spin(won=won, number=number)

        if number is not None:
            if self.is_near_miss(number):
                self.consecutive_near_misses += 1
            else:
                self.consecutive_near_misses = 0

    def get_stats(self) -> dict:
        """Get enhanced strategy statistics"""
        stats = super().get_stats()
        stats.update(
            {
                "consecutive_near_misses": self.consecutive_near_misses,
                "recent_near_misses": sum(
                    1 for num in list(self.spins_history)[-5:] if self.is_near_miss(num)
                ),
            }
        )
        return stats
