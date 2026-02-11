"""Level layout with shifting walls and invisible platforms."""

import pygame
from config import TILE_SIZE


class Level:
    """Manages level layout, shifting walls, and invisible platforms."""

    def __init__(self):
        self.walls = []
        self.shifting_walls = []  # Walls that appear/disappear
        self.platforms = []
        self.invisible_platforms = []  # Only visible near player
        self.pits = []  # Bottomless pit areas
        self.shift_phase = 0
        self.wall_shift_patterns = []

        self._build_level()

    def _build_level(self):
        """Construct the ghost house level layout."""

        # Outer walls (static)
        for y in range(0, 18):
            self.walls.append((0 * TILE_SIZE, y * TILE_SIZE))  # Left wall
            self.walls.append((24 * TILE_SIZE, y * TILE_SIZE))  # Right wall

        # Floor (with pits)
        floor_segments = [
            (1, 8),  # Safe floor
            (11, 12),  # Gap/pit
            (13, 23),  # Safe floor to door
        ]

        for start, end in floor_segments:
            for x in range(start, end):
                self.walls.append((x * TILE_SIZE, 17 * TILE_SIZE))

        # Ceiling
        for x in range(1, 24):
            self.walls.append((x * TILE_SIZE, 0))

        # ===== STATIC WALLS =====
        # Create maze-like structure
        static_wall_layout = [
            # Left room dividers
            (4, 3, 4, 8),
            (4, 11, 4, 14),
            # Middle structure
            (10, 2, 10, 6),
            (10, 10, 10, 12),
            # Right room
            (16, 3, 16, 8),
            (16, 11, 16, 15),
            # Horizontal dividers
            (7, 5, 9, 5),
            (13, 8, 15, 8),
        ]

        for layout in static_wall_layout:
            x1, y1, x2, y2 = layout
            if x1 == x2:  # Vertical
                for y in range(y1, y2 + 1):
                    self.walls.append((x1 * TILE_SIZE, y * TILE_SIZE))
            else:  # Horizontal
                for x in range(x1, x2 + 1):
                    self.walls.append((x * TILE_SIZE, y1 * TILE_SIZE))

        # ===== SHIFTING WALLS =====
        # Phase 1: Creates a barrier in middle-left
        phase1_walls = [
            (6, 6, 6, 10),
            (7, 7, 8, 7),
        ]

        # Phase 2: Creates a barrier in middle-right
        phase2_walls = [
            (18, 6, 18, 10),
            (17, 8, 19, 8),
        ]

        # Phase 3: Creates horizontal barrier
        phase3_walls = [
            (12, 12, 14, 12),
            (14, 10, 14, 11),
        ]

        self.wall_shift_patterns = [phase1_walls, phase2_walls, phase3_walls]
        self.shifting_walls = self._convert_layout_to_rects(phase1_walls)

        # ===== VISIBLE PLATFORMS =====
        platform_layout = [
            (2, 14, 5, 14),
            (7, 10, 9, 10),
            (11, 5, 13, 5),
            (17, 12, 20, 12),
        ]

        for layout in platform_layout:
            x1, y1, x2, y2 = layout
            for x in range(x1, x2 + 1):
                self.platforms.append((x * TILE_SIZE, y1 * TILE_SIZE))

        # ===== INVISIBLE PLATFORMS =====
        # These only appear when player is near
        invisible_layout = [
            (2, 8, 3, 8),   # Early hidden platform
            (20, 4, 21, 4), # Upper right platform
            (12, 15, 14, 15), # Near door platform
        ]

        for layout in invisible_layout:
            x1, y1, x2, y2 = layout
            for x in range(x1, x2 + 1):
                self.invisible_platforms.append((x * TILE_SIZE, y1 * TILE_SIZE))

    def _convert_layout_to_rects(self, layout):
        """Convert layout coordinates to rect positions."""
        rects = []
        for wall_def in layout:
            x1, y1, x2, y2 = wall_def
            if x1 == x2:  # Vertical
                for y in range(y1, y2 + 1):
                    rects.append((x1 * TILE_SIZE, y * TILE_SIZE))
            else:  # Horizontal
                for x in range(x1, x2 + 1):
                    rects.append((x * TILE_SIZE, y1 * TILE_SIZE))
        return rects

    def update_walls(self, current_time):
        """Update shifting walls based on time."""
        phase_index = (current_time // 10000) % len(self.wall_shift_patterns)
        if phase_index != self.shift_phase:
            self.shift_phase = phase_index
            pattern = self.wall_shift_patterns[phase_index]
            self.shifting_walls = self._convert_layout_to_rects(pattern)

    def get_wall_rects(self):
        """Get all wall rects as pygame.Rect objects."""
        return [pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) for x, y in self.walls]

    def get_shifting_wall_rects(self):
        """Get shifting wall rects."""
        return [pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) for x, y in self.shifting_walls]

    def get_platform_rects(self):
        """Get visible platform rects."""
        return [pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) for x, y in self.platforms]

    def get_nearby_invisible_platforms(self, player_rect, radius_tiles):
        """Get invisible platforms within radius of player."""
        nearby = []
        player_center = player_rect.center
        radius = radius_tiles * TILE_SIZE

        for x, y in self.invisible_platforms:
            plat_rect = pygame.Rect(x, y, TILE_SIZE, TILE_SIZE)
            plat_center = plat_rect.center
            dist = ((plat_center[0] - player_center[0]) ** 2 +
                   (plat_center[1] - player_center[1]) ** 2) ** 0.5
            if dist <= radius:
                nearby.append(plat_rect)

        return nearby

    def get_all_invisible_platform_rects(self):
        """Get all invisible platform rects (for collision)."""
        return [pygame.Rect(x, y, TILE_SIZE, TILE_SIZE) for x, y in self.invisible_platforms]
