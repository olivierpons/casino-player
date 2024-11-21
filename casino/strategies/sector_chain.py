from collections import deque
from typing import List, Set

from .base import Strategy, PlacedBet


class SectorChainStrategy(Strategy):
    """
    Sector Chain Strategy:
    Creates chains of connected sectors on the wheel, following the physical
    layout of the roulette wheel to identify potential 'hot chains' where
    the ball might be more likely to land based on mechanical bias.
    """

    def __init__(
        self,
        base_bet: int = 100,
        max_progression: int = 4,
        chain_size: int = 8,
        history_size: int = 30,
    ):
        super().__init__(base_bet, max_progression)
        self.chain_size = chain_size
        self.history = deque(maxlen=history_size)
        # fmt: off
        self.wheel_sequence = [
            0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23,
            10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26
        ]
        # fmt: on
        self.chains = self._initialize_chains()
        self.current_chain_index = 0
        self.chain_performance = {}

    def _initialize_chains(self) -> List[Set[int]]:
        """Initialize overlapping chains of sectors"""
        chains = []
        sequence_length = len(self.wheel_sequence)

        # Create overlapping chains around the wheel
        for start_idx in range(sequence_length):
            chain = set()
            for offset in range(self.chain_size):
                idx = (start_idx + offset) % sequence_length
                chain.add(self.wheel_sequence[idx])
            chains.append(chain)
        return chains

    def _analyze_chain_performance(self) -> int:
        """Analyze which chain has been most successful"""
        if not self.history:
            return 0

        # Count hits in each chain
        chain_hits = {i: 0 for i in range(len(self.chains))}
        for number in self.history:
            for chain_idx, chain in enumerate(self.chains):
                if number in chain:
                    chain_hits[chain_idx] += 1

        # Return the chain index with the lowest hits (cold sectors)
        return min(chain_hits.items(), key=lambda x: x[1])[0]

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets based on chain analysis"""
        # Update current chain if needed
        if self.consecutive_losses >= 2:
            self.current_chain_index = self._analyze_chain_performance()

        # Get current chain numbers
        active_numbers = self.chains[self.current_chain_index]

        # Progressive betting
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        total_bet = int(self.base_bet * multiplier)

        # Distribute bets using corners and dozens for better coverage
        bets = []
        covered_numbers = set()
        bet_amount_corner = self.validate_bet_amount(total_bet // 4)
        bet_amount_straight = self.validate_bet_amount(total_bet // 8)

        # Add corner bets where possible
        if bet_amount_corner:
            for row in range(11):
                for col in range(2):
                    corner_start = row * 3 + col + 1
                    corner_numbers = {
                        corner_start,
                        corner_start + 1,
                        corner_start + 3,
                        corner_start + 4,
                    }
                    if corner_numbers & active_numbers and corner_start <= 32:
                        bets.append(
                            PlacedBet(
                                bet_type=f"corner_{corner_start}",
                                amount=bet_amount_corner,
                            )
                        )
                        covered_numbers.update(corner_numbers)

        # Add straight bets for remaining numbers
        uncovered = active_numbers - covered_numbers
        if bet_amount_straight:
            for num in uncovered:
                bets.append(
                    PlacedBet(bet_type=f"straight_{num}", amount=bet_amount_straight)
                )

        return bets

    def update_after_spin(self, *, won: bool, number: int):
        """Update chain performance tracking"""
        super().update_after_spin(won=won, number=number)

        if number is not None:
            self.history.append(number)

            # Update chain performance metrics
            chain_hit = number in self.chains[self.current_chain_index]
            if self.current_chain_index not in self.chain_performance:
                self.chain_performance[self.current_chain_index] = []
            self.chain_performance[self.current_chain_index].append(chain_hit)

            # Trim performance history
            if len(self.chain_performance[self.current_chain_index]) > 10:
                self.chain_performance[self.current_chain_index].pop(0)
