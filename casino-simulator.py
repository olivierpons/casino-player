import casino_player

print(casino_player.__file__)

player = casino_player.Player(100000)

player.add_game(3500, 100, 17)
player.add_game(-200, 200, 24)

print(player.get_stats())
