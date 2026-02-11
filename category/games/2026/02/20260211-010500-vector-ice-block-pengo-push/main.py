"""
Vector Ice Block Pengo Push
Strategic block-pushing puzzle where you crush enemies between ice slides.
"""

import pygame
import random
from typing import List, Optional, Tuple, Set
from enum import Enum
from dataclasses import dataclass


# Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
FPS = 60

# Grid settings
GRID_SIZE = 13
CELL_SIZE = SCREEN_WIDTH // GRID_SIZE

# Colors
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_CYAN = (50, 200, 255)
COLOR_BLUE = (50, 100, 200)
COLOR_RED = (255, 50, 50)
COLOR_ORANGE = (255, 165, 0)
COLOR_YELLOW = (255, 255, 50)
COLOR_PURPLE = (200, 50, 255)
COLOR_GREEN = (50, 255, 50)
COLOR_ICE = (180, 220, 255)
COLOR_DIAMOND = (100, 255, 255)
COLOR_WALL = (80, 80, 100)

# Game settings
PLAYER_SPEED = 4
ENEMY_SPEED = 2
SLIDE_SPEED = 8

# Scoring
SCORE_ENEMY_CRUSH = 100
SCORE_BLOCK_BREAK = 10
SCORE_DIAMOND_ALIGN = 500

# Directions
DIR_UP = (0, -1)
DIR_DOWN = (0, 1)
DIR_LEFT = (-1, 0)
DIR_RIGHT = (1, 0)
DIR_NONE = (0, 0)


class CellType(Enum):
    EMPTY = 0
    WALL = 1
    ICE_BLOCK = 2
    DIAMOND_BLOCK = 3


class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1
    WON = 2


@dataclass
class SlideAnimation:
    grid_x: int
    grid_y: int
    target_x: int
    target_y: int
    pixel_x: float
    pixel_y: float
    direction: Tuple[int, int]
    active: bool = True
    crush_pending: bool = False


class Enemy:
    """Patrolling enemy that can be crushed by sliding blocks."""

    def __init__(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = grid_x * CELL_SIZE + CELL_SIZE // 2
        self.pixel_y = grid_y * CELL_SIZE + CELL_SIZE // 2
        self.direction = DIR_NONE
        self.move_timer = 0
        self.move_delay = random.randint(15, 30)
        self.alive = True
        self.color = COLOR_RED

    def set_position(self, grid_x: int, grid_y: int) -> None:
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = grid_x * CELL_SIZE + CELL_SIZE // 2
        self.pixel_y = grid_y * CELL_SIZE + CELL_SIZE // 2

    def update(self, game_state: 'Game') -> None:
        if not self.alive:
            return

        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return

        self.move_timer = 0
        self.move_delay = random.randint(15, 30)

        # Choose a direction (simple AI: 40% toward player, 60% random)
        if random.random() < 0.4:
            # Move toward player
            dx = game_state.player.grid_x - self.grid_x
            dy = game_state.player.grid_y - self.grid_y

            if abs(dx) > abs(dy):
                self.direction = DIR_RIGHT if dx > 0 else DIR_LEFT
            else:
                self.direction = DIR_DOWN if dy > 0 else DIR_UP
        else:
            # Random direction
            dirs = [DIR_UP, DIR_DOWN, DIR_LEFT, DIR_RIGHT]
            self.direction = random.choice(dirs)

        # Check if move is valid
        new_x = self.grid_x + self.direction[0]
        new_y = self.grid_y + self.direction[1]

        if self._can_move_to(new_x, new_y, game_state):
            self.grid_x = new_x
            self.grid_y = new_y

    def _can_move_to(self, x: int, y: int, game_state: 'Game') -> bool:
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return False

        cell = game_state.grid[y][x]
        if cell in [CellType.WALL, CellType.ICE_BLOCK, CellType.DIAMOND_BLOCK]:
            return False

        # Check for sliding blocks in the path
        for slide in game_state.slides:
            if slide.active and slide.target_x == x and slide.target_y == y:
                return False

        return True

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.pixel_x - CELL_SIZE // 2 + 4),
            int(self.pixel_y - CELL_SIZE // 2 + 4),
            CELL_SIZE - 8,
            CELL_SIZE - 8
        )

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return

        self.pixel_x += (self.grid_x * CELL_SIZE + CELL_SIZE // 2 - self.pixel_x) * 0.2
        self.pixel_y += (self.grid_y * CELL_SIZE + CELL_SIZE // 2 - self.pixel_y) * 0.2

        rect = self.get_rect()

        # Draw blob-like enemy
        pygame.draw.circle(surface, self.color, rect.center, rect.width // 2)
        pygame.draw.circle(surface, COLOR_ORANGE, rect.center, rect.width // 3)

        # Eyes
        eye_offset_x = 4
        eye_offset_y = -2
        pygame.draw.circle(surface, COLOR_WHITE,
                         (rect.centerx - eye_offset_x, rect.centery + eye_offset_y), 3)
        pygame.draw.circle(surface, COLOR_WHITE,
                         (rect.centerx + eye_offset_x, rect.centery + eye_offset_y), 3)
        pygame.draw.circle(surface, COLOR_BLACK,
                         (rect.centerx - eye_offset_x, rect.centery + eye_offset_y), 1)
        pygame.draw.circle(surface, COLOR_BLACK,
                         (rect.centerx + eye_offset_x, rect.centery + eye_offset_y), 1)


class Player:
    """Player controlled character that can push ice blocks."""

    def __init__(self, grid_x: int, grid_y: int):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = grid_x * CELL_SIZE + CELL_SIZE // 2
        self.pixel_y = grid_y * CELL_SIZE + CELL_SIZE // 2
        self.direction = DIR_RIGHT
        self.alive = True
        self.move_timer = 0
        self.move_delay = 8

    def set_position(self, grid_x: int, grid_y: int) -> None:
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.pixel_x = grid_x * CELL_SIZE + CELL_SIZE // 2
        self.pixel_y = grid_y * CELL_SIZE + CELL_SIZE // 2

    def update(self, keys) -> Tuple[int, int]:
        """Returns movement direction."""
        if not self.alive:
            return DIR_NONE

        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return DIR_NONE

        dx, dy = 0, 0

        if keys[pygame.K_UP]:
            dy = -1
            self.direction = DIR_UP
        elif keys[pygame.K_DOWN]:
            dy = 1
            self.direction = DIR_DOWN
        elif keys[pygame.K_LEFT]:
            dx = -1
            self.direction = DIR_LEFT
        elif keys[pygame.K_RIGHT]:
            dx = 1
            self.direction = DIR_RIGHT

        if dx != 0 or dy != 0:
            self.move_timer = 0
            return (dx, dy)

        return DIR_NONE

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.pixel_x - CELL_SIZE // 2 + 4),
            int(self.pixel_y - CELL_SIZE // 2 + 4),
            CELL_SIZE - 8,
            CELL_SIZE - 8
        )

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return

        # Smooth pixel movement toward grid position
        self.pixel_x += (self.grid_x * CELL_SIZE + CELL_SIZE // 2 - self.pixel_x) * 0.3
        self.pixel_y += (self.grid_y * CELL_SIZE + CELL_SIZE // 2 - self.pixel_y) * 0.3

        rect = self.get_rect()

        # Draw Pengo-like character
        # Body
        pygame.draw.circle(surface, COLOR_CYAN, rect.center, rect.width // 2)

        # Face
        face_color = COLOR_WHITE
        pygame.draw.circle(surface, face_color, rect.center, rect.width // 3)

        # Eyes based on direction
        eye_offset_x = self.direction[0] * 3
        eye_offset_y = self.direction[1] * 3

        left_eye_x = rect.centerx - 4 + eye_offset_x
        right_eye_x = rect.centerx + 4 + eye_offset_x
        eye_y = rect.centery - 2 + eye_offset_y

        pygame.draw.circle(surface, COLOR_BLACK, (left_eye_x, eye_y), 2)
        pygame.draw.circle(surface, COLOR_BLACK, (right_eye_x, eye_y), 2)

        # Beak
        beak_x = rect.centerx + self.direction[0] * 8
        beak_y = rect.centery + 3 + self.direction[1] * 3
        pygame.draw.polygon(surface, COLOR_ORANGE, [
            (beak_x, beak_y - 3),
            (beak_x + self.direction[0] * 4, beak_y),
            (beak_x, beak_y + 3)
        ])


class Particle:
    """Visual effect for block breaking."""

    def __init__(self, x: int, y: int, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-5, -1)
        self.life = 30
        self.color = color
        self.size = random.randint(2, 5)

    def update(self) -> bool:
        self.x += self.vx
        self.y += self.vy
        self.vy += 0.2  # Gravity
        self.life -= 1
        return self.life > 0

    def draw(self, surface: pygame.Surface) -> None:
        alpha = int(255 * (self.life / 30))
        color = (*self.color, alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.size, self.size), self.size)
        surface.blit(s, (int(self.x) - self.size, int(self.y) - self.size))


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Ice Block Pengo Push")
        self.clock = pygame.time.Clock()
        self.running = True

        # Fonts
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 36)
        self.font_small = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self) -> None:
        """Reset game to initial state."""
        self.grid: List[List[CellType]] = [[CellType.EMPTY for _ in range(GRID_SIZE)]
                                            for _ in range(GRID_SIZE)]
        self.player = Player(6, 6)
        self.enemies: List[Enemy] = []
        self.slides: List[SlideAnimation] = []
        self.particles: List[Particle] = []
        self.score = 0
        self.state = GameState.PLAYING
        self.push_cooldown = 0

        self._init_level()

    def _init_level(self) -> None:
        """Initialize level layout."""
        # Clear grid
        self.grid = [[CellType.EMPTY for _ in range(GRID_SIZE)]
                     for _ in range(GRID_SIZE)]

        # Add walls around border
        for x in range(GRID_SIZE):
            self.grid[0][x] = CellType.WALL
            self.grid[GRID_SIZE - 1][x] = CellType.WALL
        for y in range(GRID_SIZE):
            self.grid[y][0] = CellType.WALL
            self.grid[y][GRID_SIZE - 1] = CellType.WALL

        # Add some interior walls (blocks of 4)
        wall_positions = [
            (3, 3), (4, 3), (3, 4), (4, 4),
            (8, 3), (9, 3), (8, 4), (9, 4),
            (3, 8), (4, 8), (3, 9), (4, 9),
            (8, 8), (9, 8), (8, 9), (9, 9),
        ]
        for wx, wy in wall_positions:
            self.grid[wy][wx] = CellType.WALL

        # Add ice blocks
        ice_positions = [
            (2, 5), (2, 6), (2, 7),
            (5, 2), (6, 2), (7, 2),
            (10, 5), (10, 6), (10, 7),
            (5, 10), (6, 10), (7, 10),
        ]
        for ix, iy in ice_positions:
            self.grid[iy][ix] = CellType.ICE_BLOCK

        # Add diamond blocks (special blocks that give bonus when aligned)
        diamond_count = 0
        for y in range(2, GRID_SIZE - 2):
            for x in range(2, GRID_SIZE - 2):
                if diamond_count >= 6:
                    break
                if self.grid[y][x] == CellType.EMPTY:
                    if random.random() < 0.1:
                        self.grid[y][x] = CellType.DIAMOND_BLOCK
                        diamond_count += 1

        # Place player
        self.player.set_position(6, 6)

        # Place enemies
        self.enemies = []
        enemy_positions = [(2, 2), (10, 2), (2, 10), (10, 10), (5, 5), (7, 7)]
        for ex, ey in enemy_positions:
            if self.grid[ey][ex] == CellType.EMPTY:
                self.enemies.append(Enemy(ex, ey))

    def handle_input(self) -> None:
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

                if self.state != GameState.PLAYING:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                        self.reset_game()
                else:
                    # Push block
                    if event.key == pygame.K_SPACE:
                        self._try_push_block()

    def _try_push_block(self) -> None:
        """Try to push a block in the direction player is facing."""
        if self.push_cooldown > 0:
            return

        target_x = self.player.grid_x + self.player.direction[0]
        target_y = self.player.grid_y + self.player.direction[1]

        if not (0 <= target_x < GRID_SIZE and 0 <= target_y < GRID_SIZE):
            return

        cell = self.grid[target_y][target_x]

        if cell in [CellType.ICE_BLOCK, CellType.DIAMOND_BLOCK]:
            # Start the slide
            self._start_slide(target_x, target_y, self.player.direction)
            self.push_cooldown = 15

    def _start_slide(self, start_x: int, start_y: int, direction: Tuple[int, int]) -> None:
        """Start a block sliding animation."""
        cell_type = self.grid[start_y][start_x]

        # Calculate slide destination
        dest_x, dest_y = start_x, start_y
        crashed = False

        while True:
            next_x = dest_x + direction[0]
            next_y = dest_y + direction[1]

            # Check bounds
            if not (0 <= next_x < GRID_SIZE and 0 <= next_y < GRID_SIZE):
                crashed = True
                break

            next_cell = self.grid[next_y][next_x]

            # Check for collision with wall or another block
            if next_cell == CellType.WALL:
                crashed = True
                break
            elif next_cell in [CellType.ICE_BLOCK, CellType.DIAMOND_BLOCK]:
                crashed = True
                break

            dest_x, dest_y = next_x, next_y

        # Clear original position
        self.grid[start_y][start_x] = CellType.EMPTY

        # Create slide animation
        slide = SlideAnimation(
            grid_x=start_x,
            grid_y=start_y,
            target_x=dest_x,
            target_y=dest_y,
            pixel_x=start_x * CELL_SIZE,
            pixel_y=start_y * CELL_SIZE,
            direction=direction,
            active=True
        )
        self.slides.append(slide)

        # Check if block should break (crashed against wall)
        if crashed:
            slide.crush_pending = True

    def _check_diamond_alignment(self) -> int:
        """Check if 3+ diamond blocks are aligned and return bonus score."""
        diamond_positions = []

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                if self.grid[y][x] == CellType.DIAMOND_BLOCK:
                    diamond_positions.append((x, y))

        if len(diamond_positions) < 3:
            return 0

        # Check horizontal alignment
        for y in range(GRID_SIZE):
            row_diamonds = [x for x, dy in diamond_positions if dy == y]
            if len(row_diamonds) >= 3:
                row_diamonds.sort()
                # Check for 3 consecutive
                for i in range(len(row_diamonds) - 2):
                    if row_diamonds[i + 2] - row_diamonds[i] == 2:
                        return SCORE_DIAMOND_ALIGN

        # Check vertical alignment
        for x in range(GRID_SIZE):
            col_diamonds = [y for dx, y in diamond_positions if dx == x]
            if len(col_diamonds) >= 3:
                col_diamonds.sort()
                for i in range(len(col_diamonds) - 2):
                    if col_diamonds[i + 2] - col_diamonds[i] == 2:
                        return SCORE_DIAMOND_ALIGN

        return 0

    def update(self) -> None:
        """Update game state."""
        if self.push_cooldown > 0:
            self.push_cooldown -= 1

        keys = pygame.key.get_pressed()

        # Update slides first
        for slide in self.slides[:]:
            if not slide.active:
                self.slides.remove(slide)
                continue

            # Move slide
            dx = slide.target_x - slide.grid_x
            dy = slide.target_y - slide.grid_y
            dist = (dx * dx + dy * dy) ** 0.5

            if dist < 0.1:
                # Slide complete
                slide.active = False

                # Place block at destination if not crushing
                if slide.crush_pending:
                    # Block breaks - create particles
                    for _ in range(10):
                        self.particles.append(Particle(
                            slide.target_x * CELL_SIZE + CELL_SIZE // 2,
                            slide.target_y * CELL_SIZE + CELL_SIZE // 2,
                            COLOR_ICE
                        ))
                    self.score += SCORE_BLOCK_BREAK
                else:
                    self.grid[slide.target_y][slide.target_x] = CellType.ICE_BLOCK

                # Check for diamond alignment
                bonus = self._check_diamond_alignment()
                if bonus > 0:
                    self.score += bonus
            else:
                # Move toward target
                move_x = dx / dist * SLIDE_SPEED if dist > SLIDE_SPEED else dx
                move_y = dy / dist * SLIDE_SPEED if dist > SLIDE_SPEED else dy

                slide.pixel_x += move_x
                slide.pixel_y += move_y

                slide.grid_x = slide.pixel_x / CELL_SIZE
                slide.grid_y = slide.pixel_y / CELL_SIZE

                # Check for enemy collision during slide
                slide_grid_x = int(round(slide.grid_x))
                slide_grid_y = int(round(slide.grid_y))

                for enemy in self.enemies[:]:
                    if enemy.alive and enemy.grid_x == slide_grid_x and enemy.grid_y == slide_grid_y:
                        enemy.alive = False
                        self.score += SCORE_ENEMY_CRUSH
                        # Crush particles
                        for _ in range(15):
                            self.particles.append(Particle(
                                enemy.pixel_x,
                                enemy.pixel_y,
                                COLOR_RED
                            ))

        if self.state != GameState.PLAYING:
            return

        # Player movement
        move_dir = self.player.update(keys)
        if move_dir != DIR_NONE:
            new_x = self.player.grid_x + move_dir[0]
            new_y = self.player.grid_y + move_dir[1]

            if self._can_player_move_to(new_x, new_y):
                self.player.grid_x = new_x
                self.player.grid_y = new_y

        # Update enemies
        for enemy in self.enemies:
            enemy.update(self)

        # Update particles
        for particle in self.particles[:]:
            if not particle.update():
                self.particles.remove(particle)

        # Check for enemy collision with player
        player_rect = self.player.get_rect()
        for enemy in self.enemies:
            if enemy.alive:
                enemy_rect = enemy.get_rect()
                if player_rect.colliderect(enemy_rect):
                    self.state = GameState.GAME_OVER
                    self.player.alive = False

        # Check win condition (all enemies dead)
        if all(not e.alive for e in self.enemies):
            self.state = GameState.WON

    def _can_player_move_to(self, x: int, y: int) -> bool:
        if not (0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE):
            return False

        cell = self.grid[y][x]
        if cell in [CellType.WALL, CellType.ICE_BLOCK, CellType.DIAMOND_BLOCK]:
            return False

        # Check for active slides
        for slide in self.slides:
            if slide.active:
                slide_grid_x = int(round(slide.grid_x))
                slide_grid_y = int(round(slide.grid_y))
                if slide_grid_x == x and slide_grid_y == y:
                    return False

        return True

    def draw(self) -> None:
        """Draw all game elements."""
        self.screen.fill(COLOR_BLACK)

        # Draw grid
        self._draw_grid()

        # Draw slides (animated blocks)
        for slide in self.slides:
            if slide.active:
                rect = pygame.Rect(
                    int(slide.pixel_x + 2),
                    int(slide.pixel_y + 2),
                    CELL_SIZE - 4,
                    CELL_SIZE - 4
                )
                pygame.draw.rect(self.screen, COLOR_ICE, rect)
                pygame.draw.rect(self.screen, COLOR_WHITE, rect, 2)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw UI
        self._draw_ui()

        # Draw overlays
        if self.state == GameState.GAME_OVER:
            self._draw_overlay("GAME OVER", f"Score: {self.score}", "Press SPACE to Restart")
        elif self.state == GameState.WON:
            self._draw_overlay("VICTORY!", f"Final Score: {self.score}", "Press SPACE to Play Again")

        pygame.display.flip()

    def _draw_grid(self) -> None:
        """Draw the game grid."""
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                cell = self.grid[y][x]

                # Draw grid lines
                pygame.draw.rect(self.screen, (30, 30, 40), rect, 1)

                if cell == CellType.WALL:
                    pygame.draw.rect(self.screen, COLOR_WALL, rect)
                    pygame.draw.rect(self.screen, (100, 100, 120), rect, 2)

                elif cell == CellType.ICE_BLOCK:
                    inner = rect.inflate(-4, -4)
                    pygame.draw.rect(self.screen, COLOR_ICE, inner)
                    pygame.draw.rect(self.screen, COLOR_WHITE, inner, 2)
                    # Ice shine effect
                    pygame.draw.line(self.screen, (255, 255, 255),
                                   (inner.left + 4, inner.top + 4),
                                   (inner.right - 4, inner.top + 8), 2)

                elif cell == CellType.DIAMOND_BLOCK:
                    inner = rect.inflate(-6, -6)
                    # Diamond shape
                    points = [
                        (inner.centerx, inner.top),
                        (inner.right, inner.centery),
                        (inner.centerx, inner.bottom),
                        (inner.left, inner.centery)
                    ]
                    pygame.draw.polygon(self.screen, COLOR_DIAMOND, points)
                    pygame.draw.polygon(self.screen, COLOR_WHITE, points, 2)

    def _draw_ui(self) -> None:
        """Draw user interface."""
        # Score
        score_text = self.font_medium.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (10, 10))

        # Instructions
        instr_text = self.font_small.render("Arrows: Move | Space: Push", True, (150, 150, 150))
        self.screen.blit(instr_text, (10, SCREEN_HEIGHT - 25))

        # Enemies remaining
        alive_count = sum(1 for e in self.enemies if e.alive)
        enemies_text = self.font_small.render(f"Enemies: {alive_count}", True, COLOR_RED)
        self.screen.blit(enemies_text, (SCREEN_WIDTH - 120, 10))

    def _draw_overlay(self, title: str, subtitle: str, instruction: str) -> None:
        """Draw game overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        title_color = COLOR_GREEN if self.state == GameState.WON else COLOR_RED
        title_text = self.font_large.render(title, True, title_color)
        subtitle_text = self.font_medium.render(subtitle, True, COLOR_WHITE)
        instr_text = self.font_small.render(instruction, True, COLOR_YELLOW)

        title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        instr_rect = instr_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))

        self.screen.blit(title_text, title_rect)
        self.screen.blit(subtitle_text, subtitle_rect)
        self.screen.blit(instr_text, instr_rect)

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.clock.tick(FPS)

            self.handle_input()
            self.update()
            self.draw()

        pygame.quit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
