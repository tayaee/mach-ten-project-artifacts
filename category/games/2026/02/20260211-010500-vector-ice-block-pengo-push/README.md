# Vector Ice Block Pengo Push

Strategic block-pushing puzzle where you crush enemies between ice slides.

## Description

A simplified version of the classic arcade game Pengo. The player controls a character in a 13x13 grid filled with ice blocks and walls. The objective is to eliminate all patrolling enemies by pushing ice blocks into them. When a block is pushed, it slides until it hits another block, wall, or the screen boundary. Enemies move randomly or chase the player using simple pathfinding. If an enemy is caught in the path of a sliding block, it is crushed. Blocks can also be destroyed if pushed while already adjacent to a wall.

## Technical Specifications

- **Language**: Python 3.12+
- **Rendering**: pygame-ce
- **Environment**: 600x600 grid
- **Grid Size**: 13x13 cells
- **Observation Space**: Box(0, 4, (13, 13)) - grid cell types
- **Action Space**: Discrete(5) - [None, Up, Down, Left, Right]

## How to Build

```bash
uv sync
```

## How to Start

```bash
# Windows
run.bat

# Linux/Mac
./run.sh

# Or directly
uv run --no-active --python 3.12 python main.py
```

## How to Stop

Press ESC to quit, or close the window.

## How to Play

- **Arrow Keys**: Move the player character
- **SPACE**: Push ice block in the direction you're facing

### Game Elements

- **Cyan Square (Player)**: Your character that can push blocks
- **Red Blobs (Enemies)**: Patrolling enemies that chase you
- **Light Blue Blocks (Ice)**: Pushable blocks that slide when pushed
- **Diamond Shapes**: Special blocks that give bonus points when three are aligned

### Scoring

| Action | Points |
|--------|--------|
| Crush Enemy | 100 |
| Break Block | 10 |
| Diamond Alignment | 500 |

### Goal

Eliminate all enemies by crushing them with sliding ice blocks. Avoid letting enemies touch you. Align three diamond blocks for a bonus score.

### Tips

- Enemies can be crushed from any direction by sliding blocks
- Blocks slide until they hit an obstacle
- Use walls to stop blocks strategically
- Diamond blocks behave like ice blocks but offer bonus when aligned

## How to Cleanup

```bash
rm -rf .venv
rm -rf __pycache__
```

## Reward Structure (RL)

- Crush enemy: +1.0
- Diamond alignment: +5.0
- Player death: -10.0
- Time penalty: -0.01/frame
