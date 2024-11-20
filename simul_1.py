from dataclasses import dataclass
from typing import List, Dict, Set
import casino_player
from roulette_table import RouletteTable


@dataclass
class PlacedBet:
    bet_type: str
    amount: int  # Amount in cents


class ZeroNeighboursStrategy:
    """
    Strategy based on zero and its neighbours with different coverage levels
    depending on loss progression.
    """

    def __init__(self, initial_bankroll: int = 1000_00):
        self.table = RouletteTable()
        self.initial_bankroll = initial_bankroll
        self.current_bankroll = initial_bankroll
        self.consecutive_losses = 0
        self.base_bet = 100  # Base bet (100 cents = 1€)
        self.max_progression = 4

    def _calculate_progression_bet(self) -> int:
        """Calculate bet amount based on loss progression"""
        multiplier = min(2 ** self.consecutive_losses, 2 ** self.max_progression)
        return int(self.base_bet * multiplier)  # Ensure integer

    def calculate_bets(self) -> List[PlacedBet]:
        """
        Determine bets to place based on strategy and history
        Returns a list of all bets to place before the next spin
        """
        bets = []
        current_bet = self._calculate_progression_bet()

        # Base bet on zero
        bets.append(PlacedBet(bet_type="straight_0", amount=current_bet))

        # Add zero neighbours after first loss
        if self.consecutive_losses >= 1:
            bets.append(PlacedBet(bet_type="neighbours_0", amount=current_bet))

        # Add coverage bets after multiple losses
        if self.consecutive_losses >= 2:
            # Cover first dozen
            bets.append(PlacedBet(bet_type="first_dozen", amount=current_bet * 2))

        if self.consecutive_losses >= 3:
            # Add black coverage
            bets.append(PlacedBet(bet_type="black", amount=current_bet * 3))

        return bets

    def calculate_result(self, number: int, placed_bets: List[PlacedBet]) -> int:
        """
        Calculate total result for all placed bets

        Args:
            number: Winning number
            placed_bets: List of bets placed before the spin

        Returns:
            int: Total profit/loss in cents
        """
        total_profit = 0
        won_any = False

        for bet in placed_bets:
            if self.table.check_win(bet.bet_type, number):
                # Win!
                payout_multiplier = self.table.get_payout(bet.bet_type)
                # Convert float payout to cents and ensure integer
                profit = bet.amount + int(bet.amount * payout_multiplier)
                total_profit += profit
                won_any = True
            else:
                # Loss
                total_profit -= bet.amount

        # Update state
        if won_any:
            self.consecutive_losses = 0
        else:
            self.consecutive_losses = min(
                self.consecutive_losses + 1, self.max_progression
            )

        self.current_bankroll += total_profit
        return total_profit


def simulate_session(max_spins: int = 100):
    """
    Simulate a complete roulette session
    """
    table = RouletteTable()
    strategy = ZeroNeighboursStrategy(initial_bankroll=100_000)  # 1000€
    player = casino_player.Player(strategy.initial_bankroll)

    print("Starting simulation...")
    print(f"Initial bankroll: €{strategy.initial_bankroll/100:.2f}")

    for spin in range(max_spins):
        # Get bets for this round
        bets = strategy.calculate_bets()

        # Calculate total amount bet
        total_bet_amount = sum(bet.amount for bet in bets)

        # Check if enough bankroll
        if total_bet_amount > player.get_bankroll():
            print(f"\nStopping after {spin} spins: Insufficient bankroll")
            break

        # Spin the wheel
        winning_number = table.spin()

        # Calculate result
        total_profit = strategy.calculate_result(winning_number, bets)

        # Record result in player - ensure all values are integers
        player.add_game(int(total_profit), int(total_bet_amount), winning_number)

        # Display round result
        if spin % 10 == 0 or abs(total_profit) > 5000:  # €50
            print(f"\nSpin {spin + 1}:")
            print(f"Winning number: {winning_number}")
            print("Placed bets:")
            for bet in bets:
                print(f"  - {bet.bet_type}: €{bet.amount/100:.2f}")
            print(f"Result: €{total_profit/100:+.2f}")
            print(f"Bankroll: €{player.get_bankroll()/100:.2f}")

    # Display final statistics
    stats = player.get_stats()
    print("\nFinal session results:")
    print(f"Total spins played: {stats['total_games']}")
    print(f"Total profit: €{stats['total_profit']/100:+.2f}")
    print(f"Win rate: {stats['win_rate']:.1f}%")
    print(f"Biggest win: €{stats['max_profit']/100:.2f}")
    print(f"Biggest loss: €{stats['max_loss']/100:.2f}")
    print(f"Final bankroll: €{player.get_bankroll()/100:.2f}")


if __name__ == "__main__":
    simulate_session(max_spins=100)
