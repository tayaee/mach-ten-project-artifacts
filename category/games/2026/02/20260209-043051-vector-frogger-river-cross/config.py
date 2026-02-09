"""Game configuration constants for Vector Frogger River Cross."""

# Screen settings
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
FPS = 60

# Grid settings
GRID_SIZE = 60
COLS = SCREEN_WIDTH // GRID_SIZE  # 10
ROWS = SCREEN_HEIGHT // GRID_SIZE  # 10

# Colors
COLOR_BG = (20, 25, 35)
COLOR_WATER = (35, 70, 120)
COLOR_GRASS = (45, 100, 55)
COLOR_SAFE_ZONE = (50, 120, 60)
COLOR_FROG = (60, 220, 60)
COLOR_FROG_OUTLINE = (35, 170, 35)
COLOR_LOG = (130, 90, 50)
COLOR_LOG_GRAIN = (100, 65, 35)
COLOR_TEXT = (255, 255, 255)
COLOR_GAME_OVER = (220, 60, 60)
COLOR_GOAL = (100, 200, 255)

# Game zones
START_ROW = ROWS - 1  # Row 9
GOAL_ROW = 0          # Row 0
RIVER_START = 3       # Row 3
RIVER_END = 7         # Row 7

# Scoring
SCORE_LOG_LAND = 10
SCORE_GOAL = 100
STEP_PENALTY = -0.1

# Speed settings (pixels per frame)
BASE_SPEED = 2
SPEED_INCREMENT = 0.3

# Frog settings
FROG_SIZE = GRID_SIZE - 8
FROG_MOVE_COOLDOWN = 8  # Frames between moves

# Log settings
LOG_WIDTHS = {
    'short': GRID_SIZE * 2,
    'medium': GRID_SIZE * 3,
    'long': GRID_SIZE * 4,
}
LOG_HEIGHT = GRID_SIZE - 10

# Lane configuration: (row, speed, log_size, spacing)
# Speed > 0 moves right, Speed < 0 moves left
LANES = [
    (7, 1.5, 'short', 4.5),
    (6, -2.0, 'medium', 4),
    (5, 2.5, 'long', 5),
    (4, -1.8, 'medium', 3.5),
    (3, 2.2, 'short', 3),
]
