# Vector Super Mario Bros: Hammer Bro Dodge

Master the art of dodging the iconic Hammer Brother's erratic projectile arcs.

## Description

A precision timing game focused on surviving against the classic Hammer Brother enemy from Super Mario Bros. The Hammer Bro moves back and forth across platforms, tossing hammers in parabolic arcs that you must dodge to survive. The physics engine simulates gravity-affected trajectories with two distinct arc patterns: short-high throws and long-low throws. The enemy randomly switches between platforms and varies throw intervals to prevent predictable patterns.

## Specifications

- **Resolution:** 800x600
- **Frame Rate:** 60 FPS
- **Input:** Keyboard (Arrow keys + Spacebar)

## How to Build

```bash
uv sync
```

## How to Start

**Windows:**
```bash
.\run.bat
```

**Linux/Mac:**
```bash
chmod +x run.sh
./run.sh
```

## How to Stop

Press `ESC` or close the game window. To force terminate:

```bash
kill -9 $(pgrep -f 'uv run main.py')
```

## How to Play

- **Left/Right Arrow Keys:** Move the character
- **Spacebar:** Jump
- **ESC:** Quit game

**Scoring:**
- +10 points for each hammer dodged (when it leaves the screen)
- +50 points for every 5 seconds of survival

Avoid all hammers! Getting hit results in immediate game over. Use the multi-level platforms strategically to dodge incoming projectiles.

## How to Cleanup

```bash
rm -rf .venv
```

## Project Structure

```
category/games/2026/02/20260214-185500-vector-super-mario-bros-hammer-bro-dodge/
├── main.py           # Entry point
├── game.py           # Game logic and entities
├── appinfo.json      # App metadata
├── pyproject.toml    # Dependencies
├── run.bat           # Windows launcher
├── run.sh            # Linux/Mac launcher
└── README.md         # This file
```

## Game Mechanics

- **Gravity:** 9.8 (physics-simulated hammer arcs)
- **Hammer Arc Types:** short-high, long-low
- **Player Speed:** 5.0 units/frame
- **Enemy Jump Chance:** 5% per frame after 3 seconds

## AI/ML Integration Notes

The game is designed for reinforcement learning research with:
- **State Space:** player_x, player_y, hammer_positions, enemy_position
- **Action Space:** move_left, move_right, jump, idle
- **Reward:** Survival time + dodge bonuses
