#!/usr/bin/env python3
import casino_player


def test_player():
    player = casino_player.Player(1000_00)
    player.add_game(3500, 1_00, 17)
    player.add_game(-200, 2_00, 24)
    stats = player.get_stats()
    history = player.get_history()
    bet_sizes = player.get_bet_sizes()
    numbers = player.get_numbers_bet()
    bankroll = player.get_bankroll()


if __name__ == "__main__":
    test_player()
