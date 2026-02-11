"""Game configuration constants."""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60
TITLE = "Vector Super Mario Bros Jump and Dash Pro"

# Physics constants
GRAVITY = 0.6
MAX_FALL_SPEED = 12.0
JUMP_FORCE = -13.0
JUMP_HOLD_FORCE = -0.5  # Additional force when holding jump
MAX_JUMP_HOLD_TIME = 15  # Frames of additional jump force

# Movement constants
ACCELERATION = 0.4
FRICTION = 0.85
MAX_RUN_SPEED = 7.0
INITIAL_MOVE_SPEED = 3.0

# Player settings
PLAYER_WIDTH = 24
PLAYER_HEIGHT = 32
GROUND_Y = 350

# Scoring
SCORE_PER_DISTANCE = 1
GOAL_BONUS = 1000
DEATH_PENALTY = -200

# Colors (RGB)
COLOR_BG = (135, 170, 200)
COLOR_GROUND = (100, 80, 60)
COLOR_PLATFORM = (140, 100, 60)
COLOR_PLAYER = (220, 50, 50)
COLOR_PLAYER_ACCEL = (255, 100, 100)
COLOR_SPIKE = (120, 120, 130)
COLOR_GOAL = (50, 200, 50)
COLOR_GOAL_FLAG = (255, 50, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_HUD_BG = (0, 0, 0, 150)

# Level design
LEVEL_WIDTH = 3200
GOAL_X = 3100
