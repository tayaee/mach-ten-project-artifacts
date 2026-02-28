# Vector Marianne Yarn Ball Roll

A physics-based rolling platformer where you guide a yarn ball through obstacle courses to reach the kitten.

## Description

Guide a rolling yarn ball through a physics-based obstacle course to reach the kitten. The game targets casual puzzle lovers and provides a rich environment for RL agents to learn momentum-based navigation and precision timing in a 2D physics world.

## How It Works

The game is a simplified 2D physics platformer. The player controls a yarn ball that gains momentum based on tilt and gravity. The goal is to navigate from the starting point to a target kitten at the end of the level without falling off the platforms or hitting sharp needles. The ball has inertia, meaning it doesn't stop immediately when the key is released. Obstacles include moving fans that blow the ball, slippery ice patches with reduced friction, and narrow bridges.

## Rules

- **Win Condition**: Reach the kitten at the end of the level
- **Lose Conditions**: Fall off the stage or hit a sharp needle
- **Scoring**: Base score of 1000 decreases over time; bonus points for collecting small 'buttons' along the path

## Technical Specifications

- **Language**: Python 3.12+
- **Library**: pygame-ce
- **Resolution**: 800x600
- **Input Type**: Discrete Keyboard
- **Environment Management**: uv

## Installation

```bash
uv sync
```

## How to Run

**Windows:**
```bash
run.bat
```

**Linux/Mac:**
```bash
./run.sh
```

Or directly:
```bash
uv run --no-active --python 3.12 main.py
```

## How to Stop

Press ESC or close the window.

## How to Play

Use LEFT and RIGHT arrow keys to apply horizontal force. Use UP arrow key to jump. The ball will accelerate and decelerate based on physics calculations. Collect buttons for bonus points. Falling off the stage resets the level and penalizes the score.

## Cleanup

```bash
rm -rf .venv
```

## Reinforcement Learning Metadata

### Action Space

- move_left
- move_right
- jump
- none

### Observation Space

Player (x, y, vx, vy), kitten (x, y), obstacles (list of x, y, type), platform_bounds

### Reward Function

- +100: Reach the kitten (win)
- +10: Collect a button
- -50: Fall off the stage
- -100: Hit a needle
- -0.1: Each step (encourage speed)
