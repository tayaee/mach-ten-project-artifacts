# Galactic Dodge Classic

**Category:** Games
**Date:** 2026-02-06

## Description

A classic arcade survival game where you pilot a spaceship through an endless asteroid field. Dodge incoming asteroids and survive as long as possible to achieve the highest score.

## Rationale

This project demonstrates fundamental game development concepts including collision detection, player input handling, and dynamic difficulty scaling. The simple yet addictive gameplay makes it an excellent starting point for learning game engine physics and object-oriented programming patterns.

## Details

### Gameplay Features

1. **Canvas-based 2D vertical scrolling game**
2. **Player controls:**
   - Left/Right arrow keys or A/D keys for keyboard control
   - Mouse movement for precise control
   - Touch support for mobile devices
3. **Asteroid spawning system:**
   - Random sizes (15-45 pixels)
   - Random spawn positions along X-axis
   - Varied falling speeds
   - Rotating asteroid graphics with procedural vertices
4. **Collision detection:**
   - Circle-based collision system
   - Forgiving hitbox for better player experience
5. **Scoring system:**
   - Score increases based on survival time
   - High score saved to localStorage
6. **Dynamic difficulty:**
   - Every 500 points, asteroid speed increases
   - Spawn rate decreases (more frequent asteroids) as difficulty rises

### Technical Implementation

- Pure JavaScript with ES6+ class-based architecture
- HTML5 Canvas for rendering
- RequestAnimationFrame for smooth 60fps gameplay
- Responsive player movement with smooth interpolation
- Procedurally generated asteroid shapes
- Animated starfield background

## How to Build

No build process required! This game uses pure HTML5 Canvas and JavaScript. Simply open the `index.html` file in any modern web browser.

For development, you can use any static file server:

```bash
# Using Python 3
python -m http.server 8000

# Using Node.js (with npx)
npx serve

# Or simply open index.html directly in your browser
```

## How to Run

1. Open `index.html` in a web browser
2. Click "Start Game" to begin
3. Use arrow keys or mouse to move your spaceship
4. Dodge the falling asteroids
5. Survive as long as possible and beat your high score!

## Examples

When you launch the game, you'll see a dark space background with twinkling stars. Your blue spaceship appears at the bottom of the screen. Asteroids of various sizes begin falling from the top - some small and fast, others larger and slower.

Try to achieve a score of 5000 points by deftly maneuvering between asteroids! The challenge increases as your score goes up, with asteroids falling faster and appearing more frequently.

## Controls

- **Left/Right Arrow Keys** or **A/D** - Move spaceship left/right
- **Mouse** - Move spaceship to mouse position
- **Touch** - Drag to move spaceship (mobile)
- **Click "Start Game"** - Begin playing
- **Click "Play Again"** - Restart after game over

## File Structure

```
galactic-dodge-classic/
├── index.html      # Main HTML file with game container and UI
├── style.css       # Styling for game interface and screens
├── game.js         # Game logic and rendering engine
└── README.md       # This file
```

## Browser Compatibility

Works in all modern browsers that support:
- HTML5 Canvas
- ES6+ JavaScript
- CSS3

Tested on Chrome, Firefox, Safari, and Edge.
