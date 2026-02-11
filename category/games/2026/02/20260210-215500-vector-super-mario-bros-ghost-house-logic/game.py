"""Main game loop and logic."""

import pygame
import sys
from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, COLOR_BG, COLOR_WALL, COLOR_WALL_GHOST,
    COLOR_PLATFORM_VISIBLE, COLOR_PLATFORM_INVISIBLE, COLOR_TEXT,
    INVISIBLE_PLATFORM_RADIUS, SCORE_KEY, SCORE_EXIT, SCORE_PENALTY_PER_SECOND
)
from entity import Player, Ghost, Key, Door
from level import Level


class Game:
    """Main game class managing state and rendering."""

    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Ghost House Logic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        """Initialize or reset game state."""
        self.level = Level()
        self.player = Player(100, 480)
        self.ghosts = [
            Ghost(400, 300),
            Ghost(550, 200),
            Ghost(200, 400),
        ]
        self.key = Key(600, 100)
        self.door = Door(700, 496)

        self.score = 0
        self.game_won = False
        self.game_over = False
        self.start_time = pygame.time.get_ticks()
        self.next_wall_shift = pygame.time.get_ticks() + 10000

    def run(self):
        """Main game loop."""
        running = True
        while running:
            current_time = pygame.time.get_ticks()
            dt = self.clock.tick(FPS)

            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        running = False

            # Update game state
            if not self.game_won and not self.game_over:
                self.update(current_time)

            # Render
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def update(self, current_time):
        """Update all game objects."""
        # Update shifting walls
        if current_time >= self.next_wall_shift:
            self.level.update_walls(current_time)
            self.next_wall_shift = current_time + 10000

        # Get all collision objects
        walls = self.level.get_wall_rects() + self.level.get_shifting_wall_rects()
        visible_platforms = self.level.get_platform_rects()
        invisible_platforms = self.level.get_all_invisible_platform_rects()
        all_platforms = visible_platforms + invisible_platforms

        # Update player
        keys = pygame.key.get_pressed()
        self.player.update(keys, walls, all_platforms)

        # Update ghosts
        ghost_watch_states = []
        for ghost in self.ghosts:
            is_watched = ghost.update(self.player)
            ghost_watch_states.append(is_watched)

            # Check ghost collision
            if ghost.rect.colliderect(self.player.rect):
                self.game_over = True

        # Update key
        self.key.update()
        if not self.key.collected and self.player.rect.colliderect(self.key.rect):
            self.key.collected = True
            self.player.has_key = True
            self.score += SCORE_KEY

        # Check door/win condition
        if self.player.has_key and self.player.rect.colliderect(self.door.rect):
            self.game_won = True
            elapsed = (current_time - self.start_time) / 1000
            time_penalty = int(elapsed * SCORE_PENALTY_PER_SECOND)
            self.score += max(SCORE_EXIT - time_penalty, 100)

        # Check if player died
        if not self.player.alive:
            self.game_over = True

        # Store watch states for rendering
        self.ghost_watch_states = ghost_watch_states

    def draw(self):
        """Render all game objects."""
        self.screen.fill(COLOR_BG)

        # Get visible invisible platforms
        nearby_invisible = self.level.get_nearby_invisible_platforms(
            self.player.rect, INVISIBLE_PLATFORM_RADIUS
        )

        # Draw static walls
        for wall in self.level.get_wall_rects():
            pygame.draw.rect(self.screen, COLOR_WALL, wall)
            pygame.draw.rect(self.screen, (60, 50, 80), wall, 2)

        # Draw shifting walls with pulse effect
        pulse = (pygame.time.get_ticks() % 1000) / 1000
        wall_color = (
            int(COLOR_WALL_GHOST[0] + pulse * 30),
            int(COLOR_WALL_GHOST[1] + pulse * 20),
            int(COLOR_WALL_GHOST[2] + pulse * 40)
        )
        for wall in self.level.get_shifting_wall_rects():
            pygame.draw.rect(self.screen, wall_color, wall)
            pygame.draw.rect(self.screen, (100, 80, 120), wall, 2)

        # Draw visible platforms
        for plat in self.level.get_platform_rects():
            pygame.draw.rect(self.screen, COLOR_PLATFORM_VISIBLE, plat)
            pygame.draw.rect(self.screen, (80, 60, 100), plat, 2)

        # Draw invisible platforms (only nearby)
        all_invisible = self.level.get_all_invisible_platform_rects()
        for plat in all_invisible:
            if plat in nearby_invisible:
                pygame.draw.rect(self.screen, COLOR_PLATFORM_VISIBLE, plat)
            else:
                pygame.draw.rect(self.screen, COLOR_PLATFORM_INVISIBLE, plat, 1)

        # Draw key
        self.key.draw(self.screen)

        # Draw door
        self.door.draw(self.screen, self.player.has_key)

        # Draw ghosts
        if hasattr(self, 'ghost_watch_states'):
            for i, ghost in enumerate(self.ghosts):
                ghost.draw(self.screen, self.ghost_watch_states[i])
        else:
            for ghost in self.ghosts:
                ghost.draw(self.screen, False)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        self._draw_ui()

    def _draw_ui(self):
        """Draw UI elements."""
        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Key indicator
        key_color = COLOR_KEY if self.player.has_key else (100, 100, 100)
        key_text = self.small_font.render("KEY", True, key_color)
        self.screen.blit(key_text, (10, 35))

        # Wall shift timer
        time_until = max(0, self.next_wall_shift - pygame.time.get_ticks())
        timer_text = self.small_font.render(f"Wall Shift: {time_until // 1000}s", True, COLOR_TEXT)
        self.screen.blit(timer_text, (SCREEN_WIDTH - 150, 10))

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            msg = self.font.render("GHOST CAUGHT YOU!", True, (255, 100, 100))
            restart = self.small_font.render("Press R to Restart", True, COLOR_TEXT)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, SCREEN_HEIGHT // 2 + 10))

        # Win screen
        if self.game_won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            msg = self.font.render("YOU ESCAPED!", True, (100, 255, 100))
            score_msg = self.small_font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            restart = self.small_font.render("Press R to Play Again", True, COLOR_TEXT)
            self.screen.blit(msg, (SCREEN_WIDTH // 2 - msg.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(score_msg, (SCREEN_WIDTH // 2 - score_msg.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

        # Instructions
        inst_y = SCREEN_HEIGHT - 60
        instructions = [
            "Arrows: Move | Space/Up: Jump",
            "Face ghosts to stop them!",
        ]
        for i, inst in enumerate(instructions):
            inst_text = self.small_font.render(inst, True, (180, 180, 180))
            self.screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, inst_y + i * 20))
