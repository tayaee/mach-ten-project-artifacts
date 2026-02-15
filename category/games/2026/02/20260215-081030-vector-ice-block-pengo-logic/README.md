# Vector Ice Block Pengo Logic

Strategic ice-block sliding puzzle where you crush enemies and align goals.

## Description

A retro arcade puzzle game inspired by the classic Pengo. Navigate a 13x13 grid filled with ice blocks as a penguin character. Push ice blocks to slide them across the board - blocks continue sliding until they hit another block, a wall, or an enemy. Use this mechanic strategically to crush enemies between sliding blocks and walls.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## How to Stop

Press ESC key or close the window.

## How to Play

### Controls

- **Arrow Keys**: Move the penguin
- **R**: Restart game / Next level
- **ESC**: Quit

### Gameplay Tips

1. Move into ice blocks to push them - they slide until hitting an obstacle
2. Blocks that hit walls without crushing enemies will break (10 points)
3. Crush enemies between sliding blocks and walls for 400 points
4. Align the three diamond-shaped blocks in a row for a 5000 point bonus
5. Avoid direct contact with red enemies - you have 3 lives
6. Eliminate all enemies to clear the level and advance

## Technical Details

- **Language**: Python 3.12+
- **Framework**: Pygame
- **Resolution**: 640x480
- **Grid**: 13x13 cells

## State Space for RL

```
13x13 integer matrix:
0 = Empty
1 = Wall
2 = Ice Block
3 = Diamond Block
4 = Player
5 = Enemy
```

## Action Space for RL

```
0: Up
1: Down
2: Left
3: Right
```

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Project Structure

```
vector-ice-block-pengo-logic/
├── main.py           # Entry point
├── game.py           # Game implementation
├── config.py         # Configuration
├── appinfo.json      # Metadata
├── run.bat           # Windows run script
├── run.sh            # Linux/Mac run script
└── README.md         # This file
```
