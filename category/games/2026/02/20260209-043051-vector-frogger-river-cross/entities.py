"""Game entities for Vector Frogger River Cross."""

import pygame
from config import *


class Frog:
    """The player character frog."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset frog to starting position."""
        self.grid_x = COLS // 2
        self.grid_y = START_ROW
        self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
        self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2
        self.alive = True
        self.on_log = False
        self.log_speed = 0
        self.move_cooldown = 0

    def move(self, dx, dy):
        """Move frog by grid units."""
        if self.move_cooldown > 0 or not self.alive:
            return False

        new_x = self.grid_x + dx
        new_y = self.grid_y + dy

        if 0 <= new_x < COLS and 0 <= new_y < ROWS:
            self.grid_x = new_x
            self.grid_y = new_y
            self.x = self.grid_x * GRID_SIZE + GRID_SIZE // 2
            self.y = self.grid_y * GRID_SIZE + GRID_SIZE // 2
            self.move_cooldown = FROG_MOVE_COOLDOWN
            return True
        return False

    def update(self):
        """Update frog state."""
        if self.move_cooldown > 0:
            self.move_cooldown -= 1

        # Move with log if on one
        if self.on_log and self.alive:
            self.x += self.log_speed
            self.grid_x = int(self.x // GRID_SIZE)

    def draw(self, surface):
        """Draw the frog."""
        if not self.alive:
            return

        # Draw frog body
        rect = pygame.Rect(
            self.x - FROG_SIZE // 2,
            self.y - FROG_SIZE // 2,
            FROG_SIZE,
            FROG_SIZE
        )
        pygame.draw.rect(surface, COLOR_FROG, rect, border_radius=8)
        pygame.draw.rect(surface, COLOR_FROG_OUTLINE, rect, 2, border_radius=8)

        # Draw eyes
        eye_size = 7
        eye_offset = FROG_SIZE // 4
        eye_y_offset = FROG_SIZE // 5

        # Left eye
        pygame.draw.circle(
            surface, (255, 255, 255),
            (int(self.x - eye_offset), int(self.y - eye_y_offset)), eye_size
        )
        pygame.draw.circle(
            surface, (0, 0, 0),
            (int(self.x - eye_offset), int(self.y - eye_y_offset)), eye_size // 2
        )

        # Right eye
        pygame.draw.circle(
            surface, (255, 255, 255),
            (int(self.x + eye_offset), int(self.y - eye_y_offset)), eye_size
        )
        pygame.draw.circle(
            surface, (0, 0, 0),
            (int(self.x + eye_offset), int(self.y - eye_y_offset)), eye_size // 2
        )

    def get_rect(self):
        """Get collision rect for frog."""
        return pygame.Rect(
            self.x - FROG_SIZE // 2 + 4,
            self.y - FROG_SIZE // 2 + 4,
            FROG_SIZE - 8,
            FROG_SIZE - 8
        )


class Log:
    """A floating log in the river."""

    def __init__(self, row, x, size, speed):
        self.row = row
        self.x = x
        self.y = row * GRID_SIZE + GRID_SIZE // 2
        self.width = LOG_WIDTHS[size]
        self.height = LOG_HEIGHT
        self.speed = speed

    def update(self, speed_multiplier=1.0):
        """Update log position."""
        self.x += self.speed * speed_multiplier

        # Wrap around screen
        if self.speed > 0 and self.x > SCREEN_WIDTH + self.width:
            self.x = -self.width
        elif self.speed < 0 and self.x < -self.width:
            self.x = SCREEN_WIDTH + self.width

    def draw(self, surface):
        """Draw the log."""
        rect = pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )
        pygame.draw.rect(surface, COLOR_LOG, rect, border_radius=10)

        # Draw wood grain details
        grain_spacing = self.width // 4
        for i in range(1, 4):
            gx = self.x - self.width // 2 + i * grain_spacing
            if gx < self.x + self.width // 2:
                pygame.draw.line(
                    surface, COLOR_LOG_GRAIN,
                    (gx, self.y - self.height // 4),
                    (gx, self.y + self.height // 4), 2
                )

    def get_rect(self):
        """Get collision rect."""
        return pygame.Rect(
            self.x - self.width // 2,
            self.y - self.height // 2,
            self.width,
            self.height
        )


class Lane:
    """A horizontal lane containing logs."""

    def __init__(self, row, speed, log_size, spacing):
        self.row = row
        self.base_speed = speed
        self.logs = []

        # Create logs evenly spaced
        num_logs = 3
        for i in range(num_logs):
            x = (i * spacing * GRID_SIZE) % SCREEN_WIDTH
            self.logs.append(Log(row, x, log_size, speed))

    def update(self, speed_multiplier=1.0):
        """Update all logs in lane."""
        for log in self.logs:
            log.update(speed_multiplier)

    def draw(self, surface):
        """Draw all logs in lane."""
        for log in self.logs:
            log.draw(surface)

    def check_collision(self, frog_rect):
        """Check if frog collides with any log."""
        for log in self.logs:
            if log.get_rect().colliderect(frog_rect):
                return log
        return None
