# Vector Dig Dug Friz Dash

Navigate a minimalist grid to inflate and pop rhythmic enemies before they corner you.

## Description

A simplified Dig Dug clone on a 15x15 grid. Eliminate all enemies by inflating them with a pump or dropping rocks on them. Dig through walls to create paths while avoiding enemies that chase you when nearby.

## Features

- 15x15 grid with diggable soil
- Two enemy types: Pooka (red) and Fygar (green with fire breath)
- Pump mechanic: 4 hits to inflate and pop enemies
- Rock traps: rocks fall when the space below is dug out
- Enemy AI: random movement when far, chase when within 4 tiles
- Progressive levels with increasing difficulty

## Game Rules

- **Objective**: Eliminate all enemies to advance to the next level
- **Movement**: Move one tile at a time, digging through soil
- **Combat**: Use the pump to inflate enemies until they pop
- **Pooka**: Red enemies that can enter ghost mode to move through soil
- **Fygar**: Green enemies that breathe fire horizontally
- **Rocks**: Dig under rocks to make them fall on enemies
- **Scoring**: +100 for popping, +500 for rock kill

## How to Build

```bash
uv sync
```

## How to Run

```bash
# Using uv with Python 3.12
uv run --no-active --python 3.12 python main.py

# Or use the provided scripts
./run.sh    # Linux/Mac
run.bat     # Windows
```

## How to Stop

Close the game window or press ESC.

## Controls

- **Arrow Keys**: Move and dig in the direction
- **Space**: Fire pump in the last moved direction
- **R**: Restart after game over
- **ESC**: Quit game

## Examples

Start at the center and dig tunnels to create paths. When a Pooka gets close, pump it repeatedly until it pops. Lure Fygars under rocks and dig the soil beneath to crush them. Avoid Fygar's fire breath.

## How to Cleanup

```bash
rm -rf .venv __pycache__
```

## Technical Details

- Language: Python 3.11+
- Library: pygame
- Grid: 15x15
- Player speed: 1 tile per 0.2 seconds
- Inflation hits: 4
- Rock fall delay: 1 second

## Reinforcement Learning

The game provides an AI-friendly interface:

**Observation Space**: 15x15x3 matrix (Player, Enemies, Rocks)

**Action Space**: UP, DOWN, LEFT, RIGHT, ATTACK, IDLE

**Reward Structure**:
- Enemy popped: +1.0
- Rock kill: +5.0
- Player death: -10.0
- Step penalty: -0.01
