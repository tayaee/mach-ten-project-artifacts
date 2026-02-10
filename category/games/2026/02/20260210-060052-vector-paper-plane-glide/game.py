"""Main game loop and rendering."""

import pygame
from config import *
from plane import Plane
from corridor import Corridor


class Game:
    """Main game class managing rendering and game loop."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Paper Plane Glide")
        self.clock = pygame.time.Clock()
        self.running = True

        self.plane = Plane()
        self.corridor = Corridor()
        self.score = 0
        self.high_score = 0
        self.distance = 0
        self.start_time = 0
        self.game_state = "ready"  # ready, playing, game_over

        # Fonts
        self.score_font = pygame.font.Font(None, SCORE_FONT_SIZE)
        self.message_font = pygame.font.Font(None, MESSAGE_FONT_SIZE)

    def reset_game(self):
        """Reset game to initial state."""
        self.plane.reset()
        self.corridor.reset()
        self.score = 0
        self.distance = 0
        self.start_time = 0
        self.game_state = "ready"

    def handle_input(self):
        """Handle user input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    if self.game_state == "ready":
                        self.game_state = "playing"
                        self.start_time = pygame.time.get_ticks()
                    self.plane.start_lift()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_SPACE or event.key == pygame.K_UP:
                    self.plane.end_lift()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if self.game_state == "ready":
                        self.game_state = "playing"
                        self.start_time = pygame.time.get_ticks()
                    self.plane.start_lift()
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:
                    self.plane.end_lift()

    def update(self):
        """Update game state."""
        if self.game_state == "playing":
            dt = self.clock.get_time()

            self.plane.update()
            self.corridor.update(dt)

            # Check collisions
            plane_rect = self.plane.get_rect()

            # Ceiling/floor collision
            if plane_rect.top <= 0 or plane_rect.bottom >= SCREEN_HEIGHT:
                self.game_state = "game_over"
            # Cave collision
            elif self.corridor.check_collision(plane_rect):
                self.game_state = "game_over"

            # Check air current collection
            if self.corridor.check_air_current(self.plane.get_center()):
                self.score += AIR_CURRENT_POINTS

            # Update survival score
            elapsed = (pygame.time.get_ticks() - self.start_time) / 1000.0
            self.distance = self.corridor.get_distance()
            survival_score = int(elapsed * POINTS_PER_SECOND)
            self.score = survival_score * 10 + self.score % 10

    def render(self):
        """Render the game."""
        self.screen.fill(SKY_BLUE)

        # Draw corridor
        self.corridor.draw(self.screen)

        # Draw plane
        self.plane.draw(self.screen)

        # Draw score
        score_text = self.score_font.render(str(self.score), True, WHITE)
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
        self.screen.blit(score_text, score_rect)

        # Draw distance
        dist_text = self.message_font.render(f"{self.distance}m", True, WHITE)
        dist_rect = dist_text.get_rect(center=(SCREEN_WIDTH // 2, 90))
        self.screen.blit(dist_text, dist_rect)

        # Draw high score
        high_score_text = self.message_font.render(f"Best: {self.high_score}", True, WHITE)
        high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH - 80, 30))
        self.screen.blit(high_score_text, high_score_rect)

        # Draw messages
        if self.game_state == "ready":
            msg = "Hold SPACE/UP to glide through the cave"
            msg_text = self.message_font.render(msg, True, WHITE)
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(msg_text, msg_rect)

            sub_msg = "Collect blue air currents for bonus points!"
            sub_text = self.message_font.render(sub_msg, True, AIR_CURRENT_COLOR)
            sub_rect = sub_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            self.screen.blit(sub_text, sub_rect)
        elif self.game_state == "game_over":
            if self.score > self.high_score:
                self.high_score = self.score

            msg = "Game Over!"
            msg_text = self.score_font.render(msg, True, (255, 100, 100))
            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            self.screen.blit(msg_text, msg_rect)

            retry_msg = "Press SPACE to retry"
            retry_text = self.message_font.render(retry_msg, True, WHITE)
            retry_rect = retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            self.screen.blit(retry_text, retry_rect)

        pygame.display.flip()

    def step_ai(self, action):
        """
        Execute an AI action and return observation, reward, done.

        Args:
            action: 0 = release lift, 1 = apply lift

        Returns:
            (observation, reward, done)
        """
        prev_score = self.score
        prev_distance = self.distance

        if action == 1:
            self.plane.start_lift()
        else:
            self.plane.end_lift()

        self.update()

        reward = 0
        done = False

        if self.game_state == "playing":
            reward += REWARD_PER_FRAME
            distance_reward = (self.distance - prev_distance) * 0.01
            reward += distance_reward
            if self.score > prev_score:
                reward += (self.score - prev_score) * 0.1
        elif self.game_state == "game_over":
            reward = REWARD_COLLISION
            done = True

        return self.get_observation(), reward, done

    def get_observation(self):
        """Return current game state for AI."""
        # Find nearest ceiling and floor
        plane_center_x = self.plane.x + self.plane.width // 2

        ceiling_y = 0
        floor_y = SCREEN_HEIGHT

        for i, seg in enumerate(self.corridor.segments):
            seg_x = i * SEGMENT_WIDTH - self.corridor.scroll_offset
            if seg_x <= plane_center_x <= seg_x + SEGMENT_WIDTH:
                ceiling_y = seg['ceiling']
                floor_y = seg['floor']
                break

        # Find nearest air current
        nearest_current = None
        min_dist = float('inf')
        for ac in self.corridor.air_currents:
            if not ac['collected']:
                dx = ac['x'] - self.plane.x
                dy = ac['y'] - (self.plane.y + self.plane.height // 2)
                dist = (dx ** 2 + dy ** 2) ** 0.5
                if dist < min_dist:
                    min_dist = dist
                    nearest_current = ac

        obs = {
            "plane_y": self.plane.y,
            "plane_velocity": self.plane.velocity,
            "ceiling_y": ceiling_y,
            "floor_y": floor_y,
            "gap_height": floor_y - ceiling_y,
            "gap_center": (ceiling_y + floor_y) / 2,
            "distance": self.distance,
            "score": self.score,
            "game_state": self.game_state
        }

        if nearest_current:
            obs["air_current_dist_x"] = nearest_current['x'] - self.plane.x
            obs["air_current_dist_y"] = nearest_current['y'] - (self.plane.y + self.plane.height // 2)
        else:
            obs["air_current_dist_x"] = 999
            obs["air_current_dist_y"] = 0

        return obs

    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.render()
            self.clock.tick(FPS)

        pygame.quit()
