# Vector Super Mario Bros Water Swim Avoid

Master neutral buoyancy and navigate a dangerous underwater maze in this classic aquatic challenge.

## Description

Underwater levels provide a unique physics challenge distinct from land-based platforming. This game focuses on variable gravity, momentum conservation, and hitbox precision.

The player character is subject to low gravity and high drag. Pressing the jump key applies an upward impulse, while gravity slowly pulls the character down. The level consists of a horizontally scrolling sea floor filled with static obstacles (coral, pipes) and dynamic hazards (Bloobers and Cheep Cheeps).

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run python main.py
```

## How to Play

Controls:
- SPACE or UP: Swim upward (repeated tapping required to stay afloat)
- LEFT/RIGHT: Move horizontally
- R: Restart after game over
- ESC: Quit

Scoring:
- 10 points for every 100 pixels traveled horizontally
- 500 points for reaching the goal flag
- -100 points for dying (collision reset)

Goal: Navigate to the far right of the level and reach the flag without touching any enemies or obstacles.

Enemies:
- Blooper: White squid-like creatures that move in vertical wavy patterns
- Cheep Cheep: Orange fish that swim horizontally

## How to Stop

Ctrl+C or close the window

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Specifications

- Resolution: 800x600
- FPS: 60
- Physics: Neutral buoyancy with gravity 0.05, buoyancy impulse -2.5
- Engine: Pygame
