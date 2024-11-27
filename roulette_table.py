import secrets
from typing import Dict, List, Set


class RouletteTable:
    """Implementation of a European roulette table with proper number sequence and bet types."""

    NUMBERS_SEQUENCE = [
        # fmt: off
        0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24,
        16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26,
        # fmt: on
    ]
    RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}
    BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}
    PAYOUTS = {
        "straight": 35,  # Straight up (single number)
        "split": 17,  # Split bet (2 numbers)
        "street": 11,  # Street bet (3 numbers)
        "corner": 8,  # Corner bet (4 numbers)
        "sixline": 5,  # Six line bet (6 numbers)
        "column": 2,  # Column bet (12 numbers)
        "dozen": 2,  # Dozen bet (12 numbers)
        "color": 1,  # Red/Black (18 numbers)
        "even_odd": 1,  # Even/Odd (18 numbers)
        "half": 1,  # 1-18/19-36 (18 numbers)
        "neighbours": 6,  # Neighbors
    }

    def __init__(self):
        self.current_number: int | None = None
        self._validate_wheel()
        self.bets: Dict[str, Set[int]] = {}
        self._initialize_bets()

    def _validate_wheel(self) -> None:
        if set(self.NUMBERS_SEQUENCE) != set(range(37)):
            raise ValueError("Invalid wheel sequence")
        if self.RED_NUMBERS & self.BLACK_NUMBERS:
            raise ValueError("Red and black numbers overlap")
        if self.RED_NUMBERS | self.BLACK_NUMBERS != set(range(1, 37)):
            raise ValueError("Missing numbers in red/black sets")

    def _initialize_bets(self) -> None:
        # Outside bets
        self._add_bet("red", self.RED_NUMBERS)
        self._add_bet("black", self.BLACK_NUMBERS)
        self._add_bet("even", set(range(2, 37, 2)))
        self._add_bet("odd", set(range(1, 37, 2)))
        self._add_bet("low", set(range(1, 19)))
        self._add_bet("high", set(range(19, 37)))

        # Dozens
        for i, name in enumerate(["first", "second", "third"]):
            self._add_bet(f"{name}_dozen", set(range(i * 12 + 1, (i + 1) * 12 + 1)))

        # Columns
        for i in range(3):
            self._add_bet(f"column_{i + 1}", set(range(i + 1, 37, 3)))

        self._initialize_inside_bets()
        self._initialize_neighbours()

    def _add_bet(self, name: str, numbers: Set[int]) -> None:
        self.bets[name] = numbers

    def _initialize_inside_bets(self) -> None:
        # Straight bets
        for number in range(37):
            self._add_bet(f"straight_{number}", {number})

        # Split bets
        for row in range(12):
            for col in range(2):
                num = row * 3 + col + 1
                self._add_bet(f"split_h_{num}_{num + 1}", {num, num + 1})
        for num in range(1, 34):
            self._add_bet(f"split_v_{num}_{num + 3}", {num, num + 3})

        # Street bets
        for row in range(12):
            start = row * 3 + 1
            self._add_bet(f"street_{start}", {start, start + 1, start + 2})

        # Corner bets
        for row in range(11):
            for col in range(2):
                num = row * 3 + col + 1
                self._add_bet(f"corner_{num}", {num, num + 1, num + 3, num + 4})

        # Six line bets
        for row in range(11):
            start = row * 3 + 1
            self._add_bet(f"sixline_{start}", set(range(start, start + 6)))

    def _initialize_neighbours(self) -> None:
        """
        Initialize neighbours bets based on the actual roulette wheel layout.
        Using the roulette table where each row represents a number (in the center/pink column)
        and its neighbours (all other numbers in the row).
        """
        # Définir la table des voisins complète
        neighbours_table = {
            0: [12, 35, 3, 26, 32, 15, 19, 4],
            1: [5, 24, 16, 33, 20, 14, 31, 9],
            2: [15, 19, 4, 21, 25, 17, 34, 6],
            3: [7, 28, 12, 35, 26, 0, 32, 15],
            4: [0, 32, 15, 19, 21, 2, 25, 17],
            5: [30, 8, 23, 10, 24, 16, 33, 1],
            6: [2, 25, 17, 34, 27, 13, 36, 11],
            7: [9, 22, 18, 29, 28, 12, 35, 3],
            8: [13, 36, 11, 30, 23, 10, 5, 24],
            9: [1, 20, 14, 31, 22, 18, 29, 7],
            10: [11, 30, 8, 23, 5, 24, 16, 33],
            11: [6, 27, 13, 36, 30, 8, 23, 10],
            12: [18, 29, 7, 28, 35, 3, 26, 0],
            13: [17, 34, 6, 27, 36, 11, 30, 8],
            14: [16, 33, 1, 20, 31, 9, 22, 18],
            15: [3, 26, 0, 32, 19, 4, 21, 2],
            16: [23, 10, 5, 24, 33, 1, 20, 14],
            17: [4, 21, 2, 25, 34, 6, 27, 13],
            18: [14, 31, 9, 22, 29, 7, 28, 12],
            19: [26, 0, 32, 15, 4, 21, 2, 25],
            20: [24, 16, 33, 1, 14, 31, 9, 22],
            21: [32, 15, 19, 4, 2, 25, 17, 34],
            22: [20, 14, 31, 9, 18, 29, 7, 28],
            23: [36, 11, 30, 8, 10, 5, 24, 16],
            24: [8, 23, 10, 5, 16, 33, 1, 20],
            25: [19, 4, 21, 2, 17, 34, 6, 27],
            26: [28, 12, 35, 3, 0, 32, 15, 19],
            27: [22, 18, 29, 7, 13, 36, 11, 30],
            28: [31, 9, 22, 18, 12, 35, 3, 26],
            29: [34, 6, 27, 13, 7, 28, 12, 35],
            30: [27, 13, 36, 11, 8, 23, 10, 5],
            31: [33, 1, 20, 14, 9, 22, 18, 29],
            32: [35, 3, 26, 0, 15, 19, 4, 21],
            33: [10, 5, 24, 16, 1, 20, 14, 31],
            34: [21, 2, 25, 17, 6, 27, 13, 36],
            35: [29, 7, 28, 12, 3, 26, 0, 32],
            36: [34, 6, 27, 13, 11, 30, 8, 23],
        }
        for _number, neighbours in neighbours_table.items():
            self._add_bet(f"neighbours_{_number}", set(neighbours))

    def spin(self) -> int:
        self.current_number = secrets.choice(self.NUMBERS_SEQUENCE)
        return self.current_number

    def get_payout(self, bet_type: str) -> int:
        bet_category = bet_type.split("_")[0]
        if bet_category == "straight":
            return RouletteTable.PAYOUTS["straight"]
        elif bet_category == "split":
            return RouletteTable.PAYOUTS["split"]
        elif bet_category == "street":
            return RouletteTable.PAYOUTS["street"]
        elif bet_category == "corner":
            return RouletteTable.PAYOUTS["corner"]
        elif bet_category == "sixline":
            return RouletteTable.PAYOUTS["sixline"]
        elif bet_category == "neighbours":
            return RouletteTable.PAYOUTS["neighbours"]
        elif bet_category in ["first", "second", "third"]:
            return RouletteTable.PAYOUTS["dozen"]
        elif bet_category == "column":
            return RouletteTable.PAYOUTS["column"]
        elif bet_category in ["red", "black"]:
            return RouletteTable.PAYOUTS["color"]
        elif bet_category in ["even", "odd"]:
            return RouletteTable.PAYOUTS["even_odd"]
        elif bet_category in ["low", "high"]:
            return RouletteTable.PAYOUTS["half"]
        else:
            raise ValueError(f"Unknown bet type: {bet_type}")

    def check_win(self, bet_type: str, number: int) -> bool:
        if bet_type not in self.bets:
            raise ValueError(f"Invalid bet type: {bet_type}")
        return number in self.bets[bet_type]

    def get_available_bets(self) -> List[str]:
        return list(self.bets.keys())
