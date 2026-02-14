"""Game configuration constants."""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TITLE = "Vector Super Mario Bros Paratroopa Jump"

# Physics constants
GRAVITY = 0.5
MAX_FALL_SPEED = 15.0
JUMP_IMPULSE = -10.0
BOUNCE_IMPULSE = -12.0

# Movement constants
MOVE_SPEED = 5.0
FRICTION = 0.9

# Player settings
PLAYER_WIDTH = 24
PLAYER_HEIGHT = 32
GROUND_Y = 580  # Below screen - falling here is game over

# Paratroopa settings
PARATROOPA_WIDTH = 28
PARATROOPA_HEIGHT = 32
INITIAL_PARATROOPAS = 5
MAX_PARATROOPAS = 12
PARATROOPA_SPAWN_INTERVAL = 180  # frames (3 seconds at 60 FPS)

# Enemy movement patterns
VERTICAL_OSCILLATION = "vertical"
HORIZONTAL_OSCILLATION = "horizontal"
STATIC_HOVER = "static"

# Scoring
SCORE_PER_BOUNCE = 100
COMBO_MULTIPLIER = 2  # Doubles each consecutive bounce

# Colors (RGB)
COLOR_BG = (135, 170, 200)
COLOR_GROUND = (100, 80, 60)
COLOR_PLAYER = (220, 50, 50)
COLOR_PLAYER_FACE = (255, 200, 180)
COLOR_PARATROOPA_BODY = (50, 180, 50)
COLOR_PARATROOPA_SHELL = (200, 150, 50)
COLOR_PARATROOPA_WING = (240, 240, 240)
COLOR_TEXT = (255, 255, 255)
COLOR_COMBO = (255, 255, 0)
COLOR_DANGER = (255, 100, 100)
