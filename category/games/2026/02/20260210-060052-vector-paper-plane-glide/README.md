# Vector Paper Plane Glide

**Category:** Games

**Description:** Master the art of gliding through evolving narrow corridors in this physics-based flight skill game.

## Rationale

This game focuses on delicate physics management and spatial awareness. Unlike Flappy Bird's frantic tapping, this requires smooth, continuous control. The glide mechanic creates an "easy to learn, hard to master" experience that rewards finesse over reflexes. It provides an excellent environment for AI agents to learn continuous control and predictive pathfinding.

## Details

The player controls a paper plane that constantly moves forward through procedurally generated caves. Physics include gravity pulling down and "lifting" (holding a key) pushing up, with momentum conservation creating smooth gliding motion. The corridors narrow and widen unpredictably, requiring constant adjustment. Collectible air currents (blue circles) provide bonus points and encourage risk-taking. Touching any surface ends the run immediately.

## How to Build

```bash
uv venv
uv pip install pygame-ce
```

## How to Run

```bash
uv run main.py
```

## Controls

- **Spacebar** / **Up Arrow** / **Hold Left Click**: Apply lift and ascend
- **Release**: Glide down under gravity
- **Escape**: Quit the game

## Scoring

- 10 points per second survived
- 100 points per Air Current collected (blue circles)
- Distance traveled displayed in meters

## AI Integration

AI agents can interact with the game through the `Game` class:

- `get_observation()`: Returns current game state including plane position, velocity, and corridor geometry
- `step_ai(action)`: Execute an action (0: release lift, 1: apply lift) and receive (observation, reward, done)

### Reward Structure

- Per frame alive: +0.1
- Distance traveled: +0.01 per meter
- Air current collected: +10.0
- Collision: -10.0

### Observation Space

```python
{
    "plane_y": float,              # Plane Y position
    "plane_velocity": float,       # Plane vertical velocity
    "ceiling_y": float,            # Ceiling height at plane position
    "floor_y": float,              # Floor height at plane position
    "gap_height": float,           # Available gap size
    "gap_center": float,           # Center of the gap
    "distance": int,               # Total distance traveled
    "air_current_dist_x": float,   # Distance to nearest air current X
    "air_current_dist_y": float,   # Distance to nearest air current Y
    "score": int,
    "game_state": str
}
```

### Action Space

- 0: Release lift (glide down)
- 1: Apply lift (glide up)

## How to Stop

Press ESC key or close the game window. For automation, send SIGINT (Ctrl+C).

## How to Cleanup

```bash
rm -rf .venv
```

## Technical Specifications

- **Language:** Python 3.12+
- **Dependencies:** pygame-ce
- **Resolution:** 800x600
- **Input:** Keyboard hold / Mouse hold / Action space (for AI)
