# Minimalist Falling Sand Box

A pixel art physics simulation game where you can enjoy the interaction of gravity and particles.

## Description

Experience the satisfying behavior of falling sand and flowing water in this minimalist physics sandbox. Watch as particles interact with each other following simple physical laws - perfect for relaxation or educational exploration of cellular automata.

## Target Audience

- Users seeking relaxation through observing particle movements without complex controls
- Educational audience interested in visual implementations of physical laws

## How it Works

1. The canvas is a grid structure where each cell is either empty or filled with a specific particle
2. Main particle types: Sand, Water, and Wall
3. Sand falls downward each frame and flows diagonally when blocked below
4. Water falls downward but spreads horizontally when blocked
5. Walls remain fixed and immovable
6. Left-click or touch to draw particles on screen, right-click to erase
7. Physical interactions between particles (mixing, stacking) are calculated in real-time

## How to Build

Uses HTML5 Canvas and vanilla JavaScript. No build tools required - all HTML, CSS, and JS are contained in index.html.

## How to Run

1. Install dependencies: `uv sync`
2. Run the server: `uv run python main.py`
3. Open your browser to: `http://127.0.0.1:5000`

## Examples

- Drop sand from the top and watch it navigate through complex maze-like walls
- Build dams to contain water and observe pressure buildup
- Create cascading waterfalls and observe how sand settles at the bottom
- Experiment with mixing different materials to see how they interact
