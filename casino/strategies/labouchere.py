from typing import List
from .base import Strategy, PlacedBet


class LabouchereStrategy(Strategy):
    """
    Labouchere (Cancellation) strategy:
    Uses a sequence of numbers. Bet is the sum of first and last numbers.
    After a win, remove these numbers. After a loss, add the lost amount to the end.
    """

    def __init__(
        self, base_bet: int = 100, sequence_length: int = 6, bet_type: str = "red"
    ):
        super().__init__(base_bet)
        self.bet_type = bet_type
        self.sequence_length = sequence_length
        self.sequence = [1] * sequence_length  # Start with unit sequence
        self.original_sequence = self.sequence.copy()

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bet based on first and last numbers in sequence"""
        if not self.sequence:
            self.sequence = self.original_sequence.copy()

        if len(self.sequence) == 1:
            current_bet = int(self.base_bet * self.sequence[0])
        else:
            current_bet = int(self.base_bet * (self.sequence[0] + self.sequence[-1]))

        return [PlacedBet(bet_type=self.bet_type, amount=current_bet)]

    def update_after_spin(self, *, won: bool, number: int):
        """Update sequence based on win/loss"""
        if won and len(self.sequence) >= 2:
            # Remove first and last numbers after win
            self.sequence = self.sequence[1:-1]
        elif not won:
            # Add the lost amount to the end of the sequence
            if len(self.sequence) >= 2:
                lost_amount = self.sequence[0] + self.sequence[-1]
            else:
                lost_amount = self.sequence[0]
            self.sequence.append(lost_amount)

        if not self.sequence:
            # Reset sequence when empty (win achieved)
            self.sequence = self.original_sequence.copy()

        super().update_after_spin(won=won, number=number)
