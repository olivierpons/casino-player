from collections import deque
from typing import List, Dict, Set

from .base import Strategy, PlacedBet


class AdaptiveDistributionStrategy(Strategy):
    """
    Adaptive Distribution Strategy:
    Uses statistical distribution analysis to identify imbalances
    in number frequencies and adapts betting patterns accordingly.
    """

    def __init__(
        self,
        base_bet: int = 100,
        max_progression: int = 4,
        history_size: int = 100,
        confidence_threshold: float = 0.15,
    ):
        super().__init__(base_bet, max_progression)
        self.history = deque(maxlen=history_size)
        self.confidence_threshold = confidence_threshold
        self.expected_probability = 1 / 37
        self.number_frequencies: Dict[int, float] = {i: 0.0 for i in range(37)}
        self.bet_distribution = {"straight": 0.4, "corner": 0.6}

    def _calculate_chi_squared(self) -> float:
        """Calculate chi-squared statistic for current distribution"""
        if not self.history:
            return 0.0

        observed = [0] * 37
        for num in self.history:
            observed[num] += 1

        n = len(self.history)
        expected = n * self.expected_probability

        chi_squared = sum((obs - expected) ** 2 / expected for obs in observed)

        return chi_squared

    def _identify_underrepresented_numbers(self) -> Set[int]:
        """Identify numbers appearing less frequently than expected"""
        if not self.history:
            return set(range(1, 37))  # Exclude 0 for corner bets

        # Update frequencies
        total_spins = len(self.history)
        frequencies = {i: 0 for i in range(37)}
        for num in self.history:
            frequencies[num] += 1

        # Calculate probabilities
        for num in frequencies:
            self.number_frequencies[num] = frequencies[num] / total_spins

        # Find underrepresented numbers, excluding zero for corner bets
        return {
            num
            for num, freq in self.number_frequencies.items()
            if freq < (self.expected_probability - self.confidence_threshold)
            and num > 0
        }

    @staticmethod
    def _get_valid_corner_bets(numbers: Set[int]) -> List[str]:
        """Get list of valid corner bets covering target numbers"""
        corner_bets = set()

        for num in numbers:
            # A number can be the top-left corner of a corner bet if:
            # 1. It's not in the last row (num <= 32)
            # 2. It's not in the last column ((num % 3) != 0)
            if num <= 32 and (num % 3) != 0:
                corner_bets.add(f"corner_{num}")

        return list(corner_bets)

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets based on distribution analysis"""
        target_numbers = self._identify_underrepresented_numbers()

        # Progressive betting
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        total_bet = int(self.base_bet * multiplier)

        bets = []

        # Handle straight bets for zero
        if 0 in target_numbers:
            zero_bet = int(total_bet * 0.1)  # 10% on zero
            if zero_bet > 0:
                bets.append(PlacedBet(bet_type="straight_0", amount=zero_bet))
            total_bet -= zero_bet
            target_numbers.remove(0)

        # Get valid corner bets
        corner_bets = self._get_valid_corner_bets(target_numbers)

        # If we have valid corner bets
        if corner_bets:
            corner_amount = int(total_bet * self.bet_distribution["corner"])
            bet_per_corner = corner_amount // len(corner_bets)

            if bet_per_corner > 0:
                for corner in corner_bets:
                    bets.append(PlacedBet(bet_type=corner, amount=bet_per_corner))

        # Use remaining amount for straight bets
        remaining_bet = total_bet - sum(bet.amount for bet in bets)
        if remaining_bet > 0 and target_numbers:
            bet_per_number = remaining_bet // len(target_numbers)
            if bet_per_number > 0:
                for num in target_numbers:
                    bets.append(
                        PlacedBet(bet_type=f"straight_{num}", amount=bet_per_number)
                    )

        return bets

    def update_after_spin(self, *, won: bool, number: int):
        """Update distribution tracking"""
        super().update_after_spin(won=won, number=number)

        if number is not None:
            self.history.append(number)

            # Adjust confidence threshold based on chi-squared test
            if self._calculate_chi_squared() > 43.77:  # 95% confidence level
                self.confidence_threshold = min(0.2, self.confidence_threshold + 0.01)
            else:
                self.confidence_threshold = max(0.1, self.confidence_threshold - 0.01)
