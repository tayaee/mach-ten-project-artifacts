# Vector Bubble Bobble Simple Clear

Trap monsters in bubbles and pop them to clear the screen in this classic arcade reimagining.

## Description

A puzzle-action game focusing on spatial logic and timing. Players must coordinate projectile movement with platform navigation to trap floating monsters and defeat them before they escape.

## Details

The game consists of a single-screen 2D platform layout with walls and platforms. The player controls a character that can move left, right, jump, and blow bubbles. Monsters move horizontally and jump occasionally. When a bubble hits a monster, the monster is trapped inside and floats toward the top of the screen. The player must then touch the trapped bubble to pop it and defeat the monster. If a monster is not popped within a certain time, it escapes and becomes faster. The level is cleared when all monsters are defeated.

## Technical Specifications

| Property | Value |
|----------|-------|
| Engine | Pygame |
| Resolution | 800x600 |
| Frame Rate | 60 |
| Input Type | Keyboard |
| State Space | Grid-based with continuous coordinates |
| Reward Structure | Trap: +10, Pop: +50, Clear: +100, Die: -100, Time: -0.1 |

## How to Build

```bash
uv init --app
uv add pygame
```

## How to Start

```bash
uv run python main.py
```

## How to Stop

Press `ESC` to quit, or close the game window.

## How to Play

**Goal:** Clear all monsters from the screen.

**Controls:**
- `Left` / `Right` Arrow keys: Move horizontally
- `Spacebar`: Jump
- `Z` key: Blow bubble

**Mechanics:**
- Shoot bubbles to trap monsters inside them
- Trapped monsters float toward the top of the screen
- Touch trapped bubbles to pop them and defeat the monster (+50 points)
- If a monster stays in a bubble too long, it escapes and becomes faster
- Trapping a monster awards +10 points
- Clearing all monsters awards +100 points and advances to the next level

**Avoid:** Touching untrapped monsters (instant game over).

## Project Structure

```
vector-bubble-bobble-simple-clear/
+-- main.py        # Main game entry point
+-- pyproject.toml # Project configuration
+-- README.md      # This file
```
