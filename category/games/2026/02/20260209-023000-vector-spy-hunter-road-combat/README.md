# Vector Spy Hunter: Road Combat

Drive, shoot, and survive in this high-speed tactical road combat simulator.

## Description

A simplified vertical scrolling vehicular combat game with vector-style graphics. The player controls a high-speed vehicle on a three-lane highway, dodging civilian cars, destroying enemy agents, and avoiding road hazards.

## How to Build

```bash
uv venv
uv pip install pygame
```

## How to Start

```bash
uv run main.py
```

## How to Stop

```bash
pkill -f main.py
```

## How to Play

### Objective
Survive as long as possible while maximizing your score.

### Scoring
- +10 points for every 100 meters traveled
- +50 points for each enemy vehicle destroyed
- -20 points for hitting a civilian car or obstacle (plus speed penalty)
- -100 points and game over for crashing into an enemy

### Controls
- **Arrow Left/Right**: Move horizontally
- **Arrow Up**: Accelerate
- **Arrow Down**: Decelerate
- **Z**: Fire machine gun (forward)
- **X**: Deploy smoke screen (backward)
- **R**: Retry (when game over)

### Features
- Progressive difficulty - game speeds up and enemies become more aggressive
- Dynamic road curves that increase over time
- Three vehicle types: civilian cars (avoid), enemy agents (destroy), and obstacles (oil slicks)
- Weapon cooldowns requiring strategic resource management

## Technical Specifications

- **Language**: Python 3.11+
- **Framework**: Pygame
- **Resolution**: 400x600
- **Style**: Monochrome/Vector (Green on Black)
- **State Space**: Player position, enemy relative positions, weapon cooldowns, distance
- **Action Space**: Movement, acceleration/deceleration, fire gun, deploy smoke

## How to Cleanup

```bash
rm -rf .venv
```
