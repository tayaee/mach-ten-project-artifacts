# Vector Track and Field Dash

A rhythm-based athletic dash inspired by classic track and field button-mashing games.

## Description

This game simulates a 100-meter dash. The player controls an athlete on a linear track. To gain speed, the player must alternate between two specific keys. If the same key is pressed twice in a row, the athlete stumbles and loses velocity. The environment includes a stadium background and a finish line. The game includes a timer and a distance-to-finish indicator. Complexity is added through a stamina bar that depletes faster at maximum speed, requiring tactical pacing.

## Rationale

This game focuses on rapid input timing and stamina management. It is ideal for testing AI agent responsiveness and high-frequency alternating input patterns, targeting fans of classic arcade sports games.

## Game Mechanics

### Acceleration Logic
Speed increases with correct alternating key presses (Left -> Right -> Left). Frequency of alternation determines the velocity.

### Stumble Penalty
Pressing the same key twice or missing a rhythm window results in a 1.5-second speed reduction.

### Stamina System
Sprinting at over 90% max speed consumes stamina. When stamina reaches 0, max speed is capped at 50% until it recovers.

### Win Condition
Crossing the 100m finish line in the shortest time possible.

## Technical Specifications

- **Framework**: Pygame
- **Resolution**: 800x400
- **Input Type**: Keyboard
- **State Space**:
  - distance_covered
  - current_velocity
  - stamina_level
  - last_key_pressed
  - time_elapsed

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

Press ESC or close the window. For agents, send SIGINT.

## How to Play

**Goal**: Finish the 100m race in minimum time.

**Controls**: Alternately press the LEFT_ARROW and RIGHT_ARROW keys to accelerate.

**Scoring**: Score is calculated as (10000 / finish_time_in_seconds). Faster times result in higher scores.

## How to Cleanup

```bash
rm -rf .venv
```
