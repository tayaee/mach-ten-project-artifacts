"""Physics calculations for the brick stacking game."""

from typing import Tuple, List
import pygame
from block import Block
from config import Physics


class PhysicsEngine:
    """Handles collision detection and balance calculations."""

    @staticmethod
    def point_in_polygon(point: Tuple[float, float], polygon: List[Tuple[float, float]]) -> bool:
        """Check if a point is inside a polygon using ray casting.

        Args:
            point: (x, y) point to check
            polygon: List of polygon vertices

        Returns:
            True if point is inside polygon
        """
        x, y = point
        n = len(polygon)
        inside = False

        for i in range(n):
            j = (i - 1) % n
            xi, yi = polygon[i]
            xj, yj = polygon[j]

            if ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi) + xi):
                inside = not inside

        return inside

    @staticmethod
    def polygons_intersect(poly1: List[Tuple[float, float]],
                          poly2: List[Tuple[float, float]]) -> bool:
        """Check if two convex polygons intersect using SAT.

        Args:
            poly1: First polygon vertices
            poly2: Second polygon vertices

        Returns:
            True if polygons intersect
        """
        # Get all unique axes (normals to edges)
        axes = []

        for poly in [poly1, poly2]:
            for i in range(len(poly)):
                j = (i + 1) % len(poly)
                edge = (poly[j][0] - poly[i][0], poly[j][1] - poly[i][1])
                # Normal is perpendicular to edge
                normal = (-edge[1], edge[0])
                length = (normal[0]**2 + normal[1]**2)**0.5
                if length > 0:
                    axes.append((normal[0] / length, normal[1] / length))

        # Check for separation on each axis
        for axis in axes:
            min1 = max1 = poly1[0][0] * axis[0] + poly1[0][1] * axis[1]
            for point in poly1[1:]:
                proj = point[0] * axis[0] + point[1] * axis[1]
                min1 = min(min1, proj)
                max1 = max(max1, proj)

            min2 = max2 = poly2[0][0] * axis[0] + poly2[0][1] * axis[1]
            for point in poly2[1:]:
                proj = point[0] * axis[0] + point[1] * axis[1]
                min2 = min(min2, proj)
                max2 = max(max2, proj)

            if max1 < min2 or max2 < min1:
                return False  # Separating axis found, no collision

        return True  # No separating axis, collision detected

    @staticmethod
    def check_collision(block1: Block, block2: Block) -> bool:
        """Check if two blocks collide.

        Args:
            block1: First block
            block2: Second block

        Returns:
            True if blocks intersect
        """
        poly1 = block1.get_bounding_polygon()
        poly2 = block2.get_bounding_polygon()
        return PhysicsEngine.polygons_intersect(poly1, poly2)

    @staticmethod
    def calculate_center_of_mass(blocks: List[Block]) -> Tuple[float, float]:
        """Calculate the combined center of mass of stacked blocks.

        Args:
            blocks: List of landed blocks

        Returns:
            (center_x, center_y) of combined center of mass
        """
        if not blocks:
            return (0.0, 0.0)

        total_mass = sum(block.mass for block in blocks)
        weighted_x = sum(block.x * block.mass for block in blocks)
        weighted_y = sum(block.y * block.mass for block in blocks)

        return (weighted_x / total_mass, weighted_y / total_mass)

    @staticmethod
    def check_balance(blocks: List[Block], platform_center_x: float,
                     platform_half_width: float, tolerance: float) -> bool:
        """Check if the stack is balanced on the platform.

        Args:
            blocks: List of landed blocks
            platform_center_x: X coordinate of platform center
            platform_half_width: Half the platform width
            tolerance: Balance tolerance (0-1)

        Returns:
            True if stack is balanced
        """
        if not blocks:
            return True

        com_x, _ = PhysicsEngine.calculate_center_of_mass(blocks)

        # Check if center of mass is within tolerance fraction of platform width
        offset = abs(com_x - platform_center_x)
        max_offset = platform_half_width * tolerance

        return offset <= max_offset

    @staticmethod
    def get_balance_status(blocks: List[Block], platform_center_x: float,
                          platform_half_width: float, tolerance: float) -> str:
        """Get the current balance status.

        Args:
            blocks: List of landed blocks
            platform_center_x: X coordinate of platform center
            platform_half_width: Half the platform width
            tolerance: Balance tolerance (0-1)

        Returns:
            "stable", "unstable", or "collapsed"
        """
        if not blocks:
            return "stable"

        com_x, _ = PhysicsEngine.calculate_center_of_mass(blocks)
        offset = abs(com_x - platform_center_x)
        max_offset = platform_half_width * tolerance

        if offset > platform_half_width:
            return "collapsed"
        elif offset > max_offset * 0.7:
            return "unstable"
        else:
            return "stable"

    @staticmethod
    def find_landing_position(falling_block: Block, landed_blocks: List[Block],
                               platform_top_y: float) -> float:
        """Find the Y position where the falling block should land.

        Args:
            falling_block: The falling block
            landed_blocks: List of already landed blocks
            platform_top_y: Y position of the top of the platform

        Returns:
            Y position where the block should land
        """
        # Start from platform top
        land_y = platform_top_y - falling_block.height / 2

        # Check collision with each landed block from bottom up
        sorted_blocks = sorted(landed_blocks, key=lambda b: b.y, reverse=True)

        for block in sorted_blocks:
            block_min_y = block.y - block.height / 2

            # Temporarily position falling block to check collision
            temp_y = block_min_y - falling_block.height / 2
            test_block = Block(
                x=falling_block.x,
                y=temp_y,
                width=falling_block.width,
                height=falling_block.height,
                color=(0, 0, 0),
                border_color=(0, 0, 0),
                rotation=falling_block.rotation
            )

            # Check horizontal overlap first
            b1 = falling_block.get_bounds()
            b2 = block.get_bounds()
            horizontal_overlap = not (b1[2] < b2[0] or b1[0] > b2[2])

            if horizontal_overlap:
                if PhysicsEngine.check_collision(test_block, block):
                    # Found landing position
                    return temp_y

        return land_y

    @staticmethod
    def check_fall_off(blocks: List[Block], screen_height: float) -> bool:
        """Check if any block has fallen off the screen.

        Args:
            blocks: List of blocks to check
            screen_height: Height of the game screen

        Returns:
            True if any block fell off screen
        """
        for block in blocks:
            if not block.is_landed and block.y - block.height > screen_height:
                return True
        return False
