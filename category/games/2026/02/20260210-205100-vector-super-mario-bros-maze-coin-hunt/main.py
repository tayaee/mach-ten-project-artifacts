"""
Vector Super Mario Bros Maze Coin Hunt
A grid-based maze game with coin collection and enemy avoidance.
"""
import pygame
import sys
import random
from enum import Enum
from typing import Tuple, List, Optional

# Constants
SCREEN_WIDTH = 640
SCREEN_HEIGHT = 640
GRID_SIZE = 32
COLS = 20
ROWS = 20
FPS = 60

# Colors - Monochrome high-contrast palette
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
YELLOW = (255, 255, 80)
BROWN = (139, 90, 43)

# Tile types
EMPTY = 0
WALL = 1
COIN = 2
PLAYER = 3
ENEMY = 4

# Game settings
COIN_COUNT = 50
TIME_LIMIT = 120  # seconds
COIN_POINTS = 100
COMPLETION_BONUS = 1000
INITIAL_LIVES = 3
ENEMY_MOVE_INTERVAL = 15  # frames between enemy moves


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)
    NONE = (0, 0)


class Maze:
    """Fixed maze layout for the game."""

    BASE_LAYOUT = [
        "11111111111111111111",
        "10000000000000000001",
        "10111101111101111101",
        "10100000000000000101",
        "10101111111111110101",
        "10100000000000000101",
        "10101111111111110101",
        "10100000000000000101",
        "10101111111111110101",
        "10000000000000000001",
        "10101111111111110101",
        "10100000000000000101",
        "10101111111111110101",
        "10100000000000000101",
        "10101111111111110101",
        "10100000000000000101",
        "10101111111111110101",
        "10000000000000000001",
        "10111111101111111101",
        "11111111111111111111",
    ]

    def __init__(self, randomize_coins: bool = True):
        self.grid = [[EMPTY for _ in range(COLS)] for _ in range(ROWS)]
        self._parse_layout()
        self._place_coins(randomize_coins)

    def _parse_layout(self):
        """Parse the base layout into the grid."""
        for r, row in enumerate(self.BASE_LAYOUT):
            for c, char in enumerate(row):
                if char == '1':
                    self.grid[r][c] = WALL

    def _place_coins(self, randomize: bool):
        """Place coins in empty tiles."""
        empty_tiles = []
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == EMPTY:
                    # Exclude player start position and enemy paths
                    if not (r == 1 and c == 1):  # Player start
                        empty_tiles.append((r, c))

        if randomize:
            random.shuffle(empty_tiles)

        coins_placed = 0
        for r, c in empty_tiles:
            if coins_placed >= COIN_COUNT:
                break
            self.grid[r][c] = COIN
            coins_placed += 1

    def is_wall(self, row: int, col: int) -> bool:
        """Check if a tile is a wall."""
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.grid[row][col] == WALL
        return True

    def is_coin(self, row: int, col: int) -> bool:
        """Check if a tile has a coin."""
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.grid[row][col] == COIN
        return False

    def collect_coin(self, row: int, col: int) -> bool:
        """Collect a coin from the tile."""
        if self.is_coin(row, col):
            self.grid[row][col] = EMPTY
            return True
        return False

    def get_coin_count(self) -> int:
        """Count remaining coins."""
        count = 0
        for r in range(ROWS):
            for c in range(COLS):
                if self.grid[r][c] == COIN:
                    count += 1
        return count


class Entity:
    """Base class for game entities."""

    def __init__(self, row: int, col: int):
        self.row = row
        self.col = col
        self.start_row = row
        self.start_col = col

    def get_position(self) -> Tuple[int, int]:
        """Get pixel position."""
        return (self.col * GRID_SIZE + GRID_SIZE // 2,
                self.row * GRID_SIZE + GRID_SIZE // 2)

    def get_grid_position(self) -> Tuple[int, int]:
        """Get grid position."""
        return (self.row, self.col)

    def reset(self):
        """Reset to start position."""
        self.row = self.start_row
        self.col = self.start_col


class Player(Entity):
    """Player character (Mario)."""

    def __init__(self, row: int, col: int):
        super().__init__(row, col)
        self.direction = Direction.NONE

    def move(self, direction: Direction, maze: Maze) -> bool:
        """Try to move in a direction."""
        dr, dc = direction.value
        new_row = self.row + dr
        new_col = self.col + dc

        if 0 <= new_row < ROWS and 0 <= new_col < COLS:
            if not maze.is_wall(new_row, new_col):
                self.row = new_row
                self.col = new_col
                self.direction = direction
                return True
        return False


class Koopa(Entity):
    """Koopa Troopa enemy with back-and-forth patrol pattern."""

    def __init__(self, row: int, col: int, patrol_axis: str, patrol_range: Tuple[int, int]):
        super().__init__(row, col)
        self.patrol_axis = patrol_axis  # 'horizontal' or 'vertical'
        self.patrol_range = patrol_range  # (min, max) in grid units
        self.direction = 1  # 1 = forward, -1 = backward
        self.move_counter = 0

    def update(self, maze: Maze):
        """Update enemy position."""
        self.move_counter += 1
        if self.move_counter < ENEMY_MOVE_INTERVAL:
            return
        self.move_counter = 0

        if self.patrol_axis == 'horizontal':
            new_col = self.col + self.direction
            if new_col <= self.patrol_range[0] or new_col >= self.patrol_range[1]:
                self.direction *= -1
                new_col = self.col + self.direction
            if not maze.is_wall(self.row, new_col):
                self.col = new_col
        else:  # vertical
            new_row = self.row + self.direction
            if new_row <= self.patrol_range[0] or new_row >= self.patrol_range[1]:
                self.direction *= -1
                new_row = self.row + self.direction
            if not maze.is_wall(new_row, self.col):
                self.row = new_row


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros Maze Coin Hunt")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 64)

        self.reset_game()

    def reset_game(self):
        """Reset game state."""
        self.maze = Maze(randomize_coins=True)
        self.player = Player(1, 1)

        # Two Koopas patrolling different paths
        self.koopas = [
            Koopa(9, 1, 'horizontal', (1, 18)),   # Horizontal patrol in middle corridor
            Koopa(9, 9, 'horizontal', (2, 17)),   # Horizontal patrol offset
        ]

        self.score = 0
        self.lives = INITIAL_LIVES
        self.time_remaining = TIME_LIMIT
        self.game_over = False
        self.won = False
        self.frame_count = 0

    def handle_input(self) -> bool:
        """Handle player input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r and (self.game_over or self.won):
                    self.reset_game()
                elif not self.game_over and not self.won:
                    if event.key == pygame.K_UP:
                        self.player.move(Direction.UP, self.maze)
                    elif event.key == pygame.K_DOWN:
                        self.player.move(Direction.DOWN, self.maze)
                    elif event.key == pygame.K_LEFT:
                        self.player.move(Direction.LEFT, self.maze)
                    elif event.key == pygame.K_RIGHT:
                        self.player.move(Direction.RIGHT, self.maze)
        return True

    def update(self):
        """Update game state."""
        if self.game_over or self.won:
            return

        self.frame_count += 1

        # Update timer (every 60 frames = 1 second)
        if self.frame_count % FPS == 0:
            self.time_remaining -= 1
            if self.time_remaining <= 0:
                self.game_over = True
                return

        # Update enemies
        for koopa in self.koopas:
            koopa.update(self.maze)

        # Check coin collection
        pr, pc = self.player.get_grid_position()
        if self.maze.collect_coin(pr, pc):
            self.score += COIN_POINTS

        # Check win condition
        if self.maze.get_coin_count() == 0:
            self.score += COMPLETION_BONUS
            self.won = True
            return

        # Check enemy collision
        for koopa in self.koopas:
            kr, kc = koopa.get_grid_position()
            if kr == pr and kc == pc:
                self.lives -= 1
                if self.lives <= 0:
                    self.game_over = True
                else:
                    self.player.reset()
                return

    def draw_maze(self):
        """Draw the maze."""
        for r in range(ROWS):
            for c in range(COLS):
                x = c * GRID_SIZE
                y = r * GRID_SIZE

                if self.maze.grid[r][c] == WALL:
                    # Draw wall as filled rectangle with border
                    pygame.draw.rect(self.screen, DARK_GRAY, (x, y, GRID_SIZE, GRID_SIZE))
                    pygame.draw.rect(self.screen, WHITE, (x, y, GRID_SIZE, GRID_SIZE), 1)
                elif self.maze.grid[r][c] == COIN:
                    # Draw coin as circle
                    pygame.draw.circle(self.screen, YELLOW,
                                       (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 6)
                    pygame.draw.circle(self.screen, WHITE,
                                       (x + GRID_SIZE // 2, y + GRID_SIZE // 2), 6, 1)

    def draw_player(self):
        """Draw the player (Mario sprite)."""
        px, py = self.player.get_position()
        # Simple vector Mario: circle head with M mark
        pygame.draw.circle(self.screen, RED, (px, py), GRID_SIZE // 2 - 4)
        pygame.draw.circle(self.screen, WHITE, (px, py), GRID_SIZE // 2 - 4, 2)
        # M emblem
        pygame.draw.line(self.screen, WHITE, (px - 4, py - 4), (px, py - 8), 2)
        pygame.draw.line(self.screen, WHITE, (px, py - 8), (px + 4, py - 4), 2)

    def draw_enemies(self):
        """Draw the Koopa enemies."""
        for koopa in self.koopas:
            kx, ky = koopa.get_position()
            # Simple vector Koopa: turtle shell shape
            pygame.draw.circle(self.screen, GREEN, (kx, ky), GRID_SIZE // 2 - 4)
            pygame.draw.circle(self.screen, WHITE, (kx, ky), GRID_SIZE // 2 - 4, 2)
            # Shell pattern
            pygame.draw.arc(self.screen, WHITE,
                            (kx - 8, ky - 8, 16, 16), 0, 3.14, 2)

    def draw_ui(self):
        """Draw UI elements."""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        # Lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, WHITE)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 10))

        # Timer
        minutes = self.time_remaining // 60
        seconds = self.time_remaining % 60
        timer_color = RED if self.time_remaining <= 30 else WHITE
        timer_text = self.font.render(f"Time: {minutes:02d}:{seconds:02d}", True, timer_color)
        timer_rect = timer_text.get_rect(center=(SCREEN_WIDTH // 2, 20))
        self.screen.blit(timer_text, timer_rect)

        # Coins remaining
        coins_text = self.font.render(f"Coins: {self.maze.get_coin_count()}", True, YELLOW)
        self.screen.blit(coins_text, (10, SCREEN_HEIGHT - 30))

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        if self.won:
            text = self.big_font.render("YOU WIN!", True, YELLOW)
            subtext = self.font.render(f"Final Score: {self.score}", True, WHITE)
        else:
            text = self.big_font.render("GAME OVER", True, RED)
            subtext = self.font.render(f"Score: {self.score}", True, WHITE)

        restart_text = self.font.render("Press R to restart", True, GRAY)

        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        subrect = subtext.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

        self.screen.blit(text, text_rect)
        self.screen.blit(subtext, subrect)
        self.screen.blit(restart_text, restart_rect)

    def draw(self):
        """Draw everything."""
        self.screen.fill(BLACK)
        self.draw_maze()
        self.draw_player()
        self.draw_enemies()
        self.draw_ui()

        if self.game_over or self.won:
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    """Entry point."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
