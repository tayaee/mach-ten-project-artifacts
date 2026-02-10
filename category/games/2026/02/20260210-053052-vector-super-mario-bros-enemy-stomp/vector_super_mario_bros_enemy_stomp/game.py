import pygame
import random
import math

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 400
GRAVITY = 0.8
JUMP_STRENGTH = -15
PLAYER_SPEED = 5
GROUND_Y = SCREEN_HEIGHT - 50

FPS = 60
ENEMY_BASE_SPEED = 2
ENEMY_SPAWN_INTERVAL = 1500

POINT_PER_STOMP = 100


class Player:
    def __init__(self):
        self.width = 30
        self.height = 40
        self.x = 100
        self.y = GROUND_Y - self.height
        self.vel_y = 0
        self.vel_x = 0
        self.on_ground = True
        self.facing_right = True

    def jump(self):
        if self.on_ground:
            self.vel_y = JUMP_STRENGTH
            self.on_ground = False

    def move_left(self):
        self.vel_x = -PLAYER_SPEED
        self.facing_right = False

    def move_right(self):
        self.vel_x = PLAYER_SPEED
        self.facing_right = True

    def stop(self):
        self.vel_x = 0

    def update(self):
        self.vel_y += GRAVITY
        self.y += self.vel_y
        self.x += self.vel_x

        if self.y >= GROUND_Y - self.height:
            self.y = GROUND_Y - self.height
            self.vel_y = 0
            self.on_ground = True

        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

    def draw(self, surface):
        color = (255, 100, 100)
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, color, rect)

        eye_color = (255, 255, 255)
        eye_x = self.x + (self.width - 10 if self.facing_right else 5)
        pygame.draw.rect(surface, eye_color, (eye_x, self.y + 8, 10, 8))

        pupil_color = (0, 0, 0)
        pupil_x = eye_x + (6 if self.facing_right else 0)
        pygame.draw.rect(surface, pupil_color, (pupil_x, self.y + 10, 4, 4))

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_bottom_rect(self):
        return pygame.Rect(self.x + 5, self.y + self.height - 5, self.width - 10, 5)

    def get_hurtbox(self):
        return pygame.Rect(self.x, self.y, self.width, self.height - 5)


class Enemy:
    def __init__(self, speed_multiplier=1.0):
        self.width = 30
        self.height = 30
        self.x = SCREEN_WIDTH + random.randint(0, 100)
        self.y = GROUND_Y - self.height
        self.speed = ENEMY_BASE_SPEED * speed_multiplier
        self.alive = True

    def update(self):
        self.x -= self.speed
        if self.x < -self.width:
            self.alive = False

    def draw(self, surface):
        color = (150, 100, 50)
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        pygame.draw.rect(surface, color, rect)

        eye_color = (255, 255, 255)
        pygame.draw.rect(surface, eye_color, (self.x + 5, self.y + 5, 8, 8))
        pygame.draw.rect(surface, eye_color, (self.x + 17, self.y + 5, 8, 8))

        pupil_color = (0, 0, 0)
        pygame.draw.rect(surface, pupil_color, (self.x + 8, self.y + 7, 4, 4))
        pygame.draw.rect(surface, pupil_color, (self.x + 18, self.y + 7, 4, 4))

        frown_color = (100, 50, 0)
        pygame.draw.line(surface, frown_color, (self.x + 5, self.y + 22), (self.x + 25, self.y + 22), 2)

    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

    def get_top_rect(self):
        return pygame.Rect(self.x + 3, self.y, self.width - 6, 8)


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros - Enemy Stomp")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)
        self.reset()

    def reset(self):
        self.player = Player()
        self.enemies = []
        self.score = 0
        self.combo = 0
        self.game_over = False
        self.spawn_timer = 0
        self.spawn_interval = ENEMY_SPAWN_INTERVAL
        self.speed_multiplier = 1.0
        self.time_elapsed = 0
        self.last_spawn_time = pygame.time.get_ticks()

    def spawn_enemy(self):
        speed_variation = 1.0 + (self.speed_multiplier - 1.0) * 0.5
        enemy = Enemy(speed_variation)
        self.enemies.append(enemy)

    def check_stomp(self, player, enemy):
        player_bottom = player.get_bottom_rect()
        enemy_top = enemy.get_top_rect()

        if player_bottom.colliderect(enemy_top):
            return True
        return False

    def update(self):
        if self.game_over:
            return

        current_time = pygame.time.get_ticks()
        self.time_elapsed = current_time

        if current_time - self.last_spawn_time > self.spawn_interval:
            self.spawn_enemy()
            self.last_spawn_time = current_time

            difficulty_factor = min(self.score / 5000, 2.0)
            self.spawn_interval = max(500, ENEMY_SPAWN_INTERVAL - (difficulty_factor * 1000))
            self.speed_multiplier = 1.0 + difficulty_factor

        self.player.update()

        for enemy in self.enemies[:]:
            enemy.update()

            if not enemy.alive:
                self.enemies.remove(enemy)
                continue

            if self.check_stomp(self.player, enemy):
                self.enemies.remove(enemy)
                self.combo += 1
                stomp_points = POINT_PER_STOMP * (2 ** (self.combo - 1))
                self.score += stomp_points
                continue

            player_hurtbox = self.player.get_hurtbox()
            enemy_rect = enemy.get_rect()

            if player_hurtbox.colliderect(enemy_rect):
                self.game_over = True

        if self.player.on_ground:
            self.combo = 0

    def draw(self):
        self.screen.fill((50, 150, 200))

        pygame.draw.rect(self.screen, (100, 200, 100), (0, GROUND_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GROUND_Y))

        for enemy in self.enemies:
            enemy.draw(self.screen)

        self.player.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        if self.combo > 1:
            combo_text = self.font.render(f"Combo: x{self.combo}", True, (255, 255, 0))
            self.screen.blit(combo_text, (10, 50))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(128)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.large_font.render("GAME OVER", True, (255, 50, 50))
            score_final_text = self.font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            restart_text = self.font.render("Press SPACE to restart", True, (200, 200, 200))

            self.screen.blit(game_over_text, (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(score_final_text, (SCREEN_WIDTH // 2 - score_final_text.get_width() // 2, SCREEN_HEIGHT // 2 + 10))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 60))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if self.game_over:
                        if event.key == pygame.K_SPACE:
                            self.reset()
                    else:
                        if event.key == pygame.K_SPACE:
                            self.player.jump()
                        elif event.key == pygame.K_ESCAPE:
                            running = False

            keys = pygame.key.get_pressed()
            if not self.game_over:
                if keys[pygame.K_LEFT]:
                    self.player.move_left()
                elif keys[pygame.K_RIGHT]:
                    self.player.move_right()
                else:
                    self.player.stop()

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
