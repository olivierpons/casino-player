from collections import deque
from typing import List, Set

from .base import Strategy, PlacedBet


class SplitPatternStrategy(Strategy):
    """
    Split Pattern Strategy:
    Uses horizontal and vertical split bets in a pattern that follows
    recent hit concentrations on the table layout.
    """

    def __init__(
        self, base_bet: int = 100, max_progression: int = 4, history_size: int = 15
    ):
        super().__init__(base_bet, max_progression)
        self.history = deque(maxlen=history_size)
        self.pattern_index = 0
        # Définir les groupes de splits horizontaux et verticaux
        self.horizontal_splits = self._init_horizontal_splits()
        self.vertical_splits = self._init_vertical_splits()

    @staticmethod
    def _init_horizontal_splits() -> List[Set[int]]:
        """Initialize horizontal split groups"""
        splits = []
        for row in range(12):
            for col in range(2):
                num = row * 3 + col + 1
                splits.append({num, num + 1})
        return splits

    @staticmethod
    def _init_vertical_splits() -> List[Set[int]]:
        """Initialize vertical split groups"""
        splits = []
        for num in range(1, 34):
            splits.append({num, num + 3})
        return splits

    def _analyze_hot_zones(self) -> List[Set[int]]:
        """Analyze recent numbers to find hot zones"""
        if not self.history:
            return self.horizontal_splits[:4]  # Default start pattern

        # Count hits near each split
        split_scores = {}
        all_splits = self.horizontal_splits + self.vertical_splits

        for split in all_splits:
            score = 0
            for num in self.history:
                if num in split:
                    score += 2
                elif any(abs(num - split_num) <= 3 for split_num in split):
                    score += 1
            split_scores[frozenset(split)] = score

        # Select top scoring splits
        sorted_splits = sorted(split_scores.items(), key=lambda x: x[1], reverse=True)
        return [set(split) for split, _ in sorted_splits[:4]]

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate split bets based on pattern analysis"""
        # Get current hot zones
        active_splits = self._analyze_hot_zones()

        # Calculate progressive bet size
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        current_bet = int(self.base_bet * multiplier)

        # Distribute bets across active splits
        bet_per_split = self.validate_bet_amount(current_bet // len(active_splits))

        bets = []
        if bet_per_split > 0:
            for split in active_splits:
                split_list = sorted(split)
                if len(split_list) == 2:  # Valid split
                    # Determine if horizontal or vertical split
                    if split_list[1] - split_list[0] == 1:  # Horizontal
                        bet_type = f"split_h_{split_list[0]}_{split_list[1]}"
                    else:  # Vertical
                        bet_type = f"split_v_{split_list[0]}_{split_list[1]}"

                    bets.append(PlacedBet(bet_type=bet_type, amount=bet_per_split))

        return [bet for bet in bets if bet.amount > 0]

    def update_after_spin(self, *, won: bool, number: int):
        """Update strategy state and pattern analysis"""
        super().update_after_spin(won=won, number=number)

        if number is not None:
            self.history.append(number)
            if not won:
                # Rotate pattern after loss
                self.pattern_index = (self.pattern_index + 1) % 4
