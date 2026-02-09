"""
Vector Mario Platformer Lite
A minimalist side-scrolling platformer game.
"""

import pygame
import sys
from pathlib import Path

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BG = (135, 206, 235)  # Sky blue
COLOR_GROUND = (139, 69, 19)  # Brown
COLOR_PLATFORM = (100, 50, 0)
COLOR_PLAYER = (255, 0, 0)  # Red
COLOR_ENEMY = (128, 0, 128)  # Purple
COLOR_COIN = (255, 215, 0)  # Gold
COLOR_FLAG = (0, 128, 0)  # Green
COLOR_FLAG_POLE = (139, 90, 43)
COLOR_TEXT = (0, 0, 0)

# Physics
GRAVITY = 0.8
ACCELERATION = 0.5
FRICTION = 0.85
MAX_SPEED = 6
JUMP_FORCE = -14
JUMP_HOLD_FORCE = -0.5
MAX_JUMP_HOLD = 10

# Game dimensions
TILE_SIZE = 40


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 30
        self.height = 40
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(COLOR_PLAYER)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        # Physics
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.jump_held = 0
        self.is_jumping = False
        self.alive = True

        # Score tracking
        self.score = 0
        self.coins_collected = 0
        self.enemies_defeated = 0
        self.reached_goal = False

    def update(self, keys, platforms):
        if not self.alive:
            return

        # Horizontal movement
        if keys[pygame.K_LEFT]:
            self.vel_x -= ACCELERATION
        if keys[pygame.K_RIGHT]:
            self.vel_x += ACCELERATION

        # Apply friction
        self.vel_x *= FRICTION

        # Clamp horizontal speed
        self.vel_x = max(-MAX_SPEED, min(MAX_SPEED, self.vel_x))

        # Jumping
        if keys[pygame.K_SPACE] or keys[pygame.K_UP]:
            if self.on_ground and not self.is_jumping:
                self.vel_y = JUMP_FORCE
                self.is_jumping = True
                self.jump_held = 0
                self.on_ground = False
            elif self.is_jumping and self.jump_held < MAX_JUMP_HOLD:
                self.vel_y += JUMP_HOLD_FORCE
                self.jump_held += 1

        # Apply gravity
        self.vel_y += GRAVITY

        # Update position
        self.rect.x += int(self.vel_x)
        self.check_horizontal_collision(platforms)

        self.rect.y += int(self.vel_y)
        self.check_vertical_collision(platforms)

        # Check if fell off map
        if self.rect.y > SCREEN_HEIGHT + 100:
            self.alive = False

    def check_horizontal_collision(self, platforms):
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_x > 0:
                    self.rect.right = platform.rect.left
                elif self.vel_x < 0:
                    self.rect.left = platform.rect.right
                self.vel_x = 0

    def check_vertical_collision(self, platforms):
        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform.rect):
                if self.vel_y > 0:
                    self.rect.bottom = platform.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.is_jumping = False
                elif self.vel_y < 0:
                    self.rect.top = platform.rect.bottom
                    self.vel_y = 0


class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, patrol_range):
        super().__init__()
        self.width = 30
        self.height = 30
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(COLOR_ENEMY)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

        self.start_x = x
        self.patrol_range = patrol_range
        self.speed = 2
        self.direction = 1
        self.alive = True

    def update(self):
        if not self.alive:
            return

        self.rect.x += self.speed * self.direction

        # Reverse direction at patrol limits
        if self.rect.x > self.start_x + self.patrol_range:
            self.direction = -1
        elif self.rect.x < self.start_x:
            self.direction = 1


class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.size = 20
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(COLOR_COIN)
        self.rect = self.image.get_rect()
        self.rect.center = (x, y)
        self.collected = False


class Platform(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(COLOR_PLATFORM)
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y


class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.width = 20
        self.height = 120
        self.image = pygame.Surface((self.width, self.height))
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.reached = False


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Mario Platformer Lite")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        # Camera
        self.camera_x = 0
        self.level_width = 3200

        self.reset_game()

    def reset_game(self):
        self.player = Player(100, SCREEN_HEIGHT - 150)
        self.platforms = self.create_level()
        self.enemies = pygame.sprite.Group()
        self.coins = pygame.sprite.Group()
        self.flag = None

        self.create_enemies()
        self.create_coins()
        self.create_flag()

        self.lives = 3
        self.game_over = False
        self.victory = False
        self.camera_x = 0

    def create_level(self):
        platforms = pygame.sprite.Group()

        # Ground segments with gaps
        ground_data = [
            (0, SCREEN_HEIGHT - 40, 600, 40),
            (700, SCREEN_HEIGHT - 40, 400, 40),
            (1200, SCREEN_HEIGHT - 40, 300, 40),
            (1600, SCREEN_HEIGHT - 40, 500, 40),
            (2200, SCREEN_HEIGHT - 40, 400, 40),
            (2700, SCREEN_HEIGHT - 40, 500, 40),
        ]

        for x, y, w, h in ground_data:
            platforms.add(Platform(x, y, w, h))

        # Floating platforms
        platform_data = [
            (300, 450, 150, 20),
            (500, 350, 100, 20),
            (800, 400, 120, 20),
            (1050, 300, 100, 20),
            (1400, 380, 80, 20),
            (1750, 420, 150, 20),
            (2000, 320, 100, 20),
            (2350, 400, 120, 20),
            (2550, 350, 80, 20),
        ]

        for x, y, w, h in platform_data:
            platforms.add(Platform(x, y, w, h))

        return platforms

    def create_enemies(self):
        enemy_positions = [
            (400, SCREEN_HEIGHT - 70, 150),
            (800, SCREEN_HEIGHT - 70, 200),
            (1300, SCREEN_HEIGHT - 70, 100),
            (1800, SCREEN_HEIGHT - 70, 250),
            (2300, SCREEN_HEIGHT - 70, 150),
            (2800, SCREEN_HEIGHT - 70, 180),
        ]

        for x, y, patrol in enemy_positions:
            self.enemies.add(Enemy(x, y, patrol))

    def create_coins(self):
        coin_positions = [
            (350, 420),
            (400, 420),
            (450, 420),
            (530, 320),
            (850, 370),
            (1080, 270),
            (1430, 350),
            (1800, 390),
            (1850, 390),
            (2030, 290),
            (2400, 370),
            (2570, 320),
        ]

        for x, y in coin_positions:
            self.coins.add(Coin(x, y))

    def create_flag(self):
        # Place flag at the end
        self.flag = Flag(3050, SCREEN_HEIGHT - 160)

    def update_camera(self):
        # Camera follows player with some offset
        target_x = self.player.rect.centerx - SCREEN_WIDTH // 3
        self.camera_x += (target_x - self.camera_x) * 0.1

        # Clamp camera
        self.camera_x = max(0, min(self.camera_x, self.level_width - SCREEN_WIDTH))

    def check_collisions(self):
        if not self.player.alive:
            return

        # Coin collection
        coin_hits = pygame.sprite.spritecollide(self.player, self.coins, False)
        for coin in coin_hits:
            if not coin.collected:
                coin.collected = True
                self.player.coins_collected += 1
                self.player.score += 100

        # Enemy collision
        enemy_hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
        for enemy in enemy_hits:
            if not enemy.alive:
                continue

            # Check if player is falling on enemy
            if self.player.vel_y > 0 and self.player.rect.bottom - 10 < enemy.rect.centery:
                enemy.alive = False
                self.player.enemies_defeated += 1
                self.player.score += 200
                self.player.vel_y = JUMP_FORCE // 2  # Small bounce
            else:
                # Player hit by enemy
                self.player.alive = False

        # Flag collision
        if self.flag and not self.flag.reached:
            if self.player.rect.colliderect(self.flag.rect):
                self.flag.reached = True
                self.player.reached_goal = True
                self.player.score += 1000
                self.victory = True

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Apply camera offset
        offset = int(-self.camera_x)

        # Draw platforms
        for platform in self.platforms:
            self.screen.blit(platform.image, (platform.rect.x + offset, platform.rect.y))

        # Draw coins
        for coin in self.coins:
            if not coin.collected:
                self.screen.blit(coin.image, (coin.rect.x + offset, coin.rect.y))

        # Draw enemies
        for enemy in self.enemies:
            if enemy.alive:
                self.screen.blit(enemy.image, (enemy.rect.x + offset, enemy.rect.y))

        # Draw flag
        if self.flag:
            # Draw pole
            pygame.draw.rect(self.screen, COLOR_FLAG_POLE,
                           (self.flag.rect.x + offset + 8, self.flag.rect.y, 4, self.flag.height))
            # Draw flag
            flag_rect = pygame.Rect(self.flag.rect.x + offset + 12, self.flag.rect.y, 30, 20)
            pygame.draw.rect(self.screen, COLOR_FLAG, flag_rect)

        # Draw player
        if self.player.alive:
            self.screen.blit(self.player.image, (self.player.rect.x + offset, self.player.rect.y))

        # Draw HUD
        self.draw_hud()

        # Draw game over or victory screen
        if self.game_over:
            self.draw_message("GAME OVER", "Press R to restart")
        elif self.victory:
            self.draw_message("VICTORY!", f"Score: {self.player.score} - Press R to restart")

        pygame.display.flip()

    def draw_hud(self):
        # Score
        score_text = self.small_font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        # Lives
        lives_text = self.small_font.render(f"Lives: {self.lives}", True, COLOR_TEXT)
        self.screen.blit(lives_text, (10, 35))

        # Coins
        coins_text = self.small_font.render(f"Coins: {self.player.coins_collected}", True, COLOR_TEXT)
        self.screen.blit(coins_text, (10, 60))

    def draw_message(self, title, subtitle):
        title_surface = self.font.render(title, True, COLOR_TEXT)
        subtitle_surface = self.small_font.render(subtitle, True, COLOR_TEXT)

        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        subtitle_rect = subtitle_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))

        # Semi-transparent background
        bg_rect = pygame.Rect(0, 0, 400, 120)
        bg_rect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        pygame.draw.rect(self.screen, (255, 255, 255), bg_rect)
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
                    elif event.key == pygame.K_r:
                        self.reset_game()

            # Update
            if not self.game_over and not self.victory:
                keys = pygame.key.get_pressed()
                self.player.update(keys, self.platforms)

                for enemy in self.enemies:
                    enemy.update()

                self.check_collisions()
                self.update_camera()

                # Check if player died
                if not self.player.alive:
                    self.lives -= 1
                    if self.lives <= 0:
                        self.game_over = True
                    else:
                        # Respawn
                        self.player.alive = True
                        self.player.rect.x = 100
                        self.player.rect.y = SCREEN_HEIGHT - 150
                        self.player.vel_x = 0
                        self.player.vel_y = 0
                        self.camera_x = 0

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
