# Vector Super Mario Bros Ghost House Logic

Navigate a shifting maze while avoiding invisible ghosts in this strategic platformer.

## Description

A 2D grid-based platformer set in a spooky mansion where you must find a hidden key and reach the exit door. Ghosts pursue you relentlessly, but they only move when you're not looking at them - face them to freeze them in place.

## Rationale

This game introduces complex spatial reasoning and memory challenges through shifting walls and invisible platforms. It provides a rigorous test for AI agents learning pathfinding under uncertainty, while remaining intuitive for players who enjoy classic puzzle-platformer mechanics.

## Game Mechanics

- **Shifting Walls**: Every 10 seconds, specific walls appear or disappear based on a fixed pattern
- **Boo-logic Enemies**: Ghosts only move toward you when facing away. When you face them, they turn transparent and stop moving
- **Invisible Platforms**: Certain platforms are only visible when within a 3-tile radius
- **Win Condition**: Collect the key and enter the door
- **Lose Condition**: Contact with a ghost or falling into a pit

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the convenience scripts:
- Windows: `run.bat`
- Unix/Linux: `./run.sh`

## How to Stop

Close the game window or press ESC.

## How to Play

**Goal**: Reach the exit door with the key.

**Controls**:
- Arrow keys for movement
- Space or Up arrow to jump
- R to restart

**Scoring**:
- +500 for collecting the key
- +1000 for exiting the level
- -10 per second to encourage speed

**Strategy**: Facing direction is critical - press the opposite arrow key to look at ghosts and stop their pursuit. Plan your route around shifting wall patterns.

## State Space for AI

```python
{
    "player_pos": [x, y],
    "ghost_positions": [[x1, y1], [x2, y2], [x3, y3]],
    "wall_state": "binary_mask",  # Current phase of shifting walls
    "has_key": "boolean",
    "door_location": [x, y],
    "visible_platforms": [[x, y], ...],
    "player_facing": "right/left"
}
```

## Project Structure

```
category/games/2026/02/20260210-215500-vector-super-mario-bros-ghost-house-logic/
├── main.py          - Entry point
├── game.py          - Main game loop and rendering
├── config.py        - Game constants and settings
├── entity.py        - Player, ghost, key, and door classes
├── level.py         - Level layout and shifting wall logic
├── pyproject.toml   - Dependencies
├── run.bat          - Windows run script
├── run.sh           - Unix run script
└── README.md        - This file
```

## Cleanup

```bash
rm -rf .venv && find . -type d -name "__pycache__" -exec rm -rf {} +
```
