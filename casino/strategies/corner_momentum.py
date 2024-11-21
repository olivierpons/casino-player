from typing import List, Set, Dict
from collections import deque
from .base import Strategy, PlacedBet


class CornerMomentumStrategy(Strategy):
    """
    Corner Momentum Strategy:
    Tracks momentum of different quadrants of the table and
    places corner bets in areas showing strong patterns.
    """

    def __init__(
        self,
        base_bet: int = 100,
        max_progression: int = 4,
        momentum_threshold: int = 3,
        history_size: int = 20,
    ):
        super().__init__(base_bet, max_progression)
        self.momentum_threshold = momentum_threshold
        self.history = deque(maxlen=history_size)
        self.corners = self._initialize_corners()
        self.quadrants = self._initialize_quadrants()
        self.active_corners: Set[str] = set()

    @staticmethod
    def _initialize_corners() -> Dict[str, Set[int]]:
        """Initialize all possible corner bets"""
        corners = {}
        for row in range(11):
            for col in range(2):
                num = row * 3 + col + 1
                corner_key = f"{num}"
                corners[corner_key] = {num, num + 1, num + 3, num + 4}
        return corners

    @staticmethod
    def _initialize_quadrants() -> Dict[str, Set[int]]:
        """Initialize table quadrants for momentum tracking"""
        return {
            "top_left": set(range(1, 10)),
            "top_right": set(range(10, 19)),
            "bottom_left": set(range(19, 28)),
            "bottom_right": set(range(28, 37)),
        }

    @staticmethod
    def _get_corner_key(number: int) -> str:
        """Get the corner key for a given number"""
        if number < 1 or number > 36:
            return ""
        row = (number - 1) // 3
        col = (number - 1) % 3
        if col < 2 and row < 11:
            return f"{row * 3 + col + 1}"
        return ""

    def _analyze_momentum(self) -> List[str]:
        """Analyze quadrant momentum and select best corners"""
        if not self.history:
            return []

        # Count quadrant hits
        quadrant_hits = {name: 0 for name in self.quadrants}
        for num in self.history:
            for quad_name, quad_numbers in self.quadrants.items():
                if num in quad_numbers:
                    quadrant_hits[quad_name] += 1

        # Find hot quadrants
        hot_quadrants = [
            quad
            for quad, hits in quadrant_hits.items()
            if hits >= self.momentum_threshold
        ]

        # Select corners in hot quadrants
        selected_corners = []
        for quad in hot_quadrants:
            quad_numbers = self.quadrants[quad]
            for corner_key, corner_numbers in self.corners.items():
                if (
                    len(corner_numbers & quad_numbers) >= 2
                ):  # At least 2 numbers in hot quadrant
                    selected_corners.append(corner_key)

        return selected_corners[:4]  # Limit to top 4 corners

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate corner bets based on momentum analysis"""
        # Update active corners based on momentum
        active_corners = self._analyze_momentum()

        if not active_corners:
            # Default to corners around most recent numbers if no momentum
            recent_corners = set()
            for num in list(self.history)[-3:]:
                corner_key = self._get_corner_key(num)
                if corner_key:
                    recent_corners.add(corner_key)
            active_corners = list(recent_corners)[:4]

        # Calculate progressive bet size
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        current_bet = int(self.base_bet * multiplier)

        # Distribute bets across active corners
        bet_per_corner = current_bet // max(len(active_corners), 1)

        return [
            PlacedBet(bet_type=f"corner_{corner}", amount=bet_per_corner)
            for corner in active_corners
            if bet_per_corner > 0
        ]

    def update_after_spin(self, *, won: bool, number: int):
        """Update strategy state and momentum tracking"""
        super().update_after_spin(won=won, number=number)

        if number is not None:
            self.history.append(number)
            # Reset if we hit zero
            if number == 0:
                self.active_corners.clear()
