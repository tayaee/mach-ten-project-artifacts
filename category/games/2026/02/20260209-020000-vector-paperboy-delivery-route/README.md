# Vector Paperboy Delivery Route

Navigate the suburban streets and deliver newspapers to subscribers while dodging obstacles in this isometric-style arcade challenge.

## Description

This game targets fans of retro arcade classics and physics-based timing puzzles. It provides a structured environment for AI agents to learn pathfinding, projectile physics (throwing newspapers), and collision avoidance in a constrained 2D space.

## Details

The player controls a cyclist moving forward through a scrolling suburban neighborhood. The goal is to throw newspapers into the mailboxes or onto the porches of highlighted houses. Obstacles include parked cars, pedestrians, runaway lawnmowers, and street grates.

**Houses:**
- Subscriber houses: Bright colors (cream walls, red roof) - deliver here!
- Non-subscriber houses: Dark colors (brown walls, dark roof) - avoid these!

**Scoring:**
- Mailbox hit: 100 points (subscriber only)
- Porch landing: 50 points (subscriber only)
- Window hit: -50 points penalty
- Crash: Lose a life (-200 points)

**Streak Multiplier:**
- Successful deliveries build a streak multiplier (up to 5x)
- Crashes or missed deliveries reset the multiplier

The game ends when all lives are lost. Complete the level distance to finish a round.

## Technical Specifications

- Resolution: 800x600
- Frame Rate: 60 FPS
- State Space: Player position, obstacle coordinates, house target coordinates, newspaper ammo count
- Action Space: Move Left, Move Right, Accelerate, Brake, Throw Newspaper

## How to Build

```bash
uv sync
```

Note: On Windows without MSYS2, use:
```bash
python -m venv .venv
.venv/Scripts/pip install pygame
```

## How to Start

```bash
uv run main.py
```

Or with local venv:
```bash
.venv/Scripts/python main.py
```

## How to Stop

Press ESC or close the pygame window.

## How to Play

- **Arrow Keys**: Steer left/right and control speed (up/down)
- **Spacebar**: Throw a newspaper to the left
- **ESC**: Quit the game
- **R/Enter**: Restart after game over

**Tips:**
- Aim for bright-colored houses (subscribers)
- Time your throws to account for scroll speed
- Avoid cars, pedestrians, lawnmowers, and street grates
- Build streaks for higher scores
- Watch your newspaper ammo - it refills periodically
- Higher scroll speed = more points but harder to dodge

## How to Cleanup

```bash
rm -rf .venv
```
