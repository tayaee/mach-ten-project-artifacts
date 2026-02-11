# Vector Super Mario Bros Multi-Level Platformer

A classic side-scrolling platformer featuring procedural level progression and physics-based movement.

## Description

The game is a simplified 2D side-scroller. Players control a character that can move left/right and jump. The level consists of a 2D grid with solid blocks (ground/platforms), hazards (pits), and mobile enemies (moving back and forth). The goal is to reach the flagpole at the far right of the map. Physics include gravity, inertia, and collision detection for platform edges. Enemies are defeated if jumped upon from above, otherwise they damage the player on contact.

## Game Rules

- **Scoring**:
  - Coins: +100 points each
  - Enemies defeated: +200 points
  - Reaching flagpole: +5000 points (advances to next level)
- **Lives**: Start with 3 lives. Lose a life when falling into a pit or touching an enemy from the side.
- **Level Progression**: Each level is procedurally generated with increasing difficulty (longer, more enemies, more hazards).
- **Physics**: Gravity constant 0.8, jump force -15, movement speed 5.
- **High Score**: Persisted locally in high_score.json.

## Controls

- **LEFT/RIGHT Arrow Keys**: Move horizontally
- **SPACE**: Jump
- **R**: Restart (from game over or continue to next level)
- **ESC**: Quit

## How to Build

```bash
uv venv
uv pip install pygame
```

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Unix/Linux/Mac: `./run.sh`

## How to Stop

Press ESC or close the window. To force stop:
```bash
pkill -f main.py
```

## How to Cleanup

```bash
rm -rf .venv
rm -rf __pycache__
rm -f high_score.json
```

## Technical Specs

- **Language**: Python 3.10+
- **Framework**: Pygame
- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **Dependencies**: pygame

## Game Mechanics

| Parameter | Value |
|-----------|-------|
| Gravity Constant | 0.8 |
| Jump Force | -15 |
| Movement Speed | 5 |
| Screen Resolution | 800x600 |
| Frame Rate | 60 |

## AI Agent Info

**Observation Space**: Array of 2D coordinates for player, enemies, coins, and platforms within a 400px radius; current velocity; jumping state.

**Action Space**:
- 0: Stay
- 1: Left
- 2: Right
- 3: Jump

**Reward Structure**:
- Small positive (+1) per coin collected
- Medium positive (+2) per enemy defeated
- Large positive (+50) for reaching flagpole
- Large negative (-100) for death
- Small negative (-0.1) per frame to encourage efficiency
