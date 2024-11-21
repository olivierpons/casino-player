from typing import List, Set
from collections import deque
from .base import Strategy, PlacedBet


class ColumnPatternStrategy(Strategy):
    """
    Column Pattern Strategy:
    Analyzes patterns in column hits and adjusts coverage based on historical data.
    Uses progressive betting on columns showing potential patterns.
    """

    def __init__(
        self, base_bet: int = 100, max_progression: int = 4, history_size: int = 20
    ):
        super().__init__(base_bet, max_progression)
        self.history = deque(maxlen=history_size)
        self.columns = {
            1: set(range(1, 37, 3)),  # 1, 4, 7, ..., 34
            2: set(range(2, 37, 3)),  # 2, 5, 8, ..., 35
            3: set(range(3, 37, 3)),  # 3, 6, 9, ..., 36
        }
        self.current_columns: Set[int] = {1, 2}  # Start with columns 1 and 2
        self.column_streaks = {1: 0, 2: 0, 3: 0}

    def _get_column(self, number: int) -> int:
        """Get the column number (1-3) for a given number"""
        if number == 0:
            return 0
        return (number - 1) % 3 + 1

    def _analyze_patterns(self) -> Set[int]:
        """Analyze column patterns to determine best columns to bet on"""
        if not self.history:
            return {1, 2}

        # Count recent hits for each column
        column_hits = {1: 0, 2: 0, 3: 0}
        for num in self.history:
            col = self._get_column(num)
            if col > 0:  # Ignore zero
                column_hits[col] += 1

        # Find the two columns with least hits (cold columns)
        sorted_columns = sorted(column_hits.items(), key=lambda x: x[1])
        return {sorted_columns[0][0], sorted_columns[1][0]}

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets based on column analysis"""
        # Progressive betting based on consecutive losses
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        current_bet = int(self.base_bet * multiplier)

        # Update columns selection if needed
        if self.consecutive_losses >= 2:
            self.current_columns = self._analyze_patterns()

        # Distribute bet across selected columns
        bet_per_column = current_bet // len(self.current_columns)

        return [
            PlacedBet(bet_type=f"column_{col}", amount=bet_per_column)
            for col in self.current_columns
            if bet_per_column > 0
        ]

    def update_after_spin(self, *, won: bool, number: int):
        """Update strategy state and pattern analysis"""
        super().update_after_spin(won=won, number=number)

        if number is not None:
            self.history.append(number)
            col = self._get_column(number)

            # Update column streaks
            for c in self.column_streaks:
                if c == col:
                    self.column_streaks[c] += 1
                else:
                    self.column_streaks[c] = 0
