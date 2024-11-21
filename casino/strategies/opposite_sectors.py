from typing import List, Set
from .base import Strategy, PlacedBet


class OppositeSectorsStrategy(Strategy):
    """
    Opposite Sectors strategy:
    Bets simultaneously on two opposite sectors of the wheel
    with dynamic adjustment based on results.
    """

    def __init__(self, base_bet: int = 100, max_progression: int = 4):
        super().__init__(base_bet, max_progression)
        # Define opposite sectors
        self.sector_pairs = [
            (set(range(1, 13)), set(range(25, 37))),  # 1-12 vs 25-36
            (set(range(13, 25)), set(range(1, 13))),  # 13-24 vs 1-12
            (set(range(25, 37)), set(range(13, 25))),  # 25-36 vs 13-24
        ]
        self.current_pair_index = 0
        self.consecutive_pair_losses = 0

    def _get_current_sectors(self) -> tuple[Set[int], Set[int]]:
        """Get the currently active sector pair"""
        return self.sector_pairs[self.current_pair_index]

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets on both sectors with progressive sizing"""
        sector1, sector2 = self._get_current_sectors()

        # Progressive betting based on consecutive losses
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        current_base = self.validate_bet_amount(int(self.base_bet * multiplier))
        if current_base == 0:
            return []

        # Split bet between sectors
        bets = [
            (
                PlacedBet(bet_type=f"first_dozen", amount=current_base)
                if sector1 == set(range(1, 13))
                else (
                    PlacedBet(bet_type=f"second_dozen", amount=current_base)
                    if sector1 == set(range(13, 25))
                    else PlacedBet(bet_type=f"third_dozen", amount=current_base)
                )
            ),
            (
                PlacedBet(bet_type=f"first_dozen", amount=current_base)
                if sector2 == set(range(1, 13))
                else (
                    PlacedBet(bet_type=f"second_dozen", amount=current_base)
                    if sector2 == set(range(13, 25))
                    else PlacedBet(bet_type=f"third_dozen", amount=current_base)
                )
            ),
        ]

        return bets

    def update_after_spin(self, *, won: bool, number: int):
        """Update strategy state and sector selection"""
        super().update_after_spin(won=won, number=number)

        if won:
            self.consecutive_pair_losses = 0
        else:
            self.consecutive_pair_losses += 1
            if self.consecutive_pair_losses >= 2:
                # Change sector pair after 2 consecutive losses
                self.current_pair_index = (self.current_pair_index + 1) % len(
                    self.sector_pairs
                )
                self.consecutive_pair_losses = 0
