# Vector Super Mario Bros: Pipe Warp

Navigate Mario through a vertical maze of pipes and enemies to reach the secret warp zone.

## Rationale

This game focuses on vertical movement and precision timing, providing a different challenge from standard horizontal platformers. It targets casual players who enjoy classic Mario aesthetics and AI agents learning spatial navigation and obstacle avoidance.

## Details

The game features a vertical scrolling screen where Mario must jump between platforms and pipes. Some pipes act as solid ground, while others have Piranha Plants emerging at intervals. The objective is to climb as high as possible. Gravity is applied to Mario, and he can move left, right, and jump. If Mario touches a Piranha Plant or falls off the bottom of the screen, the game ends. Collecting coins increases the score, and reaching the top pipe triggers the "Warp Zone" victory.

**Game Rules:**
- Collect coins: +50 points each
- Reach new heights: +10 points per platform level
- Win condition: Reach the Golden Pipe at the top
- Lose condition: Touch a Piranha Plant or fall off screen
- Camera scrolls upward as you climb

## Technical Specs

| Property | Value |
|----------|-------|
| Game Engine | pygame |
| Resolution | 400x600 |
| FPS | 60 |

## Build / Run / Play

```bash
# Install dependencies
uv sync

# Run
uv run main.py

# Stop
Press ESC or close the window
```

### Controls

| Action | Key |
|--------|-----|
| Move Left | Left Arrow |
| Move Right | Right Arrow |
| Jump | Space |
| Restart (Game Over) | Space |
| Quit | ESC |

### Objective

Climb vertically by jumping between pipes to reach the Golden Pipe at the top. Avoid Piranha Plants that emerge from pipes at random intervals. Collect coins for bonus points. The camera scrolls upward as you ascend - don't fall off the bottom of the screen!

## AI Integration

### State Space
- Player position (x, y)
- Player velocity (vx, vy)
- Player on_ground flag
- Camera offset (height reached)
- Piranha Plant states (position, emergence height, current state)
- Coin positions
- Score

### Action Space
- **Discrete**: Left, Right, Jump, Idle

### Reward Structure
- `+1` per pixel height gained
- `+50` for coins collected
- `-1000` for death (collision/death)
- `-0.01` per step to encourage speed

### API Methods

```python
game = Game()

# Get current state
state = game.get_state()

# Set action for AI player
game.set_action("left")  # or "right", "jump", "idle"

# Get reward
reward = game.get_reward()

# Check if game is over
done = game.is_done()
```

## Cleanup

```bash
rm -rf .venv
```
