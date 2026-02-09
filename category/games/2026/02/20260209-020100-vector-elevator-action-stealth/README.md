# Vector Elevator Action Stealth

A 2D side-scrolling stealth action game inspired by the classic Elevator Action. Infiltrate a high-security building using elevators and tactical movement to retrieve secret data.

## Description

Navigate through a multi-story building, collect secret documents from red doors, and reach the basement exit. Use elevators to move between floors, avoid or neutralize patrolling enemies, and use shadows to your advantage by shooting out lights.

## Controls

- **LEFT/RIGHT arrows**: Move horizontally
- **UP/DOWN arrows**: Enter/control elevators, crouch
- **SPACE**: Jump
- **Z**: Fire weapon / interact
- **R**: Restart game (when game over)

## Gameplay

- **Red doors**: Contain secret documents (required for mission completion)
- **Blue doors**: Provide cover from enemy detection
- **Normal doors**: Empty, can be opened for passage
- **Elevators**: Move automatically between floors; press UP/DOWN to control when inside
- **Lights**: Can be shot out to create dark zones, reducing enemy detection range
- **Enemies**: Patrol floors and will detect you if you're in their line of sight

## Scoring

- +500 points per secret document collected
- +100 points per enemy neutralized
- +1000 points for successful mission completion

## Build & Run

```bash
# Install dependencies
uv sync

# Run the game
uv run python main.py
```

## Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Details

- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **State Representation**: Pixel array and vector coordinates
- **AI Training**: Suitable for reinforcement learning agents learning stealth mechanics and spatial reasoning
