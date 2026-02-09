"""Player class for Vector Boulder Dash Logic."""

import pygame
from config import *


class Player:
    """Represents the player/digger character."""

    def __init__(self, start_x, start_y):
        self.x = start_x
        self.y = start_y
        self.start_x = start_x
        self.start_y = start_y

    def reset(self):
        """Reset player to starting position."""
        self.x = self.start_x
        self.y = self.start_y

    def move(self, dx, dy, grid):
        """
        Attempt to move the player.

        Returns: (moved, diamond_collected, at_exit)
        """
        new_x = self.x + dx
        new_y = self.y + dy

        if not grid.is_valid_pos(new_x, new_y):
            return False, False, False

        tile = grid.get_tile(new_x, new_y)

        # Check for walls and rocks
        if tile == TILE_WALL:
            return False, False, False

        if tile == TILE_ROCK:
            # Try to push rock horizontally
            if dy == 0 and grid.push_rock(new_x, new_y, dx):
                self.x = new_x
                return True, False, False
            return False, False, False

        if tile == TILE_EXIT_OPEN:
            self.x = new_x
            self.y = new_y
            return True, False, True

        if grid.is_walkable(new_x, new_y):
            self.x = new_x
            self.y = new_y
            diamond_collected = grid.dig(new_x, new_y)
            return True, diamond_collected, False

        return False, False, False

    def get_pixel_pos(self):
        """Get pixel position for rendering."""
        px = GRID_OFFSET_X + self.x * CELL_SIZE
        py = GRID_OFFSET_Y + self.y * CELL_SIZE
        return px, py

    def get_rect(self):
        """Get collision rect for rendering."""
        px, py = self.get_pixel_pos()
        return pygame.Rect(px + 4, py + 4, CELL_SIZE - 8, CELL_SIZE - 8)
