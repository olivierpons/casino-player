from typing import List, Dict, Set
from collections import deque
from .base import Strategy, PlacedBet


class HotColdSectorsStrategy(Strategy):
    """
    Hot Cold Sectors strategy:
    Tracks hot and cold sectors on the wheel and progressively
    bets on neighbors of numbers that haven't hit recently.
    """

    def __init__(
        self,
        base_bet: int = 100,
        max_progression: int = 4,
        sector_size: int = 5,
        history_size: int = 50,
    ):
        super().__init__(base_bet, max_progression)
        self.sector_size = sector_size
        self.history = deque(maxlen=history_size)
        self.sectors: Dict[int, Set[int]] = self._initialize_sectors()
        self.current_sector = None

    def _initialize_sectors(self) -> Dict[int, Set[int]]:
        """Initialize wheel sectors based on physical layout"""
        wheel_sequence = [
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

        sectors = {}
        sequence_length = len(wheel_sequence)
        for i in range(37):
            idx = wheel_sequence.index(i)
            # Calculate start and end indices with wrap-around
            start_idx = (idx - self.sector_size // 2) % sequence_length
            end_idx = (idx + self.sector_size // 2 + 1) % sequence_length

            # Handle wrap-around case
            if start_idx <= end_idx:
                sector_numbers = wheel_sequence[start_idx:end_idx]
            else:
                sector_numbers = wheel_sequence[start_idx:] + wheel_sequence[:end_idx]

            sectors[i] = set(sector_numbers)

            # Ensure each sector has at least the center number
            sectors[i].add(i)

        return sectors

    def _analyze_cold_sectors(self) -> int:
        """Find the coldest sector (least frequent numbers)"""
        if not self.history:
            return 0

        sector_hits = {num: 0 for num in range(37)}
        for num in self.history:
            for sector_center, sector_nums in self.sectors.items():
                if num in sector_nums:
                    sector_hits[sector_center] += 1

        # Return center of sector with least hits
        return min(sector_hits.items(), key=lambda x: x[1])[0]

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets based on cold sector analysis"""
        if not self.current_sector:
            self.current_sector = self._analyze_cold_sectors()

        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        current_bet = int(self.base_bet * multiplier)

        # Bet on all numbers in the cold sector
        sector_numbers = self.sectors[self.current_sector]
        if not sector_numbers:  # Safety check
            sector_numbers = {self.current_sector}

        bet_per_number = current_bet // len(sector_numbers)

        return [
            PlacedBet(bet_type=f"straight_{num}", amount=bet_per_number)
            for num in sector_numbers
            if bet_per_number > 0
        ]

    def update_after_spin(self, *, won: bool, number: int):
        """Update history and sector analysis"""
        super().update_after_spin(won=won, number=number)

        if number is not None:
            self.history.append(number)

        if not won:
            # Change sector after loss
            self.current_sector = self._analyze_cold_sectors()
