"""
Vector graphics rendering for Track and Field Dash.
"""

import pygame
from game_state import State, GameState


class Colors:
    # Background
    SKY = (135, 206, 235)
    GRASS = (34, 139, 34)
    TRACK = (200, 100, 50)
    TRACK_LINES = (255, 255, 255)
    STADIUM_SEATS = (100, 100, 100)

    # UI
    TEXT = (255, 255, 255)
    TEXT_SHADOW = (0, 0, 0)
    STAMINA_HIGH = (0, 255, 0)
    STAMINA_MEDIUM = (255, 165, 0)
    STAMINA_LOW = (255, 0, 0)

    # Athlete
    ATHLETE_SKIN = (255, 200, 150)
    ATHLETE_UNIFORM = (255, 0, 0)
    ATHLETE_SHORTS = (0, 0, 255)

    # Effects
    STUMBLE_INDICATOR = (255, 50, 50)


class Renderer:
    """Handles all drawing operations."""

    def __init__(self, screen: pygame.Surface):
        self.screen = screen
        self.width, self.height = screen.get_size()
        self.font_large = pygame.font.Font(None, 48)
        self.font_medium = pygame.font.Font(None, 32)
        self.font_small = pygame.font.Font(None, 24)

        # Layout constants
        self.track_y = self.height - 100
        self.track_height = 60
        self.ground_y = self.track_y + self.track_height

    def draw_background(self):
        """Draw stadium environment."""
        # Sky
        self.screen.fill(Colors.SKY)

        # Stadium stands (background)
        stand_color = Colors.STADIUM_SEATS
        for row in range(5):
            y_pos = 50 + row * 30
            width = self.width - 100 + row * 20
            x_pos = 50 - row * 10
            rect = pygame.Rect(x_pos, y_pos, width, 25)
            pygame.draw.rect(self.screen, stand_color, rect)

        # Grass
        pygame.draw.rect(self.screen, Colors.GRASS,
                        (0, self.ground_y, self.width, self.height - self.ground_y))

        # Track
        track_rect = pygame.Rect(0, self.track_y, self.width, self.track_height)
        pygame.draw.rect(self.screen, Colors.TRACK, track_rect)

        # Track lane lines
        for i in range(1, 10):
            x = i * self.width // 10
            pygame.draw.line(self.screen, Colors.TRACK_LINES,
                           (x, self.track_y), (x, self.ground_y), 2)

    def draw_finish_line(self, distance_percent: float):
        """Draw the finish line at appropriate position."""
        finish_x = self.width * 0.9
        line_width = 5

        # Checkered pattern
        square_size = 10
        for i in range(0, self.track_height, square_size):
            color = Colors.TRACK_LINES if (i // square_size) % 2 == 0 else (0, 0, 0)
            pygame.draw.rect(self.screen, color,
                           (finish_x, self.track_y + i, line_width, square_size))

    def draw_athlete(self, state: State):
        """Draw the athlete at current position."""
        pixels_per_meter = 7.5
        athlete_x = 80 + state.distance * pixels_per_meter
        athlete_y = self.track_y + 10

        # Stumble effect
        if state.is_stumbling():
            shake = (pygame.time.get_ticks() % 100) // 25 - 2
            athlete_x += shake * 3

        # Calculate running animation
        cycle_speed = int(state.velocity * 2)
        frame = (pygame.time.get_ticks() // (150 - cycle_speed * 5)) % 2

        # Draw simple stick figure athlete
        scale = 1.0
        if state.is_stumbling():
            scale = 0.9

        # Head
        head_radius = int(8 * scale)
        pygame.draw.circle(self.screen, Colors.ATHLETE_SKIN,
                          (int(athlete_x), int(athlete_y)), head_radius)

        # Body
        body_start = (athlete_x, athlete_y + head_radius)
        body_end = (athlete_x, athlete_y + int(35 * scale))
        pygame.draw.line(self.screen, Colors.ATHLETE_UNIFORM, body_start, body_end, 3)

        # Arms (animated)
        arm_angle = 20 if frame == 0 else -20
        if state.velocity < 1:
            arm_angle = 0

        arm_pivot = (athlete_x, athlete_y + int(12 * scale))
        arm_end_l = (athlete_x - int(12 * scale), athlete_y + int(25 * scale) + arm_angle)
        arm_end_r = (athlete_x + int(12 * scale), athlete_y + int(25 * scale) - arm_angle)
        pygame.draw.line(self.screen, Colors.ATHLETE_SKIN, arm_pivot, arm_end_l, 3)
        pygame.draw.line(self.screen, Colors.ATHLETE_SKIN, arm_pivot, arm_end_r, 3)

        # Legs (animated)
        leg_pivot = body_end
        leg_angle = 15 if frame == 0 else -15
        if state.velocity < 1:
            leg_angle = 0

        leg_end_l = (athlete_x - int(6 * scale), athlete_y + int(55 * scale) - leg_angle)
        leg_end_r = (athlete_x + int(6 * scale), athlete_y + int(55 * scale) + leg_angle)
        pygame.draw.line(self.screen, Colors.ATHLETE_SHORTS, leg_pivot, leg_end_l, 3)
        pygame.draw.line(self.screen, Colors.ATHLETE_SHORTS, leg_pivot, leg_end_r, 3)

    def draw_ui(self, state: State):
        """Draw game UI elements."""
        # Distance indicator
        distance_text = f"{state.distance:.1f}m / {state.TARGET_DISTANCE}m"
        self._draw_text(distance_text, (self.width // 2, 20), self.font_medium)

        # Timer
        time_str = f"{state.time_elapsed:.2f}s"
        self._draw_text(time_str, (self.width // 2, 55), self.font_large)

        # Stamina bar
        bar_width = 200
        bar_height = 20
        bar_x = 20
        bar_y = 20

        # Background
        pygame.draw.rect(self.screen, (50, 50, 50),
                        (bar_x, bar_y, bar_width, bar_height))

        # Fill
        fill_width = int(bar_width * (state.stamina / state.max_stamina))
        if state.stamina > 60:
            fill_color = Colors.STAMINA_HIGH
        elif state.stamina > 30:
            fill_color = Colors.STAMINA_MEDIUM
        else:
            fill_color = Colors.STAMINA_LOW

        if fill_width > 0:
            pygame.draw.rect(self.screen, fill_color,
                           (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(self.screen, (255, 255, 255),
                        (bar_x, bar_y, bar_width, bar_height), 2)

        # Label
        self._draw_text("STAMINA", (bar_x + bar_width // 2, bar_y + bar_height + 5),
                       self.font_small)

        # Stumble warning
        if state.is_stumbling():
            warning_text = "STUMBLING!"
            self._draw_text(warning_text, (self.width // 2, 100),
                           self.font_medium, Colors.STUMBLE_INDICATOR)

        # Speed indicator
        speed_text = f"Speed: {state.velocity * 3:.0f} km/h"
        self._draw_text(speed_text, (self.width - 100, 20), self.font_small)

    def draw_menu(self, state: State):
        """Draw start menu."""
        self._draw_text("TRACK & FIELD DASH", (self.width // 2, 100),
                       self.font_large)
        self._draw_text("100 Meter Sprint", (self.width // 2, 150),
                       self.font_medium)
        self._draw_text("Press SPACE to Start", (self.width // 2, 250),
                       self.font_medium)
        self._draw_text("Alternate LEFT and RIGHT arrows to run!",
                       (self.width // 2, 300), self.font_small)

    def draw_finished(self, state: State):
        """Draw finish screen."""
        self._draw_text("FINISH!", (self.width // 2, 100),
                       self.font_large)

        time_str = f"Time: {state.finish_time:.2f}s"
        self._draw_text(time_str, (self.width // 2, 160),
                       self.font_medium)

        score = state.calculate_score()
        score_text = f"Score: {score}"
        self._draw_text(score_text, (self.width // 2, 200),
                       self.font_medium)

        self._draw_text("Press SPACE to play again",
                       (self.width // 2, 280), self.font_medium)
        self._draw_text("Press ESC to quit",
                       (self.width // 2, 320), self.font_small)

    def _draw_text(self, text: str, pos: tuple, font, color=None):
        """Draw centered text with shadow."""
        if color is None:
            color = Colors.TEXT

        text_surface = font.render(text, True, color)
        shadow_surface = font.render(text, True, Colors.TEXT_SHADOW)

        rect = text_surface.get_rect(center=pos)
        shadow_rect = shadow_surface.get_rect(center=(pos[0] + 2, pos[1] + 2))

        self.screen.blit(shadow_surface, shadow_rect)
        self.screen.blit(text_surface, rect)
