# snake

Classic arcade game where you control a growing snake to eat food and avoid collisions.

## Overview

**Category:** games

**Description:** Navigate the snake to eat food, grow longer, and avoid hitting walls or yourself.

**Target Audience:** Casual players, AI/ML researchers (excellent for reinforcement learning with simple state space and clear reward structure)

## How It Works

- The snake moves continuously in the current direction
- Eat food (red circles) to grow longer and increase score
- Avoid hitting walls or the snake's own body
- Score increases by 10 for each food eaten
- Game ends on collision

## Project Structure

```
20260213-143000-snake/
├── main.py         # Game implementation with SnakeGame class
├── run.bat         # Windows launch script
├── run.sh          # Linux/Mac launch script
└── README.md       # This file
```

## How to Build

```bash
uv add --python 3.12 pygame
```

## How to Start

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

**Or directly:**
```bash
uv run --no-active --python 3.12 main.py
```

## How to Play

**Controls:**
- Arrow Keys or WASD: Change direction
- R: Restart after game over
- ESC: Quit game

**Scoring:**
- Eat food: +10 points
- Collision: Game over

## How to Stop

Press ESC or close the game window.

## How to Cleanup

```bash
# Remove virtual environment
rm -rf .venv

# Remove uv cache
uv cache clean
```

## AI/ML Integration

The game is designed for AI training:

- **State Space:** 20x20 grid, 4 discrete actions
- **Observation Methods:** `get_state()` (dict), `get_grid_state()` (2D array)
- **Reward Structure:** +10 (food), -10 (collision), 0 (move)
- **Headless Mode:** Initialize with `SnakeGame(render=False)` for training

Example AI usage:
```python
from main import SnakeGame, Direction

game = SnakeGame(render=False)
game.reset()

while not game.game_over:
    action = your_ai_model.get_action(game.get_state())
    reward, done, score = game.step(action)
```
