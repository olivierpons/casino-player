from typing import Dict

from tabulate import tabulate

from casino.player import Player
from casino.strategies.adaptive_distribution import AdaptiveDistributionStrategy
from casino.strategies.column_pattern import ColumnPatternStrategy
from casino.strategies.corner_momentum import CornerMomentumStrategy
from casino.strategies.dalembert import DAlembertStrategy
from casino.strategies.dynamic_sectors import DynamicSectorsStrategy
from casino.strategies.enhanced_zero_trend import EnhancedZeroTrendStrategy
from casino.strategies.fibonacci import FibonacciStrategy
from casino.strategies.hot_cold_sectors import HotColdSectorsStrategy
from casino.strategies.hybrid_martingale import HybridMartingaleStrategy
from casino.strategies.james_bond import JamesBondStrategy
from casino.strategies.labouchere import LabouchereStrategy
from casino.strategies.martingale import MartingaleStrategy
from casino.strategies.multi_pattern import MultiPatternStrategy
from casino.strategies.opposite_sectors import OppositeSectorsStrategy
from casino.strategies.paroli import ParoliStrategy
from casino.strategies.progressive_coverage import ProgressiveCoverageStrategy
from casino.strategies.sector_chain import SectorChainStrategy
from casino.strategies.sequence import SequenceStrategy
from casino.strategies.split_pattern import SplitPatternStrategy
from casino.strategies.thirds_coverage import ThirdsCoverageStrategy
from casino.strategies.wheel_sections import WheelSectionsStrategy

from casino.strategies.zero_always import ZeroAlwaysStrategy
from casino.strategies.zero_and_half import ZeroAndHalfStrategy
from casino.strategies.zero_simple import ZeroSimpleStrategy
from casino.strategies.zero_timeout import ZeroTimeoutStrategy
from casino.strategies.zero_trend import ZeroTrendStrategy
from casino.table import Casino
from roulette_table import RouletteTable


def seconds_to_hms(seconds: int) -> str:
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def print_round_results(round_number: int, results: Dict[str, any]):

    def get_payout_type(bet_type: str) -> str:
        category = bet_type.split("_")[0]
        if category in ["black", "red"]:
            return "color"
        if category in ["even", "odd"]:
            return "even_odd"
        if category in ["low", "high"]:
            return "half"
        if category in ["first", "second", "third"]:
            return "dozen"
        return category

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
    if winning_number in red_numbers:
        number_display = f"Red {winning_number} 🔴"
    elif winning_number in black_numbers:  # black numbers
        number_display = f"Black {winning_number} ⚪"
    else:
        number_display = f"Zero {winning_number} 🎯"

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
    print(
        f"=== Round {round_number:3d} "
        f"({seconds_to_hms(round_number * 40)}) : "
        f"{number_display} {' '.join(properties)} "
    )

    # Collect all data for tables with active players
    active_tables = []
    for table_id, table_results in results.items():
        if table_results["players_results"]:
            table_data = [
                [
                    "Player",
                    "Initial",
                    "Total P&L",
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
                        payout_multiplier = RouletteTable.PAYOUTS[
                            get_payout_type(bet.bet_type.split("_")[0])
                        ]

                        winnings = bet.amount * (payout_multiplier + 1)
                        winning_entries.append(
                            f"{bet.bet_type} <€{bet.amount/100:.2f}→€{winnings/100:.2f}×{payout_multiplier}>"
                        )
                    winning_str = "\n".join(winning_entries)

                # Format losing bets string with Unicode symbols
                losing_str = ""
                if losing_bets:
                    losing_entries = []
                    for bet in losing_bets:
                        losing_entries.append(f"{bet.bet_type} <€{bet.amount/100:.2f}>")
                    losing_str = "\n".join(losing_entries)

                # Get initial bankroll from stats
                initial_bankroll = stats["initial_bankroll"]

                # Calculate P&L (difference between current and initial bankroll)
                current_bankroll = stats["bankroll"]
                pnl = current_bankroll - initial_bankroll

                table_data.append(
                    [
                        player_id,
                        f"€{initial_bankroll/100:>10.2f}",
                        f"€{pnl/100:>+10.2f}" if pnl / 100 else "-",
                        f"€{current_bankroll/100:>10.2f}",
                        (
                            f"€{stats['total_bet']/100:>8.2f}"
                            if stats["total_bet"] / 100
                            else "-"
                        ),
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
    initial_bankroll: int = 74 * 100 * 3
    base_bet: int = 3_00
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
            strategy=SequenceStrategy("custom_sequence.json", base_bet=base_bet),
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
            player_id="enhanced zero",
            initial_bankroll=initial_bankroll,
            strategy=EnhancedZeroTrendStrategy(
                base_bet=base_bet, zero_threshold=5, history_size=100
            ),
        ),
        Player(
            player_id="zero wait 10",
            initial_bankroll=initial_bankroll,
            strategy=ZeroSimpleStrategy(base_bet=base_bet, wait_before_bet=10),
        ),
        Player(
            player_id="zero wait 30",
            initial_bankroll=initial_bankroll,
            strategy=ZeroSimpleStrategy(base_bet=base_bet, wait_before_bet=30),
        ),
        Player(
            player_id="zero wait 50",
            initial_bankroll=initial_bankroll,
            strategy=ZeroSimpleStrategy(base_bet=base_bet, wait_before_bet=50),
        ),
        Player(
            player_id="zero wait 80",
            initial_bankroll=initial_bankroll,
            strategy=ZeroSimpleStrategy(base_bet=base_bet, wait_before_bet=80),
        ),
        Player(
            player_id="james bond",
            initial_bankroll=initial_bankroll,
            strategy=JamesBondStrategy(base_bet=base_bet),
        ),
        Player(
            player_id="zero all time",
            initial_bankroll=initial_bankroll,
            strategy=ZeroAlwaysStrategy(base_bet=base_bet),
        ),
        Player(
            player_id="zero 2/3, half 1/3",
            initial_bankroll=initial_bankroll,
            strategy=ZeroAndHalfStrategy(
                base_bet=base_bet,
                max_progression=4,
                other="black",
                wait_before_bet=5,
                larger_on_zero=True,
            ),
        ),
        Player(
            player_id="zero 1/3, half 2/3",
            initial_bankroll=initial_bankroll,
            strategy=ZeroAndHalfStrategy(
                base_bet=base_bet,
                max_progression=4,
                other="black",
                wait_before_bet=5,
                larger_on_zero=False,
            ),
        ),
        Player(
            player_id="zero timeout",
            initial_bankroll=initial_bankroll,
            strategy=ZeroTimeoutStrategy(
                base_bet=base_bet,
                max_progression=4,
                wait_before_bet=5,
                max_rounds_without_zero=5,
                timeout_rounds=5,
            ),
        ),
        Player(
            player_id="wheel sections",
            initial_bankroll=initial_bankroll,
            strategy=WheelSectionsStrategy(base_bet=base_bet),
        ),
        Player(
            player_id="hot cold",
            initial_bankroll=initial_bankroll,
            strategy=HotColdSectorsStrategy(base_bet=base_bet, sector_size=5),
        ),
        Player(
            player_id="opposite sectors",
            initial_bankroll=initial_bankroll,
            strategy=OppositeSectorsStrategy(base_bet=base_bet),
        ),
        Player(
            player_id="column_pattern",
            initial_bankroll=initial_bankroll,
            strategy=ColumnPatternStrategy(base_bet=base_bet),
        ),
        Player(
            player_id="dynamic_sectors",
            initial_bankroll=initial_bankroll,
            strategy=DynamicSectorsStrategy(base_bet=base_bet),
        ),
        Player(
            player_id="progressive_coverage",
            initial_bankroll=initial_bankroll,
            strategy=ProgressiveCoverageStrategy(base_bet=base_bet),
        ),
        Player(
            player_id="split pattern",
            initial_bankroll=initial_bankroll,
            strategy=SplitPatternStrategy(base_bet=base_bet),
        ),
        Player(
            player_id="corner momentum",
            initial_bankroll=initial_bankroll,
            strategy=CornerMomentumStrategy(base_bet=base_bet, momentum_threshold=3),
        ),
        Player(
            player_id="multi pattern",
            initial_bankroll=initial_bankroll,
            strategy=MultiPatternStrategy(base_bet=base_bet, pattern_memory=30),
        ),
        Player(
            player_id="sector chain",
            initial_bankroll=initial_bankroll,
            strategy=SectorChainStrategy(base_bet=base_bet, chain_size=8),
        ),
        Player(
            player_id="hybrid martingale",
            initial_bankroll=initial_bankroll,
            strategy=HybridMartingaleStrategy(base_bet=base_bet),
        ),
        Player(
            player_id="adaptive distribution",
            initial_bankroll=initial_bankroll,
            strategy=AdaptiveDistributionStrategy(base_bet=base_bet),
        ),
    ]
    ids = set(p.player_id for p in players)
    if len(ids) != len(players):
        raise ValueError("Duplicate player IDs found!")

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


def run_multiple_simulations(num_simulations: int, num_rounds: int):
    """Run multiple simulations and collect statistics."""

    def _gen_players():
        return [
            Player(
                "martingale",
                initial_bankroll,
                MartingaleStrategy(base_bet=base_bet, max_progression=4),
            ),
            Player(
                "dalembert",
                initial_bankroll,
                DAlembertStrategy(base_bet=base_bet, max_progression=8),
            ),
            Player(
                "zero wait 10",
                initial_bankroll,
                ZeroSimpleStrategy(base_bet=base_bet, wait_before_bet=10),
            ),
            Player(
                "zero wait 30",
                initial_bankroll,
                ZeroSimpleStrategy(base_bet=base_bet, wait_before_bet=30),
            ),
            Player(
                "james bond", initial_bankroll, JamesBondStrategy(base_bet=base_bet)
            ),
            Player(
                "zero all time", initial_bankroll, ZeroAlwaysStrategy(base_bet=base_bet)
            ),
            Player(
                "zero and half",
                initial_bankroll,
                ZeroAndHalfStrategy(
                    base_bet=base_bet,
                    max_progression=4,
                    other="black",
                    wait_before_bet=5,
                ),
            ),
        ]

    initial_bankroll: int = 74 * 100 * 2
    base_bet: int = 3_00
    final_stats = {}
    for player in _gen_players():
        final_stats[player.player_id] = {
            "survived": 0,
            "avg_rounds": 0,
            "total_profit": 0,
        }

    for sim in range(num_simulations):
        casino = Casino()
        players = _gen_players()
        active_players = {p.player_id: True for p in players}
        for player in players:
            casino.add_player(player)

        round_num = 1
        while round_num <= num_rounds:
            casino.assign_players()

            # Track which players are still active
            for player in players:
                if player.should_leave():
                    active_players[player.player_id] = False
                else:
                    final_stats[player.player_id]["avg_rounds"] += 1

            # Check if any players remain
            if not any(active_players.values()) and not casino.waiting_players:
                break

            results_dict = casino.simulate_round()

            # Update profit tracking
            for table_results in results_dict.values():
                for player_id, stats in table_results.get(
                    "players_results", {}
                ).items():
                    final_stats[player_id]["total_profit"] += stats["profit"]

            round_num += 1

        # Record which strategies survived
        for player_id, active in active_players.items():
            if active:
                final_stats[player_id]["survived"] += 1

    # Calculate final statistics
    for strategy in final_stats:
        final_stats[strategy]["survival_rate"] = (
            final_stats[strategy]["survived"] / num_simulations
        ) * 100
        final_stats[strategy]["avg_rounds"] = (
            final_stats[strategy]["avg_rounds"] // num_simulations
        )
        final_stats[strategy]["avg_profit"] = final_stats[strategy]["total_profit"] / (
            num_simulations * 100
        )  # Convert to euros

    return final_stats


def print_simulation_results(results: dict):
    """Print formatted simulation results."""
    print("\nSimulation Results:")
    print("-" * 80)
    print(
        f"{'Strategy':<15} {'Survival %':>10} {'Avg Rounds':>12} {'Avg Profit €':>12}"
    )
    print("-" * 80)

    # Sort by survival rate
    sorted_results = sorted(
        results.items(), key=lambda x: x[1]["survival_rate"], reverse=True
    )

    for strategy, stats in sorted_results:
        print(
            f"{strategy:<15} {stats['survival_rate']:>10.2f} {stats['avg_rounds']:>12.0f} {stats['avg_profit']:>12.2f}"
        )


if __name__ == "__main__":
    # NUM_SIMULATIONS = 200
    # NUM_ROUNDS = 300
    #
    # print(f"Running {NUM_SIMULATIONS} simulations of {NUM_ROUNDS} rounds each...")
    # results = run_multiple_simulations(NUM_SIMULATIONS, NUM_ROUNDS)
    # print_simulation_results(results)
    run_strategy_comparison(num_rounds=300)
