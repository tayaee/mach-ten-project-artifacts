import pygame
import sys
import math
import time


class Ball:
    def __init__(self, pivot_x, pivot_y, string_length, initial_angle, color):
        self.pivot_x = pivot_x
        self.pivot_y = pivot_y
        self.string_length = string_length
        self.angle = initial_angle
        self.angular_velocity = 0
        self.angular_acceleration = 0
        self.color = color
        self.radius = 20
        self.mass = 1.0

    def update(self, gravity, pivot_velocity_y, dt):
        # Pendulum physics with external pivot movement
        # The angular acceleration depends on gravity and pivot acceleration
        gravity_component = -(gravity / self.string_length) * math.sin(self.angle)
        pivot_effect = (pivot_velocity_y / self.string_length) * math.sin(self.angle)

        self.angular_acceleration = gravity_component + pivot_effect

        # Apply damping (air resistance)
        self.angular_acceleration -= 0.05 * self.angular_velocity

        # Verlet integration for stability
        self.angular_velocity += self.angular_acceleration * dt
        self.angle += self.angular_velocity * dt

    def get_position(self):
        x = self.pivot_x + self.string_length * math.sin(self.angle)
        y = self.pivot_y + self.string_length * math.cos(self.angle)
        return x, y

    def draw(self, surface):
        ball_x, ball_y = self.get_position()

        # Draw string
        pygame.draw.line(
            surface,
            (150, 150, 150),
            (int(self.pivot_x), int(self.pivot_y)),
            (int(ball_x), int(ball_y)),
            2
        )

        # Draw ball
        pygame.draw.circle(
            surface,
            self.color,
            (int(ball_x), int(ball_y)),
            self.radius
        )

        # Draw ball outline
        pygame.draw.circle(
            surface,
            (255, 255, 255),
            (int(ball_x), int(ball_y)),
            self.radius,
            2
        )


class ClackerGame:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Vector Clacker - Physics Ball")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        # Physics constants
        self.gravity = 800
        self.dt = 1 / 60

        # Pivot (handle) setup
        self.pivot_x = self.width // 2
        self.pivot_y_base = self.height // 2 - 50
        self.pivot_y = self.pivot_y_base
        self.pivot_velocity_y = 0
        self.pivot_min_y = self.height // 2 - 150
        self.pivot_max_y = self.height // 2 + 100
        self.pivot_speed = 300

        # Balls setup - starting at bottom
        string_length = 200
        self.ball1 = Ball(
            self.pivot_x, self.pivot_y, string_length,
            math.radians(10), (255, 100, 100)
        )
        self.ball2 = Ball(
            self.pivot_x, self.pivot_y, string_length,
            math.radians(-10), (100, 100, 255)
        )

        # Game state
        self.score = 0
        self.combo = 0
        self.last_collision_time = 0
        self.collision_cooldown = 0.1
        self.no_motion_timer = 0
        self.game_over = False

        # Visual effects
        self.collision_flashes = []

        # Game tracking
        self.top_collision_count = 0
        self.total_collisions = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Handle pivot movement
        old_pivot_y = self.pivot_y

        if keys[pygame.K_UP]:
            self.pivot_y -= self.pivot_speed * self.dt
        if keys[pygame.K_DOWN]:
            self.pivot_y += self.pivot_speed * self.dt

        # Clamp pivot position
        self.pivot_y = max(self.pivot_min_y, min(self.pivot_max_y, self.pivot_y))

        # Calculate pivot velocity (for physics)
        self.pivot_velocity_y = (self.pivot_y - old_pivot_y) / self.dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over and event.key == pygame.K_SPACE:
                    self.reset_game()

        return True

    def check_collision(self):
        # Get ball positions
        x1, y1 = self.ball1.get_position()
        x2, y2 = self.ball2.get_position()

        # Calculate distance
        dx = x2 - x1
        dy = y2 - y1
        distance = math.sqrt(dx * dx + dy * dy)

        # Check for collision
        min_distance = self.ball1.radius + self.ball2.radius

        if distance < min_distance:
            current_time = time.time()

            if current_time - self.last_collision_time > self.collision_cooldown:
                self.last_collision_time = current_time

                # Determine collision type
                collision_at_top = abs(self.ball1.angle) > math.radians(150)

                # Calculate score based on collision
                base_points = 100
                if collision_at_top:
                    base_points = 500
                    self.top_collision_count += 1

                # Apply combo multiplier
                self.combo += 1
                multiplier = min(self.combo, 10)
                points = base_points * multiplier
                self.score += points
                self.total_collisions += 1

                # Add visual flash
                flash_x = (x1 + x2) / 2
                flash_y = (y1 + y2) / 2
                self.collision_flashes.append({
                    'x': flash_x,
                    'y': flash_y,
                    'radius': 10,
                    'max_radius': 50 if collision_at_top else 30,
                    'alpha': 255,
                    'color': (255, 255, 100) if collision_at_top else (255, 200, 100)
                })

                # Elastic collision response
                # Swap velocities (for equal mass balls)
                self.ball1.angular_velocity, self.ball2.angular_velocity = \
                    self.ball2.angular_velocity, self.ball1.angular_velocity

                # Add some energy loss
                energy_loss = 0.9
                self.ball1.angular_velocity *= energy_loss
                self.ball2.angular_velocity *= energy_loss

    def check_no_motion(self):
        # Check if balls have stopped moving
        velocity_threshold = 0.1
        total_velocity = abs(self.ball1.angular_velocity) + abs(self.ball2.angular_velocity)

        if total_velocity < velocity_threshold:
            # Check if balls are at rest (near bottom)
            angle_threshold = math.radians(5)
            both_at_bottom = (
                abs(self.ball1.angle) < angle_threshold and
                abs(self.ball2.angle) < angle_threshold
            )

            if both_at_bottom:
                self.no_motion_timer += self.dt
                if self.no_motion_timer > 3:
                    self.game_over = True
            else:
                self.no_motion_timer = max(0, self.no_motion_timer - self.dt)
        else:
            self.no_motion_timer = max(0, self.no_motion_timer - self.dt)

        # Reset combo if too long between collisions
        time_since_last = time.time() - self.last_collision_time
        if time_since_last > 2:
            self.combo = 0

    def update(self):
        if self.game_over:
            return

        # Update ball pivots to follow handle
        self.ball1.pivot_y = self.pivot_y
        self.ball2.pivot_y = self.pivot_y

        # Update physics
        self.ball1.update(self.gravity, self.pivot_velocity_y, self.dt)
        self.ball2.update(self.gravity, self.pivot_velocity_y, self.dt)

        # Check for collision
        self.check_collision()

        # Check for game over condition
        self.check_no_motion()

        # Update visual effects
        for flash in self.collision_flashes[:]:
            flash['radius'] += 2
            flash['alpha'] -= 10
            if flash['alpha'] <= 0:
                self.collision_flashes.remove(flash)

    def reset_game(self):
        self.score = 0
        self.combo = 0
        self.last_collision_time = 0
        self.no_motion_timer = 0
        self.game_over = False
        self.top_collision_count = 0
        self.total_collisions = 0
        self.pivot_y = self.pivot_y_base
        self.pivot_velocity_y = 0

        # Reset balls
        string_length = 200
        self.ball1.angle = math.radians(10)
        self.ball1.angular_velocity = 0
        self.ball2.angle = math.radians(-10)
        self.ball2.angular_velocity = 0

        self.collision_flashes.clear()

    def draw(self):
        # Background gradient
        for y in range(self.height):
            color_value = 30 + int(20 * y / self.height)
            pygame.draw.line(
                self.screen,
                (color_value, color_value, color_value + 5),
                (0, y),
                (self.width, y)
            )

        # Draw center guide circle
        pygame.draw.circle(
            self.screen,
            (50, 50, 60),
            (int(self.pivot_x), int(self.pivot_y)),
            200,
            1
        )

        # Draw top bonus zone
        top_zone_y = int(self.pivot_y - 200)
        pygame.draw.arc(
            self.screen,
            (80, 60, 40),
            (int(self.pivot_x) - 60, top_zone_y - 60, 120, 120),
            0, math.pi,
            3
        )

        # Draw pivot handle
        handle_width = 60
        handle_height = 30
        handle_rect = pygame.Rect(
            self.pivot_x - handle_width // 2,
            self.pivot_y - handle_height // 2,
            handle_width,
            handle_height
        )
        pygame.draw.rect(self.screen, (100, 80, 60), handle_rect)
        pygame.draw.rect(self.screen, (150, 120, 100), handle_rect, 3)

        # Draw balls
        self.ball1.draw(self.screen)
        self.ball2.draw(self.screen)

        # Draw collision flashes
        for flash in self.collision_flashes:
            flash_surface = pygame.Surface(
                (flash['radius'] * 2, flash['radius'] * 2),
                pygame.SRCALPHA
            )
            pygame.draw.circle(
                flash_surface,
                (*flash['color'], int(flash['alpha'])),
                (flash['radius'], flash['radius']),
                int(flash['radius'])
            )
            self.screen.blit(
                flash_surface,
                (flash['x'] - flash['radius'], flash['y'] - flash['radius'])
            )

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, (200, 200, 200))
        self.screen.blit(score_text, (20, 20))

        combo_text = self.font.render(f"Combo: x{self.combo}", True, (255, 200, 100))
        self.screen.blit(combo_text, (20, 60))

        # Draw top collision bonus
        if self.top_collision_count > 0:
            bonus_text = self.font.render(
                f"Top Hits: {self.top_collision_count}",
                True,
                (255, 255, 100)
            )
            self.screen.blit(bonus_text, (self.width - 200, 20))

        # Draw no motion warning
        if self.no_motion_timer > 1:
            warning_alpha = int(255 * (self.no_motion_timer - 1) / 2)
            warning_text = self.font.render(
                f"Rhythm Lost: {3 - int(self.no_motion_timer)}",
                True,
                (255, 100, 100)
            )
            warning_rect = warning_text.get_rect(center=(self.width // 2, 100))

            warning_surface = pygame.Surface(
                (warning_rect.width + 20, warning_rect.height + 10),
                pygame.SRCALPHA
            )
            warning_surface.fill((50, 0, 0, warning_alpha))
            self.screen.blit(
                warning_surface,
                (warning_rect.x - 10, warning_rect.y - 5)
            )
            self.screen.blit(warning_text, warning_rect)

        # Draw game over screen
        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, (255, 100, 100))
            game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 50))
            self.screen.blit(game_over_text, game_over_rect)

            final_score_text = self.font.render(f"Final Score: {self.score}", True, (200, 200, 200))
            score_rect = final_score_text.get_rect(center=(self.width // 2, self.height // 2 + 10))
            self.screen.blit(final_score_text, score_rect)

            stats_text = self.font.render(
                f"Total Collisions: {self.total_collisions} | Top Hits: {self.top_collision_count}",
                True,
                (150, 150, 150)
            )
            stats_rect = stats_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(stats_text, stats_rect)

            restart_text = self.font.render("Press SPACE to play again", True, (255, 200, 100))
            restart_rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 100))
            self.screen.blit(restart_text, restart_rect)

        # Draw controls
        controls = [
            "UP/DOWN: Move handle vertically",
            "Make balls collide to score",
            "Top collision = bonus points!",
            "ESC: Quit"
        ]
        for i, line in enumerate(controls):
            text = pygame.font.Font(None, 20).render(line, True, (80, 80, 80))
            self.screen.blit(text, (10, self.height - 85 + i * 18))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = ClackerGame()
    game.run()
