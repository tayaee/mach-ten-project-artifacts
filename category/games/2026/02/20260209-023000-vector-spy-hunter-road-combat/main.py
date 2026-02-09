"""
Vector Spy Hunter: Road Combat
A high-speed tactical road combat simulator with vector-style graphics.
"""

import pygame
import random
import math
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Constants
SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

# Colors (Monochrome/Vector Style - Green on Black)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 150, 0)
DIM_GREEN = (0, 100, 0)
YELLOW = (255, 255, 0)
RED = (255, 50, 50)

# Game Constants
LANE_WIDTH = SCREEN_WIDTH // 3
BASE_SPEED = 3
MAX_SPEED = 8
ACCELERATION = 0.1
DECELERATION = 0.15

# Weapon Constants
GUN_COOLDOWN = 15
SMOKE_COOLDOWN = 120
SMOKE_DURATION = 90

@dataclass
class Vector2:
    x: float
    y: float

class GameObject:
    def __init__(self, x: float, y: float, width: int, height: int, color: tuple):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.color = color
        self.vel_x = 0.0
        self.vel_y = 0.0

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface: pygame.Surface, offset_x: float = 0):
        rect = self.get_rect()
        draw_x = rect.x + offset_x
        pygame.draw.rect(surface, self.color, (draw_x, rect.y, rect.width, rect.height), 2)
        # Draw center line
        center_x = draw_x + rect.width // 2
        pygame.draw.line(surface, self.color, (center_x, rect.y), (center_x, rect.y + rect.height), 1)

    def collides_with(self, other) -> bool:
        return self.get_rect().colliderect(other.get_rect())

class Player(GameObject):
    def __init__(self):
        super().__init__(
            x=SCREEN_WIDTH // 2 - 15,
            y=SCREEN_HEIGHT - 100,
            width=30,
            height=50,
            color=GREEN
        )
        self.speed = BASE_SPEED
        self.target_lane = 1
        self.gun_cooldown = 0
        self.smoke_cooldown = 0
        self.smoke_active = False
        self.smoke_timer = 0
        self.health = 1

    def update(self, keys):
        # Horizontal movement
        if keys[pygame.K_LEFT] and self.x > 10:
            self.vel_x = -4
        elif keys[pygame.K_RIGHT] and self.x < SCREEN_WIDTH - self.width - 10:
            self.vel_x = 4
        else:
            self.vel_x *= 0.8

        # Speed control
        if keys[pygame.K_UP]:
            self.speed = min(self.speed + ACCELERATION, MAX_SPEED)
        elif keys[pygame.K_DOWN]:
            self.speed = max(self.speed - DECELERATION, 2)

        self.x += self.vel_x

        # Weapon cooldowns
        if self.gun_cooldown > 0:
            self.gun_cooldown -= 1
        if self.smoke_cooldown > 0:
            self.smoke_cooldown -= 1
        if self.smoke_active:
            self.smoke_timer -= 1
            if self.smoke_timer <= 0:
                self.smoke_active = False

    def fire_gun(self) -> bool:
        if self.gun_cooldown <= 0:
            self.gun_cooldown = GUN_COOLDOWN
            return True
        return False

    def deploy_smoke(self) -> bool:
        if self.smoke_cooldown <= 0 and not self.smoke_active:
            self.smoke_cooldown = SMOKE_COOLDOWN
            self.smoke_active = True
            self.smoke_timer = SMOKE_DURATION
            return True
        return False

    def draw(self, surface: pygame.Surface, offset_x: float = 0):
        draw_x = self.x + offset_x
        rect = pygame.Rect(draw_x, self.y, self.width, self.height)

        # Draw vehicle body (vector style)
        pygame.draw.rect(surface, self.color, rect, 2)

        # Draw windshield
        windshield = pygame.Rect(draw_x + 5, self.y + 10, self.width - 10, 12)
        pygame.draw.rect(surface, self.color, windshield, 1)

        # Draw gun barrel
        pygame.draw.line(surface, self.color,
                        (draw_x + self.width // 2, self.y + 5),
                        (draw_x + self.width // 2, self.y), 2)

        # Draw rear bumper
        pygame.draw.line(surface, self.color,
                        (draw_x + 5, self.y + self.height),
                        (draw_x + self.width - 5, self.y + self.height), 2)

class Bullet(GameObject):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 4, 8, YELLOW)
        self.speed = 10

    def update(self):
        self.y -= self.speed

    def draw(self, surface: pygame.Surface, offset_x: float = 0):
        draw_x = self.x + offset_x
        pygame.draw.line(surface, self.color,
                        (draw_x + 2, self.y),
                        (draw_x + 2, self.y + self.height), 2)

class SmokeParticle(GameObject):
    def __init__(self, x: float, y: float):
        super().__init__(x, y, random.randint(8, 15), random.randint(8, 15), DIM_GREEN)
        self.life = 60
        self.max_life = 60

    def update(self, speed: float):
        self.y += speed * 0.5
        self.life -= 1
        self.x += random.uniform(-0.5, 0.5)

    def draw(self, surface: pygame.Surface, offset_x: float = 0):
        alpha = int((self.life / self.max_life) * 255)
        color = (*self.color, alpha)
        draw_x = self.x + offset_x
        s = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        pygame.draw.circle(s, color, (self.width // 2, self.height // 2), self.width // 2)
        surface.blit(s, (draw_x, self.y))

class Vehicle(GameObject):
    def __init__(self, x: float, y: float, v_type: str):
        self.v_type = v_type
        if v_type == "civilian":
            color = DARK_GREEN
            width, height = 28, 45
        elif v_type == "enemy":
            color = RED
            width, height = 32, 50
        else:  # obstacle
            color = DIM_GREEN
            width, height = 25, 25

        super().__init__(x, y, width, height, color)
        self.target_x = x
        self.aggressive = v_type == "enemy"

    def update(self, speed: float, player_x: float):
        self.y += speed

        # Enemy AI: try to ram player
        if self.aggressive and self.y > SCREEN_HEIGHT * 0.3 and self.y < SCREEN_HEIGHT * 0.7:
            if self.x < player_x - 5:
                self.vel_x = 2
            elif self.x > player_x + 5:
                self.vel_x = -2
            else:
                self.vel_x *= 0.9

            self.x += self.vel_x
            self.x = max(10, min(SCREEN_WIDTH - self.width - 10, self.x))

    def draw(self, surface: pygame.Surface, offset_x: float = 0):
        draw_x = self.x + offset_x
        rect = pygame.Rect(draw_x, self.y, self.width, self.height)

        if self.v_type == "obstacle":
            # Draw oil slick/hazard
            pygame.draw.ellipse(surface, self.color,
                              (draw_x, self.y, self.width, self.height), 2)
        else:
            # Draw vehicle
            pygame.draw.rect(surface, self.color, rect, 2)
            # Draw details
            pygame.draw.rect(surface, self.color,
                           (draw_x + 4, self.y + 8, self.width - 8, 10), 1)
            if self.v_type == "enemy":
                # Draw enemy weapon
                pygame.draw.line(surface, self.color,
                               (draw_x + 5, self.y + self.height),
                               (draw_x + 5, self.y + self.height + 5), 2)
                pygame.draw.line(surface, self.color,
                               (draw_x + self.width - 5, self.y + self.height),
                               (draw_x + self.width - 5, self.y + self.height + 5), 2)

class Road:
    def __init__(self):
        self.offset_y = 0
        self.curve_offset = 0
        self.curve_direction = 0
        self.curve_target = 0
        self.time_elapsed = 0

    def update(self, speed: float):
        self.offset_y = (self.offset_y + speed) % 40
        self.time_elapsed += 1

        # Progressive road curving
        if self.time_elapsed % 300 == 0:
            self.curve_target = random.randint(-80, 80)

        self.curve_offset += (self.curve_target - self.curve_offset) * 0.01

    def get_curve_at(self, y: float) -> float:
        # Calculate curve offset based on screen position
        factor = (y / SCREEN_HEIGHT - 0.5) * 2
        return self.curve_offset * factor

    def draw(self, surface: pygame.Surface):
        # Draw road boundaries
        for y in range(-40, SCREEN_HEIGHT + 40, 40):
            draw_y = y + self.offset_y - 40

            # Left boundary
            curve = self.get_curve_at(draw_y)
            pygame.draw.line(surface, DARK_GREEN,
                           (10 + curve, draw_y),
                           (10 + curve, draw_y + 20), 2)

            # Right boundary
            pygame.draw.line(surface, DARK_GREEN,
                           (SCREEN_WIDTH - 10 + curve, draw_y),
                           (SCREEN_WIDTH - 10 + curve, draw_y + 20), 2)

        # Draw lane markers
        for y in range(-40, SCREEN_HEIGHT + 40, 40):
            draw_y = y + self.offset_y - 40
            curve = self.get_curve_at(draw_y)

            for lane in range(1, 3):
                x = LANE_WIDTH * lane + curve
                for dy in range(0, 20, 10):
                    pygame.draw.line(surface, DIM_GREEN,
                                   (x, draw_y + dy),
                                   (x, draw_y + dy + 5), 1)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Spy Hunter: Road Combat")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset()

    def reset(self):
        self.player = Player()
        self.road = Road()
        self.bullets: List[Bullet] = []
        self.smoke_particles: List[SmokeParticle] = []
        self.vehicles: List[Vehicle] = []
        self.score = 0
        self.distance = 0
        self.game_over = False
        self.spawn_timer = 0
        self.difficulty = 1.0

    def spawn_vehicle(self):
        lane = random.randint(0, 2)
        base_x = lane * LANE_WIDTH + (LANE_WIDTH - 30) // 2

        # Consider road curve when spawning
        curve = self.road.get_curve_at(-50)
        base_x += curve

        roll = random.random()
        if roll < 0.5 * self.difficulty:
            v_type = "civilian"
        elif roll < 0.7 * self.difficulty:
            v_type = "enemy"
        else:
            v_type = "obstacle"

        vehicle = Vehicle(base_x, -60, v_type)
        self.vehicles.append(vehicle)

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_z:
                    if self.player.fire_gun():
                        self.bullets.append(Bullet(
                            self.player.x + self.player.width // 2 - 2,
                            self.player.y
                        ))
                elif event.key == pygame.K_x:
                    if self.player.deploy_smoke():
                        # Create smoke particles behind player
                        for _ in range(5):
                            self.smoke_particles.append(SmokeParticle(
                                self.player.x + random.randint(0, self.player.width),
                                self.player.y + self.player.height
                            ))
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()

        keys = pygame.key.get_pressed()
        if not self.game_over:
            self.player.update(keys)

        return True

    def update(self):
        if self.game_over:
            return

        # Update road
        self.road.update(self.player.speed)

        # Update distance and difficulty
        self.distance += self.player.speed
        self.difficulty = 1.0 + self.distance / 5000

        # Spawn vehicles
        self.spawn_timer += 1
        spawn_rate = max(30, 90 - int(self.distance / 500))
        if self.spawn_timer >= spawn_rate:
            self.spawn_timer = 0
            if len(self.vehicles) < 8:
                self.spawn_vehicle()

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y < -10:
                self.bullets.remove(bullet)

        # Update smoke particles
        for smoke in self.smoke_particles[:]:
            smoke.update(self.player.speed)
            if smoke.y > SCREEN_HEIGHT or smoke.life <= 0:
                self.smoke_particles.remove(smoke)
            elif smoke.life % 10 == 0:
                # Add more smoke while active
                if self.player.smoke_active:
                    self.smoke_particles.append(SmokeParticle(
                        self.player.x + random.randint(0, self.player.width),
                        self.player.y + self.player.height
                    ))

        # Update vehicles and check collisions
        curve_at_player = self.road.get_curve_at(self.player.y)

        for vehicle in self.vehicles[:]:
            vehicle.update(self.player.speed, self.player.x - curve_at_player)

            # Check bullet collisions
            for bullet in self.bullets[:]:
                if bullet.collides_with(vehicle):
                    if vehicle.v_type == "enemy":
                        self.score += 50
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if vehicle in self.vehicles:
                        self.vehicles.remove(vehicle)
                    break

            # Check player collision
            if vehicle.collides_with(self.player):
                if vehicle.v_type == "civilian":
                    self.score -= 20
                    self.player.speed = max(2, self.player.speed - 2)
                    self.vehicles.remove(vehicle)
                elif vehicle.v_type == "obstacle":
                    self.score -= 20
                    self.player.speed = max(2, self.player.speed - 1)
                    self.vehicles.remove(vehicle)
                elif vehicle.v_type == "enemy":
                    self.game_over = True
                    self.score -= 100

            # Remove off-screen vehicles
            if vehicle.y > SCREEN_HEIGHT + 50:
                self.vehicles.remove(vehicle)

        # Score for distance
        new_distance_score = (self.distance // 100) * 10
        self.score = max(self.score, new_distance_score)

    def draw(self):
        self.screen.fill(BLACK)

        # Draw road
        self.road.draw(self.screen)

        # Get curve at different heights for proper rendering
        curve_offset = 0

        # Draw smoke particles
        for smoke in self.smoke_particles:
            smoke.draw(self.screen, smoke.x - (smoke.x if smoke.x == smoke.x else smoke.x))

        # Draw vehicles
        for vehicle in self.vehicles:
            curve = self.road.get_curve_at(vehicle.y)
            vehicle.draw(self.screen, curve)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        score_text = self.small_font.render(f"SCORE: {self.score}", True, GREEN)
        speed_text = self.small_font.render(f"SPEED: {int(self.player.speed * 20)}", True, GREEN)
        dist_text = self.small_font.render(f"DIST: {int(self.distance)}m", True, GREEN)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(speed_text, (10, 35))
        self.screen.blit(dist_text, (10, 60))

        # Draw weapon status
        gun_ready = self.player.gun_cooldown <= 0
        smoke_ready = self.player.smoke_cooldown <= 0 and not self.player.smoke_active

        gun_color = GREEN if gun_ready else DIM_GREEN
        smoke_color = GREEN if smoke_ready else DIM_GREEN

        gun_text = self.small_font.render("[Z] GUN", True, gun_color)
        smoke_text = self.small_font.render("[X] SMOKE", True, smoke_color)

        self.screen.blit(gun_text, (SCREEN_WIDTH - 100, 10))
        self.screen.blit(smoke_text, (SCREEN_WIDTH - 100, 35))

        # Game over screen
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill(BLACK)
            self.screen.blit(overlay, (0, 0))

            go_text = self.font.render("GAME OVER", True, RED)
            score_text = self.font.render(f"Final Score: {self.score}", True, GREEN)
            retry_text = self.small_font.render("Press R to retry", True, GREEN)

            self.screen.blit(go_text, (SCREEN_WIDTH // 2 - go_text.get_width() // 2, 200))
            self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 260))
            self.screen.blit(retry_text, (SCREEN_WIDTH // 2 - retry_text.get_width() // 2, 320))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
