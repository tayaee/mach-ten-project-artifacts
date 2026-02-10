"""
Vector Missile Command Defense
Defend your cities from incoming ballistic missiles in this classic vector-style defense simulator.
"""

import pygame
import random
import math
from typing import List, Tuple, Optional


# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors (high contrast vector style)
COLOR_BLACK = (0, 0, 0)
COLOR_WHITE = (255, 255, 255)
COLOR_RED = (255, 50, 50)
COLOR_GREEN = (50, 255, 50)
COLOR_YELLOW = (255, 255, 0)
COLOR_CYAN = (0, 255, 255)
COLOR_ORANGE = (255, 165, 0)

# Game settings
CITY_COUNT = 6
CITY_WIDTH = 40
CITY_HEIGHT = 20
CITY_Y = SCREEN_HEIGHT - 30

BATTERY_COUNT = 3
BATTERY_WIDTH = 30
BATTERY_HEIGHT = 20
BATTERY_Y = SCREEN_HEIGHT - 15
AMMO_PER_BATTERY = 10

BLAST_RADIUS = 40
BLAST_DURATION = 90  # 1.5 seconds at 60 FPS

INTERCEPTOR_SPEED = 12

ENEMY_MISSILE_BASE_SPEED = 1.0
ENEMY_MISSILE_SPAWN_BASE = 120  # Frames between spawns

# Scoring
SCORE_INTERCEPT = 25
SCORE_CITY_BONUS = 100
SCORE_AMMO_BONUS = 5
SCORE_WAVE_BONUS = 500

WAVE_COUNT = 10


class Vector2:
    """Simple 2D vector class for position and velocity."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def distance_to(self, other: 'Vector2') -> float:
        return math.sqrt((self.x - other.x) ** 2 + (self.y - other.y) ** 2)

    def normalize(self) -> 'Vector2':
        length = math.sqrt(self.x ** 2 + self.y ** 2)
        if length == 0:
            return Vector2(0, 0)
        return Vector2(self.x / length, self.y / length)

    def __add__(self, other: 'Vector2') -> 'Vector2':
        return Vector2(self.x + other.x, self.y + other.y)

    def __mul__(self, scalar: float) -> 'Vector2':
        return Vector2(self.x * scalar, self.y * scalar)


class City:
    """A city that must be protected from enemy missiles."""

    def __init__(self, x: float):
        self.x = x
        self.y = CITY_Y
        self.width = CITY_WIDTH
        self.height = CITY_HEIGHT
        self.alive = True

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return

        # Draw city as a vector-style building shape
        # Main building block
        pygame.draw.rect(surface, COLOR_CYAN,
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, COLOR_WHITE,
                        (self.x, self.y, self.width, self.height), 2)

        # Building details (windows)
        window_size = 6
        for i in range(3):
            for j in range(2):
                wx = self.x + 8 + i * 12
                wy = self.y + 4 + j * 8
                pygame.draw.rect(surface, COLOR_WHITE, (wx, wy, window_size, window_size))

    def get_center(self) -> Vector2:
        return Vector2(self.x + self.width / 2, self.y + self.height / 2)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Battery:
    """A missile battery that can fire interceptor missiles."""

    def __init__(self, x: float, battery_id: int):
        self.x = x
        self.y = BATTERY_Y
        self.width = BATTERY_WIDTH
        self.height = BATTERY_HEIGHT
        self.id = battery_id
        self.ammo = AMMO_PER_BATTERY
        self.active = True

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            # Draw destroyed battery
            pygame.draw.line(surface, COLOR_RED,
                           (self.x, self.y + self.height),
                           (self.x + self.width, self.y), 2)
            pygame.draw.line(surface, COLOR_RED,
                           (self.x + self.width, self.y + self.height),
                           (self.x, self.y), 2)
            return

        # Draw battery as a vector-style turret
        # Base
        pygame.draw.rect(surface, COLOR_GREEN,
                        (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, COLOR_WHITE,
                        (self.x, self.y, self.width, self.height), 2)

        # Turret barrel
        barrel_width = 8
        barrel_height = 15
        barrel_x = self.x + (self.width - barrel_width) // 2
        barrel_y = self.y - barrel_height
        pygame.draw.rect(surface, COLOR_GREEN,
                        (barrel_x, barrel_y, barrel_width, barrel_height))
        pygame.draw.rect(surface, COLOR_WHITE,
                        (barrel_x, barrel_y, barrel_width, barrel_height), 2)

        # Battery number
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.id), True, COLOR_BLACK)
        text_rect = text.get_rect(center=(self.x + self.width // 2, self.y + self.height // 2))
        surface.blit(text, text_rect)

    def get_position(self) -> Vector2:
        return Vector2(self.x + self.width / 2, self.y)

    def has_ammo(self) -> bool:
        return self.active and self.ammo > 0

    def fire(self) -> bool:
        if self.has_ammo():
            self.ammo -= 1
            return True
        return False

    def refill(self) -> None:
        if self.active:
            self.ammo = AMMO_PER_BATTERY


class Explosion:
    """An explosion that destroys enemy missiles."""

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y
        self.radius = BLAST_RADIUS
        self.max_duration = BLAST_DURATION
        self.duration = self.max_duration
        self.active = True

    def update(self) -> None:
        self.duration -= 1
        if self.duration <= 0:
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return

        # Calculate expanding/contracting radius
        progress = self.duration / self.max_duration
        if progress > 0.5:
            # Expanding phase
            current_radius = int(self.radius * (1 - progress) * 2)
        else:
            # Contracting phase
            current_radius = int(self.radius * progress * 2)

        if current_radius < 1:
            current_radius = 1

        # Draw explosion as concentric circles
        alpha = int(255 * progress)
        center = (int(self.x), int(self.y))

        # Outer glow
        if current_radius > 5:
            glow_surface = pygame.Surface((current_radius * 2, current_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(glow_surface, (*COLOR_ORANGE, alpha // 2),
                             (current_radius, current_radius), current_radius)
            surface.blit(glow_surface, (center[0] - current_radius, center[1] - current_radius))

        # Main explosion
        pygame.draw.circle(surface, COLOR_YELLOW, center, current_radius)

        # Inner bright core
        core_radius = max(1, current_radius // 2)
        pygame.draw.circle(surface, COLOR_WHITE, center, core_radius)

        # Outer ring
        pygame.draw.circle(surface, COLOR_RED, center, current_radius, 2)

    def affects_position(self, pos: Vector2) -> bool:
        if not self.active:
            return False
        explosion_pos = Vector2(self.x, self.y)
        return explosion_pos.distance_to(pos) <= self.radius


class InterceptorMissile:
    """A player-fired interceptor missile that creates an explosion at its target."""

    def __init__(self, start_pos: Vector2, target_pos: Vector2):
        self.start_pos = start_pos
        self.current_pos = Vector2(start_pos.x, start_pos.y)
        self.target_pos = target_pos
        self.active = True

        direction = Vector2(target_pos.x - start_pos.x, target_pos.y - start_pos.y)
        self.velocity = direction.normalize() * INTERCEPTOR_SPEED

    def update(self) -> Optional['Explosion']:
        if not self.active:
            return None

        self.current_pos = self.current_pos + self.velocity

        # Check if reached target
        distance = self.current_pos.distance_to(self.target_pos)
        if distance < INTERCEPTOR_SPEED:
            self.active = False
            return Explosion(self.current_pos.x, self.current_pos.y)

        return None

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active:
            return

        # Draw missile trail
        start = (int(self.start_pos.x), int(self.start_pos.y))
        end = (int(self.current_pos.x), int(self.current_pos.y))
        pygame.draw.line(surface, COLOR_GREEN, start, end, 2)

        # Draw missile head
        pygame.draw.circle(surface, COLOR_WHITE, end, 3)


class EnemyMissile:
    """An incoming enemy missile targeting cities or batteries."""

    def __init__(self, speed_multiplier: float = 1.0):
        # Start from top of screen
        self.start_pos = Vector2(random.uniform(50, SCREEN_WIDTH - 50), 0)

        # Choose target (city or battery)
        targets = []
        for city in game_state['cities']:
            if city.alive:
                targets.append(city.get_center())
        for battery in game_state['batteries']:
            if battery.active:
                targets.append(battery.get_position())

        if not targets:
            self.target_pos = Vector2(SCREEN_WIDTH / 2, SCREEN_HEIGHT - 50)
        else:
            self.target_pos = random.choice(targets)

        self.current_pos = Vector2(self.start_pos.x, self.start_pos.y)
        self.speed = ENEMY_MISSILE_BASE_SPEED * speed_multiplier
        self.active = True
        self.trail_points: List[Tuple[float, float]] = []

        # Calculate velocity
        direction = Vector2(self.target_pos.x - self.start_pos.x,
                          self.target_pos.y - self.start_pos.y)
        self.velocity = direction.normalize() * self.speed

    def update(self) -> None:
        if not self.active:
            return

        # Store trail point
        self.trail_points.append((self.current_pos.x, self.current_pos.y))
        if len(self.trail_points) > 20:
            self.trail_points.pop(0)

        self.current_pos = self.current_pos + self.velocity

        # Check if reached target or off screen
        if (self.current_pos.y >= SCREEN_HEIGHT or
            self.current_pos.x < 0 or
            self.current_pos.x > SCREEN_WIDTH):
            self.active = False

    def draw(self, surface: pygame.Surface) -> None:
        if not self.active or len(self.trail_points) < 2:
            return

        # Draw trail
        if len(self.trail_points) >= 2:
            points = [(int(x), int(y)) for x, y in self.trail_points]
            pygame.draw.lines(surface, COLOR_RED, False, points, 2)

        # Draw missile head
        head = (int(self.current_pos.x), int(self.current_pos.y))
        pygame.draw.circle(surface, COLOR_WHITE, head, 4)
        pygame.draw.circle(surface, COLOR_RED, head, 2)

    def get_position(self) -> Vector2:
        return self.current_pos


# Global game state for enemy missile target selection
game_state = {'cities': [], 'batteries': []}


class Game:
    """Main game class managing all game state."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Missile Command Defense")
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_over = False
        self.wave_in_progress = False
        self.wave_number = 0
        self.wave_delay = 0

        # Crosshair position
        self.crosshair_pos = Vector2(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

        self.font_large = pygame.font.Font(None, 72)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)

        self.reset_game()

    def reset_game(self) -> None:
        """Reset game to initial state."""
        self.cities: List[City] = []
        self.batteries: List[Battery] = []
        self.enemy_missiles: List[EnemyMissile] = []
        self.interceptor_missiles: List[InterceptorMissile] = []
        self.explosions: List[Explosion] = []
        self.score = 0
        self.game_over = False
        self.wave_in_progress = False
        self.wave_number = 0
        self.wave_delay = 0
        self.wave_score = 0
        self.enemies_spawned = 0
        self.enemies_per_wave = 5

        self._initialize_entities()

    def _initialize_entities(self) -> None:
        """Initialize cities and batteries."""
        self.cities.clear()
        self.batteries.clear()

        # Create cities spaced evenly
        city_spacing = (SCREEN_WIDTH - CITY_COUNT * CITY_WIDTH) // (CITY_COUNT + 1)
        for i in range(CITY_COUNT):
            x = city_spacing + i * (CITY_WIDTH + city_spacing)
            self.cities.append(City(x))

        # Create 3 batteries
        battery_spacing = SCREEN_WIDTH // (BATTERY_COUNT + 1)
        for i in range(BATTERY_COUNT):
            x = battery_spacing * (i + 1) - BATTERY_WIDTH // 2
            self.batteries.append(Battery(x, i + 1))

        # Update global state
        game_state['cities'] = self.cities
        game_state['batteries'] = self.batteries

    def start_wave(self) -> None:
        """Start a new wave of enemy missiles."""
        self.wave_number += 1
        self.wave_in_progress = True
        self.enemies_spawned = 0
        self.enemies_per_wave = 5 + self.wave_number * 2
        self.wave_delay = 60  # Brief pause before wave starts
        self.wave_score = 0

        # Refill ammo
        for battery in self.batteries:
            battery.refill()

    def handle_input(self) -> None:
        """Handle keyboard and mouse input."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_r:
                    if self.game_over:
                        self.reset_game()
                # Fire interceptor with number keys
                elif not self.game_over and self.wave_in_progress:
                    if event.key == pygame.K_1:
                        self.fire_interceptor(0)
                    elif event.key == pygame.K_2:
                        self.fire_interceptor(1)
                    elif event.key == pygame.K_3:
                        self.fire_interceptor(2)
                # Start wave with space
                elif event.key == pygame.K_SPACE:
                    if not self.wave_in_progress and not self.game_over:
                        if self.get_alive_city_count() > 0:
                            self.start_wave()
            elif event.type == pygame.MOUSEMOTION:
                # Update crosshair position
                self.crosshair_pos = Vector2(event.pos[0], event.pos[1])
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Fire with left click from nearest battery with ammo
                if not self.game_over and self.wave_in_progress:
                    if event.button == 1:  # Left click
                        self.fire_from_nearest_battery()

        # Keyboard continuous input
        keys = pygame.key.get_pressed()
        crosshair_speed = 8
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.crosshair_pos.x -= crosshair_speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.crosshair_pos.x += crosshair_speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.crosshair_pos.y -= crosshair_speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.crosshair_pos.y += crosshair_speed

        # Clamp crosshair to screen
        self.crosshair_pos.x = max(0, min(SCREEN_WIDTH, self.crosshair_pos.x))
        self.crosshair_pos.y = max(0, min(SCREEN_HEIGHT, self.crosshair_pos.y))

    def fire_interceptor(self, battery_index: int) -> None:
        """Fire an interceptor from the specified battery."""
        if battery_index >= len(self.batteries):
            return

        battery = self.batteries[battery_index]
        if not battery.has_ammo():
            return

        if battery.fire():
            start_pos = battery.get_position()
            target_pos = Vector2(self.crosshair_pos.x, self.crosshair_pos.y)
            interceptor = InterceptorMissile(start_pos, target_pos)
            self.interceptor_missiles.append(interceptor)

    def fire_from_nearest_battery(self) -> None:
        """Fire from the battery with ammo that's closest to the crosshair x position."""
        best_battery = None
        best_distance = float('inf')

        for battery in self.batteries:
            if battery.has_ammo():
                distance = abs(battery.get_position().x - self.crosshair_pos.x)
                if distance < best_distance:
                    best_distance = distance
                    best_battery = battery

        if best_battery:
            for i, battery in enumerate(self.batteries):
                if battery == best_battery:
                    self.fire_interceptor(i)
                    break

    def update(self) -> None:
        """Update game state."""
        if self.game_over:
            return

        # Check for game over
        if self.get_alive_city_count() == 0:
            self.game_over = True
            self.wave_in_progress = False
            return

        # Wave management
        if self.wave_in_progress:
            if self.wave_delay > 0:
                self.wave_delay -= 1
            elif self.enemies_spawned < self.enemies_per_wave:
                # Spawn enemies with decreasing interval
                spawn_interval = max(30, ENEMY_MISSILE_SPAWN_BASE - self.wave_number * 5)
                if self.enemies_spawned == 0 or random.randint(0, spawn_interval) < 10:
                    speed_multiplier = 1.0 + self.wave_number * 0.1
                    self.enemy_missiles.append(EnemyMissile(speed_multiplier))
                    self.enemies_spawned += 1
            elif len(self.enemy_missiles) == 0:
                # Wave complete
                self.end_wave()

        # Update interceptors
        for interceptor in self.interceptor_missiles[:]:
            explosion = interceptor.update()
            if explosion:
                self.explosions.append(explosion)
            if not interceptor.active:
                self.interceptor_missiles.remove(interceptor)

        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if not explosion.active:
                self.explosions.remove(explosion)

        # Update enemy missiles
        for enemy in self.enemy_missiles[:]:
            enemy.update()

            if not enemy.active:
                # Check if it hit something
                enemy_pos = enemy.get_position()
                hit_city = False
                hit_battery = False

                # Check city collisions
                for city in self.cities:
                    if city.alive and city.get_rect().collidepoint(enemy_pos.x, enemy_pos.y):
                        city.alive = False
                        hit_city = True
                        self.explosions.append(Explosion(city.x + city.width / 2,
                                                         city.y + city.height / 2))
                        break

                # Check battery collisions
                if not hit_city:
                    for battery in self.batteries:
                        if battery.active:
                            bat_rect = pygame.Rect(battery.x, battery.y - 15,
                                                 battery.width, battery.height + 15)
                            if bat_rect.collidepoint(enemy_pos.x, enemy_pos.y):
                                battery.active = False
                                hit_battery = True
                                self.explosions.append(Explosion(battery.x + battery.width / 2,
                                                                 battery.y))
                                break

                self.enemy_missiles.remove(enemy)
                continue

            # Check explosion collisions
            for explosion in self.explosions:
                if explosion.active and explosion.affects_position(enemy.get_position()):
                    self.score += SCORE_INTERCEPT
                    self.wave_score += SCORE_INTERCEPT
                    self.enemy_missiles.remove(enemy)
                    break

    def end_wave(self) -> None:
        """End current wave and calculate bonuses."""
        self.wave_in_progress = False

        # City bonus
        alive_cities = self.get_alive_city_count()
        self.score += alive_cities * SCORE_CITY_BONUS

        # Ammo bonus
        total_ammo = sum(b.ammo for b in self.batteries if b.active)
        self.score += total_ammo * SCORE_AMMO_BONUS

        # Wave completion bonus
        self.score += SCORE_WAVE_BONUS

        # Check if game should end
        if alive_cities == 0 or self.wave_number >= WAVE_COUNT:
            self.game_over = True

    def get_alive_city_count(self) -> int:
        """Get number of cities still alive."""
        return sum(1 for city in self.cities if city.alive)

    def draw(self) -> None:
        """Draw all game elements."""
        self.screen.fill(COLOR_BLACK)

        # Draw cities
        for city in self.cities:
            city.draw(self.screen)

        # Draw batteries
        for battery in self.batteries:
            battery.draw(self.screen)

        # Draw enemy missiles
        for enemy in self.enemy_missiles:
            enemy.draw(self.screen)

        # Draw interceptors
        for interceptor in self.interceptor_missiles:
            interceptor.draw(self.screen)

        # Draw explosions
        for explosion in self.explosions:
            explosion.draw(self.screen)

        # Draw crosshair
        crosshair_x = int(self.crosshair_pos.x)
        crosshair_y = int(self.crosshair_pos.y)
        crosshair_size = 15
        pygame.draw.line(self.screen, COLOR_GREEN,
                        (crosshair_x - crosshair_size, crosshair_y),
                        (crosshair_x + crosshair_size, crosshair_y), 2)
        pygame.draw.line(self.screen, COLOR_GREEN,
                        (crosshair_x, crosshair_y - crosshair_size),
                        (crosshair_x, crosshair_y + crosshair_size), 2)
        pygame.draw.circle(self.screen, COLOR_GREEN,
                          (crosshair_x, crosshair_y), crosshair_size, 2)

        # Draw ground line
        pygame.draw.line(self.screen, COLOR_WHITE, (0, SCREEN_HEIGHT - 1),
                        (SCREEN_WIDTH, SCREEN_HEIGHT - 1), 2)

        # Draw UI
        score_text = self.font_small.render(f"SCORE: {self.score}", True, COLOR_WHITE)
        self.screen.blit(score_text, (10, 10))

        wave_text = self.font_small.render(f"WAVE: {self.wave_number}/{WAVE_COUNT}",
                                          True, COLOR_WHITE)
        self.screen.blit(wave_text, (10, 45))

        cities_text = self.font_small.render(f"CITIES: {self.get_alive_city_count()}",
                                            True, COLOR_CYAN)
        self.screen.blit(cities_text, (10, 80))

        # Draw ammo indicators
        for i, battery in enumerate(self.batteries):
            ammo_color = COLOR_GREEN if battery.ammo > 3 else COLOR_YELLOW if battery.ammo > 0 else COLOR_RED
            ammo_text = self.font_small.render(f"{battery.ammo}", True, ammo_color)
            self.screen.blit(ammo_text, (battery.x + 10, BATTERY_Y + 25))

        # Wave transition or game start
        if not self.wave_in_progress and not self.game_over:
            if self.wave_number == 0:
                title_text = self.font_medium.render("MISSILE COMMAND", True, COLOR_CYAN)
                title_rect = title_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
                self.screen.blit(title_text, title_rect)

                instruction_text = self.font_small.render(
                    "Press SPACE to Start | Aim with Mouse, Click or 1/2/3 to Fire",
                    True, COLOR_YELLOW)
                instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                                   SCREEN_HEIGHT // 2))
                self.screen.blit(instruction_text, instruction_rect)

                controls_text = self.font_small.render(
                    "Keys 1, 2, 3 fire from Left, Middle, Right batteries",
                    True, COLOR_WHITE)
                controls_rect = controls_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                             SCREEN_HEIGHT // 2 + 40))
                self.screen.blit(controls_text, controls_rect)
            elif self.get_alive_city_count() > 0:
                wave_complete_text = self.font_medium.render(
                    f"WAVE {self.wave_number} COMPLETE!", True, COLOR_GREEN)
                wave_rect = wave_complete_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                               SCREEN_HEIGHT // 2 - 40))
                self.screen.blit(wave_complete_text, wave_rect)

                bonus_text = self.font_small.render(
                    f"Wave Bonus: +{SCORE_WAVE_BONUS}",
                    True, COLOR_YELLOW)
                bonus_rect = bonus_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                        SCREEN_HEIGHT // 2 + 10))
                self.screen.blit(bonus_text, bonus_rect)

                continue_text = self.font_small.render("Press SPACE for Next Wave",
                                                     True, COLOR_WHITE)
                continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                             SCREEN_HEIGHT // 2 + 50))
                self.screen.blit(continue_text, continue_rect)

        if self.game_over:
            # Game over screen
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(COLOR_BLACK)
            self.screen.blit(overlay, (0, 0))

            if self.get_alive_city_count() == 0:
                result_text = "ALL CITIES DESTROYED"
                result_color = COLOR_RED
            else:
                result_text = "DEFENSE SUCCESSFUL!"
                result_color = COLOR_GREEN

            game_over_text = self.font_large.render("GAME OVER", True, COLOR_RED)
            result_msg_text = self.font_medium.render(result_text, True, result_color)
            score_text = self.font_medium.render(f"Final Score: {self.score}", True, COLOR_WHITE)
            restart_text = self.font_small.render("Press R to Restart or ESC to Quit",
                                                True, COLOR_YELLOW)

            game_over_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                           SCREEN_HEIGHT // 2 - 80))
            result_rect = result_msg_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                         SCREEN_HEIGHT // 2 - 20))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2,
                                                       SCREEN_HEIGHT // 2 + 80))

            self.screen.blit(game_over_text, game_over_rect)
            self.screen.blit(result_msg_text, result_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    """Entry point for the game."""
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
