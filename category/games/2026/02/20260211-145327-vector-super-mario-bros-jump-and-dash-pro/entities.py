"""Game entities: Player, Platform, Spike, Goal."""

import pygame
from config import (
    PLAYER_WIDTH, PLAYER_HEIGHT, GROUND_Y,
    GRAVITY, MAX_FALL_SPEED, JUMP_FORCE, JUMP_HOLD_FORCE, MAX_JUMP_HOLD_TIME,
    ACCELERATION, FRICTION, MAX_RUN_SPEED, INITIAL_MOVE_SPEED,
    COLOR_PLATFORM, COLOR_SPIKE, COLOR_GOAL, COLOR_GOAL_FLAG,
    COLOR_PLAYER, COLOR_PLAYER_ACCEL,
    GOAL_X, LEVEL_WIDTH
)


class Player:
    """Player character with momentum-based physics."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.on_ground = False
        self.facing_right = True
        self.jump_held = False
        self.jump_hold_timer = 0
        self.move_hold_timer = 0
        self.alive = True
        self.finished = False
        self.start_x = x
        self.start_y = y
        self.max_distance = 0

    def reset(self):
        """Reset player to starting position."""
        self.x = self.start_x
        self.y = self.start_y
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.alive = True
        self.finished = False

    def update(self, keys, platforms):
        """Update player physics and input."""
        if not self.alive or self.finished:
            return

        # Horizontal input with momentum
        move_direction = 0
        if keys[pygame.K_LEFT]:
            move_direction = -1
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            move_direction = 1
            self.facing_right = True

        # Accelerate in movement direction
        if move_direction != 0:
            self.move_hold_timer += 1
            # Speed builds up over time (running momentum)
            target_speed = INITIAL_MOVE_SPEED + min(MAX_RUN_SPEED - INITIAL_MOVE_SPEED,
                                                     self.move_hold_timer * 0.1)
            if move_direction > 0:
                self.vel_x += ACCELERATION
                if self.vel_x > target_speed:
                    self.vel_x = target_speed
            else:
                self.vel_x -= ACCELERATION
                if self.vel_x < -target_speed:
                    self.vel_x = -target_speed
        else:
            self.move_hold_timer = 0
            self.vel_x *= FRICTION
            if abs(self.vel_x) < 0.1:
                self.vel_x = 0

        # Apply horizontal velocity
        self.x += self.vel_x

        # Screen bounds (left only, right is level bound)
        if self.x < 0:
            self.x = 0
            self.vel_x = 0

        if self.x > LEVEL_WIDTH - self.width:
            self.x = LEVEL_WIDTH - self.width
            self.vel_x = 0

        # Jump input (variable jump height)
        jumping = keys[pygame.K_SPACE]

        if jumping and not self.jump_held and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False
            self.jump_held = True
            self.jump_hold_timer = 0

        if not jumping:
            self.jump_held = False

        # Variable jump height - hold longer for higher jump
        if self.jump_held and not self.on_ground and self.jump_hold_timer < MAX_JUMP_HOLD_TIME:
            self.vel_y += JUMP_HOLD_FORCE
            self.jump_hold_timer += 1

        # Apply gravity
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.y += self.vel_y

        # Check if fallen off level
        if self.y > SCREEN_HEIGHT + 100:
            self.alive = False

        # Track max distance
        if self.x > self.max_distance:
            self.max_distance = self.x

        # Platform collision
        self.on_ground = False
        player_rect = self.get_hitbox()

        for platform in platforms:
            if player_rect.colliderect(platform.get_hitbox()):
                # Land on top
                if self.vel_y > 0 and self.y + self.height - self.vel_y <= platform.y + 5:
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.on_ground = True
                # Hit from below
                elif self.vel_y < 0 and self.y - self.vel_y >= platform.y + platform.height - 5:
                    self.y = platform.y + platform.height
                    self.vel_y = 0
                # Hit from side
                else:
                    if self.vel_x > 0:
                        self.x = platform.x - self.width
                    elif self.vel_x < 0:
                        self.x = platform.x + platform.width
                    self.vel_x = 0

    def get_hitbox(self):
        """Return player collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface, camera_x):
        """Draw player at camera-relative position."""
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y)

        # Body
        color = COLOR_PLAYER_ACCEL if self.move_hold_timer > 30 else COLOR_PLAYER
        pygame.draw.rect(surface, color, (draw_x, draw_y, self.width, self.height))

        # Direction indicator (small line showing facing)
        eye_x = draw_x + (18 if self.facing_right else 4)
        pygame.draw.line(surface, (255, 255, 255), (eye_x, draw_y + 8),
                        (eye_x + (4 if self.facing_right else -4), draw_y + 8), 2)

        # Acceleration indicator
        if self.move_hold_timer > 30:
            pygame.draw.circle(surface, (255, 255, 0), (draw_x + self.width // 2, draw_y - 5), 3)


class Platform:
    """Static platform for player to stand on."""

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_hitbox(self):
        """Return platform collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface, camera_x):
        """Draw platform at camera-relative position."""
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y)

        # Platform body
        pygame.draw.rect(surface, COLOR_PLATFORM, (draw_x, draw_y, self.width, self.height))
        # Top highlight
        pygame.draw.rect(surface, (160, 120, 80), (draw_x, draw_y, self.width, 4))


class Spike:
    """Hazard that kills the player on contact."""

    def __init__(self, x, y, width=20):
        self.x = x
        self.y = y
        self.width = width
        self.height = 20

    def get_hitbox(self):
        """Return spike collision rectangle."""
        # Smaller hitbox for fairness
        return pygame.Rect(int(self.x) + 4, int(self.y) + 8, self.width - 8, self.height - 8)

    def draw(self, surface, camera_x):
        """Draw spike at camera-relative position."""
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y)

        # Draw triangle spike
        points = [
            (draw_x, draw_y + self.height),
            (draw_x + self.width // 2, draw_y),
            (draw_x + self.width, draw_y + self.height)
        ]
        pygame.draw.polygon(surface, COLOR_SPIKE, points)
        pygame.draw.polygon(surface, (80, 80, 90), points, 2)


class Pit:
    """Gap in the ground that kills the player."""

    def __init__(self, x, width):
        self.x = x
        self.width = width
        self.y = GROUND_Y
        self.height = SCREEN_HEIGHT - GROUND_Y

    def draw(self, surface, camera_x):
        """Draw pit as dark area at camera-relative position."""
        draw_x = int(self.x - camera_x)
        pygame.draw.rect(surface, (30, 30, 50), (draw_x, self.y, self.width, self.height))


class Goal:
    """Goal post that player must reach."""

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 10
        self.height = 120
        self.flag_width = 40
        self.flag_height = 30

    def get_hitbox(self):
        """Return goal collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface, camera_x):
        """Draw goal post at camera-relative position."""
        draw_x = int(self.x - camera_x)
        draw_y = int(self.y)

        # Pole
        pygame.draw.rect(surface, COLOR_GOAL, (draw_x, draw_y, self.width, self.height))

        # Flag
        flag_points = [
            (draw_x + self.width, draw_y + 10),
            (draw_x + self.width + self.flag_width, draw_y + 10 + self.flag_height // 2),
            (draw_x + self.width, draw_y + 10 + self.flag_height)
        ]
        pygame.draw.polygon(surface, COLOR_GOAL_FLAG, flag_points)

        # Base
        pygame.draw.rect(surface, (40, 150, 40), (draw_x - 10, draw_y + self.height - 10, 30, 10))


# Import SCREEN_HEIGHT after config to avoid circular dependency
from config import SCREEN_HEIGHT
