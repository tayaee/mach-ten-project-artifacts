# Vector Connect Four Logic

**Category:** Games

**Description:** A minimalist strategic gravity-based vertical alignment puzzle.

## Rationale

This game targets players who enjoy turn-based strategy and pattern recognition. It provides a clean, professional environment for AI agents to learn minimax algorithms and spatial heuristics in a 2D grid environment.

## Details

The game is a simplified version of the classic Connect Four. It features a 7x6 vertical grid. Two players (User vs AI or AI vs AI) drop colored discs from the top into one of the seven columns. The disc occupies the lowest available space within the column due to gravity. The first player to form a horizontal, vertical, or diagonal line of four of their own discs wins the game. The interface uses a high-contrast monochromatic vector style for clarity.

## How to Build

```bash
uv venv
uv pip install pygame
```

Or simply run:
```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Unix: `run.sh`

## Controls

- **Mouse Click**: Drop piece in selected column
- **Number Keys (0-6)**: Drop piece in specific column
- **R**: Reset the game
- **A**: Toggle AI (default: ON)
- **Escape**: Quit the game

## How to Play

Goal: Connect four tokens in a row before your opponent.

Players take turns selecting a column index (0-6) using the mouse or number keys. The disc falls to the lowest available space due to gravity. The first to connect four tokens horizontally, vertically, or diagonally wins.

Scoring:
- Victory: +100 points
- Draw: +10 points each

AI agents should maximize the utility function based on board control and potential lines.

## Features

- User vs AI or AI vs AI gameplay
- Toggle AI on/off for two-player mode
- Animated piece dropping
- Score tracking across multiple games
- Clean vector graphics with high-contrast colors
- AI-friendly observation interface for reinforcement learning

## AI Integration

AI agents can interact with the game through the `Game` class:

- `get_observation()`: Returns current game state including board configuration
- `get_valid_actions()`: Returns list of valid columns to drop a piece
- `step(col)`: Execute a move and return reward/done status

### Observation Space

```python
{
    "board": List[List[int]],      # 6x7 matrix with player IDs (0=empty, 1=player1, 2=player2)
    "grid_cols": int,              # 7 columns
    "grid_rows": int,              # 6 rows
    "current_player": int,         # Current player (1 or 2)
    "game_state": str,             # "playing", "win", "draw", "ai_thinking"
    "player1_score": int,          # Player 1 total score
    "player2_score": int           # Player 2 total score
}
```

### Action Space

Actions are integers 0-6 representing the column to drop a piece.

### Reward Structure

- Winning: +100
- Draw: +10
- Invalid move: -10
- Opponent wins: -100

## How to Stop

Press ESC key or close the game window. For CLI termination, use Ctrl+C.

## How to Cleanup

```bash
rm -rf .venv && find . -type d -name '__pycache__' -exec rm -rf {} +
```

## Technical Specifications

- **Grid Size:** 7 columns x 6 rows
- **Win Condition:** 4 connected tokens (Horizontal, Vertical, Diagonal)
- **State Representation:** 2D integer array (0=empty, 1=player1, 2=player2)
- **Language:** Python 3.12+
- **Dependencies:** Pygame 2.5.0+
- **Dependency Management:** uv
- **Resolution:** 800x700
- **FPS:** 60
