# Vector Minesweeper Flag Master

A refined strategic puzzle of logic and deduction to uncover hidden threats.

## Description

Minesweeper is a foundational logic puzzle that challenges spatial reasoning and deductive skills. This version features a clean, monochromatic vector style designed for clarity. The game consists of a 10x10 grid containing 15 hidden mines. Each cell can be in one of three states: covered, uncovered, or flagged. When a cell is uncovered, it reveals either a mine (game over) or a number indicating how many mines are in the 8 adjacent cells. If a cell with 0 adjacent mines is uncovered, the game recursively uncovers all connected empty cells. The game ends in victory when all non-mine cells are uncovered.

## Rationale

This classic puzzle is designed for both human players seeking a minimalist challenge and AI agents learning pattern recognition and risk assessment in a grid-based environment. The game tests deductive reasoning by requiring players to infer mine locations from incomplete information.

## Details

- **Grid Size**: 10x10 cells
- **Mine Count**: 15 mines (15% mine density)
- **Cell States**: Covered, Uncovered, Flagged
- **Number Display**: Indicates adjacent mine count (1-8)
- **Auto-uncover**: Cells with 0 adjacent mines automatically reveal neighbors
- **UI Style**: Clean, monochromatic vector design with color-coded numbers

## Build

```bash
uv sync
```

## Run

```bash
uv run --no-active --python 3.12 python main.py
```

Or use the provided scripts:
- Windows: `run.bat`
- Linux/Mac: `./run.sh`

## Stop

Press `ESC` or close the window.

## How to Play

**Controls:**
- **Left-click**: Uncover a cell
- **Right-click**: Place or remove a flag on a suspected mine

**Game Rules:**
- Your first click is always safe (no mine)
- Numbers indicate how many mines are in the 8 adjacent cells
- Flag cells you believe contain mines to help track progress
- Game Over if you uncover a mine
- Victory when all non-mine cells are uncovered

**Scoring:**
- Time elapsed (seconds) - lower is better
- Progress percentage tracked in real-time

**Restart:** Press `SPACE` after Game Over or Victory.

## AI Agent Input

For RL agent control:

**State Space:**
- Grid: 10x10 matrix
  - -1: Covered cell
  - 0-8: Uncovered cell with adjacent mine count
  - -2: Flagged cell
- Flags placed count (0-15)
- Progress percentage (0-100)

**Action Space:**
- 0: Uncover cell at (row, col)
- 1: Toggle flag at (row, col)

**Input Format:** (row, col, action)
- row: 0-9
- col: 0-9
- action: 0 (uncover) or 1 (flag)

**Reward Structure:**
- Safe cell uncovered: +1
- Mine flagged correctly: +2
- Mine uncovered (game over): -100
- Cell flagged incorrectly: -1
- Victory: +50

## Project Structure

```
category/games/2026/03/20260310-030125-vector-minesweeper-flag-master/
├── main.py          - Entry point
├── game.py          - Main game loop and state management
├── config.py        - Game constants and settings
├── pyproject.toml   - Dependencies
├── run.bat          - Windows run script
├── run.sh           - Linux/Mac run script
└── README.md        - This file
```

## Technical Specs

- **Resolution**: 600x700
- **Grid Size**: 10x10 cells
- **Cell Size**: 40px
- **Mine Density**: 15%
- **Input Type**: Mouse (Left/Right click)
- **Game Engine**: Pygame 2.0+
- **Colors**:
  - Background: Black (#000000)
  - Covered Cell: Dark Gray (#282828)
  - Uncovered Cell: Medium Gray (#505050)
  - Flag: Red-Orange (#FF6464)
  - Mine: Light Gray (#C8C8C8)
  - Numbers 1-8: Color-coded for easy reading
