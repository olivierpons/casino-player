from typing import List, Dict

from .base import Strategy, PlacedBet


class ProgressiveCoverageStrategy(Strategy):
    """
    Progressive Coverage Strategy:
    Starts with minimal coverage and progressively increases both
    coverage area and bet size based on results. Combines multiple
    bet types for optimal table coverage.
    """

    def __init__(self, base_bet: int = 100, max_progression: int = 4):
        super().__init__(base_bet, max_progression)
        self.coverage_level = 0  # Current coverage level (0-3)
        self.consecutive_stage_losses = 0
        self.bet_patterns = self._initialize_bet_patterns()

    @staticmethod
    def _initialize_bet_patterns() -> Dict[int, List[tuple[str, float]]]:
        """Initialize betting patterns for each coverage level"""
        return {
            0: [  # Basic coverage (~48.6% coverage)
                ("black", 0.5),
                ("first_dozen", 0.5),
            ],
            1: [  # Intermediate coverage (~67.6% coverage)
                ("black", 0.4),
                ("first_dozen", 0.3),
                ("second_dozen", 0.3),
                ("straight_0", 0.1),
            ],
            2: [  # Advanced coverage (~83.8% coverage)
                ("first_dozen", 0.3),
                ("second_dozen", 0.3),
                ("third_dozen", 0.3),
                ("straight_0", 0.1),
                ("neighbours_0", 0.2),
            ],
            3: [  # Maximum coverage (~91.9% coverage)
                ("first_dozen", 0.25),
                ("second_dozen", 0.25),
                ("third_dozen", 0.25),
                ("straight_0", 0.15),
                ("neighbours_0", 0.3),
            ],
        }

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets based on current coverage level"""
        # Progressive bet sizing
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        current_base = int(self.base_bet * multiplier)

        # Get current bet pattern
        pattern = self.bet_patterns[self.coverage_level]

        # Create bets according to pattern
        bets = []
        for bet_type, proportion in pattern:
            bet_amount = int(current_base * proportion)
            if bet_amount > 0:
                bets.append(PlacedBet(bet_type=bet_type, amount=bet_amount))

        return bets

    def update_after_spin(self, *, won: bool, number: int):
        """Update coverage level and progression"""
        super().update_after_spin(won=won, number=number)

        if won:
            # Reset stage losses on win
            self.consecutive_stage_losses = 0
            # Reduce coverage if winning consistently at current level
            if self.consecutive_losses == 0 and self.coverage_level > 0:
                self.coverage_level = max(0, self.coverage_level - 1)
        else:
            # Track losses at current coverage level
            self.consecutive_stage_losses += 1
            # Increase coverage after multiple losses at current level
            if self.consecutive_stage_losses >= 3:
                self.coverage_level = min(3, self.coverage_level + 1)
                self.consecutive_stage_losses = 0
