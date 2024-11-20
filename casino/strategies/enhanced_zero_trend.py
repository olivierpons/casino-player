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
        """Enhanced betting calculation with pattern recognition"""
        if not self.is_betting:
            return []

        bets = []
        current_bet = self.base_bet * (
                2 ** min(self.consecutive_losses, self.max_progression)
        )

        # Always bet on straight zero when active
        bets.append(PlacedBet(bet_type="straight_0", amount=current_bet))

        # Analyze recent near misses
        recent_spins = list(self.spins_history)[-5:]
        near_misses = sum(1 for num in recent_spins if self.is_near_miss(num))

        # If we're seeing many near misses, add coverage bets
        if near_misses >= 2:
            bets.append(PlacedBet(bet_type="neighbours_0", amount=current_bet // 2))

        # If we're far above threshold, add first dozen coverage
        if self.non_zero_count >= self.zero_threshold * 2:
            bets.append(PlacedBet(bet_type="first_dozen", amount=current_bet // 3))

        return bets

    def update_after_spin(self, won: bool, number: int = None):
        """Enhanced update with near miss tracking"""
        super().update_after_spin(won, number)

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