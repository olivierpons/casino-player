from typing import List

from .base import Strategy, PlacedBet


class DAlembertStrategy(Strategy):
    """
    D'Alembert strategy: increase bet by one unit after loss,
    decrease by one unit after win. More conservative than Martingale.
    """

    def __init__(
        self, base_bet: int = 100, max_progression: int = 8, bet_type: str = "red"
    ):
        super().__init__(base_bet, max_progression)
        self.bet_type = bet_type
        self.current_level = 0  # Current progression level

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate next bet using D'Alembert progression"""
        # Current bet is base_bet plus level * unit
        current_bet = self.base_bet + (self.current_level * (self.base_bet // 2))
        current_bet = max(self.base_bet, current_bet)  # Never go below base bet

        return [PlacedBet(bet_type=self.bet_type, amount=current_bet)]

    def update_after_spin(self, won: bool):
        """Update progression level after spin result"""
        if won:
            # Decrease level after win
            self.current_level = max(0, self.current_level - 1)
        else:
            # Increase level after loss, but respect max_progression
            self.current_level = min(self.max_progression, self.current_level + 1)
