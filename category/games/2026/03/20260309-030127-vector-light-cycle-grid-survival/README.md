# Vector Light Cycle Grid Survival

Navigate a high-speed light cycle and trap opponents with your energy trail in this neon grid arena.

## Description

A simplified top-down 2D version of a light cycle battle. The player controls a bike that moves continuously on a rectangular grid. As the bike moves, it leaves a solid energy trail (wall). If the player hits the edge of the screen or any energy trail (including their own), the game ends. To keep it simple for the initial version, the goal is to survive as long as possible while the game speed incrementally increases. The arena is a dark grid with high-contrast neon lines. No diagonal movement is allowed. The game state is updated at fixed time steps (frames), which can be adjusted to increase difficulty.

## Rationale

This game focuses on spatial awareness and predictive logic. It targets players who enjoy classic arcade snake-style mechanics with a competitive, high-stakes tactical twist. It is ideal for testing AI pathfinding and obstacle avoidance algorithms.

## Details

The game runs on an 800x600 pixel display with a 20-pixel grid (40x30 cells). The player starts at the center of the grid moving right. As the bike moves, it leaves a green trail that becomes a permanent obstacle. The game speed increases every 5 seconds from an initial 10 FPS up to a maximum of 30 FPS. Score is based on survival time (1 point per second).

## Build

```bash
uv sync
```

## Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## Stop

Press `ESC` or close the window.

## How to Play

Use Arrow Keys to control the bike's direction:
- **UP** - Move up
- **DOWN** - Move down
- **LEFT** - Move left
- **RIGHT** - Move right

The bike cannot turn 180 degrees instantly (e.g., if moving UP, DOWN is ignored).

**Scoring:**
- +1 point per second of survival

**Goal:** Survive as long as possible without hitting walls or your own trail.

**Restart:** Press `SPACE` after Game Over to restart.

## AI Agent Input

For RL agent control:

**State Space:**
- Grid coordinates (x, y): 40 cols x 30 rows = 1200 possible positions
- Trail positions: Set of coordinate tuples
- Bike head position: (x, y) coordinate
- Current direction: (dx, dy) vector

**Action Space:**
- 0: Up
- 1: Down
- 2: Left
- 3: Right

**Reward Structure:**
- Each step survived: +0.1
- Each second survived: +1
- Collision/Game Over: -100

**Observation Format:**
The game state can be represented as:
- 40x30 grid with binary encoding (0: empty, 1: trail)
- Plus head position and current direction vector

## Project Structure

```
category/games/2026/03/20260309-030127-vector-light-cycle-grid-survival/
├── main.py          - Entry point
├── game.py          - Main game loop and state management
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
├── run.bat          - Windows run script
├── run.sh           - Linux/Mac run script
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 800x600
- **Frame Rate**: 10 FPS (starts at 10, increases to 30 FPS over time)
- **Grid Size**: 20px (40 cols x 30 rows)
- **Input Type**: Discrete (Arrow keys)
- **Game Engine**: Pygame 2.0+
- **Colors**:
  - Background: Black (#000000)
  - Player: Green (#00FF00)
  - Trail: Dark Green (#008800)
  - Grid Lines: Dark Gray (#111111)
