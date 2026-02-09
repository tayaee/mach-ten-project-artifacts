"""
Vector Elevator Action Stealth
A 2D side-scrolling stealth action game inspired by Elevator Action.
Infiltrate a high-security building using elevators and tactical movement.
"""

import pygame
import sys
import random
from enum import Enum

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BG = (25, 25, 35)
COLOR_FLOOR = (60, 60, 70)
COLOR_FLOOR_EDGE = (80, 80, 90)
COLOR_WALL = (40, 40, 50)
COLOR_DOOR_RED = (180, 50, 50)
COLOR_DOOR_BLUE = (50, 100, 180)
COLOR_DOOR_OPENED = (80, 80, 80)
COLOR_PLAYER = (50, 200, 50)
COLOR_PLAYER_STEALTH = (30, 120, 30)
COLOR_ENEMY = (200, 80, 80)
COLOR_ENEMY_VISION = (255, 200, 100, 30)
COLOR_BULLET = (255, 255, 100)
COLOR_LIGHT = (255, 240, 180)
COLOR_LIGHT_BROKEN = (50, 40, 30)
COLOR_TEXT = (255, 255, 255)
COLOR_ELEVATOR = (150, 150, 160)
COLOR_ELEVATOR_CABLE = (100, 100, 100)

# Game physics
PLAYER_SPEED = 4
CLIMB_SPEED = 3
JUMP_FORCE = -10
GRAVITY = 0.5
ENEMY_SPEED = 1.5
ENEMY_VISION_RANGE = 200
ENEMY_VISION_DARK_RANGE = 80
BULLET_SPEED = 10

# Level settings
NUM_FLOORS = 10
FLOOR_HEIGHT = 50
FLOOR_Y_START = 100
FLOOR_Y_SPACING = 45
DOOR_WIDTH = 40
DOOR_HEIGHT = 70


class GameState(Enum):
    PLAYING = 0
    GAME_OVER = 1
    VICTORY = 2
    PAUSED = 3


class DoorType(Enum):
    RED = 0  # Contains secret document
    BLUE = 1  # Cover only
    NORMAL = 2  # Empty


class Door:
    def __init__(self, x, floor_y, door_type):
        self.x = x
        self.y = floor_y - DOOR_HEIGHT
        self.width = DOOR_WIDTH
        self.height = DOOR_HEIGHT
        self.door_type = door_type
        self.opened = False
        self.searched = False

    def draw(self, surface):
        if self.opened:
            color = COLOR_DOOR_OPENED
        elif self.door_type == DoorType.RED:
            color = COLOR_DOOR_RED
        elif self.door_type == DoorType.BLUE:
            color = COLOR_DOOR_BLUE
        else:
            color = (100, 100, 100)

        # Door frame
        pygame.draw.rect(surface, (60, 60, 60), (self.x - 2, self.y - 2, self.width + 4, self.height + 4))
        # Door
        pygame.draw.rect(surface, color, (self.x, self.y, self.width, self.height))

        if not self.opened:
            # Door handle
            pygame.draw.circle(surface, (200, 200, 200), (self.x + self.width - 10, self.y + self.height // 2), 4)
            # Document indicator for red doors
            if self.door_type == DoorType.RED and not self.searched:
                pygame.draw.circle(surface, (255, 255, 0), (self.x + self.width // 2, self.y - 8), 5)
        else:
            # Dark opening
            pygame.draw.rect(surface, (20, 20, 20), (self.x + 5, self.y + 5, self.width - 10, self.height - 10))


class Light:
    def __init__(self, x, floor_y):
        self.x = x
        self.y = floor_y - 15
        self.radius = 120
        self.intact = True

    def draw(self, surface):
        color = COLOR_LIGHT if self.intact else COLOR_LIGHT_BROKEN
        pygame.draw.circle(surface, color, (self.x, self.y), 8)
        if self.intact:
            # Glow effect
            s = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 240, 180, 20), (self.radius, self.radius), self.radius)
            surface.blit(s, (self.x - self.radius, self.y - self.radius))


class Elevator:
    def __init__(self, x, min_floor, max_floor):
        self.x = x
        self.width = 50
        self.height = 60
        self.min_floor = min_floor
        self.max_floor = max_floor
        self.y = self.get_floor_y(max_floor)
        self.speed = 2
        self.direction = -1  # -1 for up, 1 for down
        self.wait_time = 0
        self.player_inside = False

    def get_floor_y(self, floor_index):
        return FLOOR_Y_START + floor_index * FLOOR_Y_SPACING - self.height

    def update(self):
        if self.player_inside:
            return

        if self.wait_time > 0:
            self.wait_time -= 1
            return

        self.y += self.speed * self.direction

        min_y = self.get_floor_y(self.min_floor)
        max_y = self.get_floor_y(self.max_floor)

        if self.y <= min_y:
            self.y = min_y
            self.direction = 1
            self.wait_time = 60
        elif self.y >= max_y:
            self.y = max_y
            self.direction = -1
            self.wait_time = 60

    def draw(self, surface):
        # Cable
        pygame.draw.line(surface, COLOR_ELEVATOR_CABLE, (self.x + self.width // 2, 0), (self.x + self.width // 2, self.y), 3)

        # Elevator car
        pygame.draw.rect(surface, COLOR_ELEVATOR, (self.x, self.y, self.width, self.height))
        pygame.draw.rect(surface, (100, 100, 110), (self.x, self.y, self.width, self.height), 2)

        # Windows
        pygame.draw.rect(surface, (200, 220, 255), (self.x + 8, self.y + 10, 15, 20))
        pygame.draw.rect(surface, (200, 220, 255), (self.x + 27, self.y + 10, 15, 20))

        # Doors
        door_color = (120, 120, 130) if not self.player_inside else (100, 100, 100)
        pygame.draw.rect(surface, door_color, (self.x + 2, self.y + 35, 20, 23))
        pygame.draw.rect(surface, door_color, (self.x + 28, self.y + 35, 20, 23))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Enemy:
    def __init__(self, x, floor_index):
        self.x = x
        self.floor_index = floor_index
        self.y = FLOOR_Y_START + floor_index * FLOOR_Y_SPACING - 35
        self.width = 30
        self.height = 35
        self.speed = ENEMY_SPEED
        self.direction = 1
        self.patrol_range = 150
        self.start_x = x
        self.alive = True
        self.detection_timer = 0
        self.vision_angle = 45

    def update(self, player, lights):
        if not self.alive:
            return

        # Patrol movement
        self.x += self.speed * self.direction

        if self.x > self.start_x + self.patrol_range:
            self.direction = -1
        elif self.x < self.start_x - self.patrol_range:
            self.direction = 1

        # Keep in bounds
        self.x = max(50, min(self.x, SCREEN_WIDTH - 50))

        # Check if player is detected
        player_center = (player.x + player.width // 2, player.y + player.height // 2)
        enemy_center = (self.x + self.width // 2, self.y + self.height // 2)

        dx = player_center[0] - enemy_center[0]
        dy = player_center[1] - enemy_center[1]
        distance = (dx ** 2 + dy ** 2) ** 0.5

        # Check if in same floor
        same_floor = abs(player.y - self.y) < 30

        # Check if in darkness (reduces vision range)
        in_darkness = False
        for light in lights:
            if light.intact:
                light_distance = ((player.x - light.x) ** 2 + (player.y - light.y) ** 2) ** 0.5
                if light_distance < light.radius:
                    in_darkness = False
                    break
        else:
            in_darkness = True

        vision_range = ENEMY_VISION_DARK_RANGE if in_darkness else ENEMY_VISION_RANGE

        if same_floor and distance < vision_range:
            # Check if player is in front (based on enemy direction)
            if (self.direction == 1 and dx > 0) or (self.direction == -1 and dx < 0):
                self.detection_timer += 1
                if self.detection_timer > 30:
                    return True  # Player detected!
        else:
            self.detection_timer = max(0, self.detection_timer - 1)

        return False

    def draw(self, surface):
        if not self.alive:
            return

        # Body
        pygame.draw.rect(surface, COLOR_ENEMY, (self.x, self.y + 10, self.width, self.height - 10))

        # Head
        pygame.draw.circle(surface, COLOR_ENEMY, (self.x + self.width // 2, self.y + 8), 10)

        # Eyes (show direction)
        eye_offset = 4 if self.direction == 1 else -4
        pygame.draw.circle(surface, (255, 255, 255), (self.x + self.width // 2 + eye_offset, self.y + 6), 3)

        # Gun
        gun_x = self.x + self.width if self.direction == 1 else self.x
        pygame.draw.rect(surface, (80, 80, 80), (gun_x, self.y + 18, 15 * self.direction, 5))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Bullet:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.direction = direction
        self.speed = BULLET_SPEED
        self.active = True

    def update(self):
        self.x += self.speed * self.direction
        if self.x < 0 or self.x > SCREEN_WIDTH:
            self.active = False

    def draw(self, surface):
        pygame.draw.circle(surface, COLOR_BULLET, (int(self.x), int(self.y)), 4)

    def get_rect(self):
        return pygame.Rect(self.x - 4, self.y - 4, 8, 8)


class Player:
    def __init__(self):
        self.width = 30
        self.height = 40
        self.x = 100
        self.y = FLOOR_Y_START + (NUM_FLOORS - 1) * FLOOR_Y_SPACING - self.height
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = True
        self.in_elevator = None
        self.alive = True
        self.score = 0
        self.documents_collected = 0
        self.total_documents = 0
        self.facing_direction = 1
        self.crouching = False
        self.shoot_cooldown = 0
        self.current_floor = NUM_FLOORS - 1

    def update(self, keys, floors, doors, elevators, enemies):
        if not self.alive:
            return

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        # Crouch
        self.crouching = keys[pygame.K_DOWN] and self.on_ground and self.in_elevator is None

        # If in elevator
        if self.in_elevator:
            self.x = self.in_elevator.x + 10
            self.y = self.in_elevator.y + 10

            # Elevator controls
            if keys[pygame.K_UP]:
                self.in_elevator.direction = -1
            elif keys[pygame.K_DOWN]:
                self.in_elevator.direction = 1
            else:
                self.in_elevator.direction = 0

            # Exit elevator with left/right
            if keys[pygame.K_LEFT]:
                self.in_elevator.player_inside = False
                self.x = self.in_elevator.x - self.width - 5
                self.in_elevator = None
                self.on_ground = True
            elif keys[pygame.K_RIGHT]:
                self.in_elevator.player_inside = False
                self.x = self.in_elevator.x + self.in_elevator.width + 5
                self.in_elevator = None
                self.on_ground = True

            return

        # Check for elevator entry
        for elevator in elevators:
            if elevator.get_rect().colliderect(pygame.Rect(self.x, self.y, self.width, self.height)):
                if keys[pygame.K_UP] or keys[pygame.K_DOWN]:
                    self.in_elevator = elevator
                    elevator.player_inside = True
                    return

        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
            self.facing_direction = -1
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
            self.facing_direction = 1

        # Apply horizontal movement
        new_x = self.x + self.vel_x
        new_x = max(10, min(new_x, SCREEN_WIDTH - self.width - 10))
        self.x = new_x

        # Gravity
        if not self.on_ground:
            self.vel_y += GRAVITY

        # Apply vertical movement
        new_y = self.y + self.vel_y

        # Floor collision
        self.on_ground = False
        for i, floor_y in enumerate(floors):
            floor_rect = pygame.Rect(0, floor_y, SCREEN_WIDTH, 10)
            player_rect = pygame.Rect(self.x, new_y, self.width, self.height)

            if floor_rect.colliderect(player_rect) and self.vel_y >= 0:
                if self.y + self.height <= floor_y + 15:
                    self.y = floor_y - self.height
                    self.vel_y = 0
                    self.on_ground = True
                    self.current_floor = i
                    break

        if not self.on_ground:
            self.y = new_y

        # Prevent falling below screen
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True

        # Check door interaction
        for door in doors:
            door_rect = pygame.Rect(door.x, door.y, door.width, door.height)
            player_rect = pygame.Rect(self.x, self.y, self.width, self.height)

            if door_rect.colliderect(player_rect) and not door.opened:
                if door.door_type == DoorType.RED and not door.searched:
                    self.score += 500
                    self.documents_collected += 1
                    door.searched = True
                door.opened = True

    def shoot(self):
        if self.shoot_cooldown == 0:
            self.shoot_cooldown = 20
            return Bullet(
                self.x + (self.width if self.facing_direction == 1 else 0),
                self.y + 18,
                self.facing_direction
            )
        return None

    def draw(self, surface):
        color = COLOR_PLAYER_STEALTH if self.crouching else COLOR_PLAYER

        # Body
        body_height = self.height - 15 if not self.crouching else self.height - 25
        body_y = self.y + 15 if not self.crouching else self.y + 25
        pygame.draw.rect(surface, color, (self.x, body_y, self.width, body_height))

        # Head
        head_y = self.y if not self.crouching else self.y + 10
        pygame.draw.circle(surface, color, (self.x + self.width // 2, head_y + 8), 10)

        # Eyes
        eye_offset = 3 if self.facing_direction == 1 else -3
        pygame.draw.circle(surface, (255, 255, 255), (self.x + self.width // 2 + eye_offset, head_y + 6), 3)

        # Gun arm
        gun_start_x = self.x + self.width if self.facing_direction == 1 else self.x
        pygame.draw.rect(surface, (80, 80, 80), (gun_start_x, self.y + 20, 12 * self.facing_direction, 5))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Elevator Action Stealth")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.floors = [FLOOR_Y_START + i * FLOOR_Y_SPACING for i in range(NUM_FLOORS)]
        self.doors = []
        self.elevators = []
        self.enemies = []
        self.lights = []
        self.bullets = []
        self.state = GameState.PLAYING
        self.message_timer = 0

        self.create_level()

    def create_level(self):
        # Create doors on each floor
        for i in range(NUM_FLOORS - 1):  # All floors except basement
            floor_y = self.floors[i]
            num_doors = random.randint(2, 4)
            door_x_positions = random.sample(range(80, SCREEN_WIDTH - 80, 60), num_doors)

            for x in door_x_positions:
                # 30% chance for red door (document), 40% blue (cover), 30% normal
                rand = random.random()
                if rand < 0.3:
                    door_type = DoorType.RED
                    self.player.total_documents += 1
                elif rand < 0.7:
                    door_type = DoorType.BLUE
                else:
                    door_type = DoorType.NORMAL

                self.doors.append(Door(x, floor_y, door_type))

        # Create lights on each floor
        for i in range(NUM_FLOORS - 1):
            floor_y = self.floors[i]
            num_lights = random.randint(2, 3)
            light_x_positions = random.sample(range(100, SCREEN_WIDTH - 100, 80), num_lights)

            for x in light_x_positions:
                self.lights.append(Light(x, floor_y))

        # Create elevators
        elevator_positions = [200, 400, 600]
        for x in elevator_positions:
            # Each elevator serves 3-4 consecutive floors
            start_floor = random.randint(0, NUM_FLOORS - 4)
            end_floor = min(start_floor + random.randint(2, 3), NUM_FLOORS - 1)
            self.elevators.append(Elevator(x, start_floor, end_floor))

        # Create enemies on random floors (not top floor)
        for i in range(1, NUM_FLOORS - 1):
            if random.random() < 0.6:  # 60% chance of enemy on floor
                x = random.randint(150, SCREEN_WIDTH - 150)
                self.enemies.append(Enemy(x, i))

        # Ensure at least 3 documents
        while self.player.total_documents < 3:
            floor_y = self.floors[random.randint(0, NUM_FLOORS - 2)]
            x = random.randint(100, SCREEN_WIDTH - 100)
            self.doors.append(Door(x, floor_y, DoorType.RED))
            self.player.total_documents += 1

    def update(self):
        if self.state != GameState.PLAYING:
            return

        keys = pygame.key.get_pressed()

        # Update elevators
        for elevator in self.elevators:
            elevator.update()

        # Update player
        self.player.update(keys, self.floors, self.doors, self.elevators, self.enemies)

        # Update enemies
        for enemy in self.enemies:
            detected = enemy.update(self.player, self.lights)
            if detected:
                self.player.alive = False
                self.state = GameState.GAME_OVER

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if not bullet.active:
                self.bullets.remove(bullet)
                continue

            # Check enemy collision
            for enemy in self.enemies:
                if enemy.alive and bullet.get_rect().colliderect(enemy.get_rect()):
                    enemy.alive = False
                    self.player.score += 100
                    bullet.active = False
                    break

            # Check light collision (can shoot lights)
            for light in self.lights:
                if light.intact:
                    light_rect = pygame.Rect(light.x - 10, light.y - 10, 20, 20)
                    if bullet.get_rect().colliderect(light_rect):
                        light.intact = False
                        bullet.active = False
                        break

        # Check win condition (reached basement with all documents)
        if self.player.current_floor == NUM_FLOORS - 1:
            if self.player.documents_collected >= self.player.total_documents:
                self.player.score += 1000
                self.state = GameState.VICTORY
            else:
                # Show hint
                pass

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_z:
                bullet = self.player.shoot()
                if bullet:
                    self.bullets.append(bullet)
            elif event.key == pygame.K_SPACE and self.player.on_ground and self.player.in_elevator is None:
                self.player.vel_y = JUMP_FORCE
                self.player.on_ground = False
            elif event.key == pygame.K_r:
                self.reset_game()

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw building exterior
        pygame.draw.rect(surface, COLOR_WALL, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

        # Draw floors
        for floor_y in self.floors:
            pygame.draw.rect(self.screen, COLOR_FLOOR, (30, floor_y, SCREEN_WIDTH - 60, FLOOR_HEIGHT // 2))
            pygame.draw.line(self.screen, COLOR_FLOOR_EDGE, (30, floor_y), (SCREEN_WIDTH - 30, floor_y), 2)

        # Draw lights
        for light in self.lights:
            light.draw(self.screen)

        # Draw doors (behind player)
        for door in self.doors:
            door.draw(self.screen)

        # Draw elevators
        for elevator in self.elevators:
            elevator.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw basement exit
        exit_y = self.floors[NUM_FLOORS - 1]
        pygame.draw.rect(self.screen, (50, 150, 50), (SCREEN_WIDTH // 2 - 30, exit_y - 80, 60, 80))
        exit_text = self.small_font.render("EXIT", True, (255, 255, 255))
        self.screen.blit(exit_text, (SCREEN_WIDTH // 2 - 18, exit_y - 60))

        # Draw HUD
        self.draw_hud()

        # Draw game state messages
        if self.state == GameState.GAME_OVER:
            self.draw_message("GAME OVER", f"Score: {self.player.score} - Press R to restart")
        elif self.state == GameState.VICTORY:
            self.draw_message("MISSION COMPLETE!", f"Score: {self.player.score} - Press R for new mission")

        pygame.display.flip()

    def draw_hud(self):
        # Score
        score_text = self.small_font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Documents
        doc_text = self.small_font.render(
            f"Documents: {self.player.documents_collected}/{self.player.total_documents}",
            True, COLOR_TEXT
        )
        self.screen.blit(doc_text, (10, 35))

        # Floor
        floor_text = self.small_font.render(f"Floor: {NUM_FLOORS - self.player.current_floor}", True, COLOR_TEXT)
        self.screen.blit(floor_text, (10, 60))

        # Controls hint
        hint_text = self.small_font.render("Arrows: Move/Climb | Z: Fire | SPACE: Jump", True, (150, 150, 150))
        self.screen.blit(hint_text, (SCREEN_WIDTH - 350, 10))

        # Warning if documents missing
        if self.player.current_floor == NUM_FLOORS - 1 and self.player.documents_collected < self.player.total_documents:
            warning_text = self.small_font.render("Collect all documents first!", True, (255, 100, 100))
            self.screen.blit(warning_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT - 30))

    def draw_message(self, title, subtitle):
        title_surface = self.font.render(title, True, COLOR_TEXT)
        subtitle_surface = self.small_font.render(subtitle, True, COLOR_TEXT)

        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))

        # Semi-transparent background
        bg_rect = pygame.Rect(0, 0, 500, 120)
        bg_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        s = pygame.Surface((bg_rect.width, bg_rect.height))
        s.set_alpha(200)
        s.fill((0, 0, 0))
        self.screen.blit(s, bg_rect.topleft)
        pygame.draw.rect(self.screen, COLOR_TEXT, bg_rect, 2)

        self.screen.blit(title_surface, title_rect)
        self.screen.blit(subtitle_surface, subtitle_rect)

    def run(self):
        running = True

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        self.handle_event(event)

            # Update
            self.update()

            # Draw
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
