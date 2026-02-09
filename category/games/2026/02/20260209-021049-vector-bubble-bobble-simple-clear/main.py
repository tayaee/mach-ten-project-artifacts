"""
Vector Bubble Bobble Simple Clear
Trap monsters in bubbles and pop them to clear the screen.
"""

import pygame
import sys
import random
from pathlib import Path

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
COLOR_BG = (15, 15, 25)
COLOR_PLATFORM = (100, 80, 60)
COLOR_PLATFORM_TOP = (140, 110, 80)
COLOR_PLAYER = (50, 150, 255)
COLOR_PLAYER_OUTLINE = (30, 100, 200)
COLOR_MONSTER = (255, 80, 80)
COLOR_MONSTER_OUTLINE = (200, 50, 50)
COLOR_BUBBLE = (100, 200, 255)
COLOR_BUBBLE_SHINE = (200, 240, 255)
COLOR_TEXT = (255, 255, 255)

# Game physics
GRAVITY = 0.5
PLAYER_SPEED = 4
JUMP_FORCE = -11
BUBBLE_SPEED = 6
BUBBLE_RISE_SPEED = 1.5
MONSTER_SPEED = 1.5
ESCAPE_TIME = 300  # Frames before monster escapes bubble (5 seconds at 60fps)
COOLDOWN_TIME = 30  # Cooldown between shooting bubbles

# Platform settings
PLATFORM_HEIGHT = 20
NUM_PLATFORMS = 6


class Platform:
    def __init__(self, x, y, width):
        self.rect = pygame.Rect(x, y, width, PLATFORM_HEIGHT)

    def draw(self, surface):
        # Main platform body
        pygame.draw.rect(surface, COLOR_PLATFORM, self.rect)
        # Top surface
        top_rect = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 4)
        pygame.draw.rect(surface, COLOR_PLATFORM_TOP, top_rect)


class Bubble:
    def __init__(self, x, y, direction, player):
        self.x = x
        self.y = y
        self.radius = 18
        self.direction = direction
        self.active = True
        self.has_monster = False
        self.monster = None
        self.escape_timer = 0
        self.player = player
        self.popped = False

    def update(self, platforms):
        if not self.active:
            return

        if self.has_monster:
            # Float upward with trapped monster
            self.y -= BUBBLE_RISE_SPEED

            # Bounce horizontally
            self.x += self.direction * 0.5
            if self.x <= self.radius + 10 or self.x >= SCREEN_WIDTH - self.radius - 10:
                self.direction *= -1

            # Check if player touches to pop
            player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
            bubble_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)

            if bubble_rect.colliderect(player_rect):
                self.popped = True
                self.active = False
                return "pop"

            # Escape timer
            self.escape_timer += 1
            if self.escape_timer >= ESCAPE_TIME:
                # Monster escapes
                if self.monster:
                    self.monster.escaped = True
                    self.monster.x = int(self.x)
                    self.monster.y = int(self.y)
                    self.monster.speed = MONSTER_SPEED * 1.5  # Faster after escape
                self.active = False
                return "escape"

            # Pop if hits top of screen
            if self.y <= self.radius + 5:
                self.popped = True
                self.active = False
                if self.monster:
                    self.monster.active = False
                return "pop_top"

        else:
            # Moving horizontally
            self.x += BUBBLE_SPEED * self.direction

            # Remove if off screen
            if self.x < -50 or self.x > SCREEN_WIDTH + 50:
                self.active = False

            # Check platform collision
            bubble_rect = pygame.Rect(self.x - self.radius, self.y - self.radius, self.radius * 2, self.radius * 2)
            for platform in platforms:
                if bubble_rect.colliderect(platform.rect):
                    # Bounce or pop
                    self.direction *= -1
                    self.x += self.direction * 5

        return None

    def trap_monster(self, monster):
        self.has_monster = True
        self.monster = monster
        monster.trapped = True

    def draw(self, surface):
        if not self.active:
            return

        # Main bubble
        pygame.draw.circle(surface, COLOR_BUBBLE, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(surface, (80, 180, 230), (int(self.x), int(self.y)), self.radius, 2)

        # Shine effect
        shine_pos = (int(self.x - 6), int(self.y - 6))
        pygame.draw.circle(surface, COLOR_BUBBLE_SHINE, shine_pos, 5)

        if self.has_monster and self.monster:
            # Draw trapped monster inside bubble
            monster_size = 14
            monster_rect = pygame.Rect(
                int(self.x) - monster_size // 2,
                int(self.y) - monster_size // 2,
                monster_size,
                monster_size
            )
            pygame.draw.rect(surface, COLOR_MONSTER, monster_rect)
            pygame.draw.rect(surface, COLOR_MONSTER_OUTLINE, monster_rect, 2)


class Monster:
    def __init__(self, x, y, platforms):
        self.width = 24
        self.height = 24
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.speed = MONSTER_SPEED
        self.direction = random.choice([-1, 1])
        self.platforms = platforms
        self.active = True
        self.trapped = False
        self.escaped = False
        self.jump_timer = 0
        self.on_ground = False

    def update(self):
        if not self.active or self.trapped:
            return

        # Jump occasionally
        self.jump_timer += 1
        if self.on_ground and self.jump_timer > 60:
            if random.random() < 0.02:
                self.vel_y = JUMP_FORCE * 0.7
                self.jump_timer = 0

        # Apply gravity
        self.vel_y += GRAVITY

        # Horizontal movement
        self.vel_x = self.direction * self.speed

        # Apply horizontal movement
        new_x = self.x + self.vel_x
        if new_x <= 10 or new_x >= SCREEN_WIDTH - self.width - 10:
            self.direction *= -1
            new_x = self.x

        self.x = new_x

        # Apply vertical movement
        self.y += self.vel_y

        # Platform collision
        self.on_ground = False
        monster_rect = pygame.Rect(self.x, self.y, self.width, self.height)

        for platform in self.platforms:
            if (monster_rect.colliderect(platform.rect) and
                self.vel_y > 0 and
                self.y + self.height - 5 <= platform.rect.y + 5):
                self.y = platform.rect.y - self.height
                self.vel_y = 0
                self.on_ground = True

        # Bottom boundary
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True

    def draw(self, surface):
        if not self.active or self.trapped:
            return

        # Monster body
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, COLOR_MONSTER, rect)
        pygame.draw.rect(surface, COLOR_MONSTER_OUTLINE, rect, 2)

        # Eyes
        eye_color = (255, 255, 255)
        pupil_color = (0, 0, 0)
        pygame.draw.circle(surface, eye_color, (int(self.x + 7), int(self.y + 9)), 4)
        pygame.draw.circle(surface, eye_color, (int(self.x + 17), int(self.y + 9)), 4)
        pygame.draw.circle(surface, pupil_color, (int(self.x + 7), int(self.y + 9)), 2)
        pygame.draw.circle(surface, pupil_color, (int(self.x + 17), int(self.y + 9)), 2)


class Player:
    def __init__(self):
        self.width = 28
        self.height = 36
        self.x = SCREEN_WIDTH // 2
        self.y = SCREEN_HEIGHT - 60
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.alive = True
        self.score = 0
        self.bubbles = []
        self.cooldown = 0
        self.facing_direction = 1  # 1 for right, -1 for left

    def update(self, keys, platforms):
        if not self.alive:
            return

        # Update cooldown
        if self.cooldown > 0:
            self.cooldown -= 1

        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -PLAYER_SPEED
            self.facing_direction = -1
        if keys[pygame.K_RIGHT]:
            self.vel_x = PLAYER_SPEED
            self.facing_direction = 1

        # Jumping
        if self.on_ground and keys[pygame.K_SPACE]:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

        # Gravity
        self.vel_y += GRAVITY

        # Apply horizontal movement
        new_x = self.x + self.vel_x
        new_x = max(10, min(new_x, SCREEN_WIDTH - self.width - 10))
        self.x = new_x

        # Apply vertical movement
        new_y = self.y + self.vel_y

        # Platform collision
        self.on_ground = False
        player_rect = pygame.Rect(self.x, new_y, self.width, self.height)

        for platform in platforms:
            if (player_rect.colliderect(platform.rect) and
                self.vel_y > 0 and
                self.y + self.height - 10 <= platform.rect.y):
                self.y = platform.rect.y - self.height
                self.vel_y = 0
                self.on_ground = True
                break

        if not self.on_ground:
            self.y = new_y

        # Bottom boundary
        if self.y > SCREEN_HEIGHT - self.height:
            self.y = SCREEN_HEIGHT - self.height
            self.vel_y = 0
            self.on_ground = True

    def shoot_bubble(self):
        if self.cooldown == 0:
            bubble_x = self.x + self.width // 2
            bubble_y = self.y + 10
            bubble = Bubble(bubble_x, bubble_y, self.facing_direction, self)
            self.bubbles.append(bubble)
            self.cooldown = COOLDOWN_TIME

    def draw(self, surface):
        if not self.alive:
            return

        # Body
        body_rect = pygame.Rect(self.x, self.y + 12, self.width, self.height - 12)
        pygame.draw.rect(surface, COLOR_PLAYER, body_rect)
        pygame.draw.rect(surface, COLOR_PLAYER_OUTLINE, body_rect, 2)

        # Head
        head_rect = pygame.Rect(self.x + 4, self.y, self.width - 8, 16)
        pygame.draw.rect(surface, COLOR_PLAYER, head_rect)
        pygame.draw.rect(surface, COLOR_PLAYER_OUTLINE, head_rect, 2)

        # Eyes
        eye_y = self.y + 6
        if self.facing_direction == 1:
            eye_x1, eye_x2 = self.x + 10, self.x + 18
        else:
            eye_x1, eye_x2 = self.x + 6, self.x + 14

        pygame.draw.circle(surface, (255, 255, 255), (eye_x1, eye_y), 3)
        pygame.draw.circle(surface, (255, 255, 255), (eye_x2, eye_y), 3)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x1, eye_y), 1)
        pygame.draw.circle(surface, (0, 0, 0), (eye_x2, eye_y), 1)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Bubble Bobble Simple Clear")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)

        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.platforms = []
        self.monsters = []
        self.bubbles = []
        self.game_over = False
        self.victory = False
        self.level = 1

        self.create_level()

    def create_level(self):
        # Create platforms
        # Bottom floor
        self.platforms.append(Platform(0, SCREEN_HEIGHT - 20, SCREEN_WIDTH))

        # Additional platforms
        platform_y_positions = [480, 390, 300, 210, 120]

        for i, y in enumerate(platform_y_positions):
            # Alternating platform positions
            if i % 2 == 0:
                x = 50
                width = 300
            else:
                x = 450
                width = 300

            self.platforms.append(Platform(x, y, width))

            # Add second platform on this level for some rows
            if i in [1, 3]:
                if x == 50:
                    self.platforms.append(Platform(450, y, 300))
                else:
                    self.platforms.append(Platform(50, y, 300))

        # Create monsters
        num_monsters = 4 + self.level

        for i in range(num_monsters):
            # Place monsters on upper platforms
            platform_idx = (i % len(self.platforms))
            if platform_idx == 0:
                platform_idx = 1  # Skip floor

            platform = self.platforms[platform_idx]
            x = platform.rect.x + random.randint(20, platform.rect.width - 40)
            y = platform.rect.y - 30

            monster = Monster(x, y, self.platforms)
            self.monsters.append(monster)

    def update(self):
        if self.game_over or self.victory:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.platforms)

        # Update monsters
        for monster in self.monsters:
            monster.update()

            # Check collision with player
            if monster.active and not monster.trapped:
                player_rect = pygame.Rect(self.player.x, self.player.y, self.player.width, self.player.height)
                monster_rect = pygame.Rect(monster.x, monster.y, monster.width, monster.height)

                if player_rect.colliderect(monster_rect):
                    self.game_over = True
                    self.player.alive = False

        # Update player bubbles
        self.player.bubbles = [b for b in self.player.bubbles if b.active]
        for bubble in self.player.bubbles:
            result = bubble.update(self.platforms)

            if result == "pop":
                self.player.score += 50

            # Check collision with monsters
            if not bubble.has_monster:
                for monster in self.monsters:
                    if monster.active and not monster.trapped:
                        monster_rect = pygame.Rect(monster.x, monster.y, monster.width, monster.height)
                        bubble_rect = pygame.Rect(
                            bubble.x - bubble.radius,
                            bubble.y - bubble.radius,
                            bubble.radius * 2,
                            bubble.radius * 2
                        )

                        if bubble_rect.colliderect(monster_rect):
                            bubble.trap_monster(monster)
                            self.player.score += 10
                            break

        # Check victory condition
        active_monsters = [m for m in self.monsters if m.active and not m.trapped]
        if not active_monsters:
            self.victory = True
            self.player.score += 100

    def shoot_bubble(self):
        if not self.game_over and not self.victory:
            self.player.shoot_bubble()

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw monsters
        for monster in self.monsters:
            monster.draw(self.screen)

        # Draw bubbles (both player's and floating)
        for bubble in self.player.bubbles:
            bubble.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        self.draw_hud()

        # Draw game over/victory screen
        if self.game_over:
            self.draw_message("GAME OVER", f"Score: {self.player.score} - Press R to restart")
        elif self.victory:
            self.draw_message("LEVEL CLEARED!", f"Score: {self.player.score} - Press R for next level")

        pygame.display.flip()

    def draw_hud(self):
        # Score
        score_text = self.small_font.render(f"Score: {self.player.score}", True, COLOR_TEXT)
        self.screen.blit(score_text, (15, 15))

        # Level
        level_text = self.small_font.render(f"Level: {self.level}", True, COLOR_TEXT)
        self.screen.blit(level_text, (15, 45))

        # Monsters remaining
        active_monsters = sum(1 for m in self.monsters if m.active and not m.trapped)
        monster_text = self.small_font.render(f"Monsters: {active_monsters}", True, COLOR_TEXT)
        self.screen.blit(monster_text, (15, 75))

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

    def next_level(self):
        self.level += 1
        self.player.x = SCREEN_WIDTH // 2
        self.player.y = SCREEN_HEIGHT - 60
        self.player.vel_x = 0
        self.player.vel_y = 0
        self.player.bubbles.clear()
        self.monsters.clear()
        self.platforms.clear()
        self.victory = False

        self.create_level()

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
                        if self.victory:
                            self.next_level()
                        else:
                            self.reset_game()
                    elif event.key == pygame.K_SPACE:
                        # Space for jump is handled in update, but we need to prevent
                        # it from shooting bubbles simultaneously
                        pass

            # Check for bubble shooting (Z key or separate check)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_z]:
                self.shoot_bubble()

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
