"""Main game class for Vector Boulder Dash Logic."""

import pygame
from config import *
from grid import Grid
from player import Player


class Game:
    """Main game class managing rendering and game loop."""

    DEFAULT_LEVEL = """####################
#..................#
#..O...O...$...O...#
#..O...O...O...$...#
#..................#
#...O.....$.....O..#
#..$.....O.O....$..#
#..................#
#..O.......$....O..#
#.................X#
#......E.....E.....#
#....$.......O.$...#
#..................#
#..P...............#
####################"""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(CAPTION)
        self.clock = pygame.time.Clock()
        self.running = True

        self.grid = Grid()
        self.player = None
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.game_state = "ready"  # ready, playing, game_over, win
        self.message = ""
        self.steps_taken = 0

        # Fonts
        self.score_font = pygame.font.Font(None, FONT_SIZE_SCORE)
        self.message_font = pygame.font.Font(None, FONT_SIZE_MESSAGE)
        self.info_font = pygame.font.Font(None, FONT_SIZE_INFO)

        self.load_level(self.DEFAULT_LEVEL)

    def find_player_start(self, level_data):
        """Find player starting position from level data."""
        lines = level_data.strip().split('\n')
        for y, line in enumerate(lines):
            for x, char in enumerate(line):
                if char == 'P':
                    return x, y
        return 1, 1  # Default fallback

    def load_level(self, level_data):
        """Load a new level."""
        start_x, start_y = self.find_player_start(level_data)
        self.player = Player(start_x, start_y)
        self.grid = Grid()
        self.grid.load_level(level_data)
        self.score = 0
        self.steps_taken = 0

    def reset_game(self):
        """Reset to initial state."""
        self.load_level(self.DEFAULT_LEVEL)
        self.level = 1
        self.game_state = "ready"
        self.message = ""

    def restart_level(self):
        """Restart current level."""
        self.load_level(self.DEFAULT_LEVEL)
        self.game_state = "playing"

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    self.restart_level()
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "ready":
                        self.game_state = "playing"
                    elif self.game_state in ("game_over", "win"):
                        self.reset_game()
                elif self.game_state == "playing":
                    dx, dy = 0, 0
                    if event.key == pygame.K_UP:
                        dy = -1
                    elif event.key == pygame.K_DOWN:
                        dy = 1
                    elif event.key == pygame.K_LEFT:
                        dx = -1
                    elif event.key == pygame.K_RIGHT:
                        dx = 1

                    if dx != 0 or dy != 0:
                        moved, got_diamond, at_exit = self.player.move(dx, dy, self.grid)
                        if moved:
                            self.steps_taken += 1
                        if got_diamond:
                            self.score += SCORE_PER_DIAMOND
                        if at_exit:
                            self.score += SCORE_EXIT_BONUS
                            self.game_state = "win"
                            self.message = f"Level Complete! Score: {self.score}"

    def update(self):
        """Update game state."""
        if self.game_state == "playing":
            current_time = pygame.time.get_ticks()

            # Update physics
            crushed = self.grid.update_physics(current_time, self.player.x, self.player.y)
            if crushed:
                self.game_state = "game_over"
                self.message = "Crushed by a rock!"
                if self.score > self.high_score:
                    self.high_score = self.score

            # Update enemies
            caught = self.grid.update_enemies(current_time, self.player.x, self.player.y)
            if caught:
                self.game_state = "game_over"
                self.message = "Caught by enemy!"
                if self.score > self.high_score:
                    self.high_score = self.score

            # Check for enemy kills by rocks
            for enemy in self.grid.enemies[:]:
                ex, ey = enemy['x'], enemy['y']
                tile = self.grid.get_tile(ex, ey)
                if tile == TILE_ROCK:
                    if self.grid.check_enemy_crushed(ex, ey):
                        self.score += SCORE_ENEMY_KILL

    def draw_tile(self, x, y, tile):
        """Draw a single tile."""
        px = GRID_OFFSET_X + x * CELL_SIZE
        py = GRID_OFFSET_Y + y * CELL_SIZE
        rect = pygame.Rect(px, py, CELL_SIZE, CELL_SIZE)

        if tile == TILE_EMPTY:
            pygame.draw.rect(self.screen, COLOR_BG, rect)
            pygame.draw.rect(self.screen, COLOR_GRID, rect, 1)

        elif tile == TILE_DIRT:
            pygame.draw.rect(self.screen, COLOR_DIRT, rect)
            # Add texture
            pygame.draw.circle(self.screen, COLOR_DIRT_LIGHT,
                             (px + 10, py + 10), 3)
            pygame.draw.circle(self.screen, COLOR_DIRT_LIGHT,
                             (px + 30, py + 25), 2)

        elif tile == TILE_WALL:
            pygame.draw.rect(self.screen, COLOR_WALL, rect)
            pygame.draw.rect(self.screen, (60, 60, 70), rect, 2)

        elif tile == TILE_ROCK:
            pygame.draw.rect(self.screen, COLOR_BG, rect)
            # Draw rock circle
            center = (px + CELL_SIZE // 2, py + CELL_SIZE // 2)
            radius = CELL_SIZE // 2 - 4
            pygame.draw.circle(self.screen, COLOR_ROCK, center, radius)
            pygame.draw.circle(self.screen, COLOR_ROCK_HIGHLIGHT,
                             (px + CELL_SIZE // 2 - 5, py + CELL_SIZE // 2 - 5), 5)

        elif tile == TILE_DIAMOND:
            pygame.draw.rect(self.screen, COLOR_BG, rect)
            # Draw diamond shape
            points = [
                (px + CELL_SIZE // 2, py + 5),
                (px + CELL_SIZE - 5, py + CELL_SIZE // 2),
                (px + CELL_SIZE // 2, py + CELL_SIZE - 5),
                (px + 5, py + CELL_SIZE // 2)
            ]
            pygame.draw.polygon(self.screen, COLOR_DIAMOND, points)
            pygame.draw.polygon(self.screen, COLOR_DIAMOND_HIGHLIGHT, points, 2)

        elif tile == TILE_EXIT:
            pygame.draw.rect(self.screen, COLOR_EXIT, rect)
            pygame.draw.rect(self.screen, (80, 40, 80), rect, 3)
            # Draw X
            pygame.draw.line(self.screen, (200, 100, 200),
                           (px + 10, py + 10), (px + CELL_SIZE - 10, py + CELL_SIZE - 10), 3)
            pygame.draw.line(self.screen, (200, 100, 200),
                           (px + CELL_SIZE - 10, py + 10), (px + 10, py + CELL_SIZE - 10), 3)

        elif tile == TILE_EXIT_OPEN:
            pygame.draw.rect(self.screen, COLOR_EXIT_OPEN, rect)
            pygame.draw.rect(self.screen, (80, 150, 80), rect, 3)

    def draw_player(self):
        """Draw the player."""
        px, py = self.player.get_pixel_pos()
        center = (px + CELL_SIZE // 2, py + CELL_SIZE // 2)

        # Body
        pygame.draw.circle(self.screen, COLOR_PLAYER, center, CELL_SIZE // 2 - 4)
        pygame.draw.circle(self.screen, (255, 220, 100), center, CELL_SIZE // 2 - 8, 2)

        # Eyes
        eye_y = py + CELL_SIZE // 2 - 3
        pygame.draw.circle(self.screen, (0, 0, 0), (px + 12, eye_y), 3)
        pygame.draw.circle(self.screen, (0, 0, 0), (px + CELL_SIZE - 12, eye_y), 3)

    def draw_enemy(self, x, y):
        """Draw an enemy."""
        px = GRID_OFFSET_X + x * CELL_SIZE
        py = GRID_OFFSET_Y + y * CELL_SIZE
        center = (px + CELL_SIZE // 2, py + CELL_SIZE // 2)

        # Body
        pygame.draw.circle(self.screen, COLOR_ENEMY, center, CELL_SIZE // 2 - 4)

        # Eyes
        eye_y = py + CELL_SIZE // 2 - 2
        pygame.draw.circle(self.screen, COLOR_ENEMY_EYE, (px + 12, eye_y), 4)
        pygame.draw.circle(self.screen, COLOR_ENEMY_EYE, (px + CELL_SIZE - 12, eye_y), 4)
        pygame.draw.circle(self.screen, (0, 0, 0), (px + 12, eye_y), 2)
        pygame.draw.circle(self.screen, (0, 0, 0), (px + CELL_SIZE - 12, eye_y), 2)

    def render(self):
        """Render the game."""
        self.screen.fill(COLOR_BG)

        # Draw UI panel background
        ui_height = 80
        pygame.draw.rect(self.screen, COLOR_UI_BG, (0, 0, SCREEN_WIDTH, ui_height))

        # Draw grid
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                self.draw_tile(x, y, self.grid.get_tile(x, y))

        # Draw enemies
        for enemy in self.grid.enemies:
            self.draw_enemy(enemy['x'], enemy['y'])

        # Draw player
        if self.game_state in ("ready", "playing"):
            self.draw_player()

        # Draw UI info
        score_text = self.score_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 10))

        diamonds_text = self.info_font.render(
            f"Diamonds: {self.grid.diamonds_collected}/{DIAMONDS_TO_OPEN_EXIT}",
            True, COLOR_DIAMOND
        )
        self.screen.blit(diamonds_text, (20, 50))

        high_score_text = self.info_font.render(f"Best: {self.high_score}", True, (150, 150, 150))
        high_score_rect = high_score_text.get_rect(right=SCREEN_WIDTH - 20, top=10)
        self.screen.blit(high_score_text, high_score_rect)

        level_text = self.info_font.render(f"Level: {self.level}", True, (150, 150, 150))
        level_rect = level_text.get_rect(right=SCREEN_WIDTH - 20, top=35)
        self.screen.blit(level_text, level_rect)

        # Draw exit status
        if self.grid.exit_open:
            exit_text = self.info_font.render("EXIT OPEN!", True, COLOR_EXIT_OPEN)
            exit_rect = exit_text.get_rect(right=SCREEN_WIDTH - 20, top=60)
            self.screen.blit(exit_text, exit_rect)

        # Draw messages
        if self.game_state == "ready":
            msg = "Press SPACE to start | Arrow keys to move | R to restart"
            msg_text = self.info_font.render(msg, True, COLOR_TEXT)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 30))
            self.screen.blit(msg_text, msg_rect)

        elif self.game_state == "game_over":
            msg_text = self.message_font.render(self.message, True, (255, 100, 100))
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(msg_text, msg_rect)

            hint = "Press SPACE to restart or R to retry"
            hint_text = self.info_font.render(hint, True, COLOR_TEXT)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(hint_text, hint_rect)

        elif self.game_state == "win":
            msg_text = self.message_font.render(self.message, True, (100, 255, 100))
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(msg_text, msg_rect)

            hint = "Press SPACE to play again"
            hint_text = self.info_font.render(hint, True, COLOR_TEXT)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(hint_text, hint_rect)

        pygame.display.flip()

    def step_ai(self, action):
        """
        Execute an AI action and return observation, reward, done.

        Args:
            action: 0 = up, 1 = down, 2 = left, 3 = right, 4 = wait

        Returns:
            (observation, reward, done)
        """
        prev_score = self.score
        prev_diamonds = self.grid.diamonds_collected

        dx, dy = 0, 0
        if action == 0:
            dy = -1
        elif action == 1:
            dy = 1
        elif action == 2:
            dx = -1
        elif action == 3:
            dx = 1

        if dx != 0 or dy != 0:
            moved, got_diamond, at_exit = self.player.move(dx, dy, self.grid)
            if moved:
                self.steps_taken += 1
            if got_diamond:
                self.score += SCORE_PER_DIAMOND
            if at_exit:
                self.score += SCORE_EXIT_BONUS
                self.game_state = "win"

        self.update()

        reward = REWARD_PER_STEP

        if self.grid.diamonds_collected > prev_diamonds:
            reward += REWARD_DIAMOND

        if self.grid.enemy_killed:
            reward += REWARD_ENEMY_KILL

        if self.game_state == "win":
            reward += REWARD_EXIT
            return self.get_observation(), reward, True

        if self.game_state == "game_over":
            reward = REWARD_DEATH
            return self.get_observation(), reward, True

        return self.get_observation(), reward, False

    def get_observation(self):
        """Return current game state for AI."""
        obs = {
            "player_x": self.player.x,
            "player_y": self.player.y,
            "diamonds_collected": self.grid.diamonds_collected,
            "diamonds_total": self.grid.diamonds_total,
            "exit_open": self.grid.exit_open,
            "score": self.score,
            "game_state": self.game_state,
            "grid": [row[:] for row in self.grid.grid],
            "enemies": [{"x": e["x"], "y": e["y"]} for e in self.grid.enemies]
        }
        return obs

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
