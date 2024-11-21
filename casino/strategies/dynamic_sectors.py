from typing import List, Set, Dict
from collections import deque
from .base import Strategy, PlacedBet


class DynamicSectorsStrategy(Strategy):
    """
    Dynamic Sectors Strategy:
    Dynamically adjusts betting sectors based on recent number distributions
    and wheel momentum analysis.
    """

    def __init__(
        self, base_bet: int = 100, max_progression: int = 4, momentum_size: int = 8
    ):
        super().__init__(base_bet, max_progression)
        self.momentum_size = momentum_size
        self.history = deque(maxlen=20)
        self.wheel_sequence = [
            0,
            32,
            15,
            19,
            4,
            21,
            2,
            25,
            17,
            34,
            6,
            27,
            13,
            36,
            11,
            30,
            8,
            23,
            10,
            5,
            24,
            16,
            33,
            1,
            20,
            14,
            31,
            9,
            22,
            18,
            29,
            7,
            28,
            12,
            35,
            3,
            26,
        ]
        self.current_focus = set()  # Current betting sector

    def _get_neighbors(self, number: int, radius: int = 2) -> Set[int]:
        """Get neighboring numbers on the wheel"""
        if number not in self.wheel_sequence:
            return set()

        idx = self.wheel_sequence.index(number)
        neighbors = set()
        for i in range(-radius, radius + 1):
            neighbor_idx = (idx + i) % len(self.wheel_sequence)
            neighbors.add(self.wheel_sequence[neighbor_idx])
        return neighbors

    def _analyze_momentum(self) -> Set[int]:
        """Analyze recent numbers to detect potential wheel momentum"""
        if len(self.history) < 2:
            return set()

        recent_numbers = list(self.history)[-self.momentum_size :]
        # Look for clusters in recent numbers
        all_neighbors = set()
        for num in recent_numbers:
            all_neighbors.update(self._get_neighbors(num))

        # Find numbers that appear more frequently in neighbors
        number_frequency = {n: 0 for n in range(37)}
        for num in all_neighbors:
            number_frequency[num] += 1

        # Select numbers with highest frequency
        sorted_numbers = sorted(
            number_frequency.items(), key=lambda x: x[1], reverse=True
        )
        return {num for num, freq in sorted_numbers[:6] if freq > 1}

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets based on momentum analysis"""
        # Update focus sector based on momentum
        momentum_sector = self._analyze_momentum()
        if momentum_sector:
            self.current_focus = momentum_sector
        elif not self.current_focus:
            # Default to zero and its neighbors if no momentum detected
            self.current_focus = self._get_neighbors(0, radius=3)

        # Calculate progressive bet size
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        current_bet = int(self.base_bet * multiplier)

        # Distribute bets across focus sector
        bet_per_number = current_bet // max(len(self.current_focus), 1)

        return [
            PlacedBet(bet_type=f"straight_{num}", amount=bet_per_number)
            for num in self.current_focus
            if bet_per_number > 0
        ]

    def update_after_spin(self, *, won: bool, number: int):
        """Update history and momentum analysis"""
        super().update_after_spin(won=won, number=number)
        if number is not None:
            self.history.append(number)

        # Reset focus after significant losses
        if self.consecutive_losses >= 3:
            self.current_focus = set()
