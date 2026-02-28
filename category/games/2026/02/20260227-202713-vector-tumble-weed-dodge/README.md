# Vector Tumble Weed Dodge

Survive the desert storm by dodging endless waves of fast-moving tumbleweeds.

## Description

This game focuses on high-speed reaction and pattern recognition. It provides a clean environment for AI agents to learn collision avoidance and spatial timing in a continuous side-scrolling context.

The game features a player character (cowboy silhouette) positioned on the left side of the screen. Tumbleweeds of varying sizes and speeds spawn from the right and move leftward. The player can move vertically (Up/Down) to avoid them. As time progresses, the frequency and speed of tumbleweeds increase. The game uses a minimalist vector art style with a high contrast between the character/obstacles and the desert background.

## How to Build

```bash
uv run python -m pip install pygame
```

## How to Start

```bash
uv run main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `run.sh`

## How to Play

Controls:
- UP and DOWN arrow keys to move the character vertically

Scoring:
- 1 point for every second survived
- 10 points for every tumbleweed successfully dodged (passing the left edge)

Goal: Survive as long as possible. Touching a tumbleweed results in immediate Game Over.

## How to Stop

Press ESC key or close the window.

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Technical Specs

- Framework: Pygame
- Screen Resolution: 800x400
- Color Palette: Black (#000000), White (#FFFFFF), Dark Gray (#333333)
- Gravity: 0
- Base Scroll Speed: 5
- Difficulty Scaling: Linear increase every 10 seconds
- Collision Type: Bounding box

## Rules

- Movement: Vertical only (Up/Down)
- Tumbleweeds spawn from the right side with varying sizes (20-50 pixels) and speeds
- Difficulty increases every 10 seconds, increasing tumbleweed speed and spawn rate
- Win Condition: None (endless survival)
- Lose Condition: Collision with any tumbleweed
