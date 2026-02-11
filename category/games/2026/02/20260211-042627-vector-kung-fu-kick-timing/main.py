import pygame
import sys
import random
from enum import Enum


class KickState(Enum):
    IDLE = "idle"
    KICK_LEFT = "kick_left"
    KICK_RIGHT = "kick_right"
    RECOVERY = "recovery"


class Enemy:
    def __init__(self, direction, speed):
        self.direction = direction
        self.speed = speed
        self.width = 40
        self.height = 60

        if direction == "left":
            self.x = -self.width
        else:
            self.x = 800

        self.y = 270
        self.active = True
        self.hit = False

    def update(self):
        if self.direction == "left":
            self.x += self.speed
        else:
            self.x -= self.speed

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def draw(self, surface):
        if not self.active:
            return

        color = (200, 60, 60) if not self.hit else (100, 100, 100)
        pygame.draw.rect(surface, color, self.get_rect())

        head = pygame.Rect(self.x + 5, self.y - 20, 30, 25)
        pygame.draw.rect(surface, color, head)


class Player:
    def __init__(self):
        self.x = 380
        self.y = 270
        self.width = 40
        self.height = 60
        self.state = KickState.IDLE
        self.state_timer = 0
        self.kick_range = 100
        self.kick_duration = 15
        self.recovery_duration = 20

    def update(self):
        if self.state_timer > 0:
            self.state_timer -= 1
            if self.state_timer == 0:
                if self.state in [KickState.KICK_LEFT, KickState.KICK_RIGHT]:
                    self.state = KickState.RECOVERY
                    self.state_timer = self.recovery_duration
                elif self.state == KickState.RECOVERY:
                    self.state = KickState.IDLE

    def kick_left(self):
        if self.state == KickState.IDLE:
            self.state = KickState.KICK_LEFT
            self.state_timer = self.kick_duration
            return True
        return False

    def kick_right(self):
        if self.state == KickState.IDLE:
            self.state = KickState.KICK_RIGHT
            self.state_timer = self.kick_duration
            return True
        return False

    def get_body_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_kick_hitbox(self):
        if self.state == KickState.KICK_LEFT and self.state_timer > 5:
            return pygame.Rect(self.x - self.kick_range, self.y, self.kick_range, self.height)
        elif self.state == KickState.KICK_RIGHT and self.state_timer > 5:
            return pygame.Rect(self.x + self.width, self.y, self.kick_range, self.height)
        return None

    def draw(self, surface):
        body_color = (70, 180, 70)

        if self.state == KickState.RECOVERY:
            body_color = (50, 120, 50)
        elif self.state in [KickState.KICK_LEFT, KickState.KICK_RIGHT]:
            body_color = (100, 200, 100)

        pygame.draw.rect(surface, body_color, self.get_body_rect())

        head = pygame.Rect(self.x + 5, self.y - 20, 30, 25)
        pygame.draw.rect(surface, body_color, head)

        if self.state == KickState.KICK_LEFT and self.state_timer > 5:
            leg = pygame.Rect(self.x - 80, self.y + 20, 80, 20)
            pygame.draw.rect(surface, (50, 150, 50), leg)
        elif self.state == KickState.KICK_RIGHT and self.state_timer > 5:
            leg = pygame.Rect(self.x + self.width, self.y + 20, 80, 20)
            pygame.draw.rect(surface, (50, 150, 50), leg)


class Game:
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Vector Kung Fu Kick Timing")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        self.player = Player()
        self.enemies = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.paused = False

        self.spawn_timer = 0
        self.base_spawn_interval = 90
        self.min_spawn_interval = 30
        self.difficulty_timer = 0
        self.enemies_defeated = 0

        self.game_time = 0

    def spawn_enemy(self):
        direction = random.choice(["left", "right"])
        speed = random.uniform(3, 6 + self.game_time / 600)
        enemy = Enemy(direction, speed)
        self.enemies.append(enemy)

    def get_spawn_interval(self):
        interval = self.base_spawn_interval - (self.game_time / 60)
        return max(self.min_spawn_interval, int(interval))

    def check_collisions(self):
        kick_hitbox = self.player.get_kick_hitbox()
        player_body = self.player.get_body_rect()

        for enemy in self.enemies[:]:
            if not enemy.active:
                continue

            enemy_rect = enemy.get_rect()

            if kick_hitbox and kick_hitbox.colliderect(enemy_rect):
                enemy.active = False
                enemy.hit = True
                self.score += 100
                self.enemies_defeated += 1

            if enemy_rect.colliderect(player_body) and not enemy.hit:
                self.lives -= 1
                enemy.active = False
                if self.lives <= 0:
                    self.game_over = True

    def update(self):
        if self.game_over or self.paused:
            return

        self.game_time += 1

        self.spawn_timer += 1
        if self.spawn_timer >= self.get_spawn_interval():
            self.spawn_timer = 0
            self.spawn_enemy()

        self.player.update()

        for enemy in self.enemies[:]:
            enemy.update()

            if enemy.x < -100 or enemy.x > 900:
                self.enemies.remove(enemy)

        self.check_collisions()

    def reset_game(self):
        self.player = Player()
        self.enemies = []
        self.score = 0
        self.lives = 3
        self.game_over = False
        self.spawn_timer = 0
        self.game_time = 0
        self.enemies_defeated = 0

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                if self.game_over:
                    if event.key == pygame.K_SPACE:
                        self.reset_game()
                else:
                    if event.key == pygame.K_LEFT:
                        self.player.kick_left()
                    elif event.key == pygame.K_RIGHT:
                        self.player.kick_right()
                    elif event.key == pygame.K_p:
                        self.paused = not self.paused

        return True

    def draw(self):
        self.screen.fill((25, 25, 35))

        floor_y = 330
        pygame.draw.rect(self.screen, (50, 45, 40), (0, floor_y, self.width, self.height - floor_y))

        pygame.draw.circle(self.screen, (100, 100, 100), (self.width // 2, floor_y + 20), 15)
        pygame.draw.rect(self.screen, (80, 80, 80), (self.width // 2 - 8, floor_y + 5, 16, 15))

        self.player.draw(self.screen)

        for enemy in self.enemies:
            enemy.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 200, 100))
        self.screen.blit(score_text, (20, 20))

        for i in range(self.lives):
            pygame.draw.circle(self.screen, (200, 50, 50), (self.width - 40 - i * 35, 35), 12)

        time_text = self.font.render(f"Time: {self.game_time // 60}s", True, (150, 150, 150))
        self.screen.blit(time_text, (self.width // 2 - 40, 20))

        if self.paused:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 150))
            self.screen.blit(overlay, (0, 0))

            pause_text = self.large_font.render("PAUSED", True, (255, 255, 255))
            rect = pause_text.get_rect(center=(self.width // 2, self.height // 2))
            self.screen.blit(pause_text, rect)

        if self.game_over:
            overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, (200, 50, 50))
            rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2 - 40))
            self.screen.blit(game_over_text, rect)

            final_score = self.font.render(f"Final Score: {self.score}", True, (255, 200, 100))
            rect = final_score.get_rect(center=(self.width // 2, self.height // 2 + 10))
            self.screen.blit(final_score, rect)

            restart_text = self.font.render("Press SPACE to restart", True, (200, 200, 200))
            rect = restart_text.get_rect(center=(self.width // 2, self.height // 2 + 50))
            self.screen.blit(restart_text, rect)

        controls = [
            "Controls:",
            "Left Arrow: Kick Left",
            "Right Arrow: Kick Right",
            "P: Pause",
            "ESC: Quit"
        ]
        small_font = pygame.font.Font(None, 22)
        for i, line in enumerate(controls):
            text = small_font.render(line, True, (100, 100, 100))
            self.screen.blit(text, (10, self.height - 110 + i * 20))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
