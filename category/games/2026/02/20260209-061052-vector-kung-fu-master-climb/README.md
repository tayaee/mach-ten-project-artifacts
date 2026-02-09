# Vector Kung Fu Master

Side-scrolling martial arts action where timing and positioning are everything.

## Description

A simplified tribute to the classic arcade beat 'em up. The player controls a martial artist moving through a narrow corridor. Enemies approach from both the left and right sides. There are two main enemy types: Grippers who drain energy by contact and Knife Throwers who attack from a distance. The player must use high and low attacks to neutralize threats. The game progresses through 5 stages, ending with a boss encounter that requires specific patterns to defeat. Physics are strictly grid-based for predictable agent interaction.

## Game Mechanics

### Player Actions
- **Move Left/Right**: Arrow keys
- **High Punch (Z)**: Hits standing enemies
- **Low Kick (X)**: Hits crouching enemies and small obstacles
- **Jump (Up)**: Avoid projectiles
- **Crouch (Down)**: Dodge high attacks

### Enemy Types
- **Standard Grunt**: Melee attackers that drain HP on contact
- **Knife Thrower**: Ranged attackers that throw projectiles
- **Boss**: Large enemy with high HP on the final stage

### Scoring System
- Grunt defeat: 100 points
- Knife deflect: 200 points
- Boss defeat: 5000 points
- Time bonus: Remaining seconds x 10

### Health System
Numerical HP (0-100), decreases on contact, game over at 0.

## Technical Specifications

- **Resolution**: 800x400
- **Framework**: Pygame
- **State Representation**: Entity coordinates (x, y), enemy type, projectile velocity, player state

## How to Build

```bash
uv sync
```

## How to Start

```bash
uv run python main.py
```

## How to Stop

Press ESC key or terminate the process (SIGINT).

## How to Play

Use the Left and Right arrow keys to move. Press Z for a high punch to hit standing enemies and X for a low kick to hit crouching enemies or small obstacles. Avoid letting enemies touch you. Jump using the Up arrow to avoid projectiles. Your goal is to defeat enemies across 5 stages and defeat the boss while maintaining HP. Score increases by defeating enemies and finishing quickly.

## How to Cleanup

```bash
rm -rf .venv && rm -rf __pycache__
```

## Project Structure

```
.
├── main.py           # Entry point
├── game.py           # Game loop and state management
├── entities.py       # Player, enemy, and projectile classes
└── constants.py      # Game constants and configuration
```
