"""Renderer for Vector Super Mario Bros Water Swim Avoid."""

import pygame
from game import Game
import config


class Renderer:
    def __init__(self, game: Game):
        self.game = game
        self.screen = pygame.display.set_mode((game.width, game.height))
        pygame.display.set_caption("Vector Super Mario Bros Water Swim Avoid")
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

    def render(self):
        # Draw gradient background
        for y in range(self.game.height):
            t = y / self.game.height
            r = int(config.BG_TOP[0] * (1 - t) + config.BG_BOTTOM[0] * t)
            g = int(config.BG_TOP[1] * (1 - t) + config.BG_BOTTOM[1] * t)
            b = int(config.BG_TOP[2] * (1 - t) + config.BG_BOTTOM[2] * t)
            pygame.draw.line(self.screen, (r, g, b), (0, y), (self.game.width, y))

        # Draw water effect overlay
        water_surf = pygame.Surface((self.game.width, self.game.height), pygame.SRCALPHA)
        water_surf.fill(config.WATER_COLOR)
        self.screen.blit(water_surf, (0, 0))

        # Get visible entities
        obstacles, bloopers, cheeps = self.game.get_visible_entities()

        # Draw obstacles
        for obs in obstacles:
            screen_x = obs.pos.x - self.game.camera_x
            screen_y = obs.pos.y

            if obs.type == "coral":
                self._draw_coral(screen_x, screen_y, obs.width, obs.height)
            elif obs.type == "pipe":
                self._draw_pipe(screen_x, screen_y, obs.width, obs.height)
            else:
                # Ceiling/floor
                pygame.draw.rect(self.screen, config.PLATFORM_COLOR,
                               (screen_x, screen_y, obs.width, obs.height))

        # Draw flag
        flag_screen_x = self.game.flag_x - self.game.camera_x
        if -100 < flag_screen_x < self.game.width + 100:
            self._draw_flag(flag_screen_x, self.game.flag_y)

        # Draw bloopers
        for blooper in bloopers:
            screen_x = blooper.pos.x - self.game.camera_x
            self._draw_blooper(screen_x, blooper.pos.y, blooper)

        # Draw cheeps
        for cheep in cheeps:
            screen_x = cheep.pos.x - self.game.camera_x
            self._draw_cheep(screen_x, cheep.pos.y, cheep)

        # Draw player
        if self.game.player.alive:
            screen_x = self.game.player.pos.x - self.game.camera_x
            self._draw_player(screen_x, self.game.player.pos.y)

        # Draw bubbles
        for bubble in self.game.player.bubbles:
            screen_x = bubble[0] - self.game.camera_x
            alpha = int(255 * (1 - bubble[2]))
            bubble_surf = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(bubble_surf, (*config.BUBBLE_COLOR, alpha), (4, 4), 3)
            self.screen.blit(bubble_surf, (int(screen_x), int(bubble[1])))

        # Draw HUD
        self._draw_hud()

        # Draw game over/win message
        if self.game.game_over:
            self._draw_game_over()

        pygame.display.flip()

    def _draw_coral(self, x: float, y: float, width: float, height: float):
        # Draw coral as branching structure
        pygame.draw.circle(self.screen, config.CORAL_COLOR, (int(x + width//2), int(y + height)), int(width//2))
        # Branches
        for i in range(3):
            branch_x = x + 10 + i * 12
            branch_height = 15 + i * 5
            pygame.draw.line(self.screen, config.CORAL_COLOR,
                           (int(branch_x), int(y + height)),
                           (int(branch_x), int(y + height - branch_height)), 4)

    def _draw_pipe(self, x: float, y: float, width: float, height: float):
        # Main pipe body
        pygame.draw.rect(self.screen, config.PIPE_COLOR, (x, y, width, height))
        # Pipe rim
        pygame.draw.rect(self.screen, config.PIPE_DARK, (x - 3, y, width + 6, 10))
        # Highlight
        pygame.draw.line(self.screen, (120, 170, 120), (x + 5, y), (x + 5, y + height), 3)

    def _draw_flag(self, x: float, y: float):
        # Pole
        pygame.draw.line(self.screen, config.FLAG_POLE_COLOR,
                        (int(x), int(y - 80)), (int(x), int(y + 80)), 4)
        # Flag
        flag_points = [
            (x, y - 80),
            (x - 40, y - 60),
            (x, y - 40)
        ]
        pygame.draw.polygon(self.screen, config.FLAG_COLOR, flag_points)

    def _draw_blooper(self, x: float, y: float, blooper):
        # Body
        pygame.draw.ellipse(self.screen, config.BLOOPER_COLOR,
                           (x, y, blooper.width, blooper.height))

        # Tentacles
        for i in range(4):
            tx = x + 4 + i * 7
            ty = y + blooper.height - 5
            sway = int(5 * (blooper.phase + i * 0.5))
            pygame.draw.line(self.screen, config.BLOOPER_DARK,
                           (tx, ty), (tx + sway, ty + 15), 3)

        # Eyes
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x + 10), int(y + 12)), 6)
        pygame.draw.circle(self.screen, (255, 255, 255), (int(x + 22), int(y + 12)), 6)
        pygame.draw.circle(self.screen, (0, 0, 0), (int(x + 10), int(y + 12)), 3)
        pygame.draw.circle(self.screen, (0, 0, 0), (int(x + 22), int(y + 12)), 3)

    def _draw_cheep(self, x: float, y: float, cheep):
        # Body direction
        if cheep.vel.x > 0:
            body_points = [
                (x, y),
                (x + cheep.width, y + cheep.height // 2),
                (x, y + cheep.height),
            ]
            tail_points = [
                (x, y + 4),
                (x - 10, y + cheep.height // 2),
                (x, y + cheep.height - 4)
            ]
            eye_x = x + 20
        else:
            body_points = [
                (x + cheep.width, y),
                (x, y + cheep.height // 2),
                (x + cheep.width, y + cheep.height),
            ]
            tail_points = [
                (x + cheep.width, y + 4),
                (x + cheep.width + 10, y + cheep.height // 2),
                (x + cheep.width, y + cheep.height - 4)
            ]
            eye_x = x + 8

        pygame.draw.polygon(self.screen, config.CHEEP_COLOR, body_points)
        pygame.draw.polygon(self.screen, config.CHEEP_DARK, tail_points)

        # Eye
        pygame.draw.circle(self.screen, (255, 255, 255), (int(eye_x), int(y + 10)), 5)
        pygame.draw.circle(self.screen, (0, 0, 0), (int(eye_x), int(y + 10)), 2)

        # Fin
        fin_x = x + 12 if cheep.vel.x > 0 else x + 16
        pygame.draw.polygon(self.screen, config.CHEEP_DARK,
                           [(fin_x, y + cheep.height // 2),
                            (fin_x - 5, y + cheep.height + 4),
                            (fin_x + 5, y + cheep.height + 4)])

    def _draw_player(self, x: float, y: float):
        player = self.game.player
        pw, ph = player.width, player.height

        # Swimming animation
        leg_offset = int(4 * (player.swim_frame % 2))

        # Body
        pygame.draw.rect(self.screen, config.PLAYER_COLOR, (x, y, pw, ph))

        # Face
        face_x = x + 6 if player.facing_right else x + 4
        eye_x = x + 16 if player.facing_right else x + 6
        pygame.draw.circle(self.screen, (255, 200, 180), (int(face_x), int(y + 8)), 5)
        pygame.draw.circle(self.screen, (0, 0, 0), (int(eye_x), int(y + 8)), 2)

        # Hat
        pygame.draw.rect(self.screen, config.PLAYER_DARK, (x + 2, y - 3, pw - 4, 7))

        # Legs (swimming motion)
        pygame.draw.line(self.screen, (150, 50, 50),
                        (x + 6, y + ph - 5 + leg_offset),
                        (x + 6, y + ph + 5 + leg_offset), 4)
        pygame.draw.line(self.screen, (150, 50, 50),
                        (x + pw - 6, y + ph - 5 - leg_offset),
                        (x + pw - 6, y + ph + 5 - leg_offset), 4)

    def _draw_hud(self):
        # Score
        score_text = self.font.render(f"Score: {self.game.score}", True, config.TEXT_COLOR)
        self.screen.blit(score_text, (10, 10))

        # Progress
        progress = min(100, int(self.game.player.pos.x / config.LEVEL_LENGTH * 100))
        progress_text = self.small_font.render(f"Progress: {progress}%", True, config.TEXT_COLOR)
        self.screen.blit(progress_text, (10, 45))

        # Progress bar
        pygame.draw.rect(self.screen, (100, 100, 100), (10, 70, 200, 10))
        pygame.draw.rect(self.screen, (50, 200, 50), (10, 70, progress * 2, 10))

    def _draw_game_over(self):
        if self.game.win:
            msg = "COMPLETE! Press R to restart"
            color = (100, 255, 100)
        else:
            msg = "GAME OVER! Press R to restart"
            color = (255, 100, 100)

        text = self.font.render(msg, True, color)
        rect = text.get_rect(center=(self.game.width // 2, self.game.height // 2))
        self.screen.blit(text, rect)
