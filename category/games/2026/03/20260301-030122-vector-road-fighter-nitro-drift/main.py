import pygame
import random
import sys
import math

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
FPS = 60

COLOR_BG = (30, 30, 30)
COLOR_GRASS = (34, 139, 34)
COLOR_ROAD = (80, 80, 80)
COLOR_ROAD_LINE = (200, 200, 200)
COLOR_PLAYER = (255, 200, 50)
COLOR_PLAYER_OUTLINE = (200, 150, 0)
COLOR_NPC_CIVILIAN = (100, 150, 255)
COLOR_NPC_ERRATIC = (255, 100, 100)
COLOR_OIL_SLICK = (40, 40, 40)
COLOR_FUEL = (50, 200, 50)
COLOR_TEXT = (255, 255, 255)
COLOR_FUEL_BAR = (255, 100, 50)
COLOR_FUEL_BAR_BG = (60, 60, 60)

LANE_WIDTH = 80
NUM_LANES = 4
ROAD_LEFT = (SCREEN_WIDTH - LANE_WIDTH * NUM_LANES) // 2
ROAD_RIGHT = ROAD_LEFT + LANE_WIDTH * NUM_LANES

MAX_FUEL = 100
FUEL_DISTANCE = 10000
CRASH_PENALTY = 30
BOOST_FUEL_MULTIPLIER = 2

CAR_WIDTH = 50
CAR_HEIGHT = 70

class NPC:
    def __init__(self, y_offset, npc_type="civilian"):
        self.lane = random.randint(0, NUM_LANES - 1)
        self.x = ROAD_LEFT + self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.y = y_offset
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.type = npc_type
        self.speed = random.uniform(2, 4) if npc_type == "civilian" else random.uniform(3, 5)
        self.lane_change_timer = random.randint(60, 180) if npc_type == "erratic" else 99999
        self.lane_change_cooldown = 0
        self.overtaken = False

    def update(self, player_speed, world_speed):
        self.y += (player_speed - self.speed + world_speed)

        if self.type == "erratic":
            if self.lane_change_cooldown > 0:
                self.lane_change_cooldown -= 1
            else:
                self.lane_change_timer -= 1
                if self.lane_change_timer <= 0:
                    self.change_lane()
                    self.lane_change_timer = random.randint(60, 180)
                    self.lane_change_cooldown = 30

    def change_lane(self):
        direction = random.choice([-1, 1])
        new_lane = self.lane + direction
        if 0 <= new_lane < NUM_LANES:
            self.lane = new_lane
            target_x = ROAD_LEFT + self.lane * LANE_WIDTH + LANE_WIDTH // 2
            self.x = target_x

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                          self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        color = COLOR_NPC_CIVILIAN if self.type == "civilian" else COLOR_NPC_ERRATIC
        pygame.draw.rect(surface, color, rect, border_radius=5)
        pygame.draw.rect(surface, (50, 50, 50), rect, 2, border_radius=5)
        pygame.draw.rect(surface, (200, 200, 255),
                        (rect.x + 8, rect.y + 10, rect.width - 16, 15))
        pygame.draw.rect(surface, (200, 200, 255),
                        (rect.x + 8, rect.y + rect.height - 25, rect.width - 16, 15))

class OilSlick:
    def __init__(self, y_offset):
        self.lane = random.randint(0, NUM_LANES - 1)
        self.x = ROAD_LEFT + self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.y = y_offset
        self.radius = 30

    def update(self, player_speed, world_speed):
        self.y += (player_speed + world_speed)

    def get_rect(self):
        return pygame.Rect(self.x - self.radius, self.y - self.radius,
                          self.radius * 2, self.radius * 2)

    def draw(self, surface):
        pygame.draw.ellipse(surface, COLOR_OIL_SLICK,
                          (self.x - self.radius, self.y - self.radius,
                           self.radius * 2, self.radius * 2))
        pygame.draw.ellipse(surface, (60, 60, 60),
                          (self.x - self.radius + 3, self.y - self.radius + 3,
                           self.radius * 2 - 6, self.radius * 2 - 6))

class FuelItem:
    def __init__(self, y_offset):
        self.lane = random.randint(0, NUM_LANES - 1)
        self.x = ROAD_LEFT + self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.y = y_offset
        self.size = 25

    def update(self, player_speed, world_speed):
        self.y += (player_speed + world_speed)

    def get_rect(self):
        return pygame.Rect(self.x - self.size // 2, self.y - self.size // 2,
                          self.size, self.size)

    def draw(self, surface):
        pygame.draw.circle(surface, COLOR_FUEL, (self.x, self.y), self.size // 2)
        pygame.draw.circle(surface, (30, 150, 30), (self.x, self.y), self.size // 2, 2)
        font = pygame.font.Font(None, 24)
        text = font.render("F", True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.x, self.y))
        surface.blit(text, text_rect)

class Player:
    def __init__(self):
        self.lane = 1
        self.target_lane = 1
        self.x = ROAD_LEFT + self.lane * LANE_WIDTH + LANE_WIDTH // 2
        self.target_x = self.x
        self.y = SCREEN_HEIGHT - 120
        self.width = CAR_WIDTH
        self.height = CAR_HEIGHT
        self.speed = 3
        self.target_speed = 3
        self.max_speed = 8
        self.boosting = False
        self.fuel = MAX_FUEL
        self.crashed = False
        self.crash_timer = 0
        self.control_lost = False
        self.control_lost_timer = 0
        self.drift_direction = 0

    def update(self, world_speed):
        if self.crashed:
            self.crash_timer -= 1
            if self.crash_timer <= 0:
                self.crashed = False
                self.speed = 2
                self.target_speed = 2
            return

        if self.control_lost:
            self.control_lost_timer -= 1
            self.x += self.drift_direction * 3
            if self.control_lost_timer <= 0:
                self.control_lost = False
                if self.x < ROAD_LEFT + LANE_WIDTH // 2:
                    self.lane = 0
                    self.target_lane = 0
                elif self.x > ROAD_RIGHT - LANE_WIDTH // 2:
                    self.lane = NUM_LANES - 1
                    self.target_lane = NUM_LANES - 1
                else:
                    self.lane = int((self.x - ROAD_LEFT) // LANE_WIDTH)
                    self.target_lane = self.lane
            return

        lane_speed = 0.15
        self.target_x = ROAD_LEFT + self.target_lane * LANE_WIDTH + LANE_WIDTH // 2
        self.x += (self.target_x - self.x) * lane_speed

        speed_change = 0.1
        if self.boosting:
            self.target_speed = self.max_speed
        else:
            self.target_speed = 3

        if self.speed < self.target_speed:
            self.speed = min(self.target_speed, self.speed + speed_change)
        elif self.speed > self.target_speed:
            self.speed = max(self.target_speed, self.speed - speed_change)

        fuel_drain = 0.02 + (self.speed * 0.015)
        if self.boosting:
            fuel_drain *= BOOST_FUEL_MULTIPLIER
        self.fuel = max(0, self.fuel - fuel_drain)

    def move_left(self):
        if not self.crashed and not self.control_lost:
            self.target_lane = max(0, self.target_lane - 1)

    def move_right(self):
        if not self.crashed and not self.control_lost:
            self.target_lane = min(NUM_LANES - 1, self.target_lane + 1)

    def set_boost(self, boosting):
        self.boosting = boosting

    def crash(self):
        self.crashed = True
        self.crash_timer = 60
        self.fuel = max(0, self.fuel - CRASH_PENALTY)

    def hit_oil(self):
        self.control_lost = True
        self.control_lost_timer = 60
        self.drift_direction = random.choice([-1, 1])

    def get_rect(self):
        return pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                          self.width, self.height)

    def draw(self, surface):
        rect = self.get_rect()
        color = COLOR_PLAYER if not self.control_lost else (200, 200, 100)
        pygame.draw.rect(surface, color, rect, border_radius=5)
        pygame.draw.rect(surface, COLOR_PLAYER_OUTLINE, rect, 2, border_radius=5)

        pygame.draw.rect(surface, (150, 200, 255),
                        (rect.x + 8, rect.y + 8, rect.width - 16, 20))
        pygame.draw.rect(surface, (150, 200, 255),
                        (rect.x + 8, rect.y + rect.height - 28, rect.width - 16, 20))

        if self.boosting and not self.crashed and not self.control_lost:
            flame_points = [
                (rect.centerx - 10, rect.bottom),
                (rect.centerx, rect.bottom + random.randint(10, 20)),
                (rect.centerx + 10, rect.bottom)
            ]
            pygame.draw.polygon(surface, (255, 100, 0), flame_points)
            pygame.draw.polygon(surface, (255, 200, 0),
                               [(rect.centerx - 5, rect.bottom),
                                (rect.centerx, rect.bottom + random.randint(5, 10)),
                                (rect.centerx + 5, rect.bottom)])

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Road Fighter Nitro Drift")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 48)
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.npcs = []
        self.oil_slicks = []
        self.fuel_items = []
        self.distance = 0
        self.cars_overtaken = 0
        self.score = 0
        self.game_over = False
        self.won = False
        self.spawn_timer = 0
        self.world_speed = 0
        self.difficulty = 1

    def spawn_entities(self):
        self.spawn_timer += 1

        spawn_rate = max(30, 60 - self.difficulty * 5)

        if self.spawn_timer >= spawn_rate:
            self.spawn_timer = 0

            spawn_type = random.random()

            if spawn_type < 0.6:
                npc_type = "civilian" if random.random() < 0.7 else "erratic"
                self.npcs.append(NPC(-100, npc_type))
            elif spawn_type < 0.8:
                self.oil_slicks.append(OilSlick(-50))
            else:
                self.fuel_items.append(FuelItem(-50))

    def check_collisions(self):
        player_rect = self.player.get_rect()

        for npc in self.npcs[:]:
            if player_rect.colliderect(npc.get_rect()):
                self.player.crash()
                npc_rect = npc.get_rect()
                overlap_x = min(player_rect.right - npc_rect.left,
                               npc_rect.right - player_rect.left)
                overlap_y = min(player_rect.bottom - npc_rect.top,
                               npc_rect.bottom - player_rect.top)
                if overlap_x < overlap_y:
                    if player_rect.centerx < npc_rect.centerx:
                        self.player.x -= overlap_x
                    else:
                        self.player.x += overlap_x
                else:
                    self.player.y += overlap_y

        for oil in self.oil_slicks[:]:
            if player_rect.colliderect(oil.get_rect()):
                if not self.player.control_lost:
                    self.player.hit_oil()

        for fuel in self.fuel_items[:]:
            if player_rect.colliderect(fuel.get_rect()):
                self.player.fuel = min(MAX_FUEL, self.player.fuel + 25)
                self.fuel_items.remove(fuel)

    def check_boundaries(self):
        if self.player.x - self.player.width // 2 < ROAD_LEFT:
            self.player.crash()
            self.player.x = ROAD_LEFT + self.player.width // 2 + 5
        elif self.player.x + self.player.width // 2 > ROAD_RIGHT:
            self.player.crash()
            self.player.x = ROAD_RIGHT - self.player.width // 2 - 5

    def update(self):
        if self.game_over or self.won:
            return

        self.difficulty = 1 + self.distance / 2000
        self.world_speed = 0.5 + self.difficulty * 0.3

        self.player.update(self.world_speed)
        self.spawn_entities()
        self.check_collisions()
        self.check_boundaries()

        self.distance += self.player.speed

        for npc in self.npcs[:]:
            npc.update(self.player.speed, self.world_speed)
            if npc.y > SCREEN_HEIGHT + 100:
                if not npc.overtaken:
                    npc.overtaken = True
                    self.cars_overtaken += 1
                    self.score += 10
                self.npcs.remove(npc)

        for oil in self.oil_slicks[:]:
            oil.update(self.player.speed, self.world_speed)
            if oil.y > SCREEN_HEIGHT + 50:
                self.oil_slicks.remove(oil)

        for fuel in self.fuel_items[:]:
            fuel.update(self.player.speed, self.world_speed)
            if fuel.y > SCREEN_HEIGHT + 50:
                self.fuel_items.remove(fuel)

        self.score = int(self.distance + self.cars_overtaken * 10)

        if self.player.fuel <= 0:
            self.game_over = True
        elif self.distance >= FUEL_DISTANCE:
            self.won = True

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if self.game_over or self.won:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                    elif event.key == pygame.K_ESCAPE:
                        return False
                else:
                    if event.key == pygame.K_ESCAPE:
                        return False

        keys = pygame.key.get_pressed()
        if not self.game_over and not self.won:
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            if keys[pygame.K_RIGHT]:
                self.player.move_right()
            self.player.set_boost(keys[pygame.K_UP])

        return True

    def draw(self):
        self.screen.fill(COLOR_BG)

        pygame.draw.rect(self.screen, COLOR_GRASS, (0, 0, ROAD_LEFT, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_GRASS, (ROAD_RIGHT, 0, SCREEN_WIDTH - ROAD_RIGHT, SCREEN_HEIGHT))
        pygame.draw.rect(self.screen, COLOR_ROAD, (ROAD_LEFT, 0, ROAD_RIGHT - ROAD_LEFT, SCREEN_HEIGHT))

        for i in range(1, NUM_LANES):
            x = ROAD_LEFT + i * LANE_WIDTH
            for y in range(-50, SCREEN_HEIGHT + 50, 60):
                offset = (self.distance % 60) - 30
                pygame.draw.line(self.screen, COLOR_ROAD_LINE, (x, y + offset), (x, y + offset + 30), 2)

        road_left_line = ROAD_LEFT
        road_right_line = ROAD_RIGHT
        for y in range(-50, SCREEN_HEIGHT + 50, 40):
            offset = (self.distance % 40) - 20
            pygame.draw.line(self.screen, (255, 255, 255),
                           (road_left_line, y + offset), (road_left_line, y + offset + 20), 3)
            pygame.draw.line(self.screen, (255, 255, 255),
                           (road_right_line, y + offset), (road_right_line, y + offset + 20), 3)

        for npc in self.npcs:
            npc.draw(self.screen)

        for oil in self.oil_slicks:
            oil.draw(self.screen)

        for fuel in self.fuel_items:
            fuel.draw(self.screen)

        self.player.draw(self.screen)

        fuel_bar_width = 200
        fuel_bar_height = 20
        fuel_bar_x = 10
        fuel_bar_y = 10

        pygame.draw.rect(self.screen, COLOR_FUEL_BAR_BG,
                        (fuel_bar_x, fuel_bar_y, fuel_bar_width, fuel_bar_height))
        pygame.draw.rect(self.screen, COLOR_FUEL_BAR,
                        (fuel_bar_x, fuel_bar_y, fuel_bar_width * (self.player.fuel / MAX_FUEL), fuel_bar_height))
        pygame.draw.rect(self.screen, (255, 255, 255),
                        (fuel_bar_x, fuel_bar_y, fuel_bar_width, fuel_bar_height), 2)

        fuel_text = self.small_font.render("FUEL", True, (255, 255, 255))
        self.screen.blit(fuel_text, (fuel_bar_x + fuel_bar_width + 10, fuel_bar_y))

        distance_text = self.small_font.render(f"Distance: {int(self.distance)}m", True, COLOR_TEXT)
        score_text = self.small_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        overtaken_text = self.small_font.render(f"Overtaken: {self.cars_overtaken}", True, COLOR_TEXT)

        self.screen.blit(distance_text, (10, 40))
        self.screen.blit(score_text, (10, 60))
        self.screen.blit(overtaken_text, (10, 80))

        goal_distance = max(0, FUEL_DISTANCE - self.distance)
        goal_text = self.small_font.render(f"Goal: {int(goal_distance)}m", True, COLOR_TEXT)
        goal_rect = goal_text.get_rect(right=SCREEN_WIDTH - 10, top=10)
        self.screen.blit(goal_text, goal_rect)

        speed_text = self.small_font.render(f"Speed: {self.player.speed * 20:.0f} km/h", True, COLOR_TEXT)
        speed_rect = speed_text.get_rect(right=SCREEN_WIDTH - 10, top=35)
        self.screen.blit(speed_text, speed_rect)

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            msg_text = self.large_font.render("GAME OVER", True, COLOR_TEXT)
            score_msg = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            distance_msg = self.small_font.render(f"Distance: {int(self.distance)}m / {FUEL_DISTANCE}m", True, COLOR_TEXT)
            overtaken_msg = self.small_font.render(f"Overtaken: {self.cars_overtaken}", True, COLOR_TEXT)
            retry_msg = self.small_font.render("Press SPACE to retry or ESC to quit", True, COLOR_TEXT)

            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            score_rect = score_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
            distance_rect = distance_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            overtaken_rect = overtaken_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 45))
            retry_rect = retry_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))

            self.screen.blit(msg_text, msg_rect)
            self.screen.blit(score_msg, score_rect)
            self.screen.blit(distance_msg, distance_rect)
            self.screen.blit(overtaken_msg, overtaken_rect)
            self.screen.blit(retry_msg, retry_rect)

        elif self.won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            msg_text = self.large_font.render("GOAL REACHED!", True, COLOR_TEXT)
            score_msg = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            overtaken_msg = self.small_font.render(f"Overtaken: {self.cars_overtaken}", True, COLOR_TEXT)
            fuel_msg = self.small_font.render(f"Fuel Remaining: {int(self.player.fuel)}%", True, COLOR_TEXT)
            retry_msg = self.small_font.render("Press SPACE to play again or ESC to quit", True, COLOR_TEXT)

            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 60))
            score_rect = score_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 10))
            overtaken_rect = overtaken_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
            fuel_rect = fuel_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 45))
            retry_rect = retry_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))

            self.screen.blit(msg_text, msg_rect)
            self.screen.blit(score_msg, score_rect)
            self.screen.blit(overtaken_msg, overtaken_rect)
            self.screen.blit(fuel_msg, fuel_rect)
            self.screen.blit(retry_msg, retry_rect)

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
