"""Block entity for the brick stacking game."""

import math
import random
from typing import Tuple
import pygame
from config import Colors, BlockSizes


class Block:
    """Represents a rectangular block with physical properties."""

    def __init__(self, x: float, y: float, width: int, height: int,
                 color: Tuple[int, int, int], border_color: Tuple[int, int, int],
                 rotation: int = 0):
        """Initialize a block.

        Args:
            x: X position of the center of mass
            y: Y position of the center of mass
            width: Width of the block
            height: Height of the block
            color: Fill color (R, G, B)
            border_color: Border color (R, G, B)
            rotation: Rotation in degrees (0, 90, 180, 270)
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.border_color = border_color
        self.rotation = rotation
        self.velocity_y = 0.0
        self.is_falling = True
        self.is_landed = False
        self.mass = width * height

    def get_corners(self) -> list[Tuple[float, float]]:
        """Get the corners of the rotated block.

        Returns:
            List of (x, y) tuples for the four corners in counter-clockwise order.
        """
        w = self.width / 2
        h = self.height / 2

        # Unrotated corners relative to center
        corners = [(-w, -h), (w, -h), (w, h), (-w, h)]

        # Apply rotation
        rad = math.radians(self.rotation)
        cos_a = math.cos(rad)
        sin_a = math.sin(rad)

        rotated_corners = []
        for cx, cy in corners:
            rx = cx * cos_a - cy * sin_a
            ry = cx * sin_a + cy * cos_a
            rotated_corners.append((self.x + rx, self.y + ry))

        return rotated_corners

    def get_bounds(self) -> Tuple[float, float, float, float]:
        """Get the axis-aligned bounding box.

        Returns:
            (min_x, min_y, max_x, max_y)
        """
        corners = self.get_corners()
        min_x = min(c[0] for c in corners)
        max_x = max(c[0] for c in corners)
        min_y = min(c[1] for c in corners)
        max_y = max(c[1] for c in corners)
        return (min_x, min_y, max_x, max_y)

    def get_bounding_polygon(self) -> list[Tuple[float, float]]:
        """Get the polygon for collision detection."""
        return self.get_corners()

    def rotate(self, direction: int = 1):
        """Rotate the block by 90 degrees.

        Args:
            direction: 1 for clockwise, -1 for counter-clockwise
        """
        self.rotation = (self.rotation + 90 * direction) % 360

    def update(self, gravity: float, fall_speed: float):
        """Update block position while falling.

        Args:
            gravity: Gravity acceleration
            fall_speed: Current falling speed cap
        """
        if self.is_falling:
            self.velocity_y += gravity
            if self.velocity_y > fall_speed:
                self.velocity_y = fall_speed
            self.y += self.velocity_y

    def draw(self, surface: pygame.Surface):
        """Draw the block on the given surface.

        Args:
            surface: Pygame surface to draw on
        """
        corners = self.get_corners()
        pygame.draw.polygon(surface, self.color, corners)
        pygame.draw.polygon(surface, self.border_color, corners, 2)

        # Draw center of mass indicator
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x), int(self.y)), 3)

    def get_rotated_dimensions(self) -> Tuple[int, int]:
        """Get the dimensions after rotation.

        Returns:
            (width, height) after rotation
        """
        if self.rotation % 180 == 0:
            return (self.width, self.height)
        else:
            return (self.height, self.width)


class BlockSpawner:
    """Spawns new falling blocks with random properties."""

    def __init__(self, screen_width: int, spawn_y: float):
        """Initialize the block spawner.

        Args:
            screen_width: Width of the game screen
            spawn_y: Y position where blocks spawn
        """
        self.screen_width = screen_width
        self.spawn_y = spawn_y
        self.colors = Colors
        self.sizes = BlockSizes.VARIANTS

    def spawn_block(self) -> Block:
        """Create a new falling block.

        Returns:
            A new Block instance at the spawn position
        """
        width, height = random.choice(self.sizes)

        # Position at center of screen horizontally
        x = self.screen_width / 2

        # Random rotation (0, 90, 180, or 270 degrees)
        rotation = random.choice([0, 90, 180, 270])

        return Block(
            x=x,
            y=self.spawn_y,
            width=width,
            height=height,
            color=self.colors.FALLING_BLOCK,
            border_color=self.colors.FALLING_BLOCK_BORDER,
            rotation=rotation
        )

    def spawn_landed_block(self, x: float, y: float, width: int, height: int,
                           rotation: int = 0) -> Block:
        """Create a landed block (already on the stack).

        Args:
            x: X position
            y: Y position
            width: Block width
            height: Block height
            rotation: Block rotation

        Returns:
            A new Block instance representing a landed block
        """
        return Block(
            x=x,
            y=y,
            width=width,
            height=height,
            color=self.colors.BLOCK,
            border_color=self.colors.BLOCK_BORDER,
            rotation=rotation
        )
