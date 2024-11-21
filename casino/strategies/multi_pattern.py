from typing import List, Set, Dict
from collections import deque
from .base import Strategy, PlacedBet


class MultiPatternStrategy(Strategy):
    """
    Multi Pattern Strategy:
    Combines multiple bet types based on pattern recognition,
    dynamically adjusting bet distribution based on success rates.
    """

    def __init__(
        self, base_bet: int = 100, max_progression: int = 4, pattern_memory: int = 30
    ):
        super().__init__(base_bet, max_progression)
        self.pattern_memory = pattern_memory
        self.history = deque(maxlen=pattern_memory)
        self.pattern_results = {
            "color": deque(maxlen=pattern_memory),
            "dozen": deque(maxlen=pattern_memory),
            "column": deque(maxlen=pattern_memory),
            "split": deque(maxlen=pattern_memory),
        }
        self.bet_weights = {"color": 0.3, "dozen": 0.3, "column": 0.2, "split": 0.2}

    def _analyze_color_pattern(self) -> str:
        """Analyze color pattern"""
        red_numbers = {
            1,
            3,
            5,
            7,
            9,
            12,
            14,
            16,
            18,
            19,
            21,
            23,
            25,
            27,
            30,
            32,
            34,
            36,
        }
        red_count = sum(1 for num in self.history if num in red_numbers)
        black_count = sum(
            1 for num in self.history if num > 0 and num not in red_numbers
        )
        return "red" if red_count < black_count else "black"

    def _analyze_dozen_pattern(self) -> str:
        """Analyze dozen pattern"""
        dozens = {"first_dozen": 0, "second_dozen": 0, "third_dozen": 0}
        for num in self.history:
            if num > 0:
                if num <= 12:
                    dozens["first_dozen"] += 1
                elif num <= 24:
                    dozens["second_dozen"] += 1
                else:
                    dozens["third_dozen"] += 1
        return min(dozens.items(), key=lambda x: x[1])[0]

    def _analyze_column_pattern(self) -> str:
        """Analyze column pattern"""
        columns = {1: 0, 2: 0, 3: 0}
        for num in self.history:
            if num > 0:
                col = (num - 1) % 3 + 1
                columns[col] += 1
        coldest_column = min(columns.items(), key=lambda x: x[1])[0]
        return f"column_{coldest_column}"

    def _analyze_split_pattern(self) -> str:
        """Analyze split pattern"""
        recent_numbers = list(self.history)[-5:]
        if not recent_numbers:
            return "split_h_1_2"

        # Find most recent non-zero number
        last_num = next((num for num in reversed(recent_numbers) if num > 0), 1)
        row = (last_num - 1) // 3
        col = (last_num - 1) % 3

        # Create horizontal split if possible
        if col < 2:
            return f"split_h_{last_num}_{last_num + 1}"
        # Create vertical split if possible
        if row < 11:
            return f"split_v_{last_num}_{last_num + 3}"
        return "split_h_1_2"  # Default fallback

    def _update_weights(self):
        """Update bet weights based on pattern success rates"""
        if not any(self.pattern_results.values()):
            return

        success_rates = {}
        for pattern_type, results in self.pattern_results.items():
            if results:
                success_rates[pattern_type] = sum(results) / len(results)
            else:
                success_rates[pattern_type] = 0.25

        # Normalize weights
        total_rate = sum(success_rates.values())
        if total_rate > 0:
            for pattern_type in self.bet_weights:
                self.bet_weights[pattern_type] = (
                    success_rates[pattern_type] / total_rate
                )

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets using multiple patterns"""
        # Base progressive bet
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        current_bet = int(self.base_bet * multiplier)

        bets = []
        patterns = {
            "color": self._analyze_color_pattern(),
            "dozen": self._analyze_dozen_pattern(),
            "column": self._analyze_column_pattern(),
            "split": self._analyze_split_pattern(),
        }

        for pattern_type, bet_type in patterns.items():
            bet_amount = int(current_bet * self.bet_weights[pattern_type])
            if bet_amount > 0:
                bets.append(PlacedBet(bet_type=bet_type, amount=bet_amount))

        return bets

    def update_after_spin(self, *, won: bool, number: int):
        """Update pattern tracking and weights"""
        super().update_after_spin(won=won, number=number)

        if number is not None:
            self.history.append(number)

            # Track success of each pattern type
            if self.history:
                self.pattern_results["color"].append(1 if won else 0)
                self.pattern_results["dozen"].append(1 if won else 0)
                self.pattern_results["column"].append(1 if won else 0)
                self.pattern_results["split"].append(1 if won else 0)

                # Update weights based on pattern success
                self._update_weights()
