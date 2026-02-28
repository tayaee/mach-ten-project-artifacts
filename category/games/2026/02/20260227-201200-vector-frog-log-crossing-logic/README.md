# Vector Frog Log Crossing Logic

Cross the treacherous river by jumping on moving logs in this precision timing challenge.

## Description

This game focuses on rhythmic timing and spatial reasoning. It is designed for users who enjoy classic arcade mechanics and provides a clear state-space for reinforcement learning agents to master sequential decision-making.

The game consists of a 10x10 grid. The player starts at the bottom row (Safety Zone). Between the start and the goal (Top Row) is a river with 4 lanes of logs moving at different speeds and directions. Lane 1 and 3 move left, Lane 2 and 4 move right. If the player is on a log, they move with it. If the player falls into the water or moves off-screen, the game ends. The goal is to reach any tile in the top safety row.

## How to Build

```bash
uv venv
uv pip install pygame
```

## How to Start

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Play

Controls:
- Arrow keys (UP, DOWN, LEFT, RIGHT) to hop one grid cell at a time

Scoring:
- 10 points for each lane crossed for the first time
- 100 points for reaching the goal

Goal: Reach the top row while staying on the moving logs. Avoid the blue water tiles; only land on brown log tiles.

## How to Stop

Press ESC or close the window.

## How to Cleanup

```bash
rm -rf .venv
```

## Technical Specs

- Screen Resolution: 600x600
- Frame Rate: 30fps
- Grid Size: 60x60 pixels per cell
- Entity Types: Player, Log, Water, Goal

## Rules

- Movement: One cell per key press (Up, Down, Left, Right)
- Log Physics: Logs move periodically. Player position updates relative to log velocity while standing on one
- Win Condition: Reaching the top row (y=0)
- Lose Condition: Stepping on a Water tile or drifting outside the horizontal screen bounds (x < 0 or x > 9)

## Reward Function Info

For reinforcement learning:
- Step penalty: -0.1
- Death penalty: -100
- Goal reward: 500
- Forward progress reward: 20
