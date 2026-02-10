# Vector Super Mario Bros Jump Block Logic

Master the precision of vertical jumping to activate mystery blocks and collect hidden rewards.

## Description

This game focuses on the fundamental mechanic of vertical collision and timing. You control a character on a 2D horizontal plane with multiple platforms at various heights. The core objective is to position yourself directly under blocks and jump so that your character's head makes contact with the bottom of the block. Mystery blocks release coins when hit, while bricks provide satisfying bounce feedback. The game features a clean, vector-style monochrome aesthetic optimized for visual clarity.

## Features

- Multi-tier platform layout with blocks at various heights
- Three block types: Mystery (with coins), Brick (bounceable), and Solid (indestructible)
- Physics-based jumping with gravity (0.8) and jump force (15.0)
- Coin collection animations with parabolic arcs
- Score tracking for mystery blocks hit and coins collected
- Victory condition when all mystery blocks are activated

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run python main.py
```

## How to Stop

Press `ESC` or close the game window.

## Controls

- **Left Arrow**: Move left
- **Right Arrow**: Move right
- **Space**: Jump
- **R**: Restart game (when complete)

## Rules

- Score 100 points for hitting a mystery block
- Score 200 points for collecting the resulting coin
- Score 50 points for breaking a brick
- Position your character directly under a block
- Jump so your head makes contact with the bottom of the block
- Clear all mystery blocks to achieve victory

## Examples

Jump from the ground to hit lower blocks, then navigate up the platforms to reach higher mystery blocks. Time your jumps carefully - the gravity physics require precise positioning under each block.

## Technical Specifications

- **Engine**: Pygame
- **Resolution**: 800x600
- **Frame Rate**: 60 FPS
- **Physics Engine**: Simplified AABB Collision
- **Gravity**: 0.8
- **Jump Force**: 15.0

## Reward Structure

| Action | Points |
|--------|--------|
| Hit Mystery Block | 100 |
| Collect Coin | 200 |
| Break Brick | 50 |

## How to Cleanup

```bash
rm -rf .venv
rm -rf __pycache__
uv cache clean
```
