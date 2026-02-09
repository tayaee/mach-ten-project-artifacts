"""Vector Elevator Action Stealth - A tactical infiltration game.

Infiltrate a high-security building using elevators and tactical positioning
to retrieve secret documents.
"""

import pygame
import sys
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
BLACK = (10, 10, 15)
WHITE = (240, 240, 240)
GRAY = (100, 100, 100)
DARK_GRAY = (50, 50, 60)
RED = (200, 50, 50)
BLUE = (50, 100, 200)
GREEN = (50, 180, 80)
YELLOW = (220, 180, 40)
ORANGE = (255, 140, 40)

# Game settings
FLOOR_HEIGHT = 20
NUM_FLOORS = 30
FLOOR_PIXEL_HEIGHT = SCREEN_HEIGHT // NUM_FLOORS
PLAYER_WIDTH = 20
PLAYER_HEIGHT = 30
PLAYER_SPEED = 4
JUMP_FORCE = -10
GRAVITY = 0.5

ELEVATOR_SPEED = 2
ELEVATOR_WIDTH = 40
ELEVATOR_HEIGHT = FLOOR_PIXEL_HEIGHT - 10

GUARD_SPEED = 1.5
GUARD_WIDTH = 20
GUARD_HEIGHT = 28

DOOR_WIDTH = 30
DOOR_HEIGHT = FLOOR_PIXEL_HEIGHT - 15

BULLET_SPEED = 10
BULLET_WIDTH = 6
BULLET_HEIGHT = 3


@dataclass
class Vector:
    x: float
    y: float

    def __add__(self, other):
        return Vector(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        return Vector(self.x - other.x, self.y - other.y)

    def __mul__(self, scalar):
        return Vector(self.x * scalar, self.y * scalar)

    def length(self):
        return (self.x ** 2 + self.y ** 2) ** 0.5

    def normalize(self):
        l = self.length()
        if l == 0:
            return Vector(0, 0)
        return Vector(self.x / l, self.y / l)


class Entity:
    def __init__(self, x, y, width, height, color):
        self.pos = Vector(x, y)
        self.vel = Vector(0, 0)
        self.width = width
        self.height = height
        self.color = color
        self.alive = True

    def get_rect(self):
        return pygame.Rect(
            int(self.pos.x), int(self.pos.y),
            self.width, self.height
        )

    def draw(self, surface):
        if self.alive:
            rect = self.get_rect()
            pygame.draw.rect(surface, self.color, rect)


class Player(Entity):
    def __init__(self, x, y):
        super().__init__(x, y, PLAYER_WIDTH, PLAYER_HEIGHT, GREEN)
        self.on_ground = False
        self.crouching = False
        self.on_elevator = None
        self.health = 100
        self.score = 0
        self.start_time = pygame.time.get_ticks()

    def update(self, keys, floors, elevators, stairs, doors):
        # Horizontal movement
        self.vel.x = 0
        if not self.crouching:
            if keys[pygame.K_LEFT]:
                self.vel.x = -PLAYER_SPEED
            if keys[pygame.K_RIGHT]:
                self.vel.x = PLAYER_SPEED

        # Gravity
        self.vel.y += GRAVITY

        # Crouch
        self.crouching = keys[pygame.K_LCTRL] or keys[pygame.K_RCTRL]
        if self.crouching:
            self.height = PLAYER_HEIGHT // 2
        else:
            self.height = PLAYER_HEIGHT

        # Check elevator interaction
        self.on_elevator = None
        player_rect = self.get_rect()

        for elevator in elevators:
            if player_rect.colliderect(elevator.get_rect()):
                if self.vel.y >= 0:
                    self.on_elevator = elevator
                    self.on_ground = True
                    self.vel.y = 0
                    self.pos.y = elevator.pos.y - self.height
                    break

        # Elevator controls
        if self.on_elevator:
            if keys[pygame.K_UP]:
                self.on_elevator.moving_up = True
                self.on_elevator.moving_down = False
            elif keys[pygame.K_DOWN]:
                self.on_elevator.moving_down = True
                self.on_elevator.moving_up = False
            else:
                self.on_elevator.moving_up = False
                self.on_elevator.moving_down = False
            self.pos.y += self.on_elevator.vel.y
        else:
            # Stop elevators when not riding
            for elevator in elevators:
                elevator.moving_up = False
                elevator.moving_down = False

        # Stairs interaction
        if not self.on_elevator:
            for stair in stairs:
                if player_rect.colliderect(stair.get_rect()):
                    if keys[pygame.K_UP]:
                        self.vel.y = -PLAYER_SPEED * 0.7
                    elif keys[pygame.K_DOWN]:
                        self.vel.y = PLAYER_SPEED * 0.7

        # Apply velocity
        new_pos = self.pos + self.vel
        new_rect = pygame.Rect(
            int(new_pos.x), int(new_pos.y),
            self.width, self.height
        )

        # Floor collision
        self.on_ground = False
        if not self.on_elevator:
            for floor in floors:
                if new_rect.colliderect(floor):
                    if self.vel.y > 0:
                        self.pos.y = floor.top - self.height
                        self.vel.y = 0
                        self.on_ground = True
                    elif self.vel.y < 0:
                        self.pos.y = floor.bottom
                        self.vel.y = 0

        # Screen bounds
        if new_pos.x < 0:
            new_pos.x = 0
        if new_pos.x > SCREEN_WIDTH - self.width:
            new_pos.x = SCREEN_WIDTH - self.width
        if new_pos.y > SCREEN_HEIGHT - self.height:
            new_pos.y = SCREEN_HEIGHT - self.height

        self.pos.x = new_pos.x
        if not self.on_elevator:
            self.pos.y = min(new_pos.y, SCREEN_HEIGHT - self.height)

        # Update time-based score
        elapsed = (pygame.time.get_ticks() - self.start_time) // 1000
        time_penalty = elapsed * 10

    def draw(self, surface):
        if self.alive:
            rect = self.get_rect()
            color = self.color
            if self.crouching:
                color = (40, 140, 60)
            pygame.draw.rect(surface, color, rect)

            # Draw simple spy figure
            head_radius = 6 if not self.crouching else 4
            head_center = (int(rect.centerx), int(rect.top + head_radius + 2))
            pygame.draw.circle(surface, WHITE, head_center, head_radius)


class Guard(Entity):
    def __init__(self, x, y, floor_index, patrol_range):
        super().__init__(x, y, GUARD_WIDTH, GUARD_HEIGHT, RED)
        self.floor_index = floor_index
        self.patrol_start = x
        self.patrol_range = patrol_range
        self.direction = 1
        self.shoot_cooldown = 0
        self.alert_timer = 0

    def update(self, player):
        if not self.alive:
            return None

        # Patrol behavior
        self.pos.x += GUARD_SPEED * self.direction

        if self.pos.x > self.patrol_start + self.patrol_range:
            self.direction = -1
        elif self.pos.x < self.patrol_start:
            self.direction = 1

        # Check for player visibility
        player_rect = player.get_rect()
        guard_rect = self.get_rect()

        # Simple line of sight check
        if abs(player.pos.y - self.pos.y) < FLOOR_PIXEL_HEIGHT:
            if self.direction > 0 and player.pos.x > self.pos.x:
                distance = player.pos.x - self.pos.x
            elif self.direction < 0 and player.pos.x < self.pos.x:
                distance = self.pos.x - player.pos.x
            else:
                distance = 999

            if distance < 300:
                self.alert_timer = 60
                if self.shoot_cooldown <= 0:
                    self.shoot_cooldown = 90
                    direction_to_player = (player.pos - self.pos).normalize()
                    return Bullet(
                        self.pos.x + self.width / 2,
                        self.pos.y + self.height / 2,
                        direction_to_player,
                        is_player_bullet=False
                    )

        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        return None

    def draw(self, surface):
        if self.alive:
            rect = self.get_rect()
            pygame.draw.rect(surface, self.color, rect)

            # Draw guard alert state
            if self.alert_timer > 0:
                pygame.draw.circle(surface, ORANGE, (int(rect.centerx), int(rect.top - 5)), 3)
                self.alert_timer -= 1


class Bullet(Entity):
    def __init__(self, x, y, direction, is_player_bullet=True):
        super().__init__(x, y, BULLET_WIDTH, BULLET_HEIGHT, YELLOW if is_player_bullet else ORANGE)
        self.vel = direction * BULLET_SPEED
        self.is_player_bullet = is_player_bullet
        self.lifetime = 120

    def update(self):
        self.pos = self.pos + self.vel
        self.lifetime -= 1

        if self.lifetime <= 0:
            self.alive = False

        # Screen bounds
        if (self.pos.x < 0 or self.pos.x > SCREEN_WIDTH or
            self.pos.y < 0 or self.pos.y > SCREEN_HEIGHT):
            self.alive = False


class Elevator(Entity):
    def __init__(self, x, floor_indices):
        y = floor_indices[0] * FLOOR_PIXEL_HEIGHT + FLOOR_HEIGHT
        super().__init__(x, y, ELEVATOR_WIDTH, ELEVATOR_HEIGHT, BLUE)
        self.floor_indices = floor_indices
        self.min_floor = min(floor_indices)
        self.max_floor = max(floor_indices)
        self.moving_up = False
        self.moving_down = False

    def update(self):
        if self.moving_up:
            self.vel.y = -ELEVATOR_SPEED
        elif self.moving_down:
            self.vel.y = ELEVATOR_SPEED
        else:
            self.vel.y = 0

        # Floor constraints
        target_y = self.pos.y + self.vel.y
        min_y = self.min_floor * FLOOR_PIXEL_HEIGHT + FLOOR_HEIGHT
        max_y = self.max_floor * FLOOR_PIXEL_HEIGHT

        if target_y < min_y:
            self.pos.y = min_y
            self.vel.y = 0
        elif target_y > max_y:
            self.pos.y = max_y
            self.vel.y = 0
        else:
            self.pos.y = target_y

    def draw(self, surface):
        rect = self.get_rect()
        pygame.draw.rect(surface, DARK_GRAY, rect)
        pygame.draw.rect(surface, self.color, rect.inflate(-4, -4))

        # Draw elevator cable
        start_pos = (rect.centerx, 0)
        end_pos = (rect.centerx, rect.top)
        pygame.draw.line(surface, GRAY, start_pos, end_pos, 2)


class Door:
    def __init__(self, x, floor_index, has_document=True):
        self.x = x
        self.floor_index = floor_index
        self.y = floor_index * FLOOR_PIXEL_HEIGHT + FLOOR_HEIGHT
        self.width = DOOR_WIDTH
        self.height = DOOR_HEIGHT
        self.has_document = has_document
        self.collected = False
        self.hazard = False
        self.open_anim = 0

        # Randomly make some blue doors hazardous
        if not has_document and random.random() < 0.3:
            self.hazard = True

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def update(self):
        if self.open_anim > 0:
            self.open_anim = min(100, self.open_anim + 5)

    def draw(self, surface, camera_y):
        rect = self.get_rect()

        if self.collected:
            # Draw opened door
            open_width = self.width * self.open_anim / 100
            pygame.draw.rect(surface, DARK_GRAY, (rect.x, rect.y, open_width, rect.height))
        elif self.has_document:
            # Red door - contains document
            pygame.draw.rect(surface, RED, rect)
            pygame.draw.rect(surface, (150, 30, 30), rect.inflate(-6, -6))
            # Document icon
            pygame.draw.rect(surface, WHITE, (rect.centerx - 5, rect.centery - 8, 10, 16))
        elif self.hazard:
            # Blue door - hazard
            pygame.draw.rect(surface, BLUE, rect)
            # Warning indicator
            pygame.draw.line(surface, YELLOW, (rect.x + 5, rect.y + 5), (rect.right - 5, rect.bottom - 5), 2)
            pygame.draw.line(surface, YELLOW, (rect.right - 5, rect.y + 5), (rect.x + 5, rect.bottom - 5), 2)
        else:
            # Blue door - empty
            pygame.draw.rect(surface, BLUE, rect)
            pygame.draw.rect(surface, (30, 80, 180), rect.inflate(-6, -6))


class Stair:
    def __init__(self, x, floor_indices):
        self.x = x
        self.floor_indices = floor_indices
        self.width = 40
        self.start_y = floor_indices[0] * FLOOR_PIXEL_HEIGHT + FLOOR_HEIGHT
        self.height = (len(floor_indices) - 1) * FLOOR_PIXEL_HEIGHT + FLOOR_PIXEL_HEIGHT - 10

    def get_rect(self):
        return pygame.Rect(self.x, self.start_y, self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        pygame.draw.rect(surface, (70, 70, 80), rect)

        # Draw steps
        for i in range(len(self.floor_indices) - 1):
            y = rect.y + i * FLOOR_PIXEL_HEIGHT
            points = [
                (rect.x, y),
                (rect.x + 10, y + FLOOR_PIXEL_HEIGHT),
                (rect.right, y + FLOOR_PIXEL_HEIGHT),
                (rect.right, y)
            ]
            pygame.draw.polygon(surface, (90, 90, 100), points)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Elevator Action Stealth")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 24)
        self.title_font = pygame.font.Font(None, 48)

        self.state = "menu"  # menu, playing, gameover, win
        self.reset_game()

    def reset_game(self):
        # Create floors
        self.floors = []
        for i in range(NUM_FLOORS):
            y = i * FLOOR_PIXEL_HEIGHT + FLOOR_HEIGHT
            self.floors.append(pygame.Rect(0, y, SCREEN_WIDTH, FLOOR_HEIGHT))

        # Create elevators (3 elevator shafts)
        self.elevators = []
        elevator_positions = [150, 400, 650]
        for x in elevator_positions:
            floors = list(range(0, NUM_FLOORS, 3))  # Every 3rd floor
            self.elevators.append(Elevator(x, floors))

        # Create stairs (2 stairwells)
        self.stairs = []
        stair_positions = [250, 550]
        for x in stair_positions:
            floors = list(range(0, NUM_FLOORS, 6))
            self.stairs.append(Stair(x, floors))

        # Create doors
        self.doors = []
        self.document_doors = []
        for floor in range(1, NUM_FLOORS - 1):
            floor_doors = []
            for x in [50, 300, 500, 750]:
                has_doc = random.random() < 0.3  # 30% chance of document
                door = Door(x, floor, has_doc)
                self.doors.append(door)
                floor_doors.append(door)
                if has_doc:
                    self.document_doors.append(door)

        # Ensure at least 5 documents exist
        while len(self.document_doors) < 5:
            floor = random.randint(1, NUM_FLOORS - 2)
            x = random.choice([50, 300, 500, 750])
            door = Door(x, floor, True)
            self.doors.append(door)
            self.document_doors.append(door)

        # Create guards
        self.guards = []
        for floor in range(5, NUM_FLOORS - 5, 4):
            x = random.randint(100, 600)
            self.guards.append(Guard(x, floor * FLOOR_PIXEL_HEIGHT + FLOOR_HEIGHT - GUARD_HEIGHT, floor, 200))

        # Create player at top floor
        self.player = Player(SCREEN_WIDTH // 2, 30)

        self.bullets = []
        self.documents_collected = 0
        self.total_documents = len(self.document_doors)
        self.guards_neutralized = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()

                if self.state == "menu":
                    if event.key == pygame.K_SPACE:
                        self.state = "playing"
                        self.reset_game()

                elif self.state in ["gameover", "win"]:
                    if event.key == pygame.K_SPACE:
                        self.state = "playing"
                        self.reset_game()
                    elif event.key == pygame.K_m:
                        self.state = "menu"

                elif self.state == "playing":
                    if event.key == pygame.K_SPACE:
                        # Shoot bullet
                        direction = Vector(1, 0)
                        if self.player.vel.x < 0:
                            direction = Vector(-1, 0)
                        bullet = Bullet(
                            self.player.pos.x + self.player.width / 2,
                            self.player.pos.y + self.player.height / 2,
                            direction,
                            is_player_bullet=True
                        )
                        self.bullets.append(bullet)

    def update(self):
        if self.state != "playing":
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.floors, self.elevators, self.stairs, self.doors)

        # Update elevators
        for elevator in self.elevators:
            elevator.update()

        # Update doors
        for door in self.doors:
            door.update()

        # Check door interaction
        player_rect = self.player.get_rect()
        for door in self.document_doors:
            if not door.collected and player_rect.colliderect(door.get_rect()):
                door.collected = True
                self.documents_collected += 500
                self.documents_collected = min(self.documents_collected, self.total_documents * 500)

        # Check hazard doors
        for door in self.doors:
            if door.hazard and not door.collected:
                if player_rect.colliderect(door.get_rect()):
                    self.player.health -= 1
                    if self.player.health <= 0:
                        self.state = "gameover"

        # Update guards
        for guard in self.guards:
            new_bullet = guard.update(self.player)
            if new_bullet:
                self.bullets.append(new_bullet)

        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()

            # Check collision with guards
            if bullet.is_player_bullet:
                for guard in self.guards:
                    if guard.alive and bullet.get_rect().colliderect(guard.get_rect()):
                        guard.alive = False
                        bullet.alive = False
                        self.player.score += 100
                        self.guards_neutralized += 1
                        break
            else:
                # Enemy bullet hits player
                if bullet.get_rect().colliderect(self.player.get_rect()):
                    self.player.health -= 25
                    bullet.alive = False
                    if self.player.health <= 0:
                        self.state = "gameover"

            # Remove dead bullets
            if not bullet.alive:
                self.bullets.remove(bullet)

        # Update score with time penalty
        elapsed = (pygame.time.get_ticks() - self.player.start_time) // 1000
        self.player.score = self.documents_collected + self.guards_neutralized * 100 - elapsed * 10

        # Check win condition
        collected_count = sum(1 for d in self.document_doors if d.collected)
        if collected_count >= self.total_documents and self.player.pos.y > SCREEN_HEIGHT - 100:
            self.state = "win"

    def draw(self):
        self.screen.fill(BLACK)

        if self.state == "menu":
            self.draw_menu()
        elif self.state == "playing":
            self.draw_game()
        elif self.state == "gameover":
            self.draw_game()
            self.draw_gameover()
        elif self.state == "win":
            self.draw_game()
            self.draw_win()

        pygame.display.flip()

    def draw_menu(self):
        title = self.title_font.render("VECTOR ELEVATOR", True, GREEN)
        stealth = self.title_font.render("ACTION STEALTH", True, RED)

        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        stealth_rect = stealth.get_rect(center=(SCREEN_WIDTH // 2, 200))

        self.screen.blit(title, title_rect)
        self.screen.blit(stealth, stealth_rect)

        instructions = [
            "Infiltrate the building and collect all documents.",
            "",
            "Controls:",
            "Arrow Keys - Move, use elevators/stairs",
            "Ctrl - Crouch",
            "Space - Shoot",
            "",
            "Red Doors = Secret Documents",
            "Blue Doors = Empty or Hazard",
            "",
            "Press SPACE to start"
        ]

        y = 280
        for line in instructions:
            text = self.font.render(line, True, WHITE)
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, y))
            self.screen.blit(text, rect)
            y += 30

    def draw_game(self):
        # Draw floors
        for floor in self.floors:
            pygame.draw.rect(self.screen, DARK_GRAY, floor)

        # Draw stairs
        for stair in self.stairs:
            stair.draw(self.screen)

        # Draw elevators
        for elevator in self.elevators:
            elevator.draw(self.screen)

        # Draw doors
        for door in self.doors:
            door.draw(self.screen, 0)

        # Draw guards
        for guard in self.guards:
            guard.draw(self.screen)

        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        self.draw_hud()

    def draw_hud(self):
        # Health bar
        pygame.draw.rect(self.screen, DARK_GRAY, (10, 10, 204, 24))
        health_width = (self.player.health / 100) * 200
        health_color = GREEN if self.player.health > 50 else (ORANGE if self.player.health > 25 else RED)
        pygame.draw.rect(self.screen, health_color, (12, 12, max(0, health_width), 20))

        # Score
        score_text = self.font.render(f"Score: {max(0, self.player.score)}", True, WHITE)
        self.screen.blit(score_text, (10, 40))

        # Documents collected
        collected_count = sum(1 for d in self.document_doors if d.collected)
        doc_text = self.font.render(f"Docs: {collected_count}/{self.total_documents}", True, WHITE)
        self.screen.blit(doc_text, (10, 65))

        # Floor indicator
        current_floor = min(NUM_FLOORS - 1, int(self.player.pos.y // FLOOR_PIXEL_HEIGHT))
        floor_text = self.font.render(f"Floor: {NUM_FLOORS - current_floor}", True, WHITE)
        self.screen.blit(floor_text, (SCREEN_WIDTH - 120, 10))

    def draw_gameover(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        gameover_text = self.title_font.render("MISSION FAILED", True, RED)
        rect = gameover_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(gameover_text, rect)

        score_text = self.font.render(f"Final Score: {max(0, self.player.score)}", True, WHITE)
        rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(score_text, rect)

        retry_text = self.font.render("Press SPACE to retry or M for menu", True, WHITE)
        rect = retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(retry_text, rect)

    def draw_win(self):
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        win_text = self.title_font.render("MISSION COMPLETE", True, GREEN)
        rect = win_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(win_text, rect)

        score_text = self.font.render(f"Final Score: {max(0, self.player.score)}", True, WHITE)
        rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 10))
        self.screen.blit(score_text, rect)

        retry_text = self.font.render("Press SPACE to play again or M for menu", True, WHITE)
        rect = retry_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(retry_text, rect)

    def run(self):
        while True:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
