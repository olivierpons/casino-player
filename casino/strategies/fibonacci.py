from typing import List
from .base import Strategy, PlacedBet


class FibonacciStrategy(Strategy):
    """
    Fibonacci strategy:
    Uses the Fibonacci sequence for bet progression after losses.
    Moves back two numbers in the sequence after a win.
    """

    def __init__(
        self, base_bet: int = 100, max_progression: int = 8, bet_type: str = "black"
    ):
        super().__init__(base_bet, max_progression)
        self.bet_type = bet_type
        self.sequence = [1]  # Fibonacci sequence normalized to 1
        self.current_position = 0
        self._initialize_sequence()

    def _initialize_sequence(self):
        """Initialize Fibonacci sequence up to max_progression"""
        while len(self.sequence) <= self.max_progression:
            next_num = self.sequence[-1] + (
                self.sequence[-2] if len(self.sequence) > 1 else 0
            )
            self.sequence.append(next_num)

    def calculate_bets(self) -> List[PlacedBet]:
        multiplier = self.sequence[self.current_position]
        current_bet = self.validate_bet_amount(int(self.base_bet * multiplier))

        return (
            [PlacedBet(bet_type=self.bet_type, amount=current_bet)]
            if current_bet >= 50
            else []
        )

    def update_after_spin(self, *, won: bool, number: int):
        """Update position in Fibonacci sequence based on result"""
        if won:
            # Move back two positions after a win
            self.current_position = max(0, self.current_position - 2)
        else:
            # Move forward one position after a loss
            self.current_position = min(self.max_progression, self.current_position + 1)
        super().update_after_spin(won=won, number=number)
