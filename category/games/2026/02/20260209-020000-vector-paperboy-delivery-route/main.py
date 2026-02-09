import pygame
import sys
import random
from typing import List, Tuple, Optional
from enum import Enum

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
SKY_BLUE = (135, 206, 235)
GRASS_GREEN = (34, 139, 34)
ROAD_GRAY = (80, 80, 80)
SIDEWALK_COLOR = (180, 180, 180)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (200, 50, 50)
YELLOW = (255, 215, 0)
BROWN = (139, 69, 19)
NEWSPAPER_COLOR = (240, 240, 230)
MAILBOX_RED = (180, 50, 50)
MAILBOX_BLUE = (50, 100, 180)
PORCH_COLOR = (160, 140, 120)
CAR_COLORS = [(200, 50, 50), (50, 100, 200), (50, 150, 50), (200, 200, 50), (150, 50, 150)]
PEDESTRIAN_COLORS = [(255, 200, 180), (200, 150, 100), (180, 100, 80), (100, 150, 200)]

# Game constants
ROAD_WIDTH = 200
SIDEWALK_WIDTH = 60
HOUSE_WIDTH = 100
HOUSE_DEPTH = 80
LANE_MARKING_INTERVAL = 60
SCROLL_SPEED_BASE = 3
MAX_SCROLL_SPEED = 8
MIN_SCROLL_SPEED = 1
ACCELERATION = 0.1
DECELERATION = 0.15

# Player
PLAYER_WIDTH = 30
PLAYER_HEIGHT = 50
PLAYER_MAX_OFFSET = ROAD_WIDTH // 2 - PLAYER_WIDTH // 2 - 10
PLAYER_MOVE_SPEED = 5
MAX_NEWSPAPERS = 20

# Scoring
MAILBOX_HIT_SCORE = 100
PORCH_LAND_SCORE = 50
WINDOW_BREAK_PENALTY = -50
LIFE_LOST_PENALTY = -200

# Houses
SUBSCRIBER_HOUSE = "subscriber"
NON_SUBSCRIBER_HOUSE = "non_subscriber"

# Obstacles
class ObstacleType(Enum):
    CAR = "car"
    PEDESTRIAN = "pedestrian"
    LAWNMOWER = "lawnmower"
    GRATE = "grate"

class GameState(Enum):
    MENU = 0
    PLAYING = 1
    GAME_OVER = 2
    LEVEL_COMPLETE = 3

class Newspaper:
    def __init__(self, x: float, y: float, velocity_x: float, velocity_y: float):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.width = 12
        self.height = 8
        self.rotation = 0
        self.rotation_speed = random.uniform(-5, 5)
        self.gravity = 0.15
        self.active = True
        self.landed = False
        self.bounce_count = 0
        self.max_bounces = 2

    def update(self):
        if not self.landed:
            self.velocity_y += self.gravity
            self.x += self.velocity_x
            self.y += self.velocity_y
            self.rotation += self.rotation_speed

            # Check if landed (reached house area)
            if self.y < SCREEN_HEIGHT * 0.35:
                self.landed = True
                self.active = False

            # Check bounds
            if self.x < 0 or self.x > SCREEN_WIDTH:
                self.active = False

    def draw(self, surface: pygame.Surface):
        if self.active or self.landed:
            # Draw newspaper as a rectangle with rotation
            newspaper_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            pygame.draw.rect(newspaper_surf, NEWSPAPER_COLOR, (0, 0, self.width, self.height))
            pygame.draw.rect(newspaper_surf, BLACK, (0, 0, self.width, self.height), 1)

            # Rotate
            rotated_surf = pygame.transform.rotate(newspaper_surf, self.rotation)
            rect = rotated_surf.get_rect(center=(int(self.x), int(self.y)))
            surface.blit(rotated_surf, rect)

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.width // 2), int(self.y - self.height // 2),
                          self.width, self.height)

class House:
    def __init__(self, x: float, house_type: str):
        self.x = x
        self.y = 100
        self.width = HOUSE_WIDTH
        self.height = HOUSE_DEPTH
        self.house_type = house_type

        # Subscriber houses are bright, non-subscribers are dark
        if house_type == SUBSCRIBER_HOUSE:
            self.wall_color = (255, 230, 180)
            self.roof_color = (200, 50, 50)
            self.has_mailbox = True
            self.is_subscriber = True
        else:
            self.wall_color = (100, 90, 80)
            self.roof_color = (80, 40, 40)
            self.has_mailbox = random.choice([True, False])
            self.is_subscriber = False

        # Porch and mailbox positions
        self.porch_rect = pygame.Rect(
            int(self.x + 10), int(self.y + self.height - 30),
            self.width - 20, 30
        )

        # Mailbox on left side of house
        self.mailbox_rect = pygame.Rect(
            int(self.x - 20), int(self.y + self.height - 25),
            15, 25
        )

        # Windows
        self.windows = []
        window_size = 18
        for row in range(2):
            for col in range(2):
                wx = self.x + 15 + col * (window_size + 15)
                wy = self.y + 15 + row * (window_size + 15)
                self.windows.append(pygame.Rect(int(wx), int(wy), window_size, window_size))

        self.delivered = False
        self.window_hit = False
        self.mailbox_hit = False

    def draw(self, surface: pygame.Surface):
        # Draw house body
        pygame.draw.rect(surface, self.wall_color,
                        (int(self.x), int(self.y), self.width, self.height))

        # Draw roof
        roof_points = [
            (int(self.x - 5), int(self.y)),
            (int(self.x + self.width // 2), int(self.y - 30)),
            (int(self.x + self.width + 5), int(self.y))
        ]
        pygame.draw.polygon(surface, self.roof_color, roof_points)

        # Draw windows
        for window in self.windows:
            if self.window_hit:
                # Draw broken window
                pygame.draw.rect(surface, (50, 50, 50), window)
                # Draw cracks
                pygame.draw.line(surface, (100, 100, 100),
                               window.topleft, window.bottomright, 2)
                pygame.draw.line(surface, (100, 100, 100),
                               window.bottomleft, window.topright, 2)
            else:
                # Draw intact window
                pygame.draw.rect(surface, (150, 200, 255), window)
                pygame.draw.rect(surface, (100, 150, 200), window, 2)

        # Draw porch
        pygame.draw.rect(surface, PORCH_COLOR, self.porch_rect)

        # Draw mailbox
        if self.has_mailbox:
            mailbox_color = MAILBOX_BLUE if not self.mailbox_hit else (100, 100, 100)
            pygame.draw.rect(surface, mailbox_color, self.mailbox_rect)
            # Mailbox flag
            flag_color = RED if not self.mailbox_hit else (80, 80, 80)
            pygame.draw.polygon(surface, flag_color, [
                (self.mailbox_rect.right, self.mailbox_rect.top + 5),
                (self.mailbox_rect.right + 10, self.mailbox_rect.top + 10),
                (self.mailbox_rect.right, self.mailbox_rect.top + 15)
            ])

    def check_newspaper_collision(self, newspaper: Newspaper) -> Optional[str]:
        """Check if newspaper hit anything and return what it hit."""
        paper_rect = newspaper.get_rect()

        # Check mailbox hit
        if self.has_mailbox and not self.mailbox_hit:
            if paper_rect.colliderect(self.mailbox_rect):
                self.mailbox_hit = True
                return "mailbox"

        # Check porch landing
        if paper_rect.colliderect(self.porch_rect):
            self.delivered = True
            return "porch"

        # Check window hit
        for window in self.windows:
            if paper_rect.colliderect(window):
                self.window_hit = True
                return "window"

        return None

class Obstacle:
    def __init__(self, obstacle_type: ObstacleType, x: float, lane: str):
        self.type = obstacle_type
        self.x = x
        self.y = SCREEN_HEIGHT + 50
        self.lane = lane  # "left" or "right" on road
        self.width = 40
        self.height = 40
        self.active = True

        if obstacle_type == ObstacleType.CAR:
            self.width = 50
            self.height = 80
            self.color = random.choice(CAR_COLORS)
        elif obstacle_type == ObstacleType.PEDESTRIAN:
            self.width = 25
            self.height = 45
            self.color = random.choice(PEDESTRIAN_COLORS)
            self.move_offset = 0
            self.move_direction = random.choice([-1, 1])
        elif obstacle_type == ObstacleType.LAWNMOWER:
            self.width = 45
            self.height = 35
            self.color = (150, 100, 50)
        elif obstacle_type == ObstacleType.GRATE:
            self.width = 60
            self.height = 60
            self.color = (50, 50, 50)

    def update(self, scroll_speed: float):
        self.y -= scroll_speed

        # Pedestrians move sideways
        if self.type == ObstacleType.PEDESTRIAN:
            self.move_offset += self.move_direction * 0.5
            if abs(self.move_offset) > 15:
                self.move_direction *= -1

        if self.y < -100:
            self.active = False

    def draw(self, surface: pygame.Surface):
        draw_x = int(self.x + (self.move_offset if self.type == ObstacleType.PEDESTRIAN else 0))

        if self.type == ObstacleType.CAR:
            # Draw car body
            pygame.draw.rect(surface, self.color, (draw_x, int(self.y), self.width, self.height), border_radius=5)
            # Windows
            pygame.draw.rect(surface, (150, 200, 255),
                           (draw_x + 5, int(self.y) + 10, self.width - 10, 20))
            # Wheels
            pygame.draw.circle(surface, BLACK, (draw_x + 10, int(self.y) + self.height - 5), 8)
            pygame.draw.circle(surface, BLACK, (draw_x + self.width - 10, int(self.y) + self.height - 5), 8)

        elif self.type == ObstacleType.PEDESTRIAN:
            # Draw pedestrian body
            pygame.draw.circle(surface, self.color, (draw_x + self.width // 2, int(self.y)), 10)  # Head
            pygame.draw.rect(surface, self.color, (draw_x + 8, int(self.y) + 10, 10, 20))  # Body
            pygame.draw.line(surface, self.color, (draw_x + 10, int(self.y) + 30),
                           (draw_x + 5, int(self.y) + 45), 3)  # Left leg
            pygame.draw.line(surface, self.color, (draw_x + 15, int(self.y) + 30),
                           (draw_x + 20, int(self.y) + 45), 3)  # Right leg

        elif self.type == ObstacleType.LAWNMOWER:
            # Draw lawnmower body
            pygame.draw.rect(surface, self.color, (draw_x, int(self.y), self.width, self.height), border_radius=3)
            # Wheels
            pygame.draw.circle(surface, BLACK, (draw_x + 10, int(self.y) + self.height - 5), 8)
            pygame.draw.circle(surface, BLACK, (draw_x + self.width - 10, int(self.y) + self.height - 5), 8)
            # Handle
            pygame.draw.line(surface, (100, 100, 100), (draw_x + self.width // 2, int(self.y)),
                           (draw_x + self.width // 2, int(self.y) - 15), 3)

        elif self.type == ObstacleType.GRATE:
            # Draw street grate
            pygame.draw.rect(surface, self.color, (draw_x, int(self.y), self.width, self.height))
            # Draw grate lines
            for i in range(0, self.width, 8):
                pygame.draw.line(surface, (30, 30, 30),
                               (draw_x + i, int(self.y)),
                               (draw_x + i, int(self.y) + self.height), 2)

    def get_rect(self) -> pygame.Rect:
        offset = self.move_offset if self.type == ObstacleType.PEDESTRIAN else 0
        return pygame.Rect(int(self.x + offset), int(self.y), self.width, self.height)

class Player:
    def __init__(self):
        self.x = SCREEN_WIDTH // 2
        self.y_offset = 0
        self.y = SCREEN_HEIGHT - 150
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.speed = 0
        self.target_x = SCREEN_WIDTH // 2
        self.lane_offset = 0

    def update(self):
        # Smooth movement towards target position
        diff = self.target_x - self.x
        self.x += diff * 0.15

        # Constrain to road
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2 + PLAYER_WIDTH // 2
        road_right = (SCREEN_WIDTH + ROAD_WIDTH) // 2 - PLAYER_WIDTH // 2
        self.x = max(road_left, min(road_right, self.x))

    def move_left(self):
        self.target_x -= PLAYER_MOVE_SPEED

    def move_right(self):
        self.target_x += PLAYER_MOVE_SPEED

    def get_rect(self) -> pygame.Rect:
        return pygame.Rect(int(self.x - self.width // 2), int(self.y - self.height // 2),
                          self.width, self.height)

    def get_throwing_position(self) -> Tuple[float, float]:
        """Return the position where newspaper is thrown from."""
        return (self.x - self.width // 2, self.y - self.height // 3)

    def draw(self, surface: pygame.Surface):
        # Draw bicycle
        bike_x = int(self.x)
        bike_y = int(self.y)

        # Wheels
        pygame.draw.circle(surface, BLACK, (bike_x - 12, bike_y + 15), 10, 3)
        pygame.draw.circle(surface, BLACK, (bike_x + 12, bike_y + 15), 10, 3)

        # Frame
        pygame.draw.line(surface, RED, (bike_x - 12, bike_y + 15), (bike_x, bike_y), 3)
        pygame.draw.line(surface, RED, (bike_x + 12, bike_y + 15), (bike_x, bike_y), 3)
        pygame.draw.line(surface, RED, (bike_x, bike_y), (bike_x, bike_y - 10), 3)
        pygame.draw.line(surface, RED, (bike_x, bike_y), (bike_x + 5, bike_y + 5), 3)

        # Handlebars
        pygame.draw.line(surface, BLACK, (bike_x - 5, bike_y - 10), (bike_x + 5, bike_y - 10), 3)

        # Rider
        # Body
        pygame.draw.ellipse(surface, (100, 150, 200),
                          (bike_x - 8, bike_y - 25, 16, 20))
        # Head
        pygame.draw.circle(surface, (255, 220, 180), (bike_x, bike_y - 35), 8)
        # Hat
        pygame.draw.polygon(surface, WHITE, [
            (bike_x - 8, bike_y - 38),
            (bike_x + 8, bike_y - 38),
            (bike_x, bike_y - 50)
        ])
        # Arms
        pygame.draw.line(surface, (255, 220, 180),
                        (bike_x - 5, bike_y - 20),
                        (bike_x - 5, bike_y - 10), 4)
        pygame.draw.line(surface, (255, 220, 180),
                        (bike_x + 5, bike_y - 20),
                        (bike_x + 5, bike_y - 10), 4)
        # Legs
        pygame.draw.line(surface, (50, 50, 150),
                        (bike_x - 3, bike_y - 5),
                        (bike_x - 8, bike_y + 10), 5)
        pygame.draw.line(surface, (50, 50, 150),
                        (bike_x + 3, bike_y - 5),
                        (bike_x + 8, bike_y + 10), 5)

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Paperboy Delivery Route")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 72)

        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.newspapers: List[Newspaper] = []
        self.houses: List[House] = []
        self.obstacles: List[Obstacle] = []

        self.scroll_speed = SCROLL_SPEED_BASE
        self.scroll_offset = 0
        self.lane_marking_offset = 0

        self.score = 0
        self.lives = 3
        self.newspaper_ammo = MAX_NEWSPAPERS
        self.subscribers_delivered = 0
        self.missed_deliveries = 0
        self.streak_multiplier = 1

        self.game_state = GameState.MENU
        self.level_complete = False
        self.level_length = 2000  # Distance to complete level
        self.distance_traveled = 0
        self.house_spawn_timer = 0
        self.obstacle_spawn_timer = 0

        # Generate initial houses
        self._generate_initial_houses()

    def _generate_initial_houses(self):
        """Generate initial houses on both sides of the road."""
        house_y = 100
        while house_y < SCREEN_HEIGHT + 200:
            self._spawn_house_row(house_y)
            house_y += HOUSE_DEPTH + 60

    def _spawn_house_row(self, y_position: float):
        """Spawn a row of houses on both sides of the road."""
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        road_right = (SCREEN_WIDTH + ROAD_WIDTH) // 2

        # Left side houses
        for i in range(3):
            x = road_left - SIDEWALK_WIDTH - HOUSE_WIDTH - i * (HOUSE_WIDTH + 10)
            house_type = SUBSCRIBER_HOUSE if random.random() > 0.4 else NON_SUBSCRIBER_HOUSE
            self.houses.append(House(x, house_type))

        # Right side houses
        for i in range(3):
            x = road_right + SIDEWALK_WIDTH + i * (HOUSE_WIDTH + 10)
            house_type = SUBSCRIBER_HOUSE if random.random() > 0.4 else NON_SUBSCRIBER_HOUSE
            self.houses.append(House(x, house_type))

    def _spawn_obstacle(self):
        """Spawn a random obstacle on the road."""
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        road_right = (SCREEN_WIDTH + ROAD_WIDTH) // 2

        obstacle_type = random.choice(list(ObstacleType))
        lane = random.choice(["left", "right"])

        if lane == "left":
            x = road_left + ROAD_WIDTH // 4
        else:
            x = road_right - ROAD_WIDTH // 4

        # Add some randomness to position
        x += random.uniform(-20, 20)

        self.obstacles.append(Obstacle(obstacle_type, x, lane))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                elif self.game_state == GameState.MENU:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.game_state = GameState.PLAYING

                elif self.game_state == GameState.PLAYING:
                    if event.key == pygame.K_SPACE:
                        self._throw_newspaper()
                    elif event.key == pygame.K_UP:
                        self.scroll_speed = min(MAX_SCROLL_SPEED, self.scroll_speed + ACCELERATION * 10)
                    elif event.key == pygame.K_DOWN:
                        self.scroll_speed = max(MIN_SCROLL_SPEED, self.scroll_speed - DECELERATION * 10)

                elif self.game_state == GameState.GAME_OVER:
                    if event.key == pygame.K_r or event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.game_state = GameState.PLAYING

                elif self.game_state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.game_state = GameState.PLAYING

        # Handle continuous key presses
        if self.game_state == GameState.PLAYING:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_RIGHT]:
                self.player.move_right()
            if keys[pygame.K_UP]:
                self.scroll_speed = min(MAX_SCROLL_SPEED, self.scroll_speed + ACCELERATION)
            if keys[pygame.K_DOWN]:
                self.scroll_speed = max(MIN_SCROLL_SPEED, self.scroll_speed - DECELERATION)

        return True

    def _throw_newspaper(self):
        """Throw a newspaper to the left."""
        if self.newspaper_ammo > 0:
            throw_x, throw_y = self.player.get_throwing_position()
            # Throw towards left side houses
            velocity_x = -4 - (self.scroll_speed * 0.2)
            velocity_y = -3 - (self.scroll_speed * 0.1)
            self.newspapers.append(Newspaper(throw_x, throw_y, velocity_x, velocity_y))
            self.newspaper_ammo -= 1

    def update(self):
        if self.game_state != GameState.PLAYING:
            return

        self.player.update()
        self.distance_traveled += self.scroll_speed

        # Update scroll offset for houses and obstacles
        self.scroll_offset += self.scroll_speed
        self.lane_marking_offset = (self.lane_marking_offset + self.scroll_speed) % LANE_MARKING_INTERVAL

        # Update houses (scroll down)
        for house in self.houses[:]:
            house.y += self.scroll_speed
            if house.y > SCREEN_HEIGHT + 100:
                self.houses.remove(house)
                # Check if subscriber house was delivered to
                if house.is_subscriber and not house.delivered:
                    self.missed_deliveries += 1
                    self.streak_multiplier = 1

        # Spawn new houses
        self.house_spawn_timer += self.scroll_speed
        if self.house_spawn_timer > HOUSE_DEPTH + 60:
            self.house_spawn_timer = 0
            self._spawn_house_row(-50)

        # Update obstacles
        for obstacle in self.obstacles[:]:
            obstacle.update(self.scroll_speed)
            if not obstacle.active:
                self.obstacles.remove(obstacle)

        # Spawn obstacles
        self.obstacle_spawn_timer += self.scroll_speed
        if self.obstacle_spawn_timer > 150:
            self.obstacle_spawn_timer = 0
            if len(self.obstacles) < 5:
                self._spawn_obstacle()

        # Update newspapers
        for newspaper in self.newspapers[:]:
            newspaper.update()
            if not newspaper.active:
                self.newspapers.remove(newspaper)
                continue

            # Check collision with houses
            paper_rect = newspaper.get_rect()
            for house in self.houses:
                result = house.check_newspaper_collision(newspaper)
                if result == "mailbox":
                    if house.is_subscriber:
                        self.score += MAILBOX_HIT_SCORE * self.streak_multiplier
                        self.subscribers_delivered += 1
                        self.streak_multiplier = min(5, self.streak_multiplier + 1)
                    else:
                        self.score += WINDOW_BREAK_PENALTY
                elif result == "porch":
                    if house.is_subscriber:
                        self.score += PORCH_LAND_SCORE * self.streak_multiplier
                        self.subscribers_delivered += 1
                        self.streak_multiplier = min(5, self.streak_multiplier + 1)
                    else:
                        self.score += WINDOW_BREAK_PENALTY
                elif result == "window":
                    if house.is_subscriber:
                        self.score += WINDOW_BREAK_PENALTY * 2
                        self.streak_multiplier = 1
                    else:
                        self.score += WINDOW_BREAK_PENALTY

                if result:
                    newspaper.active = False
                    break

        # Check player collision with obstacles
        player_rect = self.player.get_rect()
        for obstacle in self.obstacles[:]:
            if player_rect.colliderect(obstacle.get_rect()):
                # Crashed!
                self.lives -= 1
                self.score += LIFE_LOST_PENALTY
                self.obstacles.remove(obstacle)
                self.streak_multiplier = 1

                if self.lives <= 0:
                    self.game_state = GameState.GAME_OVER
                else:
                    # Brief invincibility - remove nearby obstacles
                    self.obstacles = [o for o in self.obstacles if o.y > self.player.y + 100]

        # Check level completion
        if self.distance_traveled >= self.level_length:
            self.game_state = GameState.LEVEL_COMPLETE

        # Refill newspaper ammo periodically
        if self.distance_traveled % 500 < self.scroll_speed:
            self.newspaper_ammo = min(MAX_NEWSPAPERS, self.newspaper_ammo + 5)

    def draw(self):
        # Draw sky
        self.screen.fill(SKY_BLUE)

        # Draw grass areas
        road_left = (SCREEN_WIDTH - ROAD_WIDTH) // 2
        road_right = (SCREEN_WIDTH + ROAD_WIDTH) // 2

        pygame.draw.rect(self.screen, GRASS_GREEN, (0, 0, road_left, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, GRASS_GREEN, (road_right, 0, SCREEN_WIDTH - road_right, SCREEN_HEIGHT))

        # Draw sidewalks
        pygame.draw.rect(self.screen, SIDEWALK_COLOR,
                        (road_left - SIDEWALK_WIDTH, 0, SIDEWALK_WIDTH, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, SIDEWALK_COLOR,
                        (road_right, 0, SIDEWALK_WIDTH, SCREEN_HEIGHT))

        # Draw road
        pygame.draw.rect(self.screen, ROAD_GRAY, (road_left, 0, ROAD_WIDTH, SCREEN_HEIGHT))

        # Draw lane markings
        for y in range(-LANE_MARKING_INTERVAL, SCREEN_HEIGHT, LANE_MARKING_INTERVAL):
            mark_y = y + self.lane_marking_offset
            if 0 <= mark_y < SCREEN_HEIGHT:
                pygame.draw.line(self.screen, YELLOW,
                               (SCREEN_WIDTH // 2, mark_y),
                               (SCREEN_WIDTH // 2, mark_y + 30), 3)

        # Draw houses
        for house in self.houses:
            house.draw(self.screen)

        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)

        # Draw newspapers
        for newspaper in self.newspapers:
            newspaper.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw UI
        score_text = self.font.render(f"Score: {self.score}", True, BLACK)
        lives_text = self.font.render(f"Lives: {self.lives}", True, RED)
        ammo_text = self.font.render(f"Papers: {self.newspaper_ammo}", True, BLACK)
        streak_text = self.font.render(f"Streak: x{self.streak_multiplier}", True, YELLOW)
        speed_text = self.font.render(f"Speed: {self.scroll_speed:.1f}", True, BLACK)
        progress_text = self.font.render(f"Progress: {int(self.distance_traveled)}/{self.level_length}", True, BLACK)

        # Draw UI background
        pygame.draw.rect(self.screen, (255, 255, 255, 200), (5, 5, 200, 140), border_radius=5)

        self.screen.blit(score_text, (10, 10))
        self.screen.blit(lives_text, (10, 40))
        self.screen.blit(ammo_text, (10, 70))
        self.screen.blit(streak_text, (10, 100))
        self.screen.blit(speed_text, (10, 130))

        # Progress on right side
        progress_rect = progress_text.get_rect(topright=(SCREEN_WIDTH - 10, 10))
        self.screen.blit(progress_text, progress_rect)

        # Draw menu screen
        if self.game_state == GameState.MENU:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            title = self.big_font.render("PAPERBOY", True, WHITE)
            subtitle = self.font.render("Delivery Route", True, YELLOW)
            instructions = [
                "Arrow Keys: Steer and control speed",
                "Spacebar: Throw newspaper",
                "Deliver to subscriber houses (bright colors)",
                "Avoid obstacles and non-subscribers!",
                "",
                "Press SPACE to start"
            ]

            title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            subtitle_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3 + 60))

            self.screen.blit(title, title_rect)
            self.screen.blit(subtitle, subtitle_rect)

            y = SCREEN_HEIGHT // 2 + 50
            for line in instructions:
                text = self.font.render(line, True, WHITE)
                text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
                self.screen.blit(text, text_rect)
                y += 35

        # Draw game over screen
        elif self.game_state == GameState.GAME_OVER:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            text = self.big_font.render("GAME OVER", True, RED)
            score_text = self.font.render(f"Final Score: {self.score}", True, WHITE)
            delivered_text = self.font.render(f"Deliveries: {self.subscribers_delivered}", True, WHITE)
            restart_text = self.font.render("Press R or ENTER to restart", True, YELLOW)

            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            delivered_rect = delivered_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

            self.screen.blit(text, text_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(delivered_text, delivered_rect)
            self.screen.blit(restart_text, restart_rect)

        # Draw level complete screen
        elif self.game_state == GameState.LEVEL_COMPLETE:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            text = self.big_font.render("ROUND COMPLETE!", True, YELLOW)
            score_text = self.font.render(f"Score: {self.score}", True, WHITE)
            delivered_text = self.font.render(f"Deliveries: {self.subscribers_delivered}", True, WHITE)
            continue_text = self.font.render("Press SPACE or ENTER for next round", True, WHITE)

            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
            score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            delivered_rect = delivered_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))
            continue_rect = continue_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))

            self.screen.blit(text, text_rect)
            self.screen.blit(score_text, score_rect)
            self.screen.blit(delivered_text, delivered_rect)
            self.screen.blit(continue_text, continue_rect)

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

def main():
    game = Game()
    game.run()

if __name__ == "__main__":
    main()
