from enum import Enum

import casino_player

from .strategies.base import Strategy, PlacedBet


class PlayerStatus(Enum):
    WAITING = "waiting"
    PLAYING = "playing"
    FINISHED = "finished"


class Player:
    """Casino player with strategy and status tracking"""

    def __init__(
        self,
        player_id: str,
        initial_bankroll: int,
        strategy: Strategy,
        max_rounds: int = 50,
    ):
        self.player_id = player_id
        self.stats_tracker = casino_player.Player(initial_bankroll)
        self.strategy = strategy
        self.max_rounds = max_rounds
        self.rounds_played = 0
        self.status = PlayerStatus.WAITING

    def get_current_bankroll(self) -> int:
        return self.stats_tracker.get_bankroll()

    def should_leave(self) -> bool:
        """Determine if player should leave the table"""
        if self.rounds_played >= self.max_rounds:
            return True
        if self.get_current_bankroll() < self.strategy.base_bet:
            return True
        return False

    def calculate_bets(self) -> list[PlacedBet]:
        """Get bets from strategy"""
        return self.strategy.calculate_bets()

    def update_after_round(self, total_profit: int, total_bet: int, number: int):
        """Update player stats after a round"""
        self.stats_tracker.add_game(total_profit, total_bet, number)
        self.rounds_played += 1
        self.strategy.update_after_spin(total_profit > 0)
