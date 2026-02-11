# Vector Kung Fu Kick Timing

Master the art of the perfect strike in this rhythm-based martial arts defense game.

## Description

Timing-based games provide a clear reward structure for reinforcement learning agents. This project focuses on high-precision action selection and collision detection, targeting players and AI researchers interested in reflex-based mechanics.

The game is a simplified 2D side-view martial arts action game. The player character is positioned in the center of the screen. Enemies approach from both the left and right sides at varying speeds. The player can perform two actions: Left Kick and Right Kick. A kick is successful if an enemy is within the effective range during the active frame of the animation. If an enemy touches the player's central collision box before being kicked, the player loses a life. The game difficulty increases as the frequency and speed of enemies increase over time.

## Technical Specifications

| Property | Value |
|----------|-------|
| Resolution | 800x600 |
| Frame Rate | 60 FPS |
| Input Type | Discrete Key Input |
| State Representation | Enemy distance, direction, and velocity vectors |

## How to Build

```bash
uv sync
```

## How to Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the convenience scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## How to Play

**Goal:** Defeat as many enemies as possible without losing all lives. Score 100 points for each enemy defeated.

**Controls:**
| Key | Action |
|-----|--------|
| Left Arrow | Kick Left |
| Right Arrow | Kick Right |
| P | Pause |
| ESC | Quit |

**Tip:** Timing is crucial; kicking too early or too late will result in a miss and vulnerability.

## How to Stop

Press `ESC` or close the window.

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Observation Space (for AI Agents)

| Field | Description |
|-------|-------------|
| player_pos | [x, y] coordinates |
| enemies | List of [distance, direction, speed] |
| lives_remaining | Integer (1-3) |

## Action Space (for AI Agents)

| Action | Description |
|--------|-------------|
| 0 | Idle |
| 1 | Kick Left |
| 2 | Kick Right |
