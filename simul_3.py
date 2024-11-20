# main.py

import time
from typing import Dict

from tabulate import tabulate

from casino.player import Player
from casino.strategies.dalembert import DAlembertStrategy
from casino.strategies.enhanced_zero_trend import EnhancedZeroTrendStrategy
from casino.strategies.martingale import MartingaleStrategy
from casino.strategies.paroli import ParoliStrategy
from casino.strategies.sequence import SequenceStrategy
from casino.strategies.zero_trend import ZeroTrendStrategy
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


def run_strategy_comparison(num_rounds: int = 5000):
    """Run simulation with different strategies"""
    casino = Casino()

    # Create sequence file for SequenceStrategy
    sequence = [
        {"bet_type": "black", "multiplier": 1},
        {"bet_type": "first_dozen", "multiplier": 2},
        {"bet_type": "straight_0", "multiplier": 1},
        {"bet_type": "red", "multiplier": 1},
    ]
    SequenceStrategy.create_sequence_file("custom_sequence.json", sequence)

    # Create players with different strategies
    players = [
        Player(
            player_id="martingale",
            initial_bankroll=1000_00,  # 1000€
            strategy=MartingaleStrategy(base_bet=1_00, max_progression=6),
        ),
        Player(
            player_id="dalembert",
            initial_bankroll=1000_00,
            strategy=DAlembertStrategy(base_bet=1_00, max_progression=8),
        ),
        Player(
            player_id="paroli",
            initial_bankroll=1000_00,
            strategy=ParoliStrategy(base_bet=1_00, max_progression=3),
        ),
        Player(
            player_id="sequence",
            initial_bankroll=1000_00,
            strategy=SequenceStrategy("custom_sequence.json", base_bet=100),
        ),
        Player(
            player_id="zero",
            initial_bankroll=1000_00,
            strategy=ZeroTrendStrategy(base_bet=100, zero_threshold=5, history_size=100),
        ),
        Player(
            player_id="enhanced_zero",
            initial_bankroll=1000_00,
            strategy=EnhancedZeroTrendStrategy(base_bet=100, zero_threshold=5, history_size=100),
        ),
    ]

    for player in players:
        casino.add_player(player)

    print("Starting strategy comparison...")
    for round_num in range(1, num_rounds + 1):
        casino.assign_players()
        results = casino.simulate_round()
        print_round_results(round_num, results)

    print("\nSimulation finished!")


if __name__ == "__main__":
    run_strategy_comparison(num_rounds=5000)