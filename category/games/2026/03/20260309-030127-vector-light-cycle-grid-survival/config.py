"""Game configuration constants."""

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

GRID_SIZE = 20

COLS = SCREEN_WIDTH // GRID_SIZE
ROWS = SCREEN_HEIGHT // GRID_SIZE

COLORS = {
    "background": (0, 0, 0),
    "player": (0, 255, 0),
    "trail": (0, 136, 0),
    "grid_line": (17, 17, 17),
    "text": (255, 255, 255),
}

INITIAL_FPS = 10
FPS_INCREMENT_INTERVAL = 5000  # ms
FPS_INCREMENT_AMOUNT = 1

DIRECTIONS = {
    "UP": (0, -1),
    "DOWN": (0, 1),
    "LEFT": (-1, 0),
    "RIGHT": (1, 0),
}

FONT_SIZE = 24
