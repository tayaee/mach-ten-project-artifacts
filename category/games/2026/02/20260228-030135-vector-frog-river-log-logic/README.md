# Vector Frog River Log Logic

A precision-based puzzle platformer where you master river crossing by timing leaps across shifting logs.

## Description

Navigate a 10x10 grid from the bottom Safe Zone to the top Goal Zone. Between them lie 8 rows of river filled with moving logs of varying lengths (1-3 units) traveling at different speeds and directions. Each move is discrete and grid-based. Plan your path carefully - stepping on water ends the game, and riding a log off-screen is fatal.

## Features

- 10x10 grid-based movement
- 8 rows of river with logs of varying lengths (1-3 cells)
- Logs moving left or right at different constant speeds
- Horizontal velocity inheritance while standing on logs
- 60-second time limit per attempt
- Monochrome professional UI (Dark Grey and White)
- Scoring: +10 for advancing to new rows, +100 for reaching the Goal Zone

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Stop

Close the game window or press ESC.

## Controls

- **Up Arrow**: Move up one cell
- **Down Arrow**: Move down one cell
- **Left Arrow**: Move left one cell
- **Right Arrow**: Move right one cell
- **SPACE**: Retry after game over or win
- **ESC**: Quit the game

## Rules

- Start at the bottom row (Safe Zone)
- Reach any cell in the top row (Goal Zone) to win
- Stepping on Water (dark cells) ends the game
- When on a log, you move horizontally with it
- Moving off-screen while on a log ends the game
- 60 second time limit per attempt
- Score 10 points for first-time advancement to higher rows
- Score 100 points for reaching the Goal Zone

## How to Cleanup

```bash
rm -rf __pycache__
```
