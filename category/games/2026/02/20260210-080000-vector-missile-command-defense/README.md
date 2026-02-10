# Vector Missile Command Defense

Defend your cities from a rain of incoming ballistic missiles in this classic vector-style defense simulator.

## Description

A reimagining of the classic arcade game "Missile Command." Enemy missiles descend from the top of the screen toward your cities and missile batteries. You must fire interceptor missiles to destroy them before they impact. Interceptors explode at their target point, creating a blast radius that destroys any enemy missiles that enter it.

## Game Rules

| Rule | Value |
|------|-------|
| Intercept Score | +25 points |
| City Bonus | +100 points per city per wave |
| Ammo Bonus | +5 points per remaining missile |
| Wave Bonus | +500 points |
| Ammo per Battery | 10 missiles (refills each wave) |
| Blast Duration | 1.5 seconds |
| Total Waves | 10 |
| Game Over | All cities destroyed |

## How to Build

```bash
uv init
uv add pygame
```

## How to Start

```bash
uv run main.py
```

## How to Stop

Press `ESC` or close the window.

## How to Play

1. Press `SPACE` to start the first wave
2. Aim the crosshair using the mouse or arrow keys (WASD also works)
3. Fire interceptors using one of:
   - Press `1`, `2`, or `3` to fire from Left, Middle, or Right battery
   - Left mouse click fires from the nearest battery with ammo
4. Time your shots so enemy missiles fly through the explosion blast radius
5. Press `SPACE` between waves to continue
6. Press `R` to restart after game over

## Technical Details

- **Resolution:** 800x600
- **FPS:** 60
- **Graphics Style:** Vector-based high-contrast monochrome

## RL Environment Info

**Observation Space:** Crosshair position, Enemy missile positions and velocities, City status, Battery ammo counts, Current score, Wave number

**Action Space:** Move crosshair (continuous X/Y), Fire from battery 1/2/3 (discrete)

**Reward System:** +25 for intercept, +100 per saved city, +500 wave completion, Game over when all cities lost

## How to Cleanup

```bash
rm -rf .venv && rm pyproject.toml uv.lock
```
