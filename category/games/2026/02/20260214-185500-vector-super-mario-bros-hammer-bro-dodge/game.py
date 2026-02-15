"""
Hammer Bro Dodge - A precision timing game
Dodge hammers from the iconic Hammer Brother enemy.
"""

import pygame
import random
import math
from typing import List, Tuple


class Hammer:
    """Represents a hammer projectile with parabolic trajectory."""

    def __init__(self, x: float, y: float, direction: str, arc_type: str):
        self.x = x
        self.y = y
        self.start_x = x
        self.start_y = y
        self.radius = 8
        self.active = True
        self.arc_type = arc_type

        # Set velocity based on arc type
        if arc_type == "short-high":
            self.vx = 3.0 if direction == "right" else -3.0
            self.vy = -12.0
        else:  # long-low
            self.vx = 5.0 if direction == "right" else -5.0
            self.vy = -8.0

    def update(self, gravity: float, dt: float):
        """Update hammer position with gravity."""
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.vy += gravity * dt

        # Deactivate if off screen
        if self.y > 700 or self.x < -50 or self.x > 850:
            self.active = False

    def draw(self, surface: pygame.Surface):
        """Draw the hammer."""
        # Draw hammer head
        pygame.draw.circle(surface, (139, 69, 19), (int(self.x), int(self.y)), self.radius)
        # Draw handle hint
        handle_end_x = self.x - self.vx * 0.3
        handle_end_y = self.y - self.vy * 0.3
        pygame.draw.line(surface, (101, 67, 33), (int(self.x), int(self.y)), (int(handle_end_x), int(handle_end_y)), 3)


class HammerBro:
    """The Hammer Bro enemy that moves and throws hammers."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 32
        self.height = 40
        self.speed = 2.0
        self.direction = 1  # 1 for right, -1 for left
        self.min_x = 100
        self.max_x = 700
        self.throw_timer = 0
        self.throw_interval = 120  # Frames between throws
        self.jump_timer = 0
        self.on_upper = True

    def update(self, hammers: List[Hammer], platforms: List[dict]):
        """Update Hammer Bro position and throwing behavior."""
        # Move back and forth
        self.x += self.speed * self.direction

        # Change direction at boundaries
        if self.x <= self.min_x or self.x >= self.max_x:
            self.direction *= -1

        # Randomly jump between platforms
        self.jump_timer += 1
        if self.jump_timer > 180 and random.random() < 0.05:
            self.jump_timer = 0
            self.on_upper = not self.on_upper
            if self.on_upper:
                self.y = 250
            else:
                self.y = 450

        # Throw hammers
        self.throw_timer += 1
        if self.throw_timer >= self.throw_interval:
            self.throw_timer = 0
            # Vary the interval for unpredictability
            self.throw_interval = random.randint(80, 150)

            # Determine arc type and direction
            arc_type = random.choice(["short-high", "long-low"])
            direction = "right" if self.direction > 0 else "left"

            hammer = Hammer(
                self.x + self.width / 2,
                self.y,
                direction,
                arc_type
            )
            hammers.append(hammer)

    def draw(self, surface: pygame.Surface):
        """Draw the Hammer Bro."""
        # Body
        pygame.draw.rect(surface, (200, 150, 100), (int(self.x), int(self.y), self.width, self.height))

        # Shell
        shell_color = (255, 200, 0)
        pygame.draw.rect(surface, shell_color, (int(self.x) + 4, int(self.y) + 8, self.width - 8, 24))

        # Helmet
        pygame.draw.rect(surface, (50, 50, 200), (int(self.x) + 2, int(self.y) - 8, self.width - 4, 12))

        # Eyes
        eye_color = (255, 255, 255)
        pupil_color = (0, 0, 0)
        eye_y = self.y + 12
        eye_offset = 6 if self.direction > 0 else -6

        pygame.draw.circle(surface, eye_color, (int(self.x) + 10 + eye_offset // 2, int(eye_y)), 5)
        pygame.draw.circle(surface, eye_color, (int(self.x) + 22 + eye_offset // 2, int(eye_y)), 5)
        pygame.draw.circle(surface, pupil_color, (int(self.x) + 10 + eye_offset, int(eye_y)), 2)
        pygame.draw.circle(surface, pupil_color, (int(self.x) + 22 + eye_offset, int(eye_y)), 2)


class Player:
    """The player character."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.width = 24
        self.height = 32
        self.speed = 5.0
        self.vx = 0.0
        self.vy = 0.0
        self.on_ground = False
        self.jump_power = -12.0
        self.gravity = 9.8 * 60  # Scaled for 60 FPS

    def update(self, keys, platforms: List[dict], dt: float):
        """Update player movement and physics."""
        # Horizontal movement
        self.vx = 0.0
        if keys[pygame.K_LEFT]:
            self.vx = -self.speed
        if keys[pygame.K_RIGHT]:
            self.vx = self.speed

        # Apply horizontal movement
        self.x += self.vx * 60 * dt

        # Clamp to screen bounds
        if self.x < 20:
            self.x = 20
        if self.x > 780 - self.width:
            self.x = 780 - self.width

        # Apply gravity
        self.vy += self.gravity * dt

        # Apply vertical movement
        self.y += self.vy * dt

        # Platform collision
        self.on_ground = False
        player_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        for platform in platforms:
            plat_rect = pygame.Rect(platform["x"], platform["y"], platform["width"], platform["height"])

            if player_rect.colliderect(plat_rect):
                # Check if landing on top
                if self.vy > 0 and self.y + self.height - self.vy * dt <= platform["y"]:
                    self.y = platform["y"] - self.height
                    self.vy = 0.0
                    self.on_ground = True

        # Ground collision
        ground_y = 550
        if self.y + self.height > ground_y:
            self.y = ground_y - self.height
            self.vy = 0.0
            self.on_ground = True

        # Ceiling collision
        if self.y < 50:
            self.y = 50
            self.vy = 0.0

    def jump(self):
        """Make the player jump if on ground."""
        if self.on_ground:
            self.vy = self.jump_power
            self.on_ground = False

    def draw(self, surface: pygame.Surface):
        """Draw the player."""
        # Body
        pygame.draw.rect(surface, (255, 0, 0), (int(self.x), int(self.y), self.width, self.height))

        # Hat
        pygame.draw.rect(surface, (200, 0, 0), (int(self.x) + 2, int(self.y), self.width - 4, 8))
        pygame.draw.rect(surface, (200, 0, 0), (int(self.x) - 2, int(self.y) + 4, self.width + 4, 4))

        # Face
        pygame.draw.rect(surface, (255, 200, 150), (int(self.x) + 4, int(self.y) + 10, self.width - 8, 10))

        # Overalls
        pygame.draw.rect(surface, (0, 0, 200), (int(self.x) + 2, int(self.y) + 20, self.width - 4, 10))

        # Buttons
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x) + 8, int(self.y) + 25), 2)
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x) + 16, int(self.y) + 25), 2)


class Game:
    """Main game class for Hammer Bro Dodge."""

    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Hammer Bro Dodge")

        self.screen = pygame.display.set_mode((800, 600))
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.score = 0
        self.dodged_count = 0
        self.survival_timer = 0

        self.gravity = 9.8 * 60  # Scaled for 60 FPS

        # Create platforms
        self.platforms = [
            {"x": 50, "y": 550, "width": 700, "height": 50},  # Ground
            {"x": 100, "y": 450, "width": 200, "height": 20},
            {"x": 500, "y": 450, "width": 200, "height": 20},
            {"x": 250, "y": 350, "width": 150, "height": 20},
            {"x": 100, "y": 250, "width": 200, "height": 20},
            {"x": 500, "y": 250, "width": 200, "height": 20},
        ]

        # Create entities
        self.player = Player(400, 500)
        self.hammer_bro = HammerBro(400, 250)
        self.hammers: List[Hammer] = []

        # Font for UI
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        # Track hammers that have been counted
        self.counted_hammers = set()

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if self.game_over:
                        self.reset_game()
                    else:
                        self.player.jump()
                elif event.key == pygame.K_ESCAPE:
                    self.running = False

    def reset_game(self):
        """Reset the game state."""
        self.game_over = False
        self.score = 0
        self.dodged_count = 0
        self.survival_timer = 0
        self.hammers.clear()
        self.counted_hammers.clear()
        self.player = Player(400, 500)
        self.hammer_bro = HammerBro(400, 250)

    def update(self, dt: float):
        """Update game state."""
        if self.game_over:
            return

        keys = pygame.key.get_pressed()

        # Update player
        self.player.update(keys, self.platforms, dt)

        # Update hammer bro
        self.hammer_bro.update(self.hammers, self.platforms)

        # Update hammers
        for hammer in self.hammers[:]:
            hammer.update(self.gravity, dt)

            # Check if hammer left screen (dodged)
            if not hammer.active and hammer not in self.counted_hammers:
                self.counted_hammers.add(hammer)
                self.dodged_count += 1
                self.score += 10

            # Remove inactive hammers
            if not hammer.active:
                self.hammers.remove(hammer)

        # Collision detection
        player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)

        for hammer in self.hammers:
            hammer_rect = pygame.Rect(
                hammer.x - hammer.radius,
                hammer.y - hammer.radius,
                hammer.radius * 2,
                hammer.radius * 2
            )

            if player_rect.colliderect(hammer_rect):
                self.game_over = True

        # Survival score
        self.survival_timer += dt
        if self.survival_timer >= 5.0:
            self.survival_timer = 0
            self.score += 50

    def draw(self):
        """Draw the game."""
        # Background
        self.screen.fill((135, 206, 235))  # Sky blue

        # Draw platforms
        for platform in self.platforms:
            pygame.draw.rect(self.screen, (139, 90, 43), (
                platform["x"],
                platform["y"],
                platform["width"],
                platform["height"]
            ))
            # Platform top highlight
            pygame.draw.rect(self.screen, (160, 110, 63), (
                platform["x"],
                platform["y"],
                platform["width"],
                4
            ))

        # Draw entities
        self.player.draw(self.screen)
        self.hammer_bro.draw(self.screen)

        for hammer in self.hammers:
            hammer.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, (0, 0, 0))
        dodged_text = self.font.render(f"Dodged: {self.dodged_count}", True, (0, 0, 0))
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(dodged_text, (10, 50))

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((800, 600))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.big_font.render("GAME OVER", True, (255, 0, 0))
            final_score_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            restart_text = self.font.render("Press SPACE to restart", True, (255, 255, 255))

            center_x = 400
            self.screen.blit(game_over_text, (center_x - game_over_text.get_width() // 2, 200))
            self.screen.blit(final_score_text, (center_x - final_score_text.get_width() // 2, 300))
            self.screen.blit(restart_text, (center_x - restart_text.get_width() // 2, 350))

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        while self.running:
            dt = self.clock.tick(60) / 1000.0  # Delta time in seconds

            self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()
