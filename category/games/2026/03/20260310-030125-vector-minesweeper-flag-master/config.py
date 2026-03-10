"""Game configuration constants."""

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 700

CELL_SIZE = 40

GRID_ROWS = 10
GRID_COLS = 10

MINE_COUNT = 15

MARGIN = 50

UI_HEIGHT = 100

COLORS = {
    "background": (0, 0, 0),
    "cell_covered": (40, 40, 40),
    "cell_uncovered": (80, 80, 80),
    "cell_hover": (60, 60, 60),
    "flag": (255, 100, 100),
    "mine": (200, 200, 200),
    "grid_line": (60, 60, 60),
    "text": (255, 255, 255),
    "numbers": {
        1: (0, 200, 255),
        2: (0, 255, 100),
        3: (255, 100, 0),
        4: (150, 0, 200),
        5: (200, 0, 0),
        6: (0, 200, 200),
        7: (0, 0, 0),
        8: (100, 100, 100),
    },
}

FONT_SIZE = 24
TITLE_FONT_SIZE = 32
