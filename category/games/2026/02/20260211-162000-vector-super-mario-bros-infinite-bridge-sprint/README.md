# Vector Super Mario Bros: Infinite Bridge Sprint

An endless running challenge where Mario must sprint across a decaying bridge while dodging fireballs and Cheep Cheeps.

## Description

A high-speed platformer where you control a character on an infinite horizontal bridge. The bridge is composed of segments that decay and disappear after being stepped on. Fireballs jump vertically from below, and Cheep Cheep fish leap in parabolic arcs. The game speed increases over time, testing your reflexes and stamina management.

## Rationale

This game focuses on high-speed reflex testing and resource management (stamina/momentum) in a platforming environment. It serves as an excellent benchmark for reinforcement learning agents to master timing and spatial awareness in a constrained, high-threat area.

## Details

- Bridge segments randomly decay after you pass them
- Fireballs spawn from below and jump in vertical arcs
- Cheep Cheeps spawn from water and jump in parabolic trajectories
- Speed multiplier increases over time (up to 3x)
- Sprinting drains stamina but allows faster movement
- Score increases with distance traveled and segments crossed

## How to Build

```bash
uv venv
uv pip install pygame-ce
```

Or use the launcher scripts:
- Windows: `run.bat`
- Unix: `./run.sh`

## How to Start

```bash
uv run main.py
```

## How to Stop

Press ESC to quit the game.

## How to Play

- **LEFT/RIGHT arrows**: Move left or right
- **SPACE**: Jump
- **SHIFT (hold)**: Sprint (consumes stamina, increases movement speed)

Your score increases the further you travel along the bridge. Avoid falling through gaps or colliding with enemies.

## Tips

- Sprint in short bursts to cross dangerous sections
- Watch for blinking segments - they're about to collapse
- Time your jumps to avoid fireballs and Cheep Cheeps
- The game gets faster over time - stay alert
- Falling into water or touching any enemy ends the game

## Project Structure

```
category/games/2026/02/20260211-162000-vector-super-mario-bros-infinite-bridge-sprint/
|-- main.py           # Entry point
|-- game.py           # Game loop and rendering
|-- entities.py       # Player and enemy classes
|-- config.py         # Game constants
|-- pyproject.toml    # Dependencies
|-- appinfo.json      # Metadata
|-- run.bat           # Windows launcher
|-- run.sh            # Unix launcher
|-- README.md         # This file
```

## AI Agent Input

### State Space

- `player_x`: Player x position (normalized 0-1)
- `player_y`: Player y position (normalized 0-1)
- `velocity_x`: Horizontal velocity (normalized)
- `velocity_y`: Vertical velocity (normalized)
- `on_ground`: Boolean indicating if on stable ground
- `stamina`: Current stamina level (normalized 0-1)
- `bridge_states`: List of nearby segment states (0=gone, 1=stable, 2=decaying)
- `nearest_fireball_x`, `nearest_fireball_y`: Nearest fireball position (normalized)
- `nearest_cheep_x`, `nearest_cheep_y`: Nearest Cheep Cheep position (normalized)
- `speed_multiplier`: Current game speed multiplier
- `distance_traveled`: Total distance traveled

### Action Space

- Move Left, Move Right, Jump, Sprint (hold)

### Reward System

- +1 per frame survived
- +10 per bridge segment crossed
- -100 on game over

## Technical Specs

- Language: Python 3.12+
- Framework: Pygame CE
- Resolution: 800x400
- FPS: 60
