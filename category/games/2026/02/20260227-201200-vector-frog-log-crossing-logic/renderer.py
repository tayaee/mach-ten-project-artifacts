"""Renderer for Vector Frog Log Crossing Logic."""

import pygame
from game import GameState


class Renderer:
    def __init__(self, state: GameState):
        self.state = state
        self.screen = pygame.display.set_mode((state.width, state.height))
        pygame.display.set_caption("Vector Frog Log Crossing Logic")
        self.font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

        self.grass_color = (70, 140, 70)
        self.grass_dark = (50, 110, 50)
        self.water_color = (40, 100, 160)
        self.water_dark = (30, 80, 130)
        self.log_color = (130, 90, 60)
        self.log_dark = (100, 70, 45)
        self.frog_color = (80, 180, 80)
        self.frog_dark = (55, 140, 55)
        self.frog_belly = (100, 200, 100)
        self.eye_color = (255, 255, 255)
        self.pupil_color = (0, 0, 0)
        self.text_color = (255, 255, 255)
        self.goal_color = (80, 200, 80)

    def render(self):
        self.screen.fill((25, 25, 35))

        self._draw_areas()

        for log in self.state.logs:
            self._draw_log(log)

        if self.state.player.alive:
            self._draw_frog()

        self._draw_hud()

        if self.state.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_areas(self):
        water_rect = (0, self.state.grid_size,
                     self.state.width,
                     self.state.grid_size * 4)
        pygame.draw.rect(self.screen, self.water_color, water_rect)

        for row in range(4):
            y = (row + 1) * self.state.grid_size
            offset = (row * 11) % self.state.width
            for x in range(-20, self.state.width + 20, 30):
                wave_x = (x + offset) % (self.state.width + 40) - 20
                pygame.draw.line(self.screen, self.water_dark,
                               (wave_x, y), (wave_x + 15, y), 2)

        goal_rect = (0, 0, self.state.width, self.state.grid_size)
        pygame.draw.rect(self.screen, self.goal_color, goal_rect)

        for x in range(0, self.state.width, 20):
            pygame.draw.line(self.screen, self.grass_dark,
                           (x + 5, 5), (x + 5, self.state.grid_size - 5), 2)

        bottom_grass = (0, self.state.grid_size * 5,
                       self.state.width, self.state.grid_size * 5)
        pygame.draw.rect(self.screen, self.grass_color, bottom_grass)

        for row in range(5, 10):
            y = row * self.state.grid_size
            for x in range(0, self.state.width, 20):
                pygame.draw.line(self.screen, self.grass_dark,
                               (x + 5, y + 5), (x + 5, y + self.state.grid_size - 5), 2)

    def _draw_log(self, log):
        x, y = int(log.pos.x), int(log.pos.y)
        w, h = log.width, log.height

        pygame.draw.rect(self.screen, self.log_color, (x, y + 5, w, h - 10))

        pygame.draw.circle(self.screen, self.log_dark, (x, y + h // 2), h // 2 - 2)
        pygame.draw.circle(self.screen, self.log_dark, (x + w, y + h // 2), h // 2 - 2)

        for i in range(x + 10, x + w - 10, 18):
            pygame.draw.line(self.screen, self.log_dark,
                           (i, y + 12), (i, y + h - 12), 2)

        pygame.draw.rect(self.screen, (145, 105, 75), (x + 3, y + 8, w - 6, 6))

    def _draw_frog(self):
        player = self.state.player
        x = int(player.pos.x)
        y = int(player.pos.y)
        size = self.state.grid_size

        body_rect = (x + 6, y + 10, size - 12, size - 16)
        pygame.draw.ellipse(self.screen, self.frog_color, body_rect)

        belly_rect = (x + 12, y + 18, size - 24, size - 28)
        pygame.draw.ellipse(self.screen, self.frog_belly, belly_rect)

        pygame.draw.ellipse(self.screen, self.frog_color, (x + 8, y + 4, size - 16, 16))

        eye_size = 7
        pygame.draw.circle(self.screen, self.frog_color, (x + 14, y + 8), eye_size)
        pygame.draw.circle(self.screen, self.frog_color, (x + size - 14, y + 8), eye_size)
        pygame.draw.circle(self.screen, self.eye_color, (x + 14, y + 7), 5)
        pygame.draw.circle(self.screen, self.eye_color, (x + size - 14, y + 7), 5)
        pygame.draw.circle(self.screen, self.pupil_color, (x + 14, y + 7), 2)
        pygame.draw.circle(self.screen, self.pupil_color, (x + size - 14, y + 7), 2)

        leg_width = 8
        pygame.draw.ellipse(self.screen, self.frog_dark,
                          (x + 4, y + size - 14, leg_width, 14))
        pygame.draw.ellipse(self.screen, self.frog_dark,
                          (x + size - 12, y + size - 14, leg_width, 14))
        pygame.draw.ellipse(self.screen, self.frog_dark,
                          (x + 10, y + size - 10, leg_width + 2, 12))
        pygame.draw.ellipse(self.screen, self.frog_dark,
                          (x + size - 18, y + size - 10, leg_width + 2, 12))

    def _draw_hud(self):
        score_text = self.font.render(f"Score: {self.state.score}", True, self.text_color)
        self.screen.blit(score_text, (10, 10))

        lanes_text = self.font.render(f"Lanes: {len(self.state.lanes_crossed)}/4", True, self.text_color)
        self.screen.blit(lanes_text, (10, 45))

        if not self.state.game_over and self.state.player.pos.y > self.state.grid_size * 7:
            hint = self.small_font.render("Arrow keys to move", True, (200, 200, 200))
            self.screen.blit(hint, (self.state.width - 160, 10))

    def _draw_game_over(self):
        overlay = pygame.Surface((self.state.width, self.state.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.state.win:
            msg = "GOAL REACHED!"
            submsg = f"Final Score: {self.state.score}"
            color = (100, 255, 100)
        else:
            msg = "GAME OVER"
            submsg = f"Final Score: {self.state.score}"
            color = (255, 100, 100)

        text = self.font.render(msg, True, color)
        rect = text.get_rect(center=(self.state.width // 2, self.state.height // 2 - 20))
        self.screen.blit(text, rect)

        score_text = self.font.render(submsg, True, self.text_color)
        score_rect = score_text.get_rect(center=(self.state.width // 2, self.state.height // 2 + 20))
        self.screen.blit(score_text, score_rect)

        restart_text = self.small_font.render("Press R to restart", True, (200, 200, 200))
        restart_rect = restart_text.get_rect(center=(self.state.width // 2, self.state.height // 2 + 60))
        self.screen.blit(restart_text, restart_rect)
