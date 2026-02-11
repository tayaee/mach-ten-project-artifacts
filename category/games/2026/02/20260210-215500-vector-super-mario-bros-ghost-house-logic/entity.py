"""Game entities: player, ghosts, key, door."""

import pygame
import math
from config import (
    TILE_SIZE, GRAVITY, JUMP_FORCE, MOVE_SPEED, MAX_FALL_SPEED,
    GHOST_MOVE_SPEED, GHOST_STOP_DISTANCE,
    COLOR_PLAYER, COLOR_PLAYER_FACING, COLOR_GHOST,
    COLOR_GHOST_TRANSPARENT, COLOR_KEY, COLOR_DOOR, COLOR_DOOR_LOCKED
)


class Player:
    """Player entity with physics and movement."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 28)
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True  # Determines if watching ghosts
        self.alive = True
        self.has_key = False

    def update(self, keys, walls, platforms):
        """Update player position and handle input."""
        if not self.alive:
            return

        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -MOVE_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.vel_x = MOVE_SPEED
            self.facing_right = True

        # Jump
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            if self.on_ground:
                self.vel_y = JUMP_FORCE
                self.on_ground = False

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        # Move and collide
        self._move_and_collide(walls, platforms)

        # Check if fell in pit
        if self.rect.y > 700:
            self.alive = False

    def _move_and_collide(self, walls, platforms):
        """Handle movement with collision detection."""
        # All solid surfaces
        all_solids = walls + platforms

        # Horizontal
        self.rect.x += self.vel_x
        for solid in all_solids:
            if self.rect.colliderect(solid):
                if self.vel_x > 0:
                    self.rect.right = solid.left
                elif self.vel_x < 0:
                    self.rect.left = solid.right

        # Vertical
        self.rect.y += self.vel_y
        self.on_ground = False
        for solid in all_solids:
            if self.rect.colliderect(solid):
                if self.vel_y > 0:
                    self.rect.bottom = solid.top
                    self.vel_y = 0
                    self.on_ground = True
                elif self.vel_y < 0:
                    self.rect.top = solid.bottom
                    self.vel_y = 0

    def draw(self, surface):
        """Draw player with facing direction indicator."""
        color = COLOR_PLAYER_FACING if self.facing_right else COLOR_PLAYER
        if not self.facing_right:
            color = COLOR_PLAYER

        # Body
        pygame.draw.rect(surface, color, self.rect)
        # Eye indicator for facing direction
        eye_x = self.rect.right - 8 if self.facing_right else self.rect.left + 2
        pygame.draw.circle(surface, (255, 255, 255), (eye_x, self.rect.y + 8), 4)


class Ghost:
    """Ghost enemy that moves when player looks away."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 24, 28)
        self.start_x = x
        self.start_y = y

    def update(self, player):
        """Move towards player only when not being watched."""
        dx = player.rect.centerx - self.rect.centerx
        dy = player.rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)

        # Check if player is watching the ghost
        # Player watches right and ghost is to the right
        watching = False
        if player.facing_right and dx > 0:
            watching = True
        elif not player.facing_right and dx < 0:
            watching = True

        # Only move if not being watched
        if not watching and dist > GHOST_STOP_DISTANCE:
            move_x = (dx / dist) * GHOST_MOVE_SPEED if dist > 0 else 0
            move_y = (dy / dist) * GHOST_MOVE_SPEED if dist > 0 else 0
            self.rect.x += move_x
            self.rect.y += move_y

        return watching

    def draw(self, surface, is_watched):
        """Draw ghost - transparent when watched."""
        if is_watched:
            # Create transparent surface
            ghost_surf = pygame.Surface((24, 28), pygame.SRCALPHA)
            pygame.draw.ellipse(ghost_surf, COLOR_GHOST_TRANSPARENT, (0, 0, 24, 28))
            surface.blit(ghost_surf, self.rect.topleft)
        else:
            pygame.draw.ellipse(surface, COLOR_GHOST, self.rect)

        # Eyes
        pygame.draw.circle(surface, (0, 0, 0), (self.rect.x + 8, self.rect.y + 10), 3)
        pygame.draw.circle(surface, (0, 0, 0), (self.rect.x + 16, self.rect.y + 10), 3)


class Key:
    """Collectible key object."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 20, 20)
        self.collected = False
        self.bob_offset = 0

    def update(self):
        """Animate bobbing."""
        self.bob_offset = math.sin(pygame.time.get_ticks() * 0.005) * 3

    def draw(self, surface):
        """Draw key with bobbing animation."""
        if not self.collected:
            y = self.rect.y + self.bob_offset
            # Key shape
            pygame.draw.rect(surface, COLOR_KEY, (self.rect.x, y, 20, 12), border_radius=3)
            pygame.draw.circle(surface, COLOR_KEY, (self.rect.right - 4, y + 6), 5, 2)


class Door:
    """Exit door that unlocks with key."""

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 40)

    def draw(self, surface, has_key):
        """Draw door - different color when locked."""
        color = COLOR_DOOR if has_key else COLOR_DOOR_LOCKED
        pygame.draw.rect(surface, color, self.rect)
        # Door frame
        pygame.draw.rect(surface, (50, 50, 50), self.rect, 3)
        # Handle
        handle_color = (255, 215, 0) if has_key else (100, 50, 0)
        pygame.draw.circle(surface, handle_color, (self.rect.right - 8, self.rect.centery), 4)
