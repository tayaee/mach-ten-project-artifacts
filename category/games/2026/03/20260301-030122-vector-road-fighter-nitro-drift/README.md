# Vector Road Fighter Nitro Drift

High-speed vertical scrolling racing game focused on precision overtaking and fuel management.

## Description

Control a car on a multi-lane highway, dodging traffic while managing fuel consumption. Reach the 10,000m goal before running out of fuel. Collect fuel pickups and use nitro boost strategically to maximize distance and overtaking opportunities.

## State Space

- Player X-Y coordinates
- Current Speed
- Fuel Level
- Array of nearby NPC cars (X, Y, Speed, Type)
- Distance to Finish
- Oil Slick locations

## Action Space

- Move Left
- Move Right
- Accelerate (Boost) - Hold Up Arrow
- Decelerate - Release Up Arrow

## Rewards

- Positive: Distance covered (+1 per tick), Overtaking NPC cars (+10), Collecting Fuel (+50)
- Negative: Crashing (-100), Fuel depletion (Game Over)

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Stop

Close the game window or press ESC.

## How to Play

- **Left Arrow**: Move left
- **Right Arrow**: Move right
- **Up Arrow (Hold)**: Accelerate/Boost (uses more fuel)
- **ESC**: Quit the game

## Rules

- Avoid hitting other cars or the grassy borders
- Collect 'F' icons to refill fuel
- Blue cars move at constant speed, red cars change lanes erratically
- Oil slicks cause temporary loss of control
- Crashing results in fuel penalty and speed reset
- Higher speed consumes fuel faster
- Reach 10,000m to win

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```
