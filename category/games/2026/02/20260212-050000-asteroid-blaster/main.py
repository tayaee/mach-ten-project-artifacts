import pygame
import random
import math
from dataclasses import dataclass
from typing import List, Tuple

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (10, 10, 20)
WHITE = (255, 255, 255)
RED = (255, 80, 80)
CYAN = (80, 255, 255)
YELLOW = (255, 255, 80)
ORANGE = (255, 165, 80)
GRAY = (128, 128, 128)

# Game constants
PLAYER_SIZE = 20
PLAYER_SPEED = 5
BULLET_SPEED = 10
BULLET_LIFETIME = 60
ASTEROID_MIN_SIZE = 15
ASTEROID_MAX_SIZE = 50
ASTEROID_MIN_SPEED = 1
ASTEROID_MAX_SPEED = 3
SPAWN_INTERVAL = 120  # Frames between asteroid spawns


@dataclass
class Vector:
    x: float
    y: float

    def normalize(self) -> 'Vector':
        magnitude = math.sqrt(self.x**2 + self.y**2)
        if magnitude == 0:
            return Vector(0, 0)
        return Vector(self.x / magnitude, self.y / magnitude)


class Bullet:
    def __init__(self, x: float, y: float, angle: float):
        self.x = x
        self.y = y
        self.vx = math.cos(angle) * BULLET_SPEED
        self.vy = math.sin(angle) * BULLET_SPEED
        self.lifetime = BULLET_LIFETIME
        self.active = True

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1

        # Check bounds
        if (self.x < 0 or self.x > SCREEN_WIDTH or
            self.y < 0 or self.y > SCREEN_HEIGHT or
            self.lifetime <= 0):
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, YELLOW, (int(self.x), int(self.y)), 3)


class Asteroid:
    def __init__(self, x: float = None, y: float = None, size: int = None):
        if x is None:
            # Spawn from edges
            side = random.choice(['top', 'bottom', 'left', 'right'])
            if side == 'top':
                self.x = random.uniform(0, SCREEN_WIDTH)
                self.y = -ASTEROID_MAX_SIZE
            elif side == 'bottom':
                self.x = random.uniform(0, SCREEN_WIDTH)
                self.y = SCREEN_HEIGHT + ASTEROID_MAX_SIZE
            elif side == 'left':
                self.x = -ASTEROID_MAX_SIZE
                self.y = random.uniform(0, SCREEN_HEIGHT)
            else:
                self.x = SCREEN_WIDTH + ASTEROID_MAX_SIZE
                self.y = random.uniform(0, SCREEN_HEIGHT)
        else:
            self.x = x
            self.y = y

        self.size = size if size is not None else random.randint(ASTEROID_MIN_SIZE, ASTEROID_MAX_SIZE)
        self.speed = random.uniform(ASTEROID_MIN_SPEED, ASTEROID_MAX_SPEED)
        self.angle = random.uniform(0, math.pi * 2)
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.05, 0.05)

        # Calculate velocity towards center (with some randomness)
        center_x, center_y = SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2
        dx = center_x - self.x
        dy = center_y - self.y
        target_angle = math.atan2(dy, dx)
        angle_offset = random.uniform(-0.5, 0.5)
        self.angle = target_angle + angle_offset

        self.vx = math.cos(self.angle) * self.speed
        self.vy = math.sin(self.angle) * self.speed

        # Generate polygon shape
        self.points = self._generate_shape()
        self.color = random.choice([GRAY, (150, 150, 150), (100, 100, 100)])

    def _generate_shape(self) -> List[Tuple[float, float]]:
        num_points = random.randint(5, 9)
        points = []
        for i in range(num_points):
            angle = (2 * math.pi / num_points) * i
            radius = self.size * random.uniform(0.7, 1.0)
            points.append((math.cos(angle) * radius, math.sin(angle) * radius))
        return points

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed

    def is_off_screen(self) -> bool:
        return (self.x < -ASTEROID_MAX_SIZE * 2 or
                self.x > SCREEN_WIDTH + ASTEROID_MAX_SIZE * 2 or
                self.y < -ASTEROID_MAX_SIZE * 2 or
                self.y > SCREEN_HEIGHT + ASTEROID_MAX_SIZE * 2)

    def draw(self, surface: pygame.Surface) -> None:
        rotated_points = []
        for px, py in self.points:
            # Rotate point
            cos_r = math.cos(self.rotation)
            sin_r = math.sin(self.rotation)
            rx = px * cos_r - py * sin_r
            ry = px * sin_r + py * cos_r
            rotated_points.append((self.x + rx, self.y + ry))

        pygame.draw.polygon(surface, self.color, rotated_points, 2)

    def split(self) -> List['Asteroid']:
        if self.size < ASTEROID_MIN_SIZE * 2:
            return []
        new_size = self.size // 2
        new_asteroids = []
        for i in range(2):
            asteroid = Asteroid(self.x, self.y, new_size)
            # Give them different velocities
            angle_offset = random.uniform(-1, 1)
            asteroid.angle = self.angle + angle_offset
            asteroid.vx = math.cos(asteroid.angle) * asteroid.speed * 1.5
            asteroid.vy = math.sin(asteroid.angle) * asteroid.speed * 1.5
            new_asteroids.append(asteroid)
        return new_asteroids


class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2
        self.angle = -math.pi / 2  # Pointing up
        self.velocity = Vector(0, 0)
        self.thrusting = False
        self.rotating_left = False
        self.rotating_right = False
        self.shooting = False
        self.shoot_cooldown = 0
        self.invulnerable = 0
        self.lives = 3
        self.respawn_timer = 0
        self.active = True

    def update(self) -> None:
        if not self.active:
            self.respawn_timer -= 1
            if self.respawn_timer <= 0:
                self.respawn()
            return

        # Rotation
        if self.rotating_left:
            self.angle -= 0.08
        if self.rotating_right:
            self.angle += 0.08

        # Thrust
        self.thrusting = False
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.thrusting = True
            thrust = 0.15
            self.velocity.x += math.cos(self.angle) * thrust
            self.velocity.y += math.sin(self.angle) * thrust

        # Apply friction
        self.velocity.x *= 0.99
        self.velocity.y *= 0.99

        # Update position
        self.x += self.velocity.x
        self.y += self.velocity.y

        # Wrap around screen
        self.x = self.x % SCREEN_WIDTH
        self.y = self.y % SCREEN_HEIGHT

        # Shooting cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Invulnerability
        if self.invulnerable > 0:
            self.invulnerable -= 1

    def shoot(self) -> Bullet:
        if self.shoot_cooldown == 0 and self.active:
            self.shoot_cooldown = 15
            # Bullet spawns from tip of ship
            tip_x = self.x + math.cos(self.angle) * PLAYER_SIZE
            tip_y = self.y + math.sin(self.angle) * PLAYER_SIZE
            return Bullet(tip_x, tip_y, self.angle)
        return None

    def hit(self) -> bool:
        if self.invulnerable > 0 or not self.active:
            return False
        self.lives -= 1
        if self.lives > 0:
            self.active = False
            self.respawn_timer = 120
        return True

    def respawn(self) -> None:
        self.x = SCREEN_WIDTH / 2
        self.y = SCREEN_HEIGHT / 2
        self.velocity = Vector(0, 0)
        self.angle = -math.pi / 2
        self.invulnerable = 180
        self.active = True

    def get_shape(self) -> List[Tuple[float, float]]:
        # Triangle ship
        tip = (math.cos(self.angle) * PLAYER_SIZE,
               math.sin(self.angle) * PLAYER_SIZE)
        left = (math.cos(self.angle + 2.5) * PLAYER_SIZE,
                math.sin(self.angle + 2.5) * PLAYER_SIZE)
        right = (math.cos(self.angle - 2.5) * PLAYER_SIZE,
                 math.sin(self.angle - 2.5) * PLAYER_SIZE)
        return [tip, left, right]

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return

        # Flicker when invulnerable
        if self.invulnerable > 0 and (self.invulnerable // 5) % 2 == 0:
            return

        shape = self.get_shape()
        points = [(self.x + px, self.y + py) for px, py in shape]
        pygame.draw.polygon(surface, CYAN, points, 2)

        # Draw thrust flame
        if self.thrusting:
            flame_tip = (math.cos(self.angle + math.pi) * PLAYER_SIZE * 1.5,
                         math.sin(self.angle + math.pi) * PLAYER_SIZE * 1.5)
            flame_left = (math.cos(self.angle + 2.8) * PLAYER_SIZE * 0.8,
                          math.sin(self.angle + 2.8) * PLAYER_SIZE * 0.8)
            flame_right = (math.cos(self.angle - 2.8) * PLAYER_SIZE * 0.8,
                           math.sin(self.angle - 2.8) * PLAYER_SIZE * 0.8)
            flame_points = [(self.x + px, self.y + py) for px, py in [flame_tip, flame_left, flame_right]]
            pygame.draw.polygon(surface, ORANGE, flame_points)


class Particle:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.vx = random.uniform(-3, 3)
        self.vy = random.uniform(-3, 3)
        self.lifetime = random.randint(20, 40)
        self.max_lifetime = self.lifetime
        self.size = random.randint(2, 5)
        self.color = random.choice([WHITE, YELLOW, ORANGE, RED])

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy
        self.vx *= 0.98
        self.vy *= 0.98
        self.lifetime -= 1

    def draw(self, surface: pygame.Surface) -> None:
        if self.lifetime > 0:
            alpha = self.lifetime / self.max_lifetime
            size = int(self.size * alpha)
            if size > 0:
                color = tuple(int(c * alpha) for c in self.color)
                pygame.draw.circle(surface, color, (int(self.x), int(self.y)), size)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Asteroid Blaster")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.reset_game()
        self.state = 'menu'  # menu, playing, game_over

    def reset_game(self):
        self.player = Player()
        self.bullets: List[Bullet] = []
        self.asteroids: List[Asteroid] = []
        self.particles: List[Particle] = []
        self.score = 0
        self.spawn_timer = 0
        self.level = 1

    def create_explosion(self, x: float, y: float, count: int = 15) -> None:
        for _ in range(count):
            self.particles.append(Particle(x, y))

    def check_collision(self, obj1_x: float, obj1_y: float, obj1_radius: float,
                       obj2_x: float, obj2_y: float, obj2_radius: float) -> bool:
        dx = obj1_x - obj2_x
        dy = obj1_y - obj2_y
        distance = math.sqrt(dx * dx + dy * dy)
        return distance < obj1_radius + obj2_radius

    def update(self) -> None:
        if self.state == 'menu':
            return

        self.player.update()

        # Spawn asteroids
        self.spawn_timer += 1
        spawn_rate = max(30, SPAWN_INTERVAL - self.level * 10)
        if self.spawn_timer >= spawn_rate:
            self.spawn_timer = 0
            self.asteroids.append(Asteroid())

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)

        # Update asteroids
        for asteroid in self.asteroids[:]:
            asteroid.update()
            if asteroid.is_off_screen():
                self.asteroids.remove(asteroid)

        # Update particles
        for particle in self.particles[:]:
            particle.update()
            if particle.lifetime <= 0:
                self.particles.remove(particle)

        # Bullet-asteroid collisions
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                if self.check_collision(bullet.x, bullet.y, 3,
                                      asteroid.x, asteroid.y, asteroid.size):
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.create_explosion(asteroid.x, asteroid.y)

                    # Score based on size
                    points = (ASTEROID_MAX_SIZE - asteroid.size + ASTEROID_MIN_SIZE) * 10
                    self.score += points

                    # Split asteroid
                    new_asteroids = asteroid.split()
                    self.asteroids.extend(new_asteroids)
                    break

        # Player-asteroid collisions
        if self.player.active:
            for asteroid in self.asteroids[:]:
                if self.check_collision(self.player.x, self.player.y, PLAYER_SIZE * 0.7,
                                      asteroid.x, asteroid.y, asteroid.size):
                    if self.player.hit():
                        self.create_explosion(self.player.x, self.player.y, 30)
                        self.asteroids.remove(asteroid)
                        if self.player.lives <= 0:
                            self.state = 'game_over'

        # Level up
        if self.score > self.level * 1000:
            self.level += 1

    def draw(self) -> None:
        self.screen.fill(BLACK)

        if self.state == 'menu':
            self.draw_menu()
        elif self.state == 'playing':
            self.draw_game()
        elif self.state == 'game_over':
            self.draw_game_over()

        pygame.display.flip()

    def draw_menu(self) -> None:
        title = self.large_font.render("ASTEROID BLASTER", True, CYAN)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))

        instructions = [
            "Arrow Keys / WASD to Move",
            "UP / W to Thrust",
            "SPACE to Shoot",
            "",
            "Press SPACE to Start"
        ]

        for i, line in enumerate(instructions):
            text = self.font.render(line, True, WHITE)
            self.screen.blit(text, (SCREEN_WIDTH // 2 - text.get_width() // 2, 280 + i * 40))

    def draw_game(self) -> None:
        # Draw particles
        for particle in self.particles:
            particle.draw(self.screen)

        # Draw asteroids
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        lives_text = self.font.render(f"Lives: {self.player.lives}", True, WHITE)
        level_text = self.font.render(f"Level: {self.level}", True, WHITE)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 50))
        self.screen.blit(level_text, (10, 90))

    def draw_game_over(self) -> None:
        # Draw game state in background
        self.draw_game()

        # Overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))

        game_over_text = self.large_font.render("GAME OVER", True, RED)
        score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
        restart_text = self.font.render("Press R to Restart or ESC to Quit", True, WHITE)

        self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, 200))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))
        self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 380))

    def handle_events(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.state == 'menu':
                    if event.key == pygame.K_SPACE:
                        self.state = 'playing'

                elif self.state == 'playing':
                    if event.key == pygame.K_SPACE:
                        bullet = self.player.shoot()
                        if bullet:
                            self.bullets.append(bullet)

                elif self.state == 'game_over':
                    if event.key == pygame.K_r:
                        self.reset_game()
                        self.state = 'playing'

        # Handle continuous key presses
        if self.state == 'playing':
            keys = pygame.key.get_pressed()
            self.player.rotating_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            self.player.rotating_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]

        return True

    def run(self) -> None:
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
