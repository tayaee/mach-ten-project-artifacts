# Asteroid Blaster

Navigate deep space and destroy incoming asteroids in this classic arcade shooter.

## Description

A single-player arcade shooter inspired by the classic Asteroids. The player controls a triangular spaceship with realistic momentum physics. The objective is to survive as long as possible while destroying incoming asteroids. Asteroids break into smaller pieces when shot, creating dynamic gameplay where threat assessment is crucial.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## How to Stop

Press ESC key or close the window.

## How to Play

### Controls

- **Arrow Keys / WASD**: Move ship
  - UP / W: Thrust forward
  - LEFT / A: Rotate left
  - RIGHT / D: Rotate right
- **SPACE**: Fire bullets
- **ESC**: Quit game
- **R**: Restart after game over

### Gameplay Tips

1. Your ship has momentum - thrust accelerates you in the direction you're facing
2. The screen wraps around - flying off one edge brings you to the opposite side
3. Large asteroids split into 2 medium asteroids when destroyed
4. Medium asteroids split into 2 small asteroids when destroyed
5. Small asteroids are destroyed completely
6. You have 3 lives - use them wisely
7. Bullet cooldown prevents spam shooting
8. Score increases with each asteroid destroyed based on size
9. The game gets harder as your score increases (faster asteroid spawns)

### Scoring

- Large asteroids: 100-350 points (depending on size)
- Medium asteroids: 100-250 points
- Small asteroids: 100 points

### Physics

- Thrust adds velocity in the direction the ship is facing
- Friction gradually slows the ship
- Screen wrapping allows continuous movement
- Asteroids spawn from edges and drift toward center

## Technical Details

- **Language**: Python 3.12+
- **Framework**: Pygame
- **Resolution**: 800x600
- **Dependencies**: Managed via uv

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Project Structure

```
category/games/2026/02/20260212-050000-asteroid-blaster/
├── main.py           # Entry point and full game implementation
├── pyproject.toml    # Dependencies
├── appinfo.json      # Metadata
├── run.bat           # Windows run script
├── run.sh            # Linux/Mac run script
└── README.md         # This file
```
