"""
Vector Super Mario Bros Multi-Level Platformer
A classic side-scrolling platformer with procedural level progression.
"""
import pygame
import sys
import random
import json
import os
from typing import List, Tuple, Optional
from enum import Enum
from dataclasses import dataclass

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 40

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
RED = (255, 80, 80)
GREEN = (80, 255, 80)
YELLOW = (255, 255, 80)
BLUE = (80, 80, 255)
ORANGE = (255, 165, 80)
BROWN = (139, 69, 19)
SKY_BLUE = (135, 206, 235)

# Game physics
GRAVITY = 0.8
JUMP_FORCE = -15
MOVE_SPEED = 5
MAX_FALL_SPEED = 15

# Scoring
COIN_SCORE = 100
ENEMY_SCORE = 200
FLAG_SCORE = 5000
HIGH_SCORE_FILE = "high_score.json"

# Tile types
TILE_EMPTY = 0
TILE_GROUND = 1
TILE_BRICK = 2
TILE_QUESTION = 3
TILE_PIPE_L = 4
TILE_PIPE_R = 5
TILE_FLAG = 6


class Direction(Enum):
    LEFT = -1
    RIGHT = 1


@dataclass
class LevelData:
    """Procedurally generated level data."""
    tiles: List[List[int]]
    player_start: Tuple[int, int]
    enemies: List[Tuple[int, int]]
    coins: List[Tuple[int, int]]
    flag_pos: Tuple[int, int]
    length: int


class Camera:
    """Side-scrolling camera."""

    def __init__(self):
        self.offset_x = 0

    def update(self, target_x: float, level_length: int):
        """Update camera to follow target."""
        # Keep player centered horizontally
        target = target_x - SCREEN_WIDTH // 3
        target = max(0, min(target, level_length - SCREEN_WIDTH))
        # Smooth follow
        self.offset_x += (target - self.offset_x) * 0.1


class Player:
    """The player character."""

    def __init__(self, x: int, y: int):
        self.x = float(x)
        self.y = float(y)
        self.width = 30
        self.height = 40
        self.vel_x = 0.0
        self.vel_y = 0.0
        self.on_ground = False
        self.alive = True
        self.won = False
        self.invincible_timer = 0
        self.coins_collected = 0
        self.enemies_defeated = 0

    def update(self, tiles: List[List[int]], level_width: int, level_height: int):
        """Update player physics."""
        if not self.alive or self.won:
            return

        # Apply gravity
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)

        # Move X
        self.x += self.vel_x
        self.x = max(0, min(self.x, level_width - self.width))

        # Horizontal collision
        self._handle_collision(tiles, True)

        # Move Y
        self.y += self.vel_y

        # Vertical collision
        self.on_ground = False
        self._handle_collision(tiles, False)

        # Check if fell off
        if self.y > level_height:
            self.alive = False

        # Update invincibility
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def _handle_collision(self, tiles: List[List[int]], horizontal: bool):
        """Handle tile collisions."""
        tile_rects = self._get_tile_colliders(tiles)

        for tile_rect in tile_rects:
            player_rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)

            if player_rect.colliderect(tile_rect):
                if horizontal:
                    if self.vel_x > 0:
                        self.x = tile_rect.left - self.width
                    elif self.vel_x < 0:
                        self.x = tile_rect.right
                    self.vel_x = 0
                else:
                    if self.vel_y > 0:
                        self.y = tile_rect.top - self.height
                        self.on_ground = True
                    elif self.vel_y < 0:
                        self.y = tile_rect.bottom
                    self.vel_y = 0

    def _get_tile_colliders(self, tiles: List[List[int]]) -> List[pygame.Rect]:
        """Get colliding tile rectangles."""
        rects = []
        start_col = max(0, int(self.x // TILE_SIZE) - 1)
        end_col = min(len(tiles[0]), int((self.x + self.width) // TILE_SIZE) + 2)
        start_row = max(0, int(self.y // TILE_SIZE) - 1)
        end_row = min(len(tiles), int((self.y + self.height) // TILE_SIZE) + 2)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                if tiles[row][col] in (TILE_GROUND, TILE_BRICK, TILE_QUESTION, TILE_PIPE_L, TILE_PIPE_R):
                    rects.append(pygame.Rect(
                        col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE
                    ))
        return rects

    def jump(self) -> bool:
        """Jump if on ground."""
        if self.on_ground:
            self.vel_y = JUMP_FORCE
            return True
        return False

    def move(self, direction: Direction):
        """Move horizontally."""
        self.vel_x = MOVE_SPEED * direction.value

    def stop(self):
        """Stop horizontal movement."""
        self.vel_x = 0

    def take_damage(self):
        """Take damage if not invincible."""
        if self.invincible_timer == 0:
            self.alive = False
            return True
        return False

    def make_invincible(self, frames: int = 60):
        """Make player temporarily invincible."""
        self.invincible_timer = frames

    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface: pygame.Surface, camera_x: float):
        """Draw the player."""
        if not self.alive and self.invincible_timer == 0:
            return

        screen_x = int(self.x - camera_x)
        screen_y = int(self.y)

        # Flicker when invincible
        if self.invincible_timer > 0 and (self.invincible_timer // 4) % 2 == 0:
            return

        # Body
        pygame.draw.rect(surface, RED, (screen_x + 5, screen_y + 15, 20, 25))

        # Head
        pygame.draw.circle(surface, RED, (screen_x + 15, screen_y + 12), 12)
        pygame.draw.circle(surface, WHITE, (screen_x + 15, screen_y + 12), 12, 2)

        # Hat
        pygame.draw.rect(surface, RED, (screen_x + 2, screen_y, 26, 8))

        # Eyes
        pygame.draw.circle(surface, WHITE, (screen_x + 11, screen_y + 10), 3)
        pygame.draw.circle(surface, WHITE, (screen_x + 19, screen_y + 10), 3)
        pygame.draw.circle(surface, BLACK, (screen_x + 11, screen_y + 10), 1)
        pygame.draw.circle(surface, BLACK, (screen_x + 19, screen_y + 10), 1)


class Enemy:
    """A Goomba-style enemy."""

    def __init__(self, x: int, y: int):
        self.x = float(x)
        self.y = float(y)
        self.width = 30
        self.height = 30
        self.vel_x = 1.0
        self.vel_y = 0.0
        self.alive = True
        self.direction = Direction.LEFT
        self.patrol_start = x - 100
        self.patrol_end = x + 100

    def update(self, tiles: List[List[int]]):
        """Update enemy movement."""
        if not self.alive:
            return

        # Apply gravity
        self.vel_y = min(self.vel_y + GRAVITY, MAX_FALL_SPEED)

        # Move X
        self.x += self.vel_x * self.direction.value

        # Reverse at patrol bounds
        if self.x <= self.patrol_start or self.x >= self.patrol_end:
            self.direction = Direction.LEFT if self.direction == Direction.RIGHT else Direction.RIGHT

        # Horizontal collision
        tile_rects = self._get_tile_colliders(tiles)
        player_rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)

        for tile_rect in tile_rects:
            if player_rect.colliderect(tile_rect):
                self.direction = Direction.LEFT if self.direction == Direction.RIGHT else Direction.RIGHT
                self.x += self.vel_x * self.direction.value * 2
                break

        # Move Y
        self.y += self.vel_y

        # Vertical collision
        for tile_rect in tile_rects:
            player_rect = pygame.Rect(int(self.x), int(self.y), self.width, self.height)
            if player_rect.colliderect(tile_rect):
                if self.vel_y > 0:
                    self.y = tile_rect.top - self.height
                self.vel_y = 0
                break

    def _get_tile_colliders(self, tiles: List[List[int]]) -> List[pygame.Rect]:
        """Get nearby tile rectangles."""
        rects = []
        start_col = max(0, int(self.x // TILE_SIZE) - 1)
        end_col = min(len(tiles[0]), int((self.x + self.width) // TILE_SIZE) + 2)
        start_row = max(0, int(self.y // TILE_SIZE) - 1)
        end_row = min(len(tiles), int((self.y + self.height) // TILE_SIZE) + 2)

        for row in range(start_row, end_row):
            for col in range(start_col, end_col):
                if tiles[row][col] in (TILE_GROUND, TILE_BRICK, TILE_QUESTION, TILE_PIPE_L, TILE_PIPE_R):
                    rects.append(pygame.Rect(
                        col * TILE_SIZE, row * TILE_SIZE, TILE_SIZE, TILE_SIZE
                    ))
        return rects

    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface: pygame.Surface, camera_x: float):
        """Draw the enemy."""
        if not self.alive:
            return

        screen_x = int(self.x - camera_x)
        screen_y = int(self.y)

        # Goomba body
        pygame.draw.ellipse(surface, BROWN, (screen_x, screen_y + 10, 30, 20))
        pygame.draw.ellipse(surface, BLACK, (screen_x, screen_y + 10, 30, 20), 2)

        # Head
        pygame.draw.circle(surface, BROWN, (screen_x + 15, screen_y + 10), 12)
        pygame.draw.circle(surface, BLACK, (screen_x + 15, screen_y + 10), 12, 2)

        # Eyes
        eye_x = screen_x + 15
        eye_y = screen_y + 8
        pygame.draw.circle(surface, WHITE, (eye_x - 4, eye_y), 4)
        pygame.draw.circle(surface, WHITE, (eye_x + 4, eye_y), 4)
        pygame.draw.circle(surface, BLACK, (eye_x - 4, eye_y), 2)
        pygame.draw.circle(surface, BLACK, (eye_x + 4, eye_y), 2)

        # Angry eyebrows
        pygame.draw.line(surface, BLACK, (eye_x - 8, eye_y - 4), (eye_x - 1, eye_y - 2), 2)
        pygame.draw.line(surface, BLACK, (eye_x + 8, eye_y - 4), (eye_x + 1, eye_y - 2), 2)


class Coin:
    """A collectible coin."""

    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y
        self.radius = 12
        self.collected = False
        self.anim_frame = 0

    def update(self):
        """Update animation."""
        self.anim_frame = (self.anim_frame + 1) % 30

    def get_rect(self) -> pygame.Rect:
        """Get collision rectangle."""
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                          self.radius * 2, self.radius * 2)

    def draw(self, surface: pygame.Surface, camera_x: float):
        """Draw the coin."""
        if self.collected:
            return

        screen_x = int(self.x - camera_x)
        screen_y = int(self.y)

        # Spinning effect
        width_scale = abs((self.anim_frame // 5) - 3) / 3
        draw_width = int(self.radius * 2 * width_scale)
        if draw_width < 2:
            draw_width = 2

        pygame.draw.ellipse(surface, YELLOW,
                          (screen_x - draw_width // 2, screen_y - self.radius,
                           draw_width, self.radius * 2))
        pygame.draw.ellipse(surface, ORANGE,
                          (screen_x - draw_width // 2, screen_y - self.radius,
                           draw_width, self.radius * 2), 2)


class LevelGenerator:
    """Procedural level generation."""

    def __init__(self, level: int):
        self.level = level
        self.rows = SCREEN_HEIGHT // TILE_SIZE
        self.cols = 50 + level * 10  # Increase length with level

    def generate(self) -> LevelData:
        """Generate a new level."""
        # Initialize empty tiles
        tiles = [[TILE_EMPTY for _ in range(self.cols)] for _ in range(self.rows)]

        # Place ground
        ground_height = self.rows - 3
        for col in range(self.cols):
            tiles[ground_height][col] = TILE_GROUND
            tiles[ground_height + 1][col] = TILE_GROUND
            tiles[ground_height + 2][col] = TILE_GROUND

        # Place platforms and obstacles
        num_platforms = 5 + self.level
        for i in range(num_platforms):
            col = random.randint(8, self.cols - 8)
            row = ground_height - random.randint(2, 6)
            width = random.randint(3, 6)

            # Create gap in ground first
            if random.random() < 0.3 and i < num_platforms - 1:
                gap_width = random.randint(2, 4)
                for gc in range(col, min(col + gap_width, self.cols - 5)):
                    tiles[ground_height][gc] = TILE_EMPTY
                    tiles[ground_height + 1][gc] = TILE_EMPTY
                    tiles[ground_height + 2][gc] = TILE_EMPTY

            # Place platform
            for c in range(col, min(col + width, self.cols)):
                if 0 <= row < self.rows and 0 <= c < self.cols:
                    tiles[row][c] = TILE_BRICK

        # Place pipes
        num_pipes = 2 + self.level // 2
        for _ in range(num_pipes):
            col = random.randint(10, self.cols - 20)
            height = random.randint(2, 4)
            base_row = ground_height

            for h in range(height):
                if base_row - h >= 0:
                    tiles[base_row - h][col] = TILE_PIPE_L
                    tiles[base_row - h][col + 1] = TILE_PIPE_R

        # Place question blocks
        num_blocks = 3 + self.level
        for _ in range(num_blocks):
            col = random.randint(5, self.cols - 10)
            row = ground_height - random.randint(3, 7)
            if 0 <= row < self.rows and 0 <= col < self.cols:
                tiles[row][col] = TILE_QUESTION

        # Place enemies
        enemies = []
        num_enemies = 3 + self.level
        for _ in range(num_enemies):
            col = random.randint(8, self.cols - 10)
            x = col * TILE_SIZE + 5
            y = (ground_height - 1) * TILE_SIZE
            enemies.append((x, y))

        # Place coins
        coins = []
        num_coins = 5 + self.level * 2
        for _ in range(num_coins):
            col = random.randint(5, self.cols - 10)
            row = ground_height - random.randint(2, 8)
            x = col * TILE_SIZE + TILE_SIZE // 2
            y = row * TILE_SIZE + TILE_SIZE // 2
            coins.append((x, y))

        # Place flag at end
        flag_col = self.cols - 3
        flag_row = ground_height
        for r in range(flag_row - 5, flag_row):
            if r >= 0:
                tiles[r][flag_col] = TILE_GROUND
        flag_pos = (flag_col * TILE_SIZE, (flag_row - 5) * TILE_SIZE)

        # Player start
        player_start = (100, (ground_height - 2) * TILE_SIZE)

        return LevelData(
            tiles=tiles,
            player_start=player_start,
            enemies=enemies,
            coins=coins,
            flag_pos=flag_pos,
            length=self.cols * TILE_SIZE
        )


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros Multi-Level Platformer")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 64)
        self.small_font = pygame.font.Font(None, 24)

        self.high_score = self._load_high_score()
        self.current_level = 1
        self.total_score = 0
        self.lives = 3

        self.camera = Camera()
        self.state = "playing"  # playing, game_over, level_complete, victory

        self._generate_level()

    def _load_high_score(self) -> int:
        """Load high score from file."""
        try:
            if os.path.exists(HIGH_SCORE_FILE):
                with open(HIGH_SCORE_FILE, 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0

    def _save_high_score(self):
        """Save high score to file."""
        try:
            with open(HIGH_SCORE_FILE, 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass

    def _generate_level(self):
        """Generate a new level."""
        generator = LevelGenerator(self.current_level)
        level_data = generator.generate()

        self.tiles = level_data.tiles
        self.level_width = level_data.length
        self.level_height = SCREEN_HEIGHT

        self.player = Player(*level_data.player_start)

        self.enemies = [Enemy(x, y) for x, y in level_data.enemies]
        self.coins = [Coin(x, y) for x, y in level_data.coins]
        self.flag_rect = pygame.Rect(level_data.flag_pos[0], level_data.flag_pos[1],
                                    TILE_SIZE, TILE_SIZE * 5)

        self.camera.offset_x = 0
        self.state = "playing"

    def handle_input(self) -> bool:
        """Handle player input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                elif event.key == pygame.K_r:
                    if self.state in ("game_over", "victory"):
                        self.current_level = 1
                        self.total_score = 0
                        self.lives = 3
                        self._generate_level()
                    elif self.state == "level_complete":
                        self._generate_level()
                elif self.state == "playing":
                    if event.key == pygame.K_SPACE:
                        self.player.jump()
                    elif event.key == pygame.K_LEFT:
                        self.player.move(Direction.LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.player.move(Direction.RIGHT)
            elif event.type == pygame.KEYUP:
                if self.state == "playing":
                    if event.key in (pygame.K_LEFT, pygame.K_RIGHT):
                        self.player.stop()
        return True

    def update(self):
        """Update game state."""
        if self.state != "playing":
            return

        # Update player
        self.player.update(self.tiles, self.level_width, self.level_height)

        # Update camera
        self.camera.update(self.player.x, self.level_width)

        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.tiles)

            # Check collision with player
            if enemy.alive and enemy.get_rect().colliderect(self.player.get_rect()):
                # Check if player stomped enemy (from above)
                if self.player.vel_y > 0 and self.player.y + self.player.height < enemy.y + enemy.height // 2:
                    enemy.alive = False
                    self.player.vel_y = JUMP_FORCE // 2
                    self.player.enemies_defeated += 1
                    self.total_score += ENEMY_SCORE
                elif not self.player.take_damage():
                    self.lives -= 1
                    if self.lives <= 0:
                        self.state = "game_over"
                        if self.total_score > self.high_score:
                            self.high_score = self.total_score
                            self._save_high_score()
                    else:
                        # Respawn
                        self.player.x, self.player.y = self.tiles[0].index(TILE_GROUND) * TILE_SIZE if TILE_GROUND in self.tiles[0] else 100, 200
                        self.player.vel_x = 0
                        self.player.vel_y = 0
                        self.player.make_invincible()

        # Update coins
        for coin in self.coins:
            coin.update()
            if not coin.collected and coin.get_rect().colliderect(self.player.get_rect()):
                coin.collected = True
                self.player.coins_collected += 1
                self.total_score += COIN_SCORE

        # Check flag collision
        if self.player.get_rect().colliderect(self.flag_rect):
            self.player.won = True
            self.total_score += FLAG_SCORE
            self.current_level += 1
            self.state = "level_complete"

        # Check if player died
        if not self.player.alive:
            self.lives -= 1
            if self.lives <= 0:
                self.state = "game_over"
                if self.total_score > self.high_score:
                    self.high_score = self.total_score
                    self._save_high_score()
            else:
                # Respawn at start
                for row in range(len(self.tiles)):
                    if TILE_GROUND in self.tiles[row]:
                        col = self.tiles[row].index(TILE_GROUND)
                        self.player.x = col * TILE_SIZE
                        self.player.y = (row - 2) * TILE_SIZE
                        break
                self.player.vel_x = 0
                self.player.vel_y = 0
                self.player.alive = True
                self.player.make_invincible()

    def draw_background(self):
        """Draw the background."""
        self.screen.fill(SKY_BLUE)

        # Draw subtle clouds
        for i in range(5):
            x = (int(self.camera.offset_x) // 2 + i * 200) % (SCREEN_WIDTH + 100) - 50
            y = 50 + (i % 3) * 40
            pygame.draw.ellipse(self.screen, WHITE, (x, y, 80, 40))

    def draw_tiles(self):
        """Draw visible tiles."""
        start_col = max(0, int(self.camera.offset_x // TILE_SIZE))
        end_col = min(len(self.tiles[0]), start_col + (SCREEN_WIDTH // TILE_SIZE) + 2)

        for row in range(len(self.tiles)):
            for col in range(start_col, end_col):
                tile = self.tiles[row][col]
                if tile == TILE_EMPTY:
                    continue

                screen_x = col * TILE_SIZE - int(self.camera.offset_x)
                screen_y = row * TILE_SIZE
                rect = pygame.Rect(screen_x, screen_y, TILE_SIZE, TILE_SIZE)

                if tile == TILE_GROUND:
                    pygame.draw.rect(self.screen, BROWN, rect)
                    pygame.draw.rect(self.screen, DARK_GRAY, rect, 2)
                elif tile == TILE_BRICK:
                    pygame.draw.rect(self.screen, ORANGE, rect)
                    pygame.draw.rect(self.screen, RED, rect, 2)
                    # Brick pattern
                    pygame.draw.line(self.screen, RED, (screen_x, screen_y + TILE_SIZE // 2),
                                    (screen_x + TILE_SIZE, screen_y + TILE_SIZE // 2), 1)
                elif tile == TILE_QUESTION:
                    pygame.draw.rect(self.screen, YELLOW, rect)
                    pygame.draw.rect(self.screen, ORANGE, rect, 2)
                    # Question mark
                    q_text = self.small_font.render("?", True, ORANGE)
                    q_rect = q_text.get_rect(center=rect.center)
                    self.screen.blit(q_text, q_rect)
                elif tile in (TILE_PIPE_L, TILE_PIPE_R):
                    pygame.draw.rect(self.screen, GREEN, rect)
                    pygame.draw.rect(self.screen, DARK_GRAY, rect, 2)

        # Draw flag
        flag_screen_x = self.flag_rect.x - int(self.camera.offset_x)
        if -TILE_SIZE < flag_screen_x < SCREEN_WIDTH:
            # Pole
            pole_start = (flag_screen_x + TILE_SIZE // 2, self.flag_rect.y)
            pole_end = (flag_screen_x + TILE_SIZE // 2, self.flag_rect.y + TILE_SIZE * 5)
            pygame.draw.line(self.screen, GRAY, pole_start, pole_end, 4)
            # Flag
            pygame.draw.polygon(self.screen, RED, [
                (pole_start[0], pole_start[1]),
                (pole_start[0] + 30, pole_start[1] + 15),
                (pole_start[0], pole_start[1] + 30)
            ])

    def draw_ui(self):
        """Draw UI elements."""
        # Top bar background
        pygame.draw.rect(self.screen, BLACK, (0, 0, SCREEN_WIDTH, 40))

        # Score
        score_text = self.font.render(f"Score: {self.total_score}", True, WHITE)
        self.screen.blit(score_text, (10, 5))

        # Level
        level_text = self.font.render(f"Level: {self.current_level}", True, YELLOW)
        self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 40, 5))

        # Lives
        lives_text = self.font.render(f"Lives: {self.lives}", True, RED)
        self.screen.blit(lives_text, (SCREEN_WIDTH - 120, 5))

        # High score
        high_text = self.small_font.render(f"High: {self.high_score}", True, GREEN)
        self.screen.blit(high_text, (10, SCREEN_HEIGHT - 25))

        # Controls
        controls = "ARROWS: Move | SPACE: Jump | R: Restart | ESC: Quit"
        ctrl_text = self.small_font.render(controls, True, GRAY)
        ctrl_rect = ctrl_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 15))
        self.screen.blit(ctrl_text, ctrl_rect)

    def draw_level_complete(self):
        """Draw level complete screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))

        text = self.big_font.render("LEVEL COMPLETE!", True, GREEN)
        score_text = self.font.render(f"Bonus: +{FLAG_SCORE}", True, YELLOW)
        next_text = self.font.render(f"Next: Level {self.current_level}", True, WHITE)
        cont_text = self.font.render("Press R to continue", True, GRAY)

        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        next_rect = next_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
        cont_rect = cont_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))

        self.screen.blit(text, text_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(next_text, next_rect)
        self.screen.blit(cont_text, cont_rect)

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(180)
        self.screen.blit(overlay, (0, 0))

        text = self.big_font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {self.total_score}", True, WHITE)
        level_text = self.font.render(f"Level Reached: {self.current_level}", True, YELLOW)

        is_high = self.total_score >= self.high_score
        high_text = self.font.render(
            f"{'NEW ' if is_high else ''}High Score: {self.high_score}",
            True, GREEN if is_high else GRAY
        )

        restart_text = self.font.render("Press R to restart", True, GRAY)

        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        high_rect = high_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        level_rect = level_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 110))

        self.screen.blit(text, text_rect)
        self.screen.blit(score_text, score_rect)
        self.screen.blit(high_text, high_rect)
        self.screen.blit(level_text, level_rect)
        self.screen.blit(restart_text, restart_rect)

    def draw(self):
        """Draw everything."""
        self.draw_background()
        self.draw_tiles()

        # Draw coins
        for coin in self.coins:
            coin.draw(self.screen, self.camera.offset_x)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen, self.camera.offset_x)

        # Draw player
        self.player.draw(self.screen, self.camera.offset_x)

        # Draw UI
        self.draw_ui()

        # Draw overlays
        if self.state == "level_complete":
            self.draw_level_complete()
        elif self.state == "game_over":
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
