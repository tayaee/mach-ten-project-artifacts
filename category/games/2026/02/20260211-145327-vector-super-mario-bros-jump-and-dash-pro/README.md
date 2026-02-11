# Vector Super Mario Bros Jump and Dash Pro

Master the art of momentum in this high-speed precision platformer challenge.

## Description

A side-scrolling platformer focused on momentum-based physics and precise timing. Navigate treacherous terrain with bottomless pits, spike hazards, and platform jumps to reach the goal post at the end of the level.

## Rationale

This app targets AI agents and developers interested in momentum-based physics and precise timing. It bridges the gap between simple jumping and complex platforming by focusing on horizontal velocity management and obstacle avoidance, providing a rich environment for reinforcement learning.

## Details

### Physics System

- **Gravity**: 0.6 acceleration with 12.0 terminal velocity
- **Variable Jump Height**: Hold spacebar longer for higher jumps (up to 15 frames of additional lift)
- **Running Momentum**: Hold a direction to build speed over time (3.0 initial to 7.0 max)
- **Friction**: 0.85 deceleration when not moving

### Hazards

- **Bottomless Pits**: Falling kills instantly and resets position
- **Spikes**: Triangle hazards on the ground that kill on contact
- **Precision Jumps**: Various platform heights require jump timing

### Scoring

- +1 point per 10 pixels traveled
- +1000 bonus for reaching the goal
- -200 penalty for each death

## Build

```bash
uv sync
```

## Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## Stop

Press ESC or close the window.

## How to Play

### Controls

| Key | Action |
|-----|--------|
| LEFT/RIGHT | Move horizontally |
| SPACE | Jump (hold for higher jump) |
| ESC | Exit game |

### Goal

Reach the goal post at the right end of the level (3100m). The level features:
- Starting area with tutorial hints
- Pit jumps requiring running momentum
- Elevated platform sections
- Spike hazards to avoid
- Final challenge before the goal

### Tips

- Hold direction keys to build sprint speed for long jumps
- Release jump button early for short hops
- Time jumps carefully to clear pits and spikes
- Deaths reset position but maintain score (minus penalty)

## Project Structure

```
category/games/2026/02/20260211-145327-vector-super-mario-bros-jump-and-dash-pro/
├── main.py           # Entry point
├── game.py           # Game loop and rendering
├── entities.py       # Player, Platform, Spike, Goal classes
├── config.py         # Constants and settings
├── appinfo.json      # App metadata
├── pyproject.toml    # Dependencies
├── run.bat           # Windows run script
├── run.sh            # Unix run script
└── README.md         # This file
```

## AI Agent Input

### Observation Space

```python
{
    'player': {
        'x': float,           # Normalized position (0-1)
        'y': float,
        'vx': float,          # Normalized velocity
        'vy': float,
        'on_ground': bool,
        'facing_right': bool
    },
    'nearest_spike': {
        'x': float,
        'y': float,
        'distance': float     # Normalized distance
    } or None,
    'nearest_pit': {
        'x': float,
        'width': float,
        'distance': float
    } or None,
    'goal_distance': float,   # Normalized (0-1, 0 = at goal)
    'score': int
}
```

### Action Space

Discrete actions:
- 0: No action
- 1: Move left
- 2: Move right
- 3: Jump
- 4: Jump + Move left
- 5: Jump + Move right

### Reward Structure

- Distance progress: +0.1 per frame moving forward
- Goal reached: +1000
- Death: -200 (with position reset)

## Technical Specs

- **Language**: Python 3.12+
- **Library**: pygame-ce 2.5+
- **Resolution**: 800x400
- **FPS**: 60
- **Level Width**: 3200 pixels
- **Style**: Vector/minimal aesthetic
