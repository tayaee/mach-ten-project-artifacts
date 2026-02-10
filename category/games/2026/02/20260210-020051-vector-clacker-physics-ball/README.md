# Vector Clacker Physics Ball

A minimalist physics rhythm game inspired by the classic Clacker (Lato-lato) toy.

## Description

Master the momentum of swinging balls in this physics-based skill challenge. Control a pair of pendulum balls by moving their pivot point vertically, building momentum through rhythmic motion to make them collide. Chain collisions for combo multipliers and aim for the elusive top arc collision for massive bonus points.

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Press `ESC` or close the window.

## How to Play

**Goal**: Keep the balls colliding to maintain rhythm and score points.

- **UP/DOWN Arrow Keys**: Move the handle (pivot) vertically
- Move the pivot up and down with the right timing to add momentum to the balls
- **Scoring**:
  - 100 base points per collision
  - 500 bonus points for top arc collisions (180 degrees)
  - Combo multiplier up to 10x for consecutive collisions
- **Game Over**: Occurs if the balls stop moving for more than 3 seconds

**Tips**: The key is finding the right rhythm. Move the pivot up as the balls swing down, and down as they swing up to transfer energy efficiently.

## Technical Details

- **Engine**: Pygame
- **Physics**: Pendulum dynamics with elastic collision response
- **Resolution**: 800x600
- **State Space**: pivot_y, ball1_angle, ball2_angle, angular_velocity, tension
