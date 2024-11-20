# Casino Player Statistics Tracker

A Python C extension module for tracking roulette player statistics with optimized memory management and performance.

## Overview

This module provides a `Player` class that efficiently tracks and analyzes roulette game sessions. All monetary values are stored in cents to ensure precise calculations and avoid floating-point arithmetic issues.

## Features

- Track game results, bet sizes, and numbers played
- Maintain a running bankroll
- Generate comprehensive statistics including:
  - Total number of games played
  - Total profit/loss
  - Maximum single-game profit
  - Maximum single-game loss
  - Win count and win rate percentage

## Technical Details

- Written in C for optimal performance
- Uses Python's C API for seamless integration
- Memory-efficient storage of game history
- All monetary values stored in cents for precision
- Type hints and documentation via .pyi stub file

## Building and Installing

### Option 1: Using the Python Script (Recommended)
```bash
# Make the script executable
chmod +x rebuild.py

# Run the build script
./rebuild.py
```

### Option 2: Using Make
```bash
# Build and install everything
make all

# OR step by step:
make clean    # Clean previous builds
make build    # Compile the extension
make install  # Install the package
make dev      # Build everything and run tests
```

### Option 3: Manual Installation
```bash
# Clean previous build artifacts
rm -rf build/ dist/ casino_player.egg-info/

# Build and install
python3 -m pip install -e .
```

## Usage Example

```python
from casino_player import Player

# Create a player with initial bankroll of $1000.00
player = Player(100000)  # Amount in cents

# Add game results (profit/loss in cents, bet size in cents, number bet)
player.add_game(3500, 100, 17)   # Won $35.00 on a $1.00 bet on number 17
player.add_game(-200, 200, 24)   # Lost $2.00 on a $2.00 bet on number 24

# Get statistics
stats = player.get_stats()
print(f"Total games: {stats['total_games']}")
print(f"Win rate: {stats['win_rate']}%")

# Access history
history = player.get_history()        # List of game results
bet_sizes = player.get_bet_sizes()    # List of bet amounts
numbers = player.get_numbers_bet()    # List of numbers played
bankroll = player.get_bankroll()      # Current bankroll
```

## Project Structure

- `roulette-player.c`: C source code for the extension module
- `casino_player.pyi`: Type hints and detailed documentation
- `test_memory.py`: Basic testing script
- `setup.py` and `setup.cfg`: Build configuration files
- `pyproject.toml`: Project metadata and build system requirements
- `rebuild.py`: Utility script for building and installing
- `Makefile`: Make commands for building and testing

## Development Tools

### rebuild.py
A Python script that automates the build process:
- Cleans old build artifacts
- Updates build tools
- Recompiles the extension
- Installs the package
- Runs tests
- Provides clear progress feedback

### Makefile
Provides common development commands:
- `make clean`: Remove build artifacts
- `make build`: Compile the extension
- `make install`: Install the package
- `make all`: Clean, build, and install
- `make dev`: Build everything and run tests
