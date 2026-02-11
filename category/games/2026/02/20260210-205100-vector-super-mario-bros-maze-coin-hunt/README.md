# Vector Super Mario Bros Maze Coin Hunt

Navigate a dynamic Mario-themed maze to collect coins while avoiding patrolling Koopas in a race against time.

## Description

This app provides a focused environment for AI agents to learn spatial navigation and pathfinding within a constrained grid system. It targets developers and researchers interested in grid-based movement logic and collision avoidance in a classic arcade setting.

## Details

The game features a 2D grid-based maze inspired by Super Mario Bros. The player controls a Mario sprite that moves one tile at a time. The objective is to collect all 50 coins scattered throughout the maze. Two Koopa Troopa enemies move in predictable back-and-forth patterns, and touching them deducts a life. The maze layout is fixed but coin placement is randomized. The UI uses a monochrome high-contrast palette with simple vector shapes.

## Game Rules

| Setting | Value |
|---------|-------|
| Grid Size | 20x20 tiles |
| Win Condition | Collect all coins within the time limit |
| Lose Condition | Time runs out or player loses 3 lives |
| Scoring | 100 points per coin, 1000 bonus for completion |
| Time Limit | 120 seconds |

## Technical Specifications

- Language: Python 3.12+
- Graphics Library: pygame
- Resolution: 640x640
- Frame Rate: 60 FPS
- Action Space: Discrete(4) - [North, South, East, West]
- Observation Space: 2D integer array (0: empty, 1: wall, 2: player, 3: coin, 4: enemy)

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run python main.py
```

Or use the provided run scripts:
```bash
# Windows
run.bat

# Linux/macOS
./run.sh
```

## How to Stop

Press ESC or close the pygame window.

## How to Play

- Use Arrow Keys (Up, Down, Left, Right) to move the player
- Move onto a coin tile to collect it
- Avoid Koopa enemies patrolling the maze
- Collect all 50 coins before time runs out

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys | Move player |
| R | Restart game (after game over or win) |
| ESC | Quit |

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```
