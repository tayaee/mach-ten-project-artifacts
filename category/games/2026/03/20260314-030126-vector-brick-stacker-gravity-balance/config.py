"""Game configuration for Vector Brick Stacker Gravity Balance."""

from dataclasses import dataclass
from typing import Tuple


@dataclass
class Colors:
    """Color scheme for the game."""
    BACKGROUND = (20, 20, 30)
    BASE_PLATFORM = (100, 100, 120)
    BASE_PLATFORM_BORDER = (140, 140, 160)
    BLOCK = (200, 80, 60)
    BLOCK_BORDER = (240, 120, 100)
    FALLING_BLOCK = (80, 200, 100)
    FALLING_BLOCK_BORDER = (120, 240, 140)
    TEXT = (255, 255, 255)
    TEXT_SHADOW = (0, 0, 0)
    COM_INDICATOR = (255, 200, 50)
    COM_INDICATOR_STABLE = (50, 200, 100)
    COM_INDICATOR_UNSTABLE = (200, 50, 50)


@dataclass
class Display:
    """Display settings."""
    WIDTH = 800
    HEIGHT = 600
    FPS = 60
    TITLE = "Vector Brick Stacker - Gravity Balance"


@dataclass
class Physics:
    """Physics parameters."""
    GRAVITY = 0.5
    INITIAL_FALL_SPEED = 2.0
    MAX_FALL_SPEED = 8.0
    SPEED_INCREMENT = 0.1
    COLLISION_TOLERANCE = 5.0
    BALANCE_TOLERANCE = 0.85  # COM must be within this fraction of base width


@dataclass
class BlockSizes:
    """Available block dimensions (width, height)."""
    VARIANTS = [
        (40, 30),
        (50, 25),
        (60, 35),
        (70, 30),
        (80, 40),
        (90, 30),
        (100, 35),
        (45, 40),
    ]


@dataclass
class Platform:
    """Base platform settings."""
    WIDTH = 200
    HEIGHT = 20
    Y_OFFSET = 50  # Distance from bottom of screen


@dataclass
class Scoring:
    """Score and rewards."""
    POINTS_PER_BLOCK = 10
    HEIGHT_BONUS_INTERVAL = 5
    HEIGHT_BONUS_POINTS = 50
    OSCILLATION_PENALTY = -0.1
    COLLAPSE_PENALTY = -100


# Controls are defined directly in game.py using pygame constants
# pygame.K_LEFT, pygame.K_RIGHT, pygame.K_SPACE, pygame.K_ESCAPE
