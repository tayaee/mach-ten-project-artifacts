"""Game entities for Bridge Sprint."""

import pygame
import random
import math
from config import *


class BridgeSegment:
    """A single segment of the infinite bridge."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = SEGMENT_WIDTH
        self.height = SEGMENT_HEIGHT
        self.state = "stable"  # stable, decaying, gone
        self.decay_timer = 0

    def trigger_decay(self):
        """Start the decay process."""
        if self.state == "stable":
            self.state = "decaying"
            self.decay_timer = DECAY_DELAY

    def update(self):
        """Update the segment state."""
        if self.state == "decaying":
            self.decay_timer -= 1
            if self.decay_timer <= 0:
                self.state = "gone"

    def draw(self, surface, offset_x):
        """Draw the segment."""
        screen_x = self.x - offset_x
        if self.state == "stable":
            pygame.draw.rect(surface, COLOR_BRIDGE, (screen_x, self.y, self.width, self.height))
            pygame.draw.rect(surface, (100, 50, 10), (screen_x, self.y, self.width, self.height), 2)
        elif self.state == "decaying":
            # Blinking effect
            if (self.decay_timer // 5) % 2 == 0:
                color = COLOR_BRIDGE_DECAY
            else:
                color = COLOR_BRIDGE
            pygame.draw.rect(surface, color, (screen_x, self.y, self.width, self.height))
            pygame.draw.rect(surface, (100, 50, 10), (screen_x, self.y, self.width, self.height), 2)

    def get_rect(self, offset_x):
        """Get collision rect."""
        if self.state == "gone":
            return None
        return pygame.Rect(self.x - offset_x, self.y, self.width, self.height)


class Player:
    """The player character."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.stamina = STAMINA_MAX
        self.sprinting = False
        self.facing_right = True
        self.alive = True

    def update(self, keys, bridge_segments, offset_x, speed_multiplier):
        """Update player state."""
        if not self.alive:
            return

        # Horizontal movement
        move_dir = 0
        if keys[pygame.K_LEFT]:
            move_dir = -1
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            move_dir = 1
            self.facing_right = True

        # Sprint handling
        self.sprinting = keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]
        current_speed = MOVE_SPEED

        if self.sprinting and self.stamina > 0:
            current_speed *= SPRINT_MULTIPLIER
            self.stamina -= STAMINA_DRAIN * speed_multiplier
            if self.stamina < 0:
                self.stamina = 0
        else:
            self.stamina += STAMINA_REGEN
            if self.stamina > STAMINA_MAX:
                self.stamina = STAMINA_MAX

        self.vel_x = move_dir * current_speed

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

        # Gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Update position
        self.x += self.vel_x * speed_multiplier
        self.y += self.vel_y * speed_multiplier

        # Boundary checks
        if self.x < offset_x:
            self.x = offset_x
        if self.x > offset_x + SCREEN_WIDTH - self.width:
            self.x = offset_x + SCREEN_WIDTH - self.width

        # Check if fell off screen
        if self.y > SCREEN_HEIGHT:
            self.alive = False

        # Collision with bridge
        self.on_ground = False
        player_rect = pygame.Rect(self.x - offset_x, self.y, self.width, self.height)

        for segment in bridge_segments:
            seg_rect = segment.get_rect(offset_x)
            if seg_rect and player_rect.colliderect(seg_rect):
                # Landing on top
                if self.vel_y > 0 and self.y + self.height - self.vel_y <= seg_rect.top:
                    self.y = seg_rect.top - self.height
                    self.vel_y = 0
                    self.on_ground = True

    def draw(self, surface, offset_x):
        """Draw the player."""
        if not self.alive:
            return

        screen_x = self.x - offset_x

        # Body
        pygame.draw.rect(surface, COLOR_PLAYER, (screen_x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (200, 0, 0), (screen_x, self.y, self.width, self.height), 2)

        # Eyes (direction indicator)
        eye_offset = 16 if self.facing_right else 4
        pygame.draw.circle(surface, (255, 255, 255), (int(screen_x + eye_offset), int(self.y + 8)), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(screen_x + eye_offset), int(self.y + 8)), 2)

        # Hat
        pygame.draw.rect(surface, (200, 0, 0), (screen_x - 2, self.y - 6, self.width + 4, 8))
        pygame.draw.rect(surface, (255, 0, 0), (screen_x - 2, self.y - 4, self.width + 4, 4))

    def get_rect(self, offset_x):
        """Get collision rect."""
        return pygame.Rect(self.x - offset_x, self.y, self.width, self.height)


class Fireball:
    """A fireball enemy that jumps from below."""

    def __init__(self, x):
        self.x = x
        self.y = SCREEN_HEIGHT + FIREBALL_SIZE
        self.size = FIREBALL_SIZE
        self.vel_y = -FIREBALL_SPEED * 1.5
        self.active = True

    def update(self):
        """Update fireball position."""
        self.y += self.vel_y
        self.vel_y += GRAVITY * 0.5

        # Remove if off screen
        if self.y > SCREEN_HEIGHT + 50:
            self.active = False
        if self.y < -50:
            self.active = False

    def draw(self, surface, offset_x):
        """Draw the fireball."""
        screen_x = self.x - offset_x
        if 0 <= screen_x <= SCREEN_WIDTH:
            pygame.draw.circle(surface, COLOR_FIREBALL, (int(screen_x), int(self.y)), self.size // 2)
            pygame.draw.circle(surface, (255, 200, 0), (int(screen_x), int(self.y)), self.size // 3)

    def get_rect(self, offset_x):
        """Get collision rect."""
        screen_x = self.x - offset_x
        return pygame.Rect(screen_x - self.size // 2, self.y - self.size // 2, self.size, self.size)


class CheepCheep:
    """A fish enemy that jumps in parabolic arcs."""

    def __init__(self, x, direction):
        self.x = x
        self.y = SCREEN_HEIGHT + CHEEP_SIZE
        self.size = CHEEP_SIZE
        self.vel_x = CHEEP_SPEED_X * direction
        self.vel_y = CHEEP_JUMP_FORCE
        self.start_x = x
        self.active = True

    def update(self):
        """Update cheep cheep position."""
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY * 0.7

        # Remove if off screen
        if self.y > SCREEN_HEIGHT + 50:
            self.active = False
        if self.x < -100 or self.x > SCREEN_WIDTH + 100:
            self.active = False

    def draw(self, surface, offset_x):
        """Draw the cheep cheep."""
        screen_x = self.x - offset_x
        if -50 <= screen_x <= SCREEN_WIDTH + 50:
            # Body
            pygame.draw.ellipse(surface, COLOR_CHEEP, (screen_x - self.size // 2, self.y - self.size // 2, self.size, self.size))
            # Tail
            tail_dir = -1 if self.vel_x > 0 else 1
            pygame.draw.polygon(surface, COLOR_CHEEP, [
                (screen_x + tail_dir * self.size // 2, self.y),
                (screen_x + tail_dir * self.size, self.y - 5),
                (screen_x + tail_dir * self.size, self.y + 5)
            ])
            # Eye
            eye_x = screen_x - (self.size // 4) if self.vel_x > 0 else screen_x + (self.size // 4)
            pygame.draw.circle(surface, (255, 255, 255), (int(eye_x), int(self.y - 2)), 3)
            pygame.draw.circle(surface, (0, 0, 0), (int(eye_x), int(self.y - 2)), 1)

    def get_rect(self, offset_x):
        """Get collision rect."""
        screen_x = self.x - offset_x
        return pygame.Rect(screen_x - self.size // 2, self.y - self.size // 2, self.size, self.size)
