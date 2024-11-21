from typing import Dict

from tabulate import tabulate

from casino.player import Player
from casino.strategies.dalembert import DAlembertStrategy
from casino.strategies.enhanced_zero_trend import EnhancedZeroTrendStrategy
from casino.strategies.fibonacci import FibonacciStrategy
from casino.strategies.james_bond import JamesBondStrategy
from casino.strategies.labouchere import LabouchereStrategy
from casino.strategies.martingale import MartingaleStrategy
from casino.strategies.paroli import ParoliStrategy
from casino.strategies.sequence import SequenceStrategy
from casino.strategies.thirds_coverage import ThirdsCoverageStrategy

from casino.strategies.zero_always import ZeroAlwaysStrategy
from casino.strategies.zero_simple import ZeroSimpleStrategy
from casino.strategies.zero_trend import ZeroTrendStrategy
from casino.table import Casino


def print_round_results(round_number: int, results: Dict[str, any]):
    """Print results of a casino round in a formatted table with compact bet details using UTF-8 symbols"""

    # Get winning number from first table (they all have the same winning number)
    winning_number = None
    for table_results in results.values():
        winning_number = table_results["winning_number"]
        break

    # Define roulette number properties
    red_numbers = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    black_numbers = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}

    # Create number display with appropriate color and symbols
    if winning_number == 0:
        number_display = f"Zero {winning_number} 🎯"
    elif winning_number in red_numbers:
        number_display = f"Red {winning_number} 🔴"
    else:  # black numbers
        number_display = f"Black {winning_number} ⚪"

    # Additional properties
    properties = []
    if winning_number != 0:
        # Even/Odd
        properties.append("Even ↻" if winning_number % 2 == 0 else "Odd ↺")
        # High/Low
        properties.append("High △" if winning_number >= 19 else "Low ▽")
        # Dozen
        if winning_number <= 12:
            properties.append("1st dozen 1️⃣")
        elif winning_number <= 24:
            properties.append("2nd dozen 2️⃣")
        else:
            properties.append("3rd dozen 3️⃣")

    # Print round header with winning number and properties
    print(f"=== Round {round_number:3d} : {number_display} {' '.join(properties)} ")

    # Collect all data for tables with active players
    active_tables = []
    for table_id, table_results in results.items():
        if table_results["players_results"]:
            table_data = [
                [
                    "Player",
                    "Initial",
                    "P&L",
                    "Current",
                    "Total Bet",
                    "Profit",
                    "Winning Bets",
                    "Losing Bets",
                ],
            ]

            # Add player data
            for player_id, stats in table_results["players_results"].items():
                winning_bets = stats.get("winning_bets", [])
                losing_bets = stats.get("losing_bets", [])

                # Format winning bets string with Unicode symbols
                winning_str = ""
                if winning_bets:
                    winning_entries = []
                    for bet in winning_bets:
                        payout_multiplier = {
                            "straight_0": 35,
                            "split": 17,
                            "street": 11,
                            "corner": 8,
                            "first_dozen": 2,
                            "second_dozen": 2,
                            "third_dozen": 2,
                            "odd": 1,
                            "even": 1,
                            "red": 1,
                            "black": 1,
                            "first_half": 1,
                            "second_half": 1,
                        }.get(bet.bet_type, 1)

                        winnings = bet.amount * (payout_multiplier + 1)
                        winning_entries.append(
                            f"{bet.bet_type}[€{bet.amount/100:.2f}→€{winnings/100:.2f}×{payout_multiplier}]"
                        )
                    winning_str = ", ".join(winning_entries)

                # Format losing bets string with Unicode symbols
                losing_str = ""
                if losing_bets:
                    losing_entries = []
                    for bet in losing_bets:
                        losing_entries.append(
                            f"{bet.bet_type}<€{bet.amount/100:.2f}>"
                        )
                    losing_str = ", ".join(losing_entries)

                # Get initial bankroll from stats
                initial_bankroll = stats["initial_bankroll"]

                # Calculate P&L (difference between current and initial bankroll)
                current_bankroll = stats["bankroll"]
                pnl = current_bankroll - initial_bankroll

                table_data.append(
                    [
                        player_id,
                        f"€{initial_bankroll/100:>10.2f}",
                        f"€{pnl/100:>+10.2f}",
                        f"€{current_bankroll/100:>10.2f}",
                        f"€{stats['total_bet']/100:>8.2f}",
                        f"€{stats['profit']/100:>+8.2f}",
                        winning_str,
                        losing_str,
                    ]
                )

            active_tables.append(table_data)

    # Print each table's results with nice formatting
    for table_data in active_tables:
        print(
            tabulate(
                table_data,
                headers="firstrow",
                tablefmt="psql",
                colalign=(
                    "right",
                    "right",
                    "right",
                    "right",
                    "right",
                    "right",
                    "left",
                    "left",
                ),
            )
        )


def run_strategy_comparison(*, num_rounds: int):
    initial_bankroll: int = 37 * 5_00
    base_bet: int = 4_00
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
            initial_bankroll=initial_bankroll,
            strategy=MartingaleStrategy(base_bet=base_bet, max_progression=4),
        ),
        Player(
            player_id="dalembert",
            initial_bankroll=initial_bankroll,
            strategy=DAlembertStrategy(base_bet=base_bet, max_progression=8),
        ),
        Player(
            player_id="paroli",
            initial_bankroll=initial_bankroll,
            strategy=ParoliStrategy(base_bet=base_bet, max_progression=3),
        ),
        Player(
            player_id="sequence",
            initial_bankroll=initial_bankroll,
            strategy=SequenceStrategy("custom_sequence.json", base_bet=1_00),
        ),
        Player(
            player_id="zero",
            initial_bankroll=initial_bankroll,
            strategy=ZeroTrendStrategy(
                base_bet=base_bet, zero_threshold=5, history_size=100
            ),
        ),
        Player(
            player_id="fibonacci",
            initial_bankroll=initial_bankroll,
            strategy=FibonacciStrategy(base_bet=base_bet, max_progression=4),
        ),
        Player(
            player_id="labouchere",
            initial_bankroll=initial_bankroll,
            strategy=LabouchereStrategy(
                base_bet=base_bet, sequence_length=6, bet_type="red"
            ),
        ),
        Player(
            player_id="thirds coverage",
            initial_bankroll=initial_bankroll,
            strategy=ThirdsCoverageStrategy(base_bet=base_bet, max_progression=4),
        ),
        Player(
            player_id="enhanced_zero",
            initial_bankroll=initial_bankroll,
            strategy=EnhancedZeroTrendStrategy(
                base_bet=base_bet, zero_threshold=5, history_size=100
            ),
        ),
        Player(
            player_id="zero_simple",
            initial_bankroll=initial_bankroll,
            strategy=ZeroSimpleStrategy(base_bet=base_bet, zero_threshold=10),
        ),
        Player(
            player_id="james bond",
            initial_bankroll=initial_bankroll,
            strategy=JamesBondStrategy(base_bet=base_bet),
        ),
        Player(
            player_id="olivier : zero_always",
            initial_bankroll=initial_bankroll,
            strategy=ZeroAlwaysStrategy(base_bet=2_00),
        ),
    ]

    for player in players:
        casino.add_player(player)

    print("Starting strategy comparison...")
    round_num = 1
    while round_num <= num_rounds:
        casino.assign_players()

        # Check if there are any active players
        has_active_players = False
        for table in casino.tables:
            if table.current_players:
                has_active_players = True
                break

        # If no active players and no waiting players, stop the simulation
        if not has_active_players and not casino.waiting_players:
            print("Simulation stopped: No more active players!")
            break

        results = casino.simulate_round()
        print_round_results(round_num, results)
        round_num += 1

    print("Simulation finished!")
    print(f"Completed rounds: {round_num - 1}")


if __name__ == "__main__":
    run_strategy_comparison(num_rounds=300)
