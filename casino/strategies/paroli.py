from typing import List

from .base import Strategy, PlacedBet


class ParoliStrategy(Strategy):
    """
    Paroli (Reverse Martingale) strategy:
    Double bet after wins, reset after loss or reaching target progression
    """

    def __init__(
        self, base_bet: int = 100, max_progression: int = 3, bet_type: str = "black"
    ):
        super().__init__(base_bet, max_progression)
        self.bet_type = bet_type
        self.consecutive_wins = 0

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate next bet using Paroli progression"""
        # Double bet after each win up to max_progression
        multiplier = min(2**self.consecutive_wins, 2**self.max_progression)
        current_bet = int(self.base_bet * multiplier)

        return [PlacedBet(bet_type=self.bet_type, amount=current_bet)]

    def update_after_spin(self, won: bool):
        """Update progression after spin result"""
        if won:
            self.consecutive_wins += 1
            if self.consecutive_wins >= self.max_progression:
                # Reset after reaching target progression
                self.consecutive_wins = 0
        else:
            # Reset after any loss
            self.consecutive_wins = 0
        # Update parent class tracking
        super().update_after_spin(won)
