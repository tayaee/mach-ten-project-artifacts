# Vector Boulder Dash Logic

**Category:** Games

**Description:** Navigate a hazardous cave to collect diamonds while avoiding falling rocks.

## Rationale

This game focuses on spatial reasoning and gravity-based physics puzzles. It targets players who enjoy retro arcade logic games and provides an excellent environment for RL agents to learn pathfinding under environmental constraints.

## Details

The game consists of a 2D grid filled with dirt, rocks, and diamonds. The player (the digger) moves through the grid, removing dirt to create paths.

### Rules

1. **Gravity** affects rocks and diamonds; they fall if there is empty space below them
2. Rocks **roll** off other rounded objects (rocks, diamonds)
3. A **falling rock** will crush the player, ending the game
4. Players can **push rocks horizontally** if there is empty space behind the rock
5. Collecting a **specific number of diamonds** opens the exit door
6. **Enemies** move in predictable patterns and must be avoided or crushed by falling rocks

### Technical Specifications

- **Grid Size:** 20x15 cells
- **Engine:** Pygame
- **Target FPS:** 30
- **Input Type:** Discrete (Up, Down, Left, Right)
- **State Representation:** Multi-channel 2D Array

## How to Build

```bash
uv venv
uv pip install pygame-ce
```

## How to Run

```bash
uv run main.py
```

## How to Play

**Goal:** Collect all diamonds and reach the exit.

**Controls:**
- **Arrow Keys** - Move the player
- **R** - Restart level
- **ESC** - Quit the game

**Scoring:**
- +10 points per diamond
- +20 points for crushing an enemy
- +50 points for reaching the exit

**Game Over:**
- Player is hit by a falling rock
- Player is caught by an enemy

### RL Strategy

Maximize reward by finding the shortest path to diamonds while predicting rock fall trajectories.

## How to Stop

Press ESC key or close the game window. For automation, send SIGINT (Ctrl+C).

## How to Cleanup

```bash
rm -rf .venv
```

## AI Integration

AI agents can interact with the game through the `Game` class:

- `get_observation()`: Returns current game state including player position, grid state, and enemy positions
- `step_ai(action)`: Execute an action and receive (observation, reward, done)

### Action Space

- 0: Move Up
- 1: Move Down
- 2: Move Left
- 3: Move Right
- 4: Wait

### Reward Structure

- Per step: -0.01 (encourage efficiency)
- Diamond collected: +10.0
- Enemy crushed: +20.0
- Reach exit: +50.0
- Death: -100.0

### Observation Space

```python
{
    "player_x": int,
    "player_y": int,
    "diamonds_collected": int,
    "diamonds_total": int,
    "exit_open": bool,
    "score": int,
    "game_state": str,
    "grid": List[List[int]],  # 2D array of tile types
    "enemies": List[{"x": int, "y": int}]
}
```
