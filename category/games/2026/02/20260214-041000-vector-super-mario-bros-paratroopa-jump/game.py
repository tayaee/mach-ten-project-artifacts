"""Game loop and rendering."""

import pygame
import sys
import random
from config import *
from entities import Player, Paratroopa


class Game:
    """Main game class handling the game loop and rendering."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        self.tiny_font = pygame.font.Font(None, 20)

        self.reset_game()

    def reset_game(self):
        """Reset game state."""
        # Start player in the middle of the screen
        self.player = Player(SCREEN_WIDTH // 2 - PLAYER_WIDTH // 2, SCREEN_HEIGHT - 150)
        self.paratroopas = []
        self.score = 0
        self.combo = 0
        self.max_combo = 0
        self.game_over = False
        self.game_started = False
        self.spawn_timer = 0
        self.height_reached = 0

        # Create initial paratroopas at varying heights
        self.create_initial_paratroopas()

    def create_initial_paratroopas(self):
        """Create initial set of paratroopas at various heights."""
        rows = 5
        for row in range(rows):
            y = SCREEN_HEIGHT - 200 - (row * 80)
            cols = 2 + (row % 2)  # Alternate between 2 and 3 per row
            spacing = SCREEN_WIDTH // (cols + 1)

            for col in range(cols):
                x = spacing * (col + 1) - PARATROOPA_WIDTH // 2
                pattern = random.choice([
                    VERTICAL_OSCILLATION,
                    HORIZONTAL_OSCILLATION,
                    STATIC_HOVER
                ])
                self.paratroopas.append(Paratroopa(x, y, pattern))

    def spawn_new_paratroopa(self):
        """Spawn a new paratroopa at the top of the screen."""
        x = random.randint(50, SCREEN_WIDTH - PARATROOPA_WIDTH - 50)
        y = -PARATROOPA_HEIGHT
        pattern = random.choice([
            VERTICAL_OSCILLATION,
            HORIZONTAL_OSCILLATION,
            STATIC_HOVER
        ])
        self.paratroopas.append(Paratroopa(x, y, pattern))

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        # Don't update player until game starts
        if self.game_started:
            self.player.update(keys)
        else:
            # Allow initial jump to start
            if keys[pygame.K_SPACE]:
                self.game_started = True
                self.player.update(keys)

        # Track height reached
        current_height = SCREEN_HEIGHT - self.player.y
        if current_height > self.height_reached:
            self.height_reached = current_height

        # Spawn new paratroopas periodically
        if self.game_started:
            self.spawn_timer += 1
            if self.spawn_timer >= PARATROOPA_SPAWN_INTERVAL:
                self.spawn_timer = 0
                if len(self.paratroopas) < MAX_PARATROOPAS:
                    self.spawn_new_paratroopa()

        # Update paratroopas
        for paratroopa in self.paratroopas[:]:
            paratroopa.update()

            # Check collision with player
            player_rect = self.player.get_hitbox()
            paratroopa_rect = paratroopa.get_hitbox()

            if player_rect.colliderect(paratroopa_rect):
                # Check if player bounced from above
                bounce_zone = self.player.get_bounce_zone()
                bounce_hitbox = paratroopa.get_bounce_hitbox()

                can_bounce = (
                    bounce_zone.colliderect(bounce_hitbox) and
                    self.player.vel_y > 0 and
                    paratroopa.id != self.player.last_bounced_enemy
                )

                if can_bounce:
                    # Successful bounce
                    self.player.bounce(paratroopa.id)
                    self.paratroopas.remove(paratroopa)

                    # Update combo
                    self.combo += 1
                    if self.combo > self.max_combo:
                        self.max_combo = self.combo

                    # Score with combo multiplier
                    combo_multiplier = 2 ** (self.combo - 1)
                    points = SCORE_PER_BOUNCE * combo_multiplier
                    self.score += points

                else:
                    # Player hit the side or bottom - game over
                    self.player.alive = False
                    self.game_over = True

        # Check if player fell off screen
        if not self.player.alive:
            self.game_over = True

    def draw(self):
        """Render the game."""
        self.screen.fill(COLOR_BG)

        # Draw clouds in background
        for i in range(8):
            cloud_x = (i * 120 + pygame.time.get_ticks() // 50) % (SCREEN_WIDTH + 100) - 50
            cloud_y = 50 + (i % 3) * 40
            pygame.draw.ellipse(self.screen, (200, 220, 240), (cloud_x, cloud_y, 60, 30))

        # Draw height indicator zones
        for zone in range(1, 6):
            zone_y = SCREEN_HEIGHT - zone * 100
            if zone_y > 0:
                alpha = 30 - zone * 5
                zone_surface = pygame.Surface((SCREEN_WIDTH, 2), pygame.SRCALPHA)
                zone_surface.fill((255, 255, 255, alpha))
                self.screen.blit(zone_surface, (0, zone_y))

        # Draw paratroopas
        for paratroopa in self.paratroopas:
            can_bounce = paratroopa.id != self.player.last_bounced_enemy
            paratroopa.draw(self.screen, can_bounce)

        # Draw player
        self.player.draw(self.screen)

        # Draw danger zone at bottom
        danger_surface = pygame.Surface((SCREEN_WIDTH, 50), pygame.SRCALPHA)
        danger_surface.fill((255, 100, 100, 50))
        self.screen.blit(danger_surface, (0, SCREEN_HEIGHT - 50))
        danger_text = self.tiny_font.render("DANGER ZONE", True, COLOR_DANGER)
        self.screen.blit(danger_text, (SCREEN_WIDTH // 2 - danger_text.get_width() // 2, SCREEN_HEIGHT - 35))

        # Draw HUD
        self.draw_hud()

        # Start screen overlay
        if not self.game_started:
            self.draw_start_screen()

        # Game over overlay
        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def draw_hud(self):
        """Draw heads-up display."""
        # Score background
        pygame.draw.rect(self.screen, (0, 0, 0, 180), (10, 10, 220, 100))
        pygame.draw.rect(self.screen, (255, 255, 255), (10, 10, 220, 100), 2)

        # Score
        score_text = self.small_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (20, 20))

        # Height reached
        height_m = self.height_reached // 100
        height_text = self.small_font.render(f"Height: {height_m}m", True, COLOR_TEXT)
        self.screen.blit(height_text, (20, 50))

        # Combo
        if self.combo > 0:
            combo_mult = 2 ** (self.combo - 1)
            combo_text = self.small_font.render(f"Combo: x{combo_mult}", True, COLOR_COMBO)
            self.screen.blit(combo_text, (20, 80))

        # Controls hint
        if not self.game_started:
            hints = [
                "LEFT/RIGHT: Move",
                "SPACE: Start & Jump",
                "Bounce from above!"
            ]
            for i, hint in enumerate(hints):
                hint_text = self.tiny_font.render(hint, True, (255, 255, 0))
                self.screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 10, 10 + i * 22))

    def draw_start_screen(self):
        """Draw start screen overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        self.screen.blit(overlay, (0, 0))

        title_text = self.font.render("PARATROOPA JUMP", True, (255, 255, 255))
        self.screen.blit(
            title_text,
            (SCREEN_WIDTH // 2 - title_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60)
        )

        subtitle_text = self.small_font.render("Bounce from above - Don't touch the ground!", True, (200, 200, 200))
        self.screen.blit(
            subtitle_text,
            (SCREEN_WIDTH // 2 - subtitle_text.get_width() // 2, SCREEN_HEIGHT // 2)
        )

        start_text = self.small_font.render("Press SPACE to start", True, COLOR_COMBO)
        self.screen.blit(
            start_text,
            (SCREEN_WIDTH // 2 - start_text.get_width() // 2, SCREEN_HEIGHT // 2 + 50)
        )

    def draw_game_over(self):
        """Draw game over screen."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        # Game Over text
        game_over_text = self.font.render("GAME OVER", True, (255, 50, 50))
        self.screen.blit(
            game_over_text,
            (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 100)
        )

        # Reason
        reason = "You fell to the ground!"
        reason_text = self.small_font.render(reason, True, (200, 200, 200))
        self.screen.blit(
            reason_text,
            (SCREEN_WIDTH // 2 - reason_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50)
        )

        # Final score
        score_text = self.small_font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(
            score_text,
            (SCREEN_WIDTH // 2 - score_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10)
        )

        # Max combo
        max_combo = 2 ** (self.max_combo - 1) if self.max_combo > 0 else 0
        combo_text = self.small_font.render(f"Max Combo: x{max_combo}", True, COLOR_COMBO)
        self.screen.blit(
            combo_text,
            (SCREEN_WIDTH // 2 - combo_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40)
        )

        # Height reached
        height_m = self.height_reached // 100
        height_text = self.small_font.render(f"Max Height: {height_m}m", True, (100, 200, 255))
        self.screen.blit(
            height_text,
            (SCREEN_WIDTH // 2 - height_text.get_width() // 2, SCREEN_HEIGHT // 2 + 70)
        )

        # Restart prompt
        restart_text = self.small_font.render("Press SPACE to play again", True, COLOR_TEXT)
        self.screen.blit(
            restart_text,
            (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 120)
        )

        # Quit prompt
        quit_text = self.tiny_font.render("Press ESC to quit", True, (150, 150, 150))
        self.screen.blit(
            quit_text,
            (SCREEN_WIDTH // 2 - quit_text.get_width() // 2, SCREEN_HEIGHT // 2 + 155)
        )

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
                    elif event.key == pygame.K_SPACE and self.game_over:
                        # Restart game
                        self.reset_game()

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

    def get_state(self):
        """Return current game state for AI agents."""
        nearest_paratroopa = None
        min_dist = float('inf')

        for p in self.paratroopas:
            dist = ((p.x - self.player.x) ** 2 + (p.y - self.player.y) ** 2) ** 0.5
            if dist < min_dist:
                min_dist = dist
                nearest_paratroopa = p

        return {
            'player': {
                'x': self.player.x / SCREEN_WIDTH,
                'y': self.player.y / SCREEN_HEIGHT,
                'vx': self.player.vel_x / MOVE_SPEED,
                'vy': self.player.vel_y / MAX_FALL_SPEED,
                'has_bounced': self.player.has_bounced_once
            },
            'nearest_paratroopa': {
                'x': nearest_paratroopa.x / SCREEN_WIDTH if nearest_paratroopa else 0.5,
                'y': nearest_paratroopa.y / SCREEN_HEIGHT if nearest_paratroopa else 0.0,
                'distance': min_dist / SCREEN_HEIGHT if nearest_paratroopa else 1.0,
                'can_bounce': nearest_paratroopa.id != self.player.last_bounced_enemy if nearest_paratroopa else False,
                'pattern': nearest_paratroopa.pattern if nearest_paratroopa else None
            } if nearest_paratroopa else None,
            'paratroopa_count': len(self.paratroopas),
            'combo': self.combo,
            'score': self.score,
            'height_reached': self.height_reached,
            'game_started': self.game_started
        }
