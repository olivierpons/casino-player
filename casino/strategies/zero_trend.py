from typing import List, Deque
from collections import deque

from .base import Strategy, PlacedBet


class ZeroTrendStrategy(Strategy):
    """
    Strategy that monitors zero frequency and bets when zero hasn't appeared
    for a specified number of spins.
    """

    def __init__(
        self,
        base_bet: int = 100,
        max_progression: int = 4,
        zero_threshold: int = 5,
        history_size: int = 100,
    ):
        """
        Initialize strategy

        Args:
            base_bet: Base betting amount in cents
            max_progression: Maximum progression multiplier for consecutive losses
            zero_threshold: Number of non-zero spins before betting on zero
            history_size: Maximum size of spin history to maintain
        """
        super().__init__(base_bet, max_progression)
        self.zero_threshold = zero_threshold
        self.spins_history: Deque[int] = deque(maxlen=history_size)
        self.non_zero_count = 0
        self.is_betting = False

    def update_history(self, number: int):
        """Update spin history and count since last zero"""
        self.spins_history.append(number)

        if number == 0:
            self.non_zero_count = 0
            self.is_betting = False
        else:
            self.non_zero_count += 1
            if self.non_zero_count >= self.zero_threshold:
                self.is_betting = True

    def calculate_bets(self) -> List[PlacedBet]:
        """
        Calculate bets based on zero trend analysis
        Returns empty list if conditions aren't met
        """
        if not self.is_betting:
            return []

        # If betting, use progressive sizing based on consecutive losses
        current_bet = self.base_bet * (
            2 ** min(self.consecutive_losses, self.max_progression)
        )

        bets = [
            # Main bet on zero
            PlacedBet(bet_type="straight_0", amount=current_bet)
        ]

        # If we've been waiting for a long time, add some coverage
        if self.non_zero_count >= self.zero_threshold * 2:
            # Add neighbors bet for coverage
            bets.append(
                PlacedBet(
                    bet_type="neighbours_0",
                    amount=current_bet // 2,  # Half size on coverage
                )
            )

        return bets

    def update_after_spin(self, *, won: bool, number: int):
        """
        Update strategy state after a spin

        Args:
            won: Whether any bet was won
            number: The actual number that came up
        """
        super().update_after_spin(won=won, number=number)

        if number is not None:
            self.update_history(number)

    def get_stats(self) -> dict:
        """Get current strategy statistics"""
        return {
            "spins_since_zero": self.non_zero_count,
            "is_betting": self.is_betting,
            "history_size": len(self.spins_history),
            "zero_frequency": self.spins_history.count(0)
            / max(1, len(self.spins_history)),
        }
