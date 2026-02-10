"""Paper plane entity with physics."""

import pygame
from config import *


class Plane:
    """Player-controlled paper plane with glide physics."""

    def __init__(self):
        self.x = PLANE_START_X
        self.y = PLANE_START_Y
        self.velocity = 0.0
        self.lifting = False
        self.width = PLANE_WIDTH
        self.height = PLANE_HEIGHT

    def reset(self):
        """Reset plane to initial state."""
        self.x = PLANE_START_X
        self.y = PLANE_START_Y
        self.velocity = 0.0
        self.lifting = False

    def start_lift(self):
        """Start applying lift force."""
        self.lifting = True

    def end_lift(self):
        """Stop applying lift force."""
        self.lifting = False

    def update(self):
        """Update plane physics."""
        if self.lifting:
            self.velocity += LIFT_FORCE
        else:
            self.velocity += GRAVITY

        # Clamp velocity
        self.velocity = max(-TERMINAL_VELOCITY, min(TERMINAL_VELOCITY, self.velocity))

        # Apply drag for smoother gliding
        self.velocity *= 0.98

        self.y += self.velocity

    def get_rect(self):
        """Get collision rectangle."""
        # Smaller hitbox for fairness
        hitbox_padding = 4
        return pygame.Rect(
            self.x + hitbox_padding,
            self.y + hitbox_padding,
            self.width - hitbox_padding * 2,
            self.height - hitbox_padding * 2
        )

    def get_center(self):
        """Get center point of plane."""
        return (self.x + self.width // 2, self.y + self.height // 2)

    def draw(self, screen):
        """Draw the paper plane as a simple triangle."""
        # Nose of the plane
        nose = (self.x + self.width, self.y + self.height // 2)
        # Top corner
        top = (self.x, self.y)
        # Bottom corner
        bottom = (self.x, self.y + self.height)
        # Tail notch (folded paper look)
        tail = (self.x + 8, self.y + self.height // 2)

        # Draw main body
        pygame.draw.polygon(screen, PLANE_COLOR, [nose, top, tail, bottom])
        # Draw outline
        pygame.draw.polygon(screen, CAVE_COLOR, [nose, top, tail, bottom], 2)
