from typing import Dict

from tabulate import tabulate

from casino.player import Player
from casino.strategies.zero_neighbours import ZeroNeighboursStrategy
from casino.table import Casino


def print_round_results(round_number: int, results: Dict[str, any]):
    """Print results of a casino round in a formatted table"""
    print(f"\n=== Round {round_number} ===")

    # Collect all data for tables with active players
    active_tables = []
    for table_id, table_results in results.items():
        if table_results["players_results"]:
            table_data = []

            # Header row for the table with winning number
            table_data.append(
                [
                    "Table " + table_id,
                    f"Winning Number: {table_results['winning_number']}",
                    "",
                    "",
                ]
            )

            # Column headers
            table_data.append(["Player", "Bet", "Profit", "Bankroll"])

            # Add player data
            for player_id, stats in table_results["players_results"].items():
                table_data.append(
                    [
                        player_id,
                        f"€{stats['total_bet']/100:>8.2f}",
                        f"€{stats['profit']/100:>+8.2f}",
                        f"€{stats['bankroll']/100:>10.2f}",
                    ]
                )

            active_tables.append(table_data)

    # Print each table's results with nice formatting
    for table_data in active_tables:
        print(
            "\n"
            + tabulate(
                table_data[1:],  # Skip the header row for tabulate
                headers="firstrow",
                tablefmt="pretty",
                colalign=("left", "right", "right", "right"),
            )
        )


def run_simulation(num_rounds: int = 50):
    """Run a complete casino simulation"""
    casino = Casino()

    # Create players with different strategies/bankrolls
    initial_players = [
        Player(
            player_id="player_1",
            initial_bankroll=1000_00,
            strategy=ZeroNeighboursStrategy(base_bet=100),  # 1€ base
        ),
        Player(
            player_id="player_2",
            initial_bankroll=1000_00,
            strategy=ZeroNeighboursStrategy(base_bet=500),  # 5€ base
        ),
        Player(
            player_id="player_3",
            initial_bankroll=1000_00,
            strategy=ZeroNeighboursStrategy(base_bet=1000),  # 10€ base
        ),
    ]

    for player in initial_players:
        casino.add_player(player)

    print("Starting casino simulation...")
    for round_num in range(1, num_rounds + 1):
        casino.assign_players()
        results = casino.simulate_round()
        print_round_results(round_num, results)

    print("\nSimulation finished!")


if __name__ == "__main__":
    run_simulation(num_rounds=50)
