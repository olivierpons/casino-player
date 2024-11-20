from typing import List, Dict

from .player import PlayerStatus, Player
from roulette_table import RouletteTable


class CasinoTable:
    """Single roulette table in the casino"""

    def __init__(self, table_id: str, min_bet: int = 100, max_bet: int = 100_000):
        self.table_id = table_id
        self.min_bet = min_bet
        self.max_bet = max_bet
        self.roulette = RouletteTable()
        self.current_players: List[Player] = []
        self.max_players = 70

    def can_add_player(self) -> bool:
        return len(self.current_players) < self.max_players

    def add_player(self, player: Player) -> bool:
        if not self.can_add_player():
            return False
        self.current_players.append(player)
        player.status = PlayerStatus.PLAYING
        return True

    def remove_player(self, player: Player):
        if player in self.current_players:
            self.current_players.remove(player)
            player.status = PlayerStatus.FINISHED

    def play_round(self) -> Dict[str, any]:
        """Play one round at the table"""
        round_stats = {"winning_number": None, "players_results": {}}

        if not self.current_players:
            return round_stats

        # Collect bets
        player_bets = {}
        for player in self.current_players:
            bets = player.calculate_bets()
            total_bet = sum(bet.amount for bet in bets)

            if total_bet <= player.get_current_bankroll():
                player_bets[player.player_id] = bets

        # Spin wheel
        winning_number = self.roulette.spin()
        round_stats["winning_number"] = winning_number

        # Process results
        for player in self.current_players[:]:
            player_id = player.player_id
            if player_id not in player_bets:
                continue

            bets = player_bets[player_id]
            total_profit = 0
            total_bet = 0
            winning_bets = []
            losing_bets = []

            for bet in bets:
                total_bet += bet.amount
                if self.roulette.check_win(bet.bet_type, winning_number):
                    payout_multiplier = self.roulette.get_payout(bet.bet_type)
                    profit = bet.amount + int(bet.amount * payout_multiplier)
                    total_profit += profit
                    winning_bets.append(bet)
                else:
                    total_profit -= bet.amount
                    losing_bets.append(bet)

            player.update_after_round(total_profit, total_bet, winning_number)

            round_stats["players_results"][player_id] = {
                "profit": total_profit,
                "total_bet": total_bet,
                "bankroll": player.get_current_bankroll(),
                "winning_bets": winning_bets,
                "losing_bets": losing_bets,
            }

            if player.should_leave():
                self.remove_player(player)

        return round_stats


class Casino:
    """Main casino class managing tables and players"""

    def __init__(self):
        self.tables: List[CasinoTable] = [
            CasinoTable("table_1", min_bet=100),
            CasinoTable("table_2", min_bet=500),
            CasinoTable("table_3", min_bet=1000),
        ]
        self.waiting_players: List[Player] = []
        self.finished_players: List[Player] = []

    def add_player(self, player: Player):
        self.waiting_players.append(player)

    def assign_players(self):
        """Assign waiting players to tables"""
        for player in self.waiting_players[:]:
            for table in self.tables:
                if (
                    table.can_add_player()
                    and table.min_bet <= player.strategy.base_bet <= table.max_bet
                ):
                    if table.add_player(player):
                        self.waiting_players.remove(player)
                        break

    def simulate_round(self) -> Dict[str, any]:
        """Simulate one round at all tables"""
        round_results = {}
        for table in self.tables:
            round_results[table.table_id] = table.play_round()
        return round_results
