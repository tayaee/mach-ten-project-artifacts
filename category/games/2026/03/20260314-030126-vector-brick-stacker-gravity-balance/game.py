"""Main game logic for Vector Brick Stacker Gravity Balance."""

import pygame
import random
from typing import Dict, Tuple, Optional, List
from config import (
    Display, Physics, Colors, Platform, Scoring, BlockSizes
)
from block import Block, BlockSpawner
from physics import PhysicsEngine


class Game:
    """Main game class managing the brick stacking game."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        pygame.display.set_caption(Display.TITLE)

        self.screen = pygame.display.set_mode((Display.WIDTH, Display.HEIGHT))
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 48)

        # Game state
        self.running = True
        self.game_over = False
        self.paused = False

        # Platform
        self.platform_rect = pygame.Rect(
            (Display.WIDTH - Platform.WIDTH) // 2,
            Display.HEIGHT - Platform.Y_OFFSET - Platform.HEIGHT,
            Platform.WIDTH,
            Platform.HEIGHT
        )
        self.platform_center_x = Display.WIDTH / 2

        # Blocks
        self.landed_blocks: List[Block] = []
        self.falling_block: Optional[Block] = None
        self.block_spawner = BlockSpawner(Display.WIDTH, 50)

        # Physics
        self.current_fall_speed = Physics.INITIAL_FALL_SPEED
        self.physics_engine = PhysicsEngine()

        # Camera
        self.camera_offset_y = 0

        # Scoring
        self.score = 0
        self.blocks_placed = 0
        self.height_levels = 0

        # AI interface
        self.observation = {}
        self.last_balance = 1.0

        self._spawn_new_block()

    def _spawn_new_block(self):
        """Spawn a new falling block at the top."""
        self.falling_block = self.block_spawner.spawn_block()

    def _land_block(self):
        """Land the current falling block."""
        if not self.falling_block:
            return

        # Create landed block at current position
        landed = self.block_spawner.spawn_landed_block(
            x=self.falling_block.x,
            y=self.falling_block.y,
            width=self.falling_block.width,
            height=self.falling_block.height,
            rotation=self.falling_block.rotation
        )
        landed.is_falling = False
        landed.is_landed = True
        landed.velocity_y = 0

        self.landed_blocks.append(landed)
        self.falling_block = None

        # Update score
        self.score += Scoring.POINTS_PER_BLOCK
        self.blocks_placed += 1

        # Check height bonus
        tower_height = self._get_tower_height()
        new_levels = tower_height // 30
        if new_levels > self.height_levels:
            bonus = (new_levels - self.height_levels) // Scoring.HEIGHT_BONUS_INTERVAL
            self.score += bonus * Scoring.HEIGHT_BONUS_POINTS
            self.height_levels = new_levels

        # Increase difficulty
        self.current_fall_speed = min(
            Physics.MAX_FALL_SPEED,
            self.current_fall_speed + Physics.SPEED_INCREMENT
        )

        # Check balance
        status = self.physics_engine.get_balance_status(
            self.landed_blocks,
            self.platform_center_x,
            Platform.WIDTH / 2,
            Physics.BALANCE_TOLERANCE
        )

        if status == "collapsed":
            self.game_over = True
        else:
            self._spawn_new_block()

    def _get_tower_height(self) -> int:
        """Get the current tower height in pixels."""
        if not self.landed_blocks:
            return 0
        min_y = min(b.y - b.height / 2 for b in self.landed_blocks)
        platform_top = self.platform_rect.top
        return max(0, int(platform_top - min_y))

    def _update_camera(self):
        """Update camera to follow the tower."""
        if not self.landed_blocks:
            self.camera_offset_y = 0
            return

        top_y = min(b.y - b.height / 2 for b in self.landed_blocks)
        target_offset = max(0, Display.HEIGHT * 0.4 - top_y)

        # Smooth camera movement
        self.camera_offset_y += (target_offset - self.camera_offset_y) * 0.1

    def _update_falling_block(self):
        """Update the falling block physics."""
        if not self.falling_block:
            return

        # Update position
        self.falling_block.update(Physics.GRAVITY, self.current_fall_speed)

        # Check for landing
        block_bottom = self.falling_block.y + self.falling_block.height / 2

        # Check platform collision
        if block_bottom >= self.platform_rect.top - self.camera_offset_y:
            # Check horizontal overlap with platform
            b1 = self.falling_block.get_bounds()
            b2 = (self.platform_rect.left, self.platform_rect.top - self.camera_offset_y,
                  self.platform_rect.right, self.platform_rect.bottom - self.camera_offset_y)
            horizontal_overlap = not (b1[2] < b2[0] or b1[0] > b2[2])

            if horizontal_overlap:
                self.falling_block.y = self.platform_rect.top - self.camera_offset_y - self.falling_block.height / 2
                self._land_block()
                return

        # Check collision with landed blocks
        for block in self.landed_blocks:
            # Adjust landed block position for camera
            test_block = Block(
                x=block.x,
                y=block.y - self.camera_offset_y,
                width=block.width,
                height=block.height,
                color=(0, 0, 0),
                border_color=(0, 0, 0),
                rotation=block.rotation
            )

            if self.physics_engine.check_collision(self.falling_block, test_block):
                # Find landing position
                landing_y = self.physics_engine.find_landing_position(
                    self.falling_block,
                    [Block(b.x, b.y - self.camera_offset_y, b.width, b.height,
                           (0, 0, 0), (0, 0, 0), b.rotation) for b in self.landed_blocks],
                    self.platform_rect.top - self.camera_offset_y
                )
                self.falling_block.y = landing_y
                self._land_block()
                return

        # Check if block fell off screen
        if block_bottom > Display.HEIGHT + 100:
            self.game_over = True

    def _handle_input(self):
        """Handle keyboard input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_over:
                        self._reset_game()
                    else:
                        self.running = False
                elif not self.game_over:
                    if event.key == pygame.K_LEFT:
                        self._move_block(-20)
                    elif event.key == pygame.K_RIGHT:
                        self._move_block(20)
                    elif event.key == pygame.K_SPACE:
                        if self.falling_block:
                            self.falling_block.rotate()
                    elif event.key == pygame.K_r:
                        self._reset_game()

    def _move_block(self, delta: int):
        """Move the falling block horizontally."""
        if self.falling_block:
            self.falling_block.x += delta
            # Keep within screen bounds
            half_w = self.falling_block.width / 2
            self.falling_block.x = max(half_w, min(Display.WIDTH - half_w, self.falling_block.x))

    def _reset_game(self):
        """Reset the game to initial state."""
        self.game_over = False
        self.landed_blocks.clear()
        self.falling_block = None
        self.score = 0
        self.blocks_placed = 0
        self.height_levels = 0
        self.current_fall_speed = Physics.INITIAL_FALL_SPEED
        self.camera_offset_y = 0
        self._spawn_new_block()

    def _draw_platform(self):
        """Draw the base platform."""
        rect = self.platform_rect.copy()
        rect.y -= self.camera_offset_y
        pygame.draw.rect(self.screen, Colors.BASE_PLATFORM, rect)
        pygame.draw.rect(self.screen, Colors.BASE_PLATFORM_BORDER, rect, 3)

        # Draw center line
        center_x = rect.centerx
        pygame.draw.line(self.screen, Colors.BASE_PLATFORM_BORDER,
                         (center_x, rect.top), (center_x, rect.bottom), 2)

    def _draw_blocks(self):
        """Draw all blocks."""
        for block in self.landed_blocks:
            # Adjust for camera
            draw_block = Block(
                x=block.x,
                y=block.y - self.camera_offset_y,
                width=block.width,
                height=block.height,
                color=block.color,
                border_color=block.border_color,
                rotation=block.rotation
            )
            draw_block.draw(self.screen)

        if self.falling_block:
            self.falling_block.draw(self.screen)

    def _draw_ui(self):
        """Draw the user interface."""
        # Score
        score_text = self.font.render(f"Score: {self.score}", True, Colors.TEXT)
        self.screen.blit(score_text, (10, 10))

        # Tower height
        height = self._get_tower_height()
        height_text = self.font.render(f"Height: {height}", True, Colors.TEXT)
        self.screen.blit(height_text, (10, 50))

        # Balance indicator
        if self.landed_blocks:
            com_x, _ = self.physics_engine.calculate_center_of_mass(self.landed_blocks)
            balance_ratio = 1.0 - (abs(com_x - self.platform_center_x) / (Platform.WIDTH / 2))

            balance_color = Colors.COM_INDICATOR_STABLE if balance_ratio > 0.5 else Colors.COM_INDICATOR_UNSTABLE
            balance_text = self.font.render(f"Balance: {int(balance_ratio * 100)}%", True, balance_color)
            self.screen.blit(balance_text, (10, 90))

            # Draw COM indicator on platform
            platform_rect = self.platform_rect.copy()
            platform_rect.y -= self.camera_offset_y
            com_screen_x = com_x
            pygame.draw.circle(self.screen, balance_color, (int(com_screen_x), int(platform_rect.top - 15)), 8)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(com_screen_x), int(platform_rect.top - 15)), 8, 2)

        # Controls hint
        hint_text = self.font.render("Arrows: Move | Space: Rotate | R: Reset | ESC: Quit", True, Colors.TEXT)
        text_rect = hint_text.get_rect(center=(Display.WIDTH // 2, Display.HEIGHT - 20))
        self.screen.blit(hint_text, text_rect)

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((Display.WIDTH, Display.HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, (255, 100, 100))
            text_rect = game_over_text.get_rect(center=(Display.WIDTH // 2, Display.HEIGHT // 2 - 50))
            self.screen.blit(game_over_text, text_rect)

            final_score_text = self.font.render(f"Final Score: {self.score}", True, Colors.TEXT)
            text_rect = final_score_text.get_rect(center=(Display.WIDTH // 2, Display.HEIGHT // 2 + 10))
            self.screen.blit(final_score_text, text_rect)

            restart_text = self.font.render("Press R to Restart or ESC to Quit", True, Colors.TEXT)
            text_rect = restart_text.get_rect(center=(Display.WIDTH // 2, Display.HEIGHT // 2 + 60))
            self.screen.blit(restart_text, text_rect)

    def update(self):
        """Update game state."""
        if not self.game_over:
            self._update_falling_block()
            self._update_camera()

        # Update observation for AI
        self._update_observation()

    def _update_observation(self):
        """Update the observation dictionary for AI agents."""
        self.observation = {
            "block_position": (self.falling_block.x, self.falling_block.y) if self.falling_block else (0, 0),
            "block_rotation": self.falling_block.rotation if self.falling_block else 0,
            "block_dimensions": (self.falling_block.width, self.falling_block.height) if self.falling_block else (0, 0),
            "stack_com": self.physics_engine.calculate_center_of_mass(self.landed_blocks),
            "tower_height": self._get_tower_height(),
            "score": self.score,
            "game_over": self.game_over
        }

    def draw(self):
        """Draw the game."""
        self.screen.fill(Colors.BACKGROUND)
        self._draw_platform()
        self._draw_blocks()
        self._draw_ui()
        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            self._handle_input()
            self.update()
            self.draw()
            self.clock.tick(Display.FPS)

        pygame.quit()

    def get_observation(self) -> Dict:
        """Get the current game observation for AI.

        Returns:
            Dictionary containing game state information
        """
        return self.observation.copy()

    def step_ai(self, action: int) -> Tuple[Dict, float, bool]:
        """Execute an AI action and get results.

        Args:
            action: 0=move left, 1=move right, 2=rotate, 3=do nothing

        Returns:
            Tuple of (observation, reward, done)
        """
        if self.game_over:
            return self.get_observation(), Scoring.COLLAPSE_PENALTY, True

        # Execute action
        if action == 0:
            self._move_block(-20)
        elif action == 1:
            self._move_block(20)
        elif action == 2:
            if self.falling_block:
                self.falling_block.rotate()

        # Update game state (multiple steps for faster AI training)
        for _ in range(3):
            if not self.game_over:
                self._update_falling_block()
                self._update_camera()

        # Calculate reward
        reward = Scoring.OSCILLATION_PENALTY

        if not self.game_over and self.falling_block:
            prev_blocks = self.blocks_placed
            if self.blocks_placed > prev_blocks:
                reward += Scoring.POINTS_PER_BLOCK

        if self.game_over:
            reward = Scoring.COLLAPSE_PENALTY

        return self.get_observation(), reward, self.game_over
