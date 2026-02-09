# Vector Mario Platformer Lite

A minimalist side-scrolling platformer inspired by classic 2D adventure games.

## Description

Platforming is a fundamental genre for testing spatial reasoning and timing in AI agents. This app provides a clean, vector-based environment for reinforcement learning agents to master jump trajectories, collision detection, and enemy avoidance without complex textures.

## Details

The game consists of a 2D side-scrolling world with physics-based movement. The player controls a rectangular agent that must navigate through platforms, gaps, and moving enemies to reach a goal flag at the end of the level. Key features include horizontal acceleration, friction, gravity, and variable jump height based on key press duration. Enemies move in fixed patterns and can be defeated by jumping on top of them. Collecting coins increases the score. The game engine uses a simple grid-based collision system and a fixed camera that follows the player.

## Technical Specifications

| Property | Value |
|----------|-------|
| Engine | Pygame |
| Resolution | 800x600 |
| Frame Rate | 60 |
| Input Type | Keyboard |
| Reward Structure | Positive for moving right, collecting coins, and reaching the flag. Negative for falling off cliffs or colliding with enemies from the side/bottom. |

## How to Build

```bash
uv init --app
uv add pygame
```

## How to Start

```bash
uv run main.py
```

Or using python directly:

```bash
python main.py
```

## How to Stop

Press `ESC` to quit, or `Ctrl+C` in the terminal.

## How to Play

**Goal:** Reach the flag at the right end of the map.

**Controls:**
- `Left` / `Right` Arrow keys: Horizontal movement
- `Spacebar` or `Up` Arrow: Jump

**Scoring:**
- 100 points per coin collected
- 200 points per enemy defeated (jump on top)
- 1000 points for reaching the goal

**Avoid:** Falling into pits or touching enemies from the side (loses one life).

## Project Structure

```
vector-mario-platformer-lite/
+-- main.py        # Main game entry point with all game logic
+-- pyproject.toml # Project configuration
+-- README.md      # This file
```
