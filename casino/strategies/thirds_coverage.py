from typing import List
from .base import Strategy, PlacedBet


class ThirdsCoverageStrategy(Strategy):
    """
    Thirds Coverage strategy:
    Bets on two thirds of the table, adjusting coverage based on recent results.
    Uses pattern recognition to switch between different thirds combinations.
    """

    def __init__(self, base_bet: int = 100, max_progression: int = 4):
        super().__init__(base_bet, max_progression)
        self.thirds = {
            "first": list(range(1, 13)),  # 1-12
            "second": list(range(13, 25)),  # 13-24
            "third": list(range(25, 37)),  # 25-36
        }
        self.last_numbers = []
        self.max_history = 10
        self.current_coverage = ["first", "second"]  # Default coverage

    def _analyze_pattern(self) -> None:
        """Analyze recent numbers to adjust coverage"""
        if len(self.last_numbers) < 5:
            return

        # Count hits in each third
        hits = {third: 0 for third in self.thirds.keys()}
        for num in self.last_numbers[-5:]:
            for third, numbers in self.thirds.items():
                if num in numbers:
                    hits[third] += 1

        # Sort thirds by hits, choose the two with fewer hits
        sorted_thirds = sorted(hits.items(), key=lambda x: x[1])
        self.current_coverage = [third for third, _ in sorted_thirds[:2]]

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets for two thirds coverage"""
        self._analyze_pattern()

        # Base bet increases with consecutive losses but split between coverage areas
        multiplier = min(2 ** (self.consecutive_losses // 2), 2**self.max_progression)
        bet_per_third = int(self.base_bet * multiplier)

        bets = []
        for third in self.current_coverage:
            bets.append(PlacedBet(bet_type=f"{third}_dozen", amount=bet_per_third))

        return bets

    def update_after_spin(self, *, won: bool, number: int):
        """Update strategy state and number history"""
        super().update_after_spin(won=won, number=number)

        if number is not None:
            self.last_numbers.append(number)
            if len(self.last_numbers) > self.max_history:
                self.last_numbers.pop(0)
