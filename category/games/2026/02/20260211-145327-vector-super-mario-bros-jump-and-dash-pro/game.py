"""Game loop and rendering."""

import pygame
import sys
from config import *
from entities import Player, Platform, Spike, Pit, Goal


class Game:
    """Main game class handling the game loop and rendering."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()
        self.create_level()

    def reset_game(self):
        """Reset game state."""
        self.player = Player(50, GROUND_Y - PLAYER_HEIGHT)
        self.score = 0
        self.attempts = 1
        self.game_over = False
        self.won = False
        self.camera_x = 0
        self.start_time = pygame.time.get_ticks()

    def create_level(self):
        """Create level layout with platforms, spikes, and goal."""
        self.platforms = []
        self.spikes = []
        self.pits = []

        # Starting ground
        self.platforms.append(Platform(0, GROUND_Y, 400, SCREEN_HEIGHT - GROUND_Y))

        # First challenge: pit with spikes
        self.pits.append(Pit(400, 100))
        self.platforms.append(Platform(500, GROUND_Y, 300, SCREEN_HEIGHT - GROUND_Y))

        # Elevated platform section
        self.platforms.append(Platform(850, GROUND_Y - 60, 100, 20))
        self.platforms.append(Platform(1000, GROUND_Y - 100, 100, 20))
        self.platforms.append(Platform(1150, GROUND_Y - 60, 100, 20))

        # Ground return
        self.platforms.append(Platform(1300, GROUND_Y, 200, SCREEN_HEIGHT - GROUND_Y))

        # Spike section
        for i in range(5):
            self.spikes.append(Spike(1550 + i * 25, GROUND_Y - 20))

        self.platforms.append(Platform(1700, GROUND_Y, 100, SCREEN_HEIGHT - GROUND_Y))

        # Staircase up
        self.platforms.append(Platform(1850, GROUND_Y - 40, 80, 20))
        self.platforms.append(Platform(1980, GROUND_Y - 80, 80, 20))
        self.platforms.append(Platform(2110, GROUND_Y - 120, 80, 20))

        # High platform with spike hazard below
        self.platforms.append(Platform(2250, GROUND_Y - 120, 200, 20))

        # Spikes below high section
        for i in range(3):
            self.spikes.append(Spike(2280 + i * 60, GROUND_Y - 20))

        # Gap to goal
        self.pits.append(Pit(2450, 150))

        # Final stretch
        self.platforms.append(Platform(2600, GROUND_Y, 400, SCREEN_HEIGHT - GROUND_Y))

        # Goal
        self.goal = Goal(GOAL_X, GROUND_Y - 120)

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.platforms)

        # Score based on distance traveled
        distance_score = int(self.player.x / 10)
        if distance_score > self.score:
            self.score = distance_score

        # Check spike collision
        player_rect = self.player.get_hitbox()
        for spike in self.spikes:
            if player_rect.colliderect(spike.get_hitbox()):
                self.player.alive = False

        # Check goal collision
        if player_rect.colliderect(self.goal.get_hitbox()):
            self.won = True
            self.score += GOAL_BONUS
            self.player.finished = True

        # Camera follows player
        target_camera_x = self.player.x - SCREEN_WIDTH // 3
        target_camera_x = max(0, min(target_camera_x, LEVEL_WIDTH - SCREEN_WIDTH))
        self.camera_x += (target_camera_x - self.camera_x) * 0.1

        # Check death
        if not self.player.alive:
            self.score += DEATH_PENALTY
            self.attempts += 1
            self.player.reset()

    def draw(self):
        """Render the game."""
        self.screen.fill(COLOR_BG)

        # Draw clouds (parallax background)
        for i in range(5):
            cloud_x = (i * 300 - int(self.camera_x * 0.3)) % (LEVEL_WIDTH + 200) - 100
            pygame.draw.ellipse(self.screen, (200, 220, 240), (cloud_x, 30 + i * 20, 80, 40))

        # Draw pits
        for pit in self.pits:
            pit.draw(self.screen, self.camera_x)

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen, self.camera_x)

        # Draw spikes
        for spike in self.spikes:
            spike.draw(self.screen, self.camera_x)

        # Draw goal
        self.goal.draw(self.screen, self.camera_x)

        # Draw player
        self.player.draw(self.screen, self.camera_x)

        # Draw HUD
        self.draw_hud()

        pygame.display.flip()

    def draw_hud(self):
        """Draw heads-up display."""
        # Background
        pygame.draw.rect(self.screen, (0, 0, 0, 150), (5, 5, 220, 85))

        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (15, 10))

        # Distance
        distance = int(self.player.x)
        dist_text = self.small_font.render(f"Distance: {distance}m", True, COLOR_TEXT)
        self.screen.blit(dist_text, (15, 35))

        # Attempts
        attempts_text = self.small_font.render(f"Attempts: {self.attempts}", True, COLOR_TEXT)
        self.screen.blit(attempts_text, (15, 60))

        # Controls hint (show at start)
        if self.player.x < 300 and self.attempts == 1:
            hints = [
                "Left/Right: Move",
                "Space: Jump (hold higher)",
                "Hold direction to sprint!"
            ]
            for i, hint in enumerate(hints):
                hint_text = self.small_font.render(hint, True, (255, 255, 0))
                self.screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 10, 10 + i * 22))

        # Win overlay
        if self.won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            win_text = self.font.render("GOAL REACHED!", True, (0, 255, 0))
            score_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            attempts_text = self.small_font.render(f"Attempts: {self.attempts}", True, COLOR_TEXT)
            restart_text = self.small_font.render("Press SPACE to play again", True, COLOR_TEXT)

            self.screen.blit(win_text, (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(attempts_text, (SCREEN_WIDTH // 2 - attempts_text.get_width() // 2, SCREEN_HEIGHT // 2 + 35))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70))

    def run(self):
        """Main game loop."""
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE and self.won:
                        # Restart game
                        self.reset_game()

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def get_state(self):
        """Return current game state for AI agents."""
        player_rect = self.player.get_hitbox()

        # Find nearest spike
        nearest_spike = None
        min_spike_dist = float('inf')
        for spike in self.spikes:
            dist = abs(spike.x - self.player.x)
            if dist < min_spike_dist:
                min_spike_dist = dist
                nearest_spike = spike

        # Find nearest pit
        nearest_pit = None
        min_pit_dist = float('inf')
        for pit in self.pits:
            dist = abs(pit.x - self.player.x)
            if dist < min_pit_dist:
                min_pit_dist = dist
                nearest_pit = pit

        return {
            'player': {
                'x': self.player.x / LEVEL_WIDTH,
                'y': self.player.y / SCREEN_HEIGHT,
                'vx': self.player.vel_x / MAX_RUN_SPEED,
                'vy': self.player.vel_y / MAX_FALL_SPEED,
                'on_ground': self.player.on_ground,
                'facing_right': self.player.facing_right
            },
            'nearest_spike': {
                'x': nearest_spike.x / LEVEL_WIDTH if nearest_spike else 1.0,
                'y': nearest_spike.y / SCREEN_HEIGHT if nearest_spike else 0.0,
                'distance': min_spike_dist / SCREEN_WIDTH if nearest_spike else 1.0
            } if nearest_spike else None,
            'nearest_pit': {
                'x': nearest_pit.x / LEVEL_WIDTH if nearest_pit else 1.0,
                'width': nearest_pit.width / SCREEN_WIDTH if nearest_pit else 0.0,
                'distance': min_pit_dist / SCREEN_WIDTH if nearest_pit else 1.0
            } if nearest_pit else None,
            'goal_distance': (GOAL_X - self.player.x) / LEVEL_WIDTH,
            'score': self.score
        }
