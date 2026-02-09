# Vector Frogger River Cross

Navigate a frog across a busy river by jumping on moving logs and avoiding obstacles.

## Description

A focused river-crossing challenge where you control a frog starting at the bottom of the screen. The goal is to reach the goal area at the top while jumping on floating logs that move at different speeds and directions. Falling into the water costs a life.

## Rationale

This game focuses on timing and spatial reasoning. It provides a classic arcade challenge that is ideal for testing reinforcement learning agents' ability to predict moving patterns and execute precise movements.

## Details

The game area consists of:
- **Start Zone**: Bottom 2 rows (grass) - safe starting position
- **River Zone**: Middle 5 rows (rows 3-7) with floating logs moving horizontally at different speeds and directions
- **Safe Zone**: Row 2 (grass) - brief rest area
- **Goal Zone**: Top row - reaching this area grants points and resets position

Each successful crossing increases your score. Every 3 crossings increases the level, making logs move faster. If you stay on a log that moves off-screen, or jump into water (missing a log), you lose a life.

## Build

```bash
uv sync
```

## Run

```bash
uv run main.py
```

## Stop

Press `ESC` or close the window.

## How to Play

Use Arrow Keys to move the frog one grid square at a time:
- **UP/DOWN/LEFT/RIGHT** - Move frog

**Scoring:**
- +10 points each time you land on a log (once per jump)
- +100 points for reaching the goal area
- Level increases every 3 successful crossings (log speed increases)
- -10 penalty for losing a life

**Goal:** Reach the goal area as many times as possible. Game ends when all 3 lives are lost.

## AI Agent Input

For RL agent control:

**Observation Space:**
- 10x10 grid with categorical encoding:
  - 0: Empty/grass/safe zone
  - 1: Water
  - 2: Log (moving right)
  - 3: Log (moving left)
  - 4: Frog position
  - 5: Goal area

**Action Space:**
- Discrete: [UP, DOWN, LEFT, RIGHT]

**Reward Structure:**
- +10 for landing on a log (per jump)
- +100 for reaching goal
- -10 for death (falling in water or going off-screen)
- -0.1 per step (encourage efficiency)

## Project Structure

```
category/games/2026/02/20260209-043051-vector-frogger-river-cross/
├── main.py          - Entry point
├── game.py          - Main game loop and state management
├── entities.py      - Game objects (Frog, Log, Lane)
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 600x600
- **Frame Rate**: 60 FPS
- **Grid Size**: 60px (10 cols x 10 rows)
- **Input Type**: Discrete (Arrow keys)
- **Language**: Python 3.11+
- **Library**: pygame-ce
