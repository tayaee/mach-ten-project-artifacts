"""Renderer for Vector Tumble Weed Dodge."""

import pygame
import math
from game import GameState


class Renderer:
    def __init__(self, state: GameState):
        self.state = state
        self.screen = pygame.display.set_mode((state.width, state.height))
        pygame.display.set_caption("Vector Tumble Weed Dodge")
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

        self.bg_color = (30, 25, 20)
        self.bg_light = (40, 33, 27)
        self.text_color = (255, 255, 255)
        self.player_color = (50, 50, 50)
        self.player_light = (80, 80, 80)
        self.tumbleweed_color = (100, 90, 70)
        self.tumbleweed_light = (130, 115, 90)
        self.tumbleweed_dark = (70, 60, 50)

    def render(self):
        self._draw_background()

        for tumbleweed in self.state.tumbleweeds:
            self._draw_tumbleweed(tumbleweed)

        if self.state.player.alive:
            self._draw_player()

        self._draw_hud()

        if self.state.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_background(self):
        self.screen.fill(self.bg_color)

        # Draw ground texture
        for x in range(0, self.state.width + 40, 40):
            offset = (x + int(self.state.game_time * 10)) % 80
            ground_x = x - offset
            for y in range(0, self.state.height, 20):
                if ((x // 40) + (y // 20)) % 2 == 0:
                    pygame.draw.circle(self.screen, self.bg_light, (ground_x, y), 2)

        # Draw horizon line
        pygame.draw.line(self.screen, (60, 50, 40), (0, 0), (self.state.width, 0), 2)
        pygame.draw.line(self.screen, (60, 50, 40), (0, self.state.height - 1),
                        (self.state.width, self.state.height - 1), 2)

    def _draw_player(self):
        player = self.state.player
        x = int(player.pos.x)
        y = int(player.pos.y)
        w = player.width
        h = player.height

        # Cowboy hat silhouette
        hat_brim_y = y
        pygame.draw.ellipse(self.screen, self.player_color,
                           (x - 5, hat_brim_y, w + 10, 10))
        pygame.draw.rect(self.screen, self.player_color,
                        (x + 5, hat_brim_y - 8, w - 10, 12))

        # Head
        head_y = y + 8
        pygame.draw.ellipse(self.screen, self.player_color,
                           (x + 4, head_y, w - 8, h // 3))

        # Body
        body_y = y + h // 3 + 6
        pygame.draw.rect(self.screen, self.player_color,
                        (x + 4, body_y, w - 8, h // 2))

        # Legs
        leg_width = 8
        pygame.draw.rect(self.screen, self.player_color,
                        (x + 6, y + h - 10, leg_width, 10))
        pygame.draw.rect(self.screen, self.player_color,
                        (x + w - 14, y + h - 10, leg_width, 10))

        # Simple outline highlight
        pygame.draw.ellipse(self.screen, self.player_light,
                           (x + 6, head_y + 2, w - 16, 4))

    def _draw_tumbleweed(self, tumbleweed):
        x = int(tumbleweed.pos.x)
        y = int(tumbleweed.pos.y)
        size = tumbleweed.size
        rotation = tumbleweed.rotation

        center_x = x + size // 2
        center_y = y + size // 2

        # Draw rotating tumbleweed using vector lines
        num_spokes = 8
        for i in range(num_spokes):
            angle = rotation + (i * math.pi * 2 / num_spokes)
            end_x = center_x + math.cos(angle) * (size // 2 - 2)
            end_y = center_y + math.sin(angle) * (size // 2 - 2)

            # Outer rim segments
            pygame.draw.line(self.screen, self.tumbleweed_light,
                           (center_x, center_y), (end_x, end_y), 2)

            # Inner darker segments
            mid_x = center_x + math.cos(angle) * (size // 4)
            mid_y = center_y + math.sin(angle) * (size // 4)
            pygame.draw.line(self.screen, self.tumbleweed_dark,
                           (center_x, center_y), (mid_x, mid_y), 3)

        # Draw outer rim
        pygame.draw.circle(self.screen, self.tumbleweed_color,
                          (center_x, center_y), size // 2 - 1, 2)

        # Inner cross pattern
        for i in range(num_spokes):
            angle = rotation + (i * math.pi * 2 / num_spokes) + math.pi / num_spokes
            inner_radius = size // 4
            outer_radius = size // 2 - 4

            start_x = center_x + math.cos(angle) * inner_radius
            start_y = center_y + math.sin(angle) * inner_radius
            end_x = center_x + math.cos(angle) * outer_radius
            end_y = center_y + math.sin(angle) * outer_radius

            pygame.draw.line(self.screen, self.tumbleweed_light,
                           (start_x, start_y), (end_x, end_y), 1)

    def _draw_hud(self):
        score_text = self.font.render(f"Score: {self.state.score}", True, self.text_color)
        self.screen.blit(score_text, (10, 10))

        difficulty_text = self.small_font.render(f"Level: {self.state.difficulty_level}",
                                                 True, (200, 200, 200))
        self.screen.blit(difficulty_text, (10, 45))

        time_text = self.small_font.render(f"Time: {int(self.state.game_time)}s",
                                           True, (200, 200, 200))
        self.screen.blit(time_text, (10, 70))

        hint = self.small_font.render("UP/DOWN to move", True, (150, 150, 150))
        self.screen.blit(hint, (self.state.width - 140, 10))

    def _draw_game_over(self):
        overlay = pygame.Surface((self.state.width, self.state.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        msg = "GAME OVER"
        color = (255, 100, 100)

        text = self.font.render(msg, True, color)
        rect = text.get_rect(center=(self.state.width // 2, self.state.height // 2 - 30))
        self.screen.blit(text, rect)

        score_text = self.font.render(f"Final Score: {self.state.score}",
                                      True, self.text_color)
        score_rect = score_text.get_rect(center=(self.state.width // 2,
                                                 self.state.height // 2 + 10))
        self.screen.blit(score_text, score_rect)

        time_text = self.small_font.render(f"Survived: {int(self.state.game_time)} seconds",
                                           True, (200, 200, 200))
        time_rect = time_text.get_rect(center=(self.state.width // 2,
                                               self.state.height // 2 + 50))
        self.screen.blit(time_text, time_rect)

        restart_text = self.small_font.render("Press R to restart", True, (180, 180, 180))
        restart_rect = restart_text.get_rect(center=(self.state.width // 2,
                                                     self.state.height // 2 + 80))
        self.screen.blit(restart_text, restart_rect)
