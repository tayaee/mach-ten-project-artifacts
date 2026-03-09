"""Main game class for Vector Light Cycle Grid Survival."""

import pygame
import sys
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    GRID_SIZE,
    COLORS,
    COLS,
    ROWS,
    INITIAL_FPS,
    FPS_INCREMENT_INTERVAL,
    FPS_INCREMENT_AMOUNT,
    DIRECTIONS,
    FONT_SIZE,
)


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Light Cycle Grid Survival")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.reset_game()

    def reset_game(self):
        self.trail = []
        self.head_x = COLS // 2
        self.head_y = ROWS // 2
        self.direction = DIRECTIONS["RIGHT"]
        self.next_direction = DIRECTIONS["RIGHT"]
        self.grid = [[None for _ in range(ROWS)] for _ in range(COLS)]
        self.grid[self.head_x][self.head_y] = COLORS["trail"]
        self.trail.append((self.head_x, self.head_y))
        self.score = 0
        self.start_time = pygame.time.get_ticks()
        self.game_over = False
        self.last_speed_increase = pygame.time.get_ticks()
        self.current_fps = INITIAL_FPS

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.game_over and event.key == pygame.K_SPACE:
                    self.reset_game()
                elif not self.game_over:
                    if event.key == pygame.K_UP and self.direction != DIRECTIONS["DOWN"]:
                        self.next_direction = DIRECTIONS["UP"]
                    elif event.key == pygame.K_DOWN and self.direction != DIRECTIONS["UP"]:
                        self.next_direction = DIRECTIONS["DOWN"]
                    elif event.key == pygame.K_LEFT and self.direction != DIRECTIONS["RIGHT"]:
                        self.next_direction = DIRECTIONS["LEFT"]
                    elif event.key == pygame.K_RIGHT and self.direction != DIRECTIONS["LEFT"]:
                        self.next_direction = DIRECTIONS["RIGHT"]

    def update(self):
        if self.game_over:
            return

        now = pygame.time.get_ticks()
        if now - self.last_speed_increase > FPS_INCREMENT_INTERVAL:
            self.current_fps = min(30, self.current_fps + FPS_INCREMENT_AMOUNT)
            self.last_speed_increase = now

        self.direction = self.next_direction
        dx, dy = self.direction
        self.head_x += dx
        self.head_y += dy

        if self.check_collision():
            self.game_over = True
            return

        self.grid[self.head_x][self.head_y] = COLORS["trail"]
        self.trail.append((self.head_x, self.head_y))

        self.score = (now - self.start_time) // 1000

    def check_collision(self):
        if not (0 <= self.head_x < COLS and 0 <= self.head_y < ROWS):
            return True
        if self.grid[self.head_x][self.head_y] is not None:
            return True
        return False

    def draw(self):
        self.screen.fill(COLORS["background"])

        self.draw_grid()

        for x, y in self.trail:
            pygame.draw.rect(
                self.screen,
                COLORS["trail"],
                (x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE),
            )

        pygame.draw.rect(
            self.screen,
            COLORS["player"],
            (self.head_x * GRID_SIZE, self.head_y * GRID_SIZE, GRID_SIZE, GRID_SIZE),
        )

        self.draw_ui()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_grid(self):
        for x in range(0, SCREEN_WIDTH, GRID_SIZE):
            pygame.draw.line(
                self.screen, COLORS["grid_line"], (x, 0), (x, SCREEN_HEIGHT)
            )
        for y in range(0, SCREEN_HEIGHT, GRID_SIZE):
            pygame.draw.line(
                self.screen, COLORS["grid_line"], (0, y), (SCREEN_WIDTH, y)
            )

    def draw_ui(self):
        score_text = self.font.render(f"Score: {self.score}", True, COLORS["text"])
        speed_text = self.font.render(f"Speed: {self.current_fps} FPS", True, COLORS["text"])
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(speed_text, (10, 40))

    def draw_game_over(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
        final_score_text = self.font.render(f"Final Score: {self.score}", True, COLORS["text"])
        restart_text = self.font.render("Press SPACE to restart", True, COLORS["text"])

        game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        final_score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))

        self.screen.blit(game_over_text, game_over_rect)
        self.screen.blit(final_score_text, final_score_rect)
        self.screen.blit(restart_text, restart_rect)

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(self.current_fps)
