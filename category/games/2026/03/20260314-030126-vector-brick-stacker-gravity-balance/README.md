# Vector Brick Stacker - Gravity Balance

**Category:** Games

**Description:** Stack falling blocks precisely to build the highest tower without toppling over.

## Rationale

This game targets fans of physics-based puzzles and classic stacking games. It provides a unique challenge for AI agents to learn spatial reasoning and real-time balance adjustment under gravity constraints.

## Details

The game consists of a base platform and various rectangular blocks that fall from the top of the screen one by one. The player must move and rotate the falling block to land it on the existing stack. The game uses a 2D physics engine where each block has a center of mass. If the cumulative center of mass of the stack shifts outside the base width, the tower collapses. As the tower gets higher, the camera scrolls up, and the falling speed of blocks increases. The game ends when any block falls off the screen or the stack collapses.

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

## Controls

- **Left Arrow**: Move falling block left
- **Right Arrow**: Move falling block right
- **Spacebar**: Rotate block (90 degrees)
- **R**: Reset game
- **Escape**: Quit game (or reset when game over)

## How to Play

Move the falling block left or right using the arrow keys and rotate it using the spacebar. Align the block to maintain the tower balance. Watch the balance indicator on screen - it shows the center of mass position relative to the platform center. Keep the stack balanced by placing blocks strategically. As the tower grows higher, blocks fall faster, requiring quicker reactions.

## Scoring

- +10 points for each successfully placed block
- +50 bonus points for every 5 levels of height achieved
- The goal is to maximize the total score before the tower falls

## Features

- Physics-based gravity and collision detection
- Center of mass calculation for balance mechanics
- Rotatable rectangular blocks
- Camera scrolling to follow tower growth
- Progressive difficulty (faster falling blocks)
- Balance indicator showing stack stability
- AI-friendly observation interface

## AI Integration

AI agents can interact with the game through the `Game` class:

- `get_observation()`: Returns current game state including block position, rotation, center of mass, and tower height
- `step_ai(action)`: Execute an action and receive (observation, reward, done)

### Action Space

- 0: Move left
- 1: Move right
- 2: Rotate
- 3: Do nothing

### Observation Space

```python
{
    "block_position": (float, float),      # Falling block (x, y) position
    "block_rotation": int,                 # Block rotation in degrees (0-270)
    "block_dimensions": (int, int),        # Block (width, height)
    "stack_com": (float, float),           # Stack center of mass (x, y)
    "tower_height": int,                   # Current tower height in pixels
    "score": int,                          # Current score
    "game_over": bool                      # Game state
}
```

### Reward Structure

- Per frame: -0.1 (time penalty)
- Block placed: +10
- Height bonus: +50 per 5 levels
- Collapse: -100

## How to Stop

Press ESC key or close the game window. For automation, send SIGINT (Ctrl+C).

## How to Cleanup

```bash
rm -rf .venv
rm -rf __pycache__
```

## Technical Specifications

- **Language:** Python 3.12+
- **Dependencies:** pygame
- **Resolution:** 800x600
- **Input:** Keyboard / Action space (for AI)
- **Physics Engine:** Pygame-based simple gravity and collision logic
