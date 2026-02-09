# Vector Elevator Action Stealth

A tactical infiltration game where you must infiltrate a high-security building using elevators and tactical positioning to retrieve secret documents.

## Description

Infiltrate a 30-story high-security building as a spy. The building consists of floors connected by elevators and stairs. Navigate through the facility, collect secret documents from red doors, avoid hazards in blue doors, and evade or neutralize guards patrolling the corridors.

## Features

- 30-floor building with vertical navigation
- Functional elevator system (3 elevator shafts)
- Stairwells for alternative routes
- Guard AI with patrol behavior and line-of-sight detection
- Document collection system with score tracking
- Combat mechanics with shooting
- Hazard system with random trap doors

## Controls

| Action | Key |
|--------|-----|
| Move Left/Right | Left/Right Arrow |
| Operate Elevator | Up/Down Arrow (while on elevator) |
| Use Stairs | Up/Down Arrow (while on stairs) |
| Crouch | Left/Right Ctrl |
| Shoot | Spacebar |
| Quit | ESC |

## Objective

- Collect all documents from red doors
- Neutralize guards for bonus points
- Reach the bottom floor exit after collecting all documents
- Avoid hazards and guard fire

## Scoring

- +500 points per document collected
- +100 points per guard neutralized
- -10 points per second elapsed

## Technical Specs

- Language: Python 3.12+
- Library: pygame-ce
- Resolution: 800x600
- Frame Rate: 60 FPS

## How to Build

```bash
uv venv
uv pip install pygame-ce
```

## How to Run

```bash
uv run main.py
```

## How to Stop

Press ESC key or close the window.

## Cleanup

```bash
rm -rf .venv
```

## RL Agent Data

For reinforcement learning integration:

- **Observation Space**: `Box(low=0, high=255, shape=(600, 800, 3), dtype=uint8)` - Raw pixel input
- **Action Space**: `Discrete(6)` - [idle, left, right, up, down, shoot]
- **Reward Function**: Dense reward based on distance to nearest document and exit progress

## License

MIT
