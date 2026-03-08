"""Game configuration constants."""

# Window settings
WINDOW_WIDTH = 750
WINDOW_HEIGHT = 850
FPS = 60

# Grid settings
GRID_COLS = 15
GRID_ROWS = 15
CELL_SIZE = 50
PLAYER_MOVE_DELAY = 12  # Frames per move (~0.2s at 60 FPS)

# Gameplay settings
CHASE_RADIUS = 4  # Tiles - enemies chase when player is this close
PUMP_RANGE = 3
INFLATION_REQUIRED = 4
INFLATION_DECAY_RATE = 60  # Frames before inflation decreases
ENEMY_MOVE_DELAY = 15  # Enemy movement speed
FYGAR_BREATH_RANGE = 4
FYGAR_BREATH_COOLDOWN = 180  # Frames
ROCK_WOBBLE_TIME = 60  # Frames before rock falls
ROCK_FALL_SPEED = 4  # Frames per cell

# Scoring
SCORE_PUMP_KILL = 100
SCORE_ROCK_KILL = 500
SCORE_DIG_SOIL = 10

# Colors
COLOR_BG = (20, 20, 30)
COLOR_SOIL = (139, 90, 43)
COLOR_SOIL_DARK = (100, 60, 30)
COLOR_TUNNEL = (30, 30, 40)
COLOR_PLAYER = (255, 255, 255)
COLOR_POOKA = (220, 50, 50)
COLOR_FYGAR = (50, 180, 50)
COLOR_ROCK = (128, 128, 128)
COLOR_PUMP = (255, 200, 50)
COLOR_HUD = (50, 50, 70)
COLOR_TEXT = (255, 255, 255)
COLOR_FIRE = (255, 150, 0)
