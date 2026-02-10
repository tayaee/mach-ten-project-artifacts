"""Procedurally generated cave corridor."""

import pygame
import random
import math
from config import *


class Corridor:
    """Scrolling cave corridor with smooth terrain."""

    def __init__(self):
        self.reset()

    def reset(self):
        """Reset corridor to initial state."""
        self.segments = []
        self.air_currents = []
        self.scroll_offset = 0
        self.scroll_speed = BASE_SCROLL_SPEED

        # Initialize starting segments
        self.generate_starting_cave()

    def generate_starting_cave(self):
        """Generate initial flat cave area."""
        gap_height = (MIN_GAP_HEIGHT + MAX_GAP_HEIGHT) // 2
        ceiling_y = (SCREEN_HEIGHT - gap_height) // 2
        floor_y = ceiling_y + gap_height

        for i in range(30):
            self.segments.append({
                'ceiling': ceiling_y,
                'floor': floor_y
            })

    def add_segment(self):
        """Add new segment at the end."""
        last = self.segments[-1]

        # Random gap height change
        gap_change = random.randint(-30, 30)
        new_gap = max(MIN_GAP_HEIGHT, min(MAX_GAP_HEIGHT,
                                          (last['floor'] - last['ceiling']) + gap_change))

        # Vertical position change (gradual)
        vertical_shift = random.randint(-20, 20)
        total_height = last['floor'] - last['ceiling']
        center_y = (last['ceiling'] + last['floor']) / 2 + vertical_shift * 0.3

        # Keep within screen bounds
        new_ceiling = max(50, min(SCREEN_HEIGHT // 2 - 50, center_y - new_gap / 2))
        new_floor = new_ceiling + new_gap

        self.segments.append({
            'ceiling': new_ceiling,
            'floor': new_floor
        })

        # Maybe spawn air current
        if random.random() < AIR_CURRENT_SPAWN_CHANCE:
            self.air_currents.append({
                'x': len(self.segments) * SEGMENT_WIDTH,
                'y': new_ceiling + new_gap / 2,
                'collected': False
            })

    def update(self, dt):
        """Update corridor scroll."""
        scroll_amount = self.scroll_speed * (dt / 16.67)
        self.scroll_offset += scroll_amount
        self.scroll_speed += SCROLL_SPEED_INCREMENT * (dt / 16.67)

        # Add new segments as needed
        while (len(self.segments) * SEGMENT_WIDTH) < (SCREEN_WIDTH + self.scroll_offset + 200):
            self.add_segment()

        # Remove old segments
        segments_to_remove = int(self.scroll_offset // SEGMENT_WIDTH)
        if segments_to_remove > 0:
            self.segments = self.segments[segments_to_remove:]
            self.scroll_offset %= SEGMENT_WIDTH

            # Update air currents positions
            for ac in self.air_currents:
                ac['x'] -= segments_to_remove * SEGMENT_WIDTH

        # Remove off-screen air currents
        self.air_currents = [ac for ac in self.air_currents if ac['x'] > -50]

    def check_collision(self, rect):
        """Check if rect collides with cave walls."""
        # Check each visible segment
        for i, seg in enumerate(self.segments):
            seg_x = i * SEGMENT_WIDTH - self.scroll_offset
            seg_rect = pygame.Rect(seg_x, 0, SEGMENT_WIDTH, SCREEN_HEIGHT)

            if seg_rect.colliderect(rect):
                # Check ceiling
                ceiling_rect = pygame.Rect(seg_x, 0, SEGMENT_WIDTH, seg['ceiling'])
                if ceiling_rect.colliderect(rect):
                    return True

                # Check floor
                floor_rect = pygame.Rect(seg_x, seg['floor'], SEGMENT_WIDTH, SCREEN_HEIGHT - seg['floor'])
                if floor_rect.colliderect(rect):
                    return True

        return False

    def check_air_current(self, center):
        """Check if plane center collects an air current."""
        cx, cy = center
        for ac in self.air_currents:
            if not ac['collected']:
                dist = math.sqrt((cx - ac['x']) ** 2 + (cy - ac['y']) ** 2)
                if dist < AIR_CURRENT_RADIUS + 10:
                    ac['collected'] = True
                    return True
        return False

    def draw(self, screen):
        """Draw the cave corridor."""
        # Draw ceiling
        ceiling_points = [(0, 0)]
        for i, seg in enumerate(self.segments):
            x = i * SEGMENT_WIDTH - self.scroll_offset
            ceiling_points.append((x, seg['ceiling']))
        ceiling_points.append((SCREEN_WIDTH, 0))

        if len(ceiling_points) > 2:
            pygame.draw.polygon(screen, CAVE_COLOR, ceiling_points)
            pygame.draw.lines(screen, CAVE_HIGHLIGHT, False, ceiling_points[1:-1], 2)

        # Draw floor
        floor_points = [(0, SCREEN_HEIGHT)]
        for i, seg in enumerate(self.segments):
            x = i * SEGMENT_WIDTH - self.scroll_offset
            floor_points.append((x, seg['floor']))
        floor_points.append((SCREEN_WIDTH, SCREEN_HEIGHT))

        if len(floor_points) > 2:
            pygame.draw.polygon(screen, CAVE_COLOR, floor_points)
            pygame.draw.lines(screen, CAVE_HIGHLIGHT, False, floor_points[1:-1], 2)

        # Draw air currents
        for ac in self.air_currents:
            if not ac['collected']:
                # Draw glow
                glow_surf = pygame.Surface((AIR_CURRENT_RADIUS * 4, AIR_CURRENT_RADIUS * 4), pygame.SRCALPHA)
                pygame.draw.circle(glow_surf, (*AIR_CURRENT_COLOR, 50),
                                 (AIR_CURRENT_RADIUS * 2, AIR_CURRENT_RADIUS * 2), AIR_CURRENT_RADIUS * 1.5)
                screen.blit(glow_surf, (ac['x'] - AIR_CURRENT_RADIUS * 2, ac['y'] - AIR_CURRENT_RADIUS * 2))

                # Draw core
                pygame.draw.circle(screen, AIR_CURRENT_COLOR, (int(ac['x']), int(ac['y'])), AIR_CURRENT_RADIUS)
                pygame.draw.circle(screen, WHITE, (int(ac['x']), int(ac['y'])), AIR_CURRENT_RADIUS - 3)

    def get_distance(self):
        """Get total distance traveled."""
        return int(self.scroll_offset)
