"""Game configuration constants for Bridge Sprint."""

# Display settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60
TITLE = "Vector Super Mario Bros: Infinite Bridge Sprint"

# Colors
COLOR_BG = (135, 206, 235)           # Sky blue
COLOR_BRIDGE = (139, 69, 19)         # Saddle brown
COLOR_BRIDGE_DECAY = (205, 133, 63)  # Lighter brown for decaying segments
COLOR_BRIDGE_GONE = (100, 149, 237)  # Cornflower blue for water
COLOR_PLAYER = (255, 0, 0)           # Red
COLOR_FIREBALL = (255, 140, 0)       # Orange
COLOR_CHEEP = (0, 191, 255)          # Deep sky blue
COLOR_TEXT = (255, 255, 255)         # White
COLOR_STAMINA = (255, 215, 0)        # Gold

# Physics
GRAVITY = 0.6
JUMP_FORCE = -14
MOVE_SPEED = 5
SPRINT_MULTIPLIER = 1.6
MAX_FALL_SPEED = 15

# Player settings
PLAYER_WIDTH = 24
PLAYER_HEIGHT = 32
PLAYER_START_X = 100
PLAYER_START_Y = 200
STAMINA_MAX = 100
STAMINA_DRAIN = 0.8
STAMINA_REGEN = 0.3

# Bridge settings
BRIDGE_Y = 300
SEGMENT_WIDTH = 40
SEGMENT_HEIGHT = 40
VISIBLE_SEGMENTS = 30
DECAY_CHANCE_BASE = 0.02
DECAY_DELAY = 60  # Frames before segment disappears
DECAY_TIME = 90   # Frames a segment stays in decaying state

# Enemy settings
FIREBALL_SIZE = 16
FIREBALL_SPEED = 4
FIREBALL_SPAWN_CHANCE = 0.008
FIREBALL_MAX_Y = BRIDGE_Y - FIREBALL_SIZE * 2

CHEEP_SIZE = 20
CHEEP_SPEED_X = 3
CHEEP_JUMP_FORCE = -12
CHEEP_SPAWN_CHANCE = 0.005
CHEEP_MIN_X = 200
CHEEP_MAX_X = 700

# Game progression
BASE_SPEED_INCREASE = 0.0001
MAX_SPEED_MULTIPLIER = 3.0

# Scoring
SCORE_PER_FRAME = 1
SCORE_PER_SEGMENT = 10
GAME_OVER_PENALTY = -100

# AI Agent Interface
STATE_SPACE = {
    "player_x": "float - player x position relative to bridge",
    "player_y": "float - player y position",
    "velocity_x": "float - horizontal velocity",
    "velocity_y": "float - vertical velocity",
    "on_ground": "bool - whether player is on a bridge segment",
    "stamina": "float - current stamina value",
    "bridge_states": "list - state of nearby bridge segments (0=gone, 1=stable, 2=decaying)",
    "nearest_fireball_x": "float - x position of nearest fireball, or 1.0 if none",
    "nearest_fireball_y": "float - y position of nearest fireball, or 1.0 if none",
    "nearest_cheep_x": "float - x position of nearest cheep, or 1.0 if none",
    "nearest_cheep_y": "float - y position of nearest cheep, or 1.0 if none",
    "speed_multiplier": "float - current game speed multiplier",
    "distance_traveled": "float - total distance traveled"
}

ACTION_SPACE = {
    "move_left": "hold to move left",
    "move_right": "hold to move right",
    "jump": "press to jump",
    "sprint": "hold to sprint (consumes stamina, increases move speed)"
}

REWARD_SYSTEM = {
    "survival": f"{SCORE_PER_FRAME} per frame",
    "progression": f"{SCORE_PER_SEGMENT} per bridge segment crossed",
    "death": f"{GAME_OVER_PENALTY} on game over"
}
