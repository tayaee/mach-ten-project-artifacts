"""Game configuration constants."""

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
FPS = 60

# Colors
COLOR_BG = (20, 20, 30)
COLOR_GROUND = (40, 40, 50)
COLOR_PLAYER = (100, 200, 100)
COLOR_OPPONENT = (200, 100, 100)
COLOR_ATTACK = (255, 255, 100)
COLOR_BLOCK = (100, 150, 255)
COLOR_TEXT = (220, 220, 220)
COLOR_UI = (60, 60, 80)

# Fighter dimensions
FIGHTER_WIDTH = 50
FIGHTER_HEIGHT = 100
GROUND_Y = SCREEN_HEIGHT - 80

# Physics
MOVE_SPEED = 5
ATTACK_DURATION = 20  # frames
BLOCK_DURATION = 30   # frames
COOLDOWN_FRAMES = 10  # frames after attack

# Combat
POINTS_TO_WIN = 2
HIGH_ATTACK_DAMAGE = 1
LOW_ATTACK_DAMAGE = 1

# Hitboxes
HIGH_ATTACK_HITBOX = (40, 30)   # width, height
LOW_ATTACK_HITBOX = (50, 25)

# AI
AIReactionTime = 15  # frames
AIAttackChance = 0.02
AIBlockChance = 0.05

# Actions
ACTION_IDLE = "idle"
ACTION_MOVE_LEFT = "move_left"
ACTION_MOVE_RIGHT = "move_right"
ACTION_ATTACK_HIGH = "attack_high"
ACTION_ATTACK_LOW = "attack_low"
ACTION_BLOCK = "block"

# States
STATE_IDLE = "idle"
STATE_MOVING = "moving"
STATE_ATTACKING = "attacking"
STATE_BLOCKING = "blocking"
STATE_STUNNED = "stunned"
STATE_HIT = "hit"
STATE_VICTORY = "victory"
STATE_DEFEAT = "defeat"

# Keys
KEY_LEFT = "left"
KEY_RIGHT = "right"
KEY_ATTACK_HIGH = "a"
KEY_ATTACK_LOW = "s"
KEY_BLOCK = "d"
KEY_QUIT = "escape"
