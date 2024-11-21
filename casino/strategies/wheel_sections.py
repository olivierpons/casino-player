from typing import List
from .base import Strategy, PlacedBet


class WheelSectionsStrategy(Strategy):
    """
    Wheel Sections strategy:
    Bets on 'Tier du Cylindre' (12 numbers) and 'Orphelins' (8 numbers)
    covering a total of 20 numbers on the wheel.
    """

    def __init__(self, base_bet: int = 100, max_progression: int = 4):
        super().__init__(base_bet, max_progression)
        self.tier_numbers = {27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33}  # 12 numbers
        self.orphans_numbers = {1, 20, 14, 31, 9, 17, 34, 6}  # 8 numbers
        self.current_focus = "tier"  # Alternates between "tier" and "orphans"

    def calculate_bets(self) -> List[PlacedBet]:
        """Calculate bets focusing alternately on Tier and Orphans"""
        multiplier = min(2**self.consecutive_losses, 2**self.max_progression)
        current_bet = int(self.base_bet * multiplier)
        current_bet_div_12 = self.validate_bet_amount(current_bet // 12)
        current_bet_div_8 = self.validate_bet_amount(current_bet // 8)

        bets = []
        # Main bet
        if current_bet_div_12 and self.current_focus == "tier":
            for num in self.tier_numbers:
                bets.append(
                    PlacedBet(
                        bet_type=f"straight_{num}",
                        amount=current_bet_div_12,  # Split bet among tier numbers
                    )
                )
        elif current_bet_div_8:  # orphans
            for num in self.orphans_numbers:
                bets.append(
                    PlacedBet(
                        bet_type=f"straight_{num}",
                        amount=current_bet_div_8,  # Split bet among orphans numbers
                    )
                )

        return [bet for bet in bets if bet.amount > 0]

    def update_after_spin(self, *, won: bool, number: int):
        """Update strategy state and alternate between sections"""
        super().update_after_spin(won=won, number=number)

        if won:
            # Keep current focus if winning
            pass
        else:
            # Switch focus after loss
            self.current_focus = "orphans" if self.current_focus == "tier" else "tier"
