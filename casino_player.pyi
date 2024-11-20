from typing import List, Dict, Union, Optional

class Player:
    """Roulette player object to track game history and statistics (all monetary values in cents)
    
    The Player class maintains a complete history of games played, including:
    - Results of each game (wins/losses)
    - Bet sizes
    - Numbers bet on
    - Current bankroll
    """

    def __init__(self, initial_bankroll: int = 100000) -> None:
        """Initialize a new Player with an optional initial bankroll.
        
        Args:
            initial_bankroll: Initial bankroll in cents (default: 100000 = 1000.00€)
        """
        ...

    def add_game(self, result: int, bet_size: int, number: int) -> None:
        """Add a game result with bet size and number.
        
        Args:
            result: Game result in cents (positive for wins, negative for losses)
            bet_size: Amount bet in cents
            number: Number bet on (0-36)
            
        Example:
            >>> player = Player(10000)  # Start with 100€
            >>> player.add_game(3500, 100, 17)  # Won 35€ on a 1€ bet on 17
        """
        ...

    def get_history(self) -> List[int]:
        """Get the complete history of game results.
        
        Returns:
            List of game results in cents (positive for wins, negative for losses)
            
        Example:
            >>> player.get_history()
            [3500, -100, 3500]  # Won 35€, lost 1€, won 35€
        """
        ...

    def get_bet_sizes(self) -> List[int]:
        """Get the history of bet sizes.
        
        Returns:
            List of bet amounts in cents
            
        Example:
            >>> player.get_bet_sizes()
            [100, 100, 100]  # Three bets of 1€ each
        """
        ...

    def get_numbers_bet(self) -> List[int]:
        """Get the history of numbers bet on.
        
        Returns:
            List of numbers bet on (0-36)
            
        Example:
            >>> player.get_numbers_bet()
            [17, 23, 17]  # Bet on 17, then 23, then 17 again
        """
        ...

    def get_bankroll(self) -> int:
        """Get current bankroll.
        
        Returns:
            Current bankroll in cents
            
        Example:
            >>> player.get_bankroll()
            16900  # 169.00€
        """
        ...

    def get_stats(self) -> Dict[str, Union[int, float]]:
        """Get comprehensive player statistics.
        
        Returns:
            Dictionary containing:
                - total_games (int): Total number of games played
                - total_profit (int): Total profit/loss in cents
                - max_profit (int): Maximum profit in a single game in cents
                - max_loss (int): Maximum loss in a single game in cents
                - wins (int): Number of winning games
                - win_rate (float): Percentage of games won
                
        Example:
            >>> player.get_stats()
            {
                'total_games': 3,
                'total_profit': 6900,
                'max_profit': 3500,
                'max_loss': -100,
                'wins': 2,
                'win_rate': 66.67
            }
        """
        ...