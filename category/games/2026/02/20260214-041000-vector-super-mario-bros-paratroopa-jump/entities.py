"""Game entities: Player, Paratroopa."""

import pygame
import random
import math
from config import (
    PLAYER_WIDTH, PLAYER_HEIGHT, GROUND_Y,
    PARATROOPA_WIDTH, PARATROOPA_HEIGHT,
    GRAVITY, MAX_FALL_SPEED, JUMP_IMPULSE, BOUNCE_IMPULSE,
    MOVE_SPEED, FRICTION,
    COLOR_PLAYER, COLOR_PLAYER_FACE,
    COLOR_PARATROOPA_BODY, COLOR_PARATROOPA_SHELL, COLOR_PARATROOPA_WING,
    SCREEN_WIDTH, SCREEN_HEIGHT,
    VERTICAL_OSCILLATION, HORIZONTAL_OSCILLATION, STATIC_HOVER
)


class Player:
    """Player character with gravity-based physics."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.on_ground = False
        self.alive = True
        self.has_bounced_once = False
        self.last_bounced_enemy = None

    def reset(self, x, y):
        """Reset player position."""
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.alive = True
        self.has_bounced_once = False
        self.last_bounced_enemy = None

    def update(self, keys):
        """Update player physics and input."""
        if not self.alive:
            return

        # Horizontal input
        if keys[pygame.K_LEFT]:
            self.vel_x = -MOVE_SPEED
        elif keys[pygame.K_RIGHT]:
            self.vel_x = MOVE_SPEED
        else:
            self.vel_x *= FRICTION
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0

        # Apply horizontal velocity
        self.x += self.vel_x

        # Screen bounds
        if self.x < 0:
            self.x = 0
            self.vel_x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.vel_x = 0

        # Jump input
        if keys[pygame.K_SPACE] and not self.has_bounced_once:
            # Initial jump to start the game
            self.vel_y = JUMP_IMPULSE
            self.on_ground = False
            self.has_bounced_once = True

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.y += self.vel_y

        # Check if fallen off screen (game over - touched ground)
        if self.y > SCREEN_HEIGHT:
            self.alive = False

    def bounce(self, enemy_id):
        """Apply bounce impulse from stomping an enemy."""
        self.vel_y = BOUNCE_IMPULSE
        self.on_ground = False
        self.last_bounced_enemy = enemy_id

    def get_hitbox(self):
        """Return player collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def get_bounce_zone(self):
        """Return the bounce zone (bottom of player)."""
        return pygame.Rect(
            int(self.x + 4),
            int(self.y + self.height - 6),
            self.width - 8,
            6
        )

    def get_safe_zone(self):
        """Return safe zone (top and sides - for side/bottom collision)."""
        return pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height - 6
        )

    def draw(self, surface):
        """Draw player."""
        # Body
        pygame.draw.rect(surface, COLOR_PLAYER, (int(self.x), int(self.y), self.width, self.height))

        # Face
        face_x = int(self.x + 4)
        face_y = int(self.y + 4)
        pygame.draw.rect(surface, COLOR_PLAYER_FACE, (face_x, face_y, 16, 12))

        # Eyes
        pygame.draw.circle(surface, (0, 0, 0), (face_x + 5, face_y + 5), 2)
        pygame.draw.circle(surface, (0, 0, 0), (face_x + 11, face_y + 5), 2)

        # Hat brim
        pygame.draw.rect(surface, (200, 30, 30), (int(self.x), int(self.y - 2), self.width, 4))


class Paratroopa:
    """Flying Koopa Paratroopa with various movement patterns."""

    _id_counter = 0

    def __init__(self, x, y, pattern=None):
        Paratroopa._id_counter += 1
        self.id = Paratroopa._id_counter
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.width = PARATROOPA_WIDTH
        self.height = PARATROOPA_HEIGHT
        self.speed = random.uniform(1.5, 3.5)
        self.amplitude = random.uniform(40, 100)
        self.frequency = random.uniform(0.02, 0.04)
        self.phase = random.uniform(0, math.pi * 2)
        self.time_offset = 0
        self.direction = 1 if random.choice([True, False]) else -1
        self.alive = True
        self.pattern = pattern or random.choice([
            VERTICAL_OSCILLATION,
            HORIZONTAL_OSCILLATION,
            STATIC_HOVER
        ])

    def update(self):
        """Update paratroopa position based on movement pattern."""
        self.time_offset += 1

        if self.pattern == VERTICAL_OSCILLATION:
            # Vertical sinusoidal movement with slight horizontal drift
            self.y = self.start_y + math.sin(self.time_offset * self.frequency + self.phase) * self.amplitude
            self.x += self.speed * 0.3 * self.direction

        elif self.pattern == HORIZONTAL_OSCILLATION:
            # Horizontal oscillation
            self.x = self.start_x + math.sin(self.time_offset * self.frequency + self.phase) * self.amplitude
            self.y += self.speed * 0.2 * self.direction

        else:  # STATIC_HOVER
            # Gentle hovering
            self.y = self.start_y + math.sin(self.time_offset * 0.03 + self.phase) * 15
            self.x += math.cos(self.time_offset * 0.02) * 0.5

        # Bounce off walls
        if self.x <= 0:
            self.x = 0
            self.direction *= -1
        elif self.x >= SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width
            self.direction *= -1

        # Bounce off ceiling
        if self.y <= 50:
            self.start_y = 50
            self.direction *= -1

    def get_hitbox(self):
        """Return paratroopa collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def get_bounce_hitbox(self):
        """Return hitbox for bouncing (top portion)."""
        return pygame.Rect(
            int(self.x + 2),
            int(self.y),
            self.width - 4,
            10
        )

    def draw(self, surface, can_bounce=True):
        """Draw paratroopa."""
        # Wings with animation
        wing_offset = math.sin(self.time_offset * 0.3) * 3
        wing_color = COLOR_PARATROOPA_WING if can_bounce else (200, 200, 200)

        pygame.draw.ellipse(
            surface,
            wing_color,
            (int(self.x - 8), int(self.y + 8 + wing_offset), 12, 20)
        )
        pygame.draw.ellipse(
            surface,
            wing_color,
            (int(self.x + self.width - 4), int(self.y + 8 - wing_offset), 12, 20)
        )

        # Shell/body
        pygame.draw.ellipse(
            surface,
            COLOR_PARATROOPA_SHELL,
            (int(self.x), int(self.y + 8), self.width, self.height - 8)
        )

        # Shell pattern
        pygame.draw.ellipse(
            surface,
            (150, 100, 30),
            (int(self.x + 4), int(self.y + 12), self.width - 8, self.height - 16)
        )

        # Head
        pygame.draw.circle(
            surface,
            COLOR_PARATROOPA_BODY,
            (int(self.x + self.width // 2), int(self.y + 6)),
            8
        )

        # Eyes
        eye_offset_x = 4 if self.direction > 0 else -4
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(self.x + self.width // 2 + eye_offset_x), int(self.y + 4)),
            3
        )
        pygame.draw.circle(
            surface,
            (0, 0, 0),
            (int(self.x + self.width // 2 + eye_offset_x + self.direction), int(self.y + 4)),
            1
        )
