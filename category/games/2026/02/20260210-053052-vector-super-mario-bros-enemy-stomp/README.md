# Vector Super Mario Bros - Enemy Stomp

Master the art of the precision jump by stomping enemies in a continuous gauntlet.

## Description

This game focuses on the most fundamental skill of classic platformers: jump timing and spatial accuracy. It provides a perfect environment for Reinforcement Learning agents to learn parabolic movement and collision detection without the complexity of full level navigation.

A 2D side-scrolling gauntlet where the player controls a character moving only horizontally and jumping. Enemies (Goomba-like squares) spawn from the right side and move left at varying speeds. The player must stomp on top of them to defeat them and gain points. Falling on the side or being touched by an enemy results in a game over. The speed and frequency of enemy spawns increase over time.

## Technical Specifications

- Engine: Pygame
- Resolution: 800x400
- Gravity: 0.8
- Jump Strength: -15
- Player Speed: 5

## How to Build

```bash
uv run python -m build
```

## How to Start

```bash
uv run python main.py
```

## How to Stop

```bash
# Windows
taskkill /F /IM python.exe

# Unix-like systems
kill $(pgrep -f 'python main.py')
```

## How to Play

**Goal**: Survive as long as possible and achieve a high score by stomping enemies.

**Controls**:
- Left/Right arrow keys: Move
- Space: Jump
- Escape: Quit

**Scoring**:
- +100 points for every enemy stomped
- Combo Multiplier: Stomping multiple enemies without touching the ground doubles the points per stomp (100, 200, 400...)

**Game Over**: Occurs if the player makes contact with an enemy's side or corner without falling downward.

## Agent Observations

- player_x_position
- player_y_velocity
- nearest_enemy_distance
- nearest_enemy_speed
- is_grounded

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```
