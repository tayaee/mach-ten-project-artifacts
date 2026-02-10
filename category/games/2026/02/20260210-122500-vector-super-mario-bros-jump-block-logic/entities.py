import pygame
from config import *


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = PLAYER_WIDTH
        self.height = PLAYER_HEIGHT
        self.vel_x = 0
        self.vel_y = 0
        self.on_ground = False
        self.facing_right = True

    def move_left(self):
        self.vel_x = -PLAYER_SPEED
        self.facing_right = False

    def move_right(self):
        self.vel_x = PLAYER_SPEED
        self.facing_right = True

    def stop_horizontal(self):
        self.vel_x = 0

    def jump(self):
        if self.on_ground:
            self.vel_y = -JUMP_FORCE
            self.on_ground = False

    def update(self):
        self.vel_y += GRAVITY
        if self.vel_y > MAX_FALL_SPEED:
            self.vel_y = MAX_FALL_SPEED

        self.x += self.vel_x
        self.y += self.vel_y

        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def draw(self, screen):
        pygame.draw.rect(screen, PLAYER_COLOR, (int(self.x), int(self.y), self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (int(self.x), int(self.y), self.width, self.height), 2)

        cap_x = int(self.x) - 3 if self.facing_right else int(self.x) + 3
        pygame.draw.rect(screen, (200, 30, 30), (cap_x, int(self.y) - 10, self.width + 6, 12))
        pygame.draw.rect(screen, (0, 0, 0), (cap_x, int(self.y) - 10, self.width + 6, 12), 2)

        eye_offset = 5 if self.facing_right else 15
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x) + eye_offset, int(self.y) + 12), 4)
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x) + eye_offset + (1 if self.facing_right else -1), int(self.y) + 12), 2)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def get_head_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, 10)

    def get_feet_rect(self):
        return pygame.Rect(int(self.x), int(self.y) + self.height - 4, self.width, 6)


class Block:
    def __init__(self, x, y, block_type="solid"):
        self.x = x
        self.y = y
        self.width = BLOCK_SIZE
        self.height = BLOCK_SIZE
        self.block_type = block_type
        self.alive = True
        self.bounce_offset = 0
        self.bounce_velocity = 0
        self.has_reward = True if block_type == "mystery" else False
        self.coins_spawned = 0

    def hit(self):
        if self.block_type == "mystery" and self.has_reward:
            self.has_reward = False
            self.bounce_velocity = -8
            self.coins_spawned += 1
            return "coin"
        elif self.block_type == "brick":
            self.bounce_velocity = -5
            return "bounce"
        return None

    def break_block(self):
        self.alive = False
        return "broken"

    def update(self):
        if self.bounce_velocity != 0:
            self.bounce_offset += self.bounce_velocity
            self.bounce_velocity += 1
            if self.bounce_offset >= 0:
                self.bounce_offset = 0
                self.bounce_velocity = 0

    def draw(self, screen):
        if not self.alive:
            return

        draw_y = int(self.y) + self.bounce_offset

        if self.block_type == "mystery":
            color = QUESTION_BLOCK_HIT_COLOR if not self.has_reward else QUESTION_BLOCK_COLOR
            pygame.draw.rect(screen, color, (int(self.x), draw_y, self.width, self.height))
            pygame.draw.rect(screen, (0, 0, 0), (int(self.x), draw_y, self.width, self.height), 2)

            if self.has_reward:
                font = pygame.font.Font(None, 32)
                text = font.render("?", True, (255, 255, 255))
                screen.blit(text, (int(self.x) + 12, draw_y + 4))
        elif self.block_type == "brick":
            pygame.draw.rect(screen, BRICK_COLOR, (int(self.x), draw_y, self.width, self.height))
            pygame.draw.rect(screen, (0, 0, 0), (int(self.x), draw_y, self.width, self.height), 2)
            pygame.draw.line(screen, (0, 0, 0), (int(self.x), draw_y + 20), (int(self.x) + self.width, draw_y + 20), 2)
            pygame.draw.line(screen, (0, 0, 0), (int(self.x) + 20, draw_y), (int(self.x) + 20, draw_y + 20), 2)
        else:
            pygame.draw.rect(screen, SOLID_BLOCK_COLOR, (int(self.x), draw_y, self.width, self.height))
            pygame.draw.rect(screen, (0, 0, 0), (int(self.x), draw_y, self.width, self.height), 2)

    def get_rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)


class Coin:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_y = -10
        self.life = 40
        self.radius = 14
        self.collected = False

    def update(self):
        self.vel_y += GRAVITY * 0.6
        self.y += self.vel_y
        self.life -= 1
        return self.life > 0

    def draw(self, screen):
        if self.life <= 0:
            return

        alpha = min(255, self.life * 8)
        coin_surface = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)

        pygame.draw.circle(coin_surface, (255, 215, 0, alpha), (self.radius, self.radius), self.radius)
        pygame.draw.circle(coin_surface, (255, 235, 100, alpha), (self.radius - 4, self.radius - 4), 5)
        pygame.draw.circle(coin_surface, (200, 150, 0, alpha), (self.radius, self.radius), self.radius, 2)

        screen.blit(coin_surface, (int(self.x) - self.radius, int(self.y) - self.radius))

    def get_rect(self):
        return pygame.Rect(int(self.x) - self.radius, int(self.y) - self.radius, self.radius * 2, self.radius * 2)


class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def draw(self, screen):
        pygame.draw.rect(screen, (80, 60, 40), (self.x, self.y, self.width, self.height))
        pygame.draw.rect(screen, (0, 0, 0), (self.x, self.y, self.width, self.height), 2)

        for i in range(0, self.width, 20):
            pygame.draw.line(screen, (60, 45, 30), (self.x + i, self.y), (self.x + i, self.y + self.height), 1)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)
