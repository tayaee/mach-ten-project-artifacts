"""Game entities for Vector Kung Fu Master."""

import pygame
from constants import *


class Entity:
    """Base class for all game entities."""

    def __init__(self, x, y, width, height, color):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vx = 0
        self.vy = 0
        self.alive = True

    def get_rect(self):
        """Return the collision rect."""
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        """Draw the entity."""
        if self.alive:
            pygame.draw.rect(surface, self.color, (self.x, self.y, self.width, self.height))


class Player(Entity):
    """The player character."""

    def __init__(self):
        super().__init__(100, FLOOR_Y - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, COLOR_PLAYER)
        self.hp = MAX_HP
        self.facing_right = True
        self.is_jumping = False
        self.is_crouching = False
        self.is_attacking = False
        self.attack_type = None  # 'punch' or 'kick'
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.invincible_timer = 0

    def update(self):
        """Update player state."""
        # Apply gravity
        if self.is_jumping:
            self.vy += GRAVITY
            self.y += self.vy

            if self.y >= FLOOR_Y - self.height:
                self.y = FLOOR_Y - self.height
                self.is_jumping = False
                self.vy = 0

        # Move horizontally
        self.x += self.vx
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

        # Update attack
        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0:
                self.is_attacking = False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Update invincibility
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def attack(self, attack_type):
        """Start an attack."""
        if self.attack_cooldown == 0 and not self.is_crouching:
            self.is_attacking = True
            self.attack_type = attack_type
            self.attack_timer = 15 if attack_type == 'punch' else 20
            self.attack_cooldown = 25

    def get_attack_rect(self):
        """Get the attack hitbox."""
        if not self.is_attacking:
            return None

        range_val = PUNCH_RANGE if self.attack_type == 'punch' else KICK_RANGE
        offset = self.width if self.facing_right else -range_val

        if self.attack_type == 'punch':
            return pygame.Rect(
                self.x + offset,
                self.y + 10,
                range_val,
                20
            )
        else:  # kick
            return pygame.Rect(
                self.x + offset,
                self.y + self.height - 25,
                range_val,
                20
            )

    def take_damage(self, amount):
        """Take damage if not invincible."""
        if self.invincible_timer == 0:
            self.hp -= amount
            self.invincible_timer = 60
            return True
        return False

    def draw(self, surface):
        """Draw the player with visual feedback."""
        if self.invincible_timer > 0 and self.invincible_timer % 4 < 2:
            return  # Flash effect

        # Draw body
        draw_y = self.y + (self.height // 2) if self.is_crouching else self.y
        draw_height = self.height // 2 if self.is_crouching else self.height

        pygame.draw.rect(surface, self.color, (self.x, draw_y, self.width, draw_height))

        # Draw attack indicator
        if self.is_attacking:
            attack_rect = self.get_attack_rect()
            if attack_rect:
                color = (255, 255, 0) if self.attack_type == 'punch' else (255, 150, 0)
                pygame.draw.rect(surface, color, attack_rect, 2)


class Enemy(Entity):
    """Base enemy class."""

    def __init__(self, x, y, width, height, color, enemy_type):
        super().__init__(x, y, width, height, color)
        self.enemy_type = enemy_type
        self.hp = 50 if enemy_type == 'boss' else 25
        self.max_hp = self.hp
        self.speed = 2 if enemy_type == 'boss' else 3
        self.direction = 1  # 1 = right, -1 = left
        self.attack_cooldown = 0
        self.state = 'move'  # 'move' or 'attack'
        self.attack_timer = 0

    def update(self, player_x):
        """Update enemy AI."""
        if not self.alive:
            return

        # Simple AI: move toward player
        dx = player_x - self.x

        if abs(dx) > 40:
            self.direction = 1 if dx > 0 else -1
            self.x += self.direction * self.speed
        else:
            # Attack when close
            if self.attack_cooldown == 0:
                self.state = 'attack'
                self.attack_timer = 30
                self.attack_cooldown = 90

        # Keep on screen
        self.x = max(0, min(self.x, SCREEN_WIDTH - self.width))

        if self.attack_timer > 0:
            self.attack_timer -= 1
            if self.attack_timer == 0:
                self.state = 'move'

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

    def is_attacking(self):
        """Check if enemy is currently attacking."""
        return self.state == 'attack' and self.attack_timer > 20

    def draw(self, surface):
        """Draw the enemy."""
        if not self.alive:
            return

        super().draw(surface)

        # Draw health bar
        if self.hp < self.max_hp:
            bar_width = self.width
            bar_height = 4
            health_pct = self.hp / self.max_hp
            pygame.draw.rect(surface, COLOR_HEALTH_BG, (self.x, self.y - 8, bar_width, bar_height))
            pygame.draw.rect(surface, COLOR_HEALTH_BAR, (self.x, self.y - 8, bar_width * health_pct, bar_height))


class Projectile(Entity):
    """Knife projectile thrown by enemies."""

    def __init__(self, x, y, direction):
        super().__init__(x, y, 15, 8, COLOR_PROJECTILE)
        self.direction = direction  # 1 = right, -1 = left
        self.speed = 8

    def update(self):
        """Update projectile position."""
        self.x += self.direction * self.speed

        # Remove if off screen
        if self.x < -50 or self.x > SCREEN_WIDTH + 50:
            self.alive = False

    def draw(self, surface):
        """Draw the projectile."""
        if self.alive:
            pygame.draw.polygon(surface, self.color, [
                (self.x, self.y + 4),
                (self.x + self.width, self.y),
                (self.x + self.width, self.y + self.height),
                (self.x, self.y + self.height - 4)
            ])
