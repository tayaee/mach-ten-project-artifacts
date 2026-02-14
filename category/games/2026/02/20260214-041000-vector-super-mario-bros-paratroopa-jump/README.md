# Vector Super Mario Bros Paratroopa Jump

Master the art of sequential paratroopa bouncing to reach the highest heights.

## Description

This game focuses on precise aerial movement and timing mechanics. The player controls a character on a single-screen course with multiple winged turtles (Paratroopas) hovering at varying heights and moving in predictable patterns (vertical or horizontal oscillations). The player must jump from one Paratroopa to another without touching the ground.

## Technical Details

- **Framework**: Pygame
- **Resolution**: 800x600
- **Gravity**: 0.5
- **Bounce Impulse**: -12

### State Space
- player_x, player_y
- player_vx, player_vy
- enemy_positions
- distance_to_nearest_enemy

### Action Space
- move_left
- move_right
- jump
- idle

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## How to Stop

Press ESC in the game window, or use:
```bash
kill $(pgrep -f main.py)
```

## How to Play

- Use **Left/Right Arrow keys** to move
- Press **Spacebar** to start and jump
- Land on top of a Paratroopa to bounce
- Each consecutive bounce awards points (100, 200, 400, 800, etc.)
- The goal is to accumulate the highest score before falling to the ground
- You cannot bounce off the same Paratroopa twice in a row
- Falling to the bottom or hitting a Paratroopa from the side/bottom results in game over

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Project Structure

```
category/games/2026/02/20260214-041000-vector-super-mario-bros-paratroopa-jump/
├── main.py              # Entry point
├── game.py              # Game loop and rendering
├── entities.py          # Player and Paratroopa classes
├── config.py            # Configuration constants
├── pyproject.toml       # Dependencies & build config
├── run.bat              # Windows run script
├── run.sh               # Linux/Mac run script
└── README.md            # This file
```
