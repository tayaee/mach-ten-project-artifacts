"""Main game class for Bridge Sprint."""

import pygame
import random
import math
from config import *
from entities import BridgeSegment, Player, Fireball, CheepCheep


class BridgeSprintGame:
    """Main game class managing the infinite bridge sprint game."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.running = True
        self.game_over = False
        self.game_started = False

        # Game state
        self.offset_x = 0
        self.speed_multiplier = 1.0
        self.score = 0
        self.distance_traveled = 0
        self.last_segment_x = 0
        self.segments_crossed = 0

        # Entities
        self.player = None
        self.bridge_segments = []
        self.fireballs = []
        self.cheeps = []

        self.reset_game()

    def reset_game(self):
        """Reset the game to initial state."""
        self.offset_x = 0
        self.speed_multiplier = 1.0
        self.score = 0
        self.distance_traveled = 0
        self.segments_crossed = 0
        self.game_over = False

        # Create player
        self.player = Player(PLAYER_START_X, PLAYER_START_Y)

        # Create initial bridge
        self.bridge_segments = []
        for i in range(VISIBLE_SEGMENTS + 5):
            x = i * SEGMENT_WIDTH
            segment = BridgeSegment(x, BRIDGE_Y)
            self.bridge_segments.append(segment)
            self.last_segment_x = x

        self.fireballs = []
        self.cheeps = []

    def generate_bridge_segment(self):
        """Generate a new bridge segment."""
        self.last_segment_x += SEGMENT_WIDTH
        segment = BridgeSegment(self.last_segment_x, BRIDGE_Y)

        # Random decay chance - increases with speed
        decay_chance = DECAY_CHANCE_BASE * self.speed_multiplier
        if random.random() < decay_chance:
            segment.trigger_decay()

        self.bridge_segments.append(segment)

    def spawn_enemy(self):
        """Spawn fireballs and cheep cheeps."""
        # Spawn fireball
        if random.random() < FIREBALL_SPAWN_CHANCE * self.speed_multiplier:
            x = self.offset_x + random.randint(100, SCREEN_WIDTH - 100)
            self.fireballs.append(Fireball(x))

        # Spawn cheep cheep
        if random.random() < CHEEP_SPAWN_CHANCE * self.speed_multiplier:
            x = self.offset_x + random.randint(CHEEP_MIN_X, CHEEP_MAX_X)
            direction = random.choice([-1, 1])
            self.cheeps.append(CheepCheep(x, direction))

    def check_collisions(self):
        """Check collisions between player and enemies."""
        player_rect = self.player.get_rect(self.offset_x)

        # Check fireball collisions
        for fireball in self.fireballs:
            if fireball.active:
                fireball_rect = fireball.get_rect(self.offset_x)
                if player_rect.colliderect(fireball_rect):
                    self.player.alive = False
                    self.game_over = True

        # Check cheep cheep collisions
        for cheep in self.cheeps:
            if cheep.active:
                cheep_rect = cheep.get_rect(self.offset_x)
                if player_rect.colliderect(cheep_rect):
                    self.player.alive = False
                    self.game_over = True

        # Check if player fell through gaps
        if not self.player.on_ground and self.player.y > BRIDGE_Y:
            # Check if there's a segment below
            has_ground = False
            for segment in self.bridge_segments:
                seg_rect = segment.get_rect(self.offset_x)
                if seg_rect:
                    player_bottom = self.player.y + self.player.height
                    if (seg_rect.left <= self.player.x + self.player.width and
                        seg_rect.right >= self.player.x and
                        seg_rect.top >= self.player.y and
                        seg_rect.top <= player_bottom):
                        has_ground = True
                        break
            if not has_ground and self.player.vel_y > 0:
                # No ground below, falling into gap
                pass

    def get_nearby_segments(self):
        """Get bridge segments near the player for AI observation."""
        nearby = []
        player_grid_x = int(self.player.x // SEGMENT_WIDTH)
        for offset in range(-5, 10):
            grid_x = player_grid_x + offset
            for segment in self.bridge_segments:
                seg_grid_x = int(segment.x // SEGMENT_WIDTH)
                if seg_grid_x == grid_x:
                    state_val = 0 if segment.state == "gone" else (1 if segment.state == "stable" else 2)
                    nearby.append(state_val)
                    break
        return nearby

    def get_nearest_enemy(self, enemies):
        """Get the nearest enemy position normalized to 0-1 range."""
        nearest_dist = float('inf')
        nearest_x, nearest_y = 1.0, 1.0

        for enemy in enemies:
            if enemy.active:
                dist = math.sqrt((enemy.x - self.player.x)**2 + (enemy.y - self.player.y)**2)
                if dist < nearest_dist:
                    nearest_dist = dist
                    nearest_x = (enemy.x - self.offset_x) / SCREEN_WIDTH
                    nearest_y = enemy.y / SCREEN_HEIGHT

        if nearest_dist == float('inf'):
            return 1.0, 1.0
        return nearest_x, nearest_y

    def get_state(self):
        """Get current game state for AI agent."""
        nearby_segments = self.get_nearby_segments()
        fb_x, fb_y = self.get_nearest_enemy(self.fireballs)
        cheep_x, cheep_y = self.get_nearest_enemy(self.cheeps)

        return {
            "player_x": (self.player.x - self.offset_x) / SCREEN_WIDTH,
            "player_y": self.player.y / SCREEN_HEIGHT,
            "velocity_x": self.player.vel_x / MOVE_SPEED,
            "velocity_y": self.player.vel_y / JUMP_FORCE,
            "on_ground": self.player.on_ground,
            "stamina": self.player.stamina / STAMINA_MAX,
            "bridge_states": nearby_segments,
            "nearest_fireball_x": fb_x,
            "nearest_fireball_y": fb_y,
            "nearest_cheep_x": cheep_x,
            "nearest_cheep_y": cheep_y,
            "speed_multiplier": self.speed_multiplier,
            "distance_traveled": self.distance_traveled / 1000
        }

    def update(self):
        """Update game state."""
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        # Update player
        self.player.update(keys, self.bridge_segments, self.offset_x, self.speed_multiplier)

        # Check for game over
        if not self.player.alive:
            self.game_over = True
            self.score += GAME_OVER_PENALTY
            return

        # Update speed multiplier
        self.speed_multiplier = min(self.speed_multiplier + BASE_SPEED_INCREASE, MAX_SPEED_MULTIPLIER)

        # Move camera forward
        player_screen_x = self.player.x - self.offset_x
        if player_screen_x > SCREEN_WIDTH * 0.6:
            self.offset_x += (player_screen_x - SCREEN_WIDTH * 0.6)
            self.distance_traveled += (player_screen_x - SCREEN_WIDTH * 0.6)

        # Update bridge segments
        for segment in self.bridge_segments:
            segment.update()

        # Trigger decay for segments player has passed
        player_grid_x = int(self.player.x // SEGMENT_WIDTH)
        for segment in self.bridge_segments:
            seg_grid_x = int(segment.x // SEGMENT_WIDTH)
            if seg_grid_x < player_grid_x - 2 and segment.state == "stable":
                if random.random() < 0.3:
                    segment.trigger_decay()

        # Remove old segments and generate new ones
        self.bridge_segments = [s for s in self.bridge_segments if s.x > self.offset_x - SEGMENT_WIDTH * 2]
        while len(self.bridge_segments) < VISIBLE_SEGMENTS + 5:
            self.generate_bridge_segment()

        # Update enemies
        for fireball in self.fireballs:
            fireball.update()
        for cheep in self.cheeps:
            cheep.update()

        # Remove inactive enemies
        self.fireballs = [f for f in self.fireballs if f.active]
        self.cheeps = [c for c in self.cheeps if c.active]

        # Spawn new enemies
        self.spawn_enemy()

        # Check collisions
        self.check_collisions()

        # Update score
        self.score += SCORE_PER_FRAME

        # Track segments crossed
        current_segment = int(self.player.x // SEGMENT_WIDTH)
        if current_segment > self.segments_crossed:
            self.score += SCORE_PER_SEGMENT * (current_segment - self.segments_crossed)
            self.segments_crossed = current_segment

    def draw(self):
        """Draw the game."""
        self.screen.fill(COLOR_BG)

        # Draw water below
        pygame.draw.rect(self.screen, COLOR_BRIDGE_GONE, (0, BRIDGE_Y + SEGMENT_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT - BRIDGE_Y - SEGMENT_HEIGHT))

        # Draw bridge segments
        for segment in self.bridge_segments:
            segment.draw(self.screen, self.offset_x)

        # Draw enemies
        for fireball in self.fireballs:
            fireball.draw(self.screen, self.offset_x)
        for cheep in self.cheeps:
            cheep.draw(self.screen, self.offset_x)

        # Draw player
        self.player.draw(self.screen, self.offset_x)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Draw stamina bar
        stamina_width = 150
        stamina_height = 15
        pygame.draw.rect(self.screen, (100, 100, 100), (10, 50, stamina_width, stamina_height))
        stamina_fill = int((self.player.stamina / STAMINA_MAX) * stamina_width)
        pygame.draw.rect(self.screen, COLOR_STAMINA, (10, 50, stamina_fill, stamina_height))
        pygame.draw.rect(self.screen, (255, 255, 255), (10, 50, stamina_width, stamina_height), 2)

        # Draw speed multiplier
        speed_text = self.font.render(f"Speed: {self.speed_multiplier:.1f}x", True, COLOR_TEXT)
        self.screen.blit(speed_text, (10, 75))

        # Draw distance
        dist_text = self.font.render(f"Distance: {int(self.distance_traveled)}m", True, COLOR_TEXT)
        self.screen.blit(dist_text, (SCREEN_WIDTH - 200, 10))

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, (255, 0, 0))
            restart_text = self.font.render("Press SPACE to restart or ESC to quit", True, COLOR_TEXT)

            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE and self.game_over:
                        self.reset_game()
                    elif event.key == pygame.K_SPACE and not self.game_started:
                        self.game_started = True

            if not self.game_over:
                self.update()
            else:
                # Still allow drawing when game over
                pass

            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
