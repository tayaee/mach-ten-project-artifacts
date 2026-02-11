import pygame
import sys

# Constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
TILE_SIZE = 40

# Physics
GRAVITY = 0.5
JUMP_FORCE = -12
MOVE_SPEED = 5
FIREBALL_SPEED = 8

# Colors
COLOR_BG = (135, 206, 235)
COLOR_GROUND = (139, 69, 19)
COLOR_BRICK = (205, 92, 92)
COLOR_BLOCK = (255, 215, 0)
COLOR_MARIO_SMALL = (255, 0, 0)
COLOR_MARIO_SUPER = (255, 100, 100)
COLOR_MARIO_FIRE = (255, 50, 0)
COLOR_GOOMBA = (139, 69, 19)
COLOR_MUSHROOM = (255, 100, 0)
COLOR_FLOWER = (255, 0, 255)
COLOR_FIREBALL = (255, 200, 0)
COLOR_BARRIER = (100, 100, 100)
COLOR_EXIT = (0, 255, 0)
COLOR_TEXT = (255, 255, 255)

# Power-up states
STATE_SMALL = 0
STATE_SUPER = 1
STATE_FIRE = 2


class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = 0
        self.vel_y = 0
        self.width = 30
        self.height = 30
        self.state = STATE_SMALL
        self.on_ground = False
        self.facing_right = True
        self.invincible_timer = 0

    def update(self, keys, platforms, barriers):
        # Horizontal movement
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -MOVE_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.vel_x = MOVE_SPEED
            self.facing_right = True

        # Apply horizontal velocity
        self.x += self.vel_x

        # Screen bounds
        if self.x < 0:
            self.x = 0
        if self.x > SCREEN_WIDTH - self.width:
            self.x = SCREEN_WIDTH - self.width

        # Check barrier collision (only Super/Fire Mario can break)
        player_rect = self.get_hitbox()
        for barrier in barriers:
            if not barrier.broken and player_rect.colliderect(barrier.get_hitbox()):
                if self.state >= STATE_SUPER:
                    barrier.break_barrier()
                    self.x += self.vel_x * 2  # Momentum through
                else:
                    # Bounce back
                    if self.vel_x > 0:
                        self.x = barrier.x - self.width
                    else:
                        self.x = barrier.x + barrier.width

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.vel_y = JUMP_FORCE
            self.on_ground = False

        # Apply gravity
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Platform collision
        self.on_ground = False
        player_rect = self.get_hitbox()
        for platform in platforms:
            if player_rect.colliderect(platform.get_hitbox()):
                # Land on top
                if self.vel_y > 0 and self.y + self.height - self.vel_y <= platform.y:
                    self.y = platform.y - self.height
                    self.vel_y = 0
                    self.on_ground = True

        # Ground collision
        ground_y = SCREEN_HEIGHT - TILE_SIZE - self.height
        if self.y >= ground_y:
            self.y = ground_y
            self.vel_y = 0
            self.on_ground = True

        # Update invincibility
        if self.invincible_timer > 0:
            self.invincible_timer -= 1

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def power_up(self, power_type):
        if power_type == "mushroom":
            if self.state == STATE_SMALL:
                self.state = STATE_SUPER
                self.height = 40
                self.y -= 10
            elif self.state == STATE_SUPER:
                self.state = STATE_FIRE
        elif power_type == "flower":
            if self.state == STATE_SMALL:
                self.state = STATE_SUPER
                self.height = 40
                self.y -= 10
            self.state = STATE_FIRE

    def damage(self):
        if self.invincible_timer > 0:
            return False

        if self.state == STATE_FIRE:
            self.state = STATE_SUPER
        elif self.state == STATE_SUPER:
            self.state = STATE_SMALL
            self.height = 30
        else:
            return True  # Game over
        self.invincible_timer = 60
        return False

    def draw(self, surface):
        # Blinking when invincible
        if self.invincible_timer > 0 and self.invincible_timer // 4 % 2 == 0:
            return

        if self.state == STATE_SMALL:
            color = COLOR_MARIO_SMALL
        elif self.state == STATE_SUPER:
            color = COLOR_MARIO_SUPER
        else:
            color = COLOR_MARIO_FIRE

        pygame.draw.rect(surface, color, (int(self.x), int(self.y), self.width, self.height))

        # Draw hat
        hat_color = (255, 0, 0)
        pygame.draw.rect(surface, hat_color, (int(self.x), int(self.y), self.width, 10))

        # Draw fire indicator
        if self.state == STATE_FIRE:
            pygame.draw.circle(surface, COLOR_FIREBALL, (int(self.x) + 5, int(self.y) + 20), 3)


class Fireball:
    def __init__(self, x, y, direction):
        self.x = x
        self.y = y
        self.vel_x = FIREBALL_SPEED * direction
        self.vel_y = -3
        self.width = 12
        self.height = 12
        self.active = True
        self.bounce_count = 0

    def update(self, platforms):
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_y += GRAVITY * 0.5

        # Ground bounce
        if self.y >= SCREEN_HEIGHT - TILE_SIZE - self.height:
            self.y = SCREEN_HEIGHT - TILE_SIZE - self.height
            self.vel_y = -4
            self.bounce_count += 1

        # Platform collision
        fireball_rect = self.get_hitbox()
        for platform in platforms:
            if fireball_rect.colliderect(platform.get_hitbox()):
                if self.vel_y > 0:
                    self.y = platform.y - self.height
                    self.vel_y = -4
                    self.bounce_count += 1

        # Deactivate after 3 bounces or off screen
        if self.bounce_count >= 3 or self.x < 0 or self.x > SCREEN_WIDTH:
            self.active = False

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface):
        pygame.draw.circle(surface, COLOR_FIREBALL, (int(self.x) + 6, int(self.y) + 6), 6)
        pygame.draw.circle(surface, (255, 255, 0), (int(self.x) + 6, int(self.y) + 6), 3)


class Enemy:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vel_x = -1.5
        self.width = 30
        self.height = 30
        self.active = True

    def update(self):
        self.x += self.vel_x

        # Turn around at edges or screen bounds
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.vel_x *= -1

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface):
        # Goomba body
        pygame.draw.ellipse(surface, COLOR_GOOMBA, (int(self.x), int(self.y), self.width, self.height))
        # Eyes
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x) + 8, int(self.y) + 10), 4)
        pygame.draw.circle(surface, (255, 255, 255), (int(self.x) + 22, int(self.y) + 10), 4)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x) + 8, int(self.y) + 10), 2)
        pygame.draw.circle(surface, (0, 0, 0), (int(self.x) + 22, int(self.y) + 10), 2)


class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.vel_x = 2
        self.vel_y = 0
        self.width = 25
        self.height = 25
        self.power_type = power_type  # "mushroom" or "flower"
        self.active = True
        self.emerging = True
        self.target_y = y - TILE_SIZE
        self.emerge_progress = 0

    def update(self, platforms):
        if self.emerging:
            self.emerge_progress += 1
            self.y = self.target_y - TILE_SIZE + (self.emerge_progress * 2)
            if self.emerge_progress >= TILE_SIZE // 2:
                self.emerging = False
                self.y = self.target_y
            return

        # Movement
        self.x += self.vel_x
        self.vel_y += GRAVITY
        self.y += self.vel_y

        # Turn at edges
        if self.x <= 0 or self.x >= SCREEN_WIDTH - self.width:
            self.vel_x *= -1

        # Ground collision
        ground_y = SCREEN_HEIGHT - TILE_SIZE - self.height
        if self.y >= ground_y:
            self.y = ground_y
            self.vel_y = 0

        # Platform collision
        power_rect = self.get_hitbox()
        for platform in platforms:
            if power_rect.colliderect(platform.get_hitbox()):
                if self.vel_y > 0:
                    self.y = platform.y - self.height
                    self.vel_y = 0

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface):
        if self.power_type == "mushroom":
            # Mushroom cap
            pygame.draw.ellipse(surface, COLOR_MUSHROOM, (int(self.x), int(self.y), self.width, self.height))
            pygame.draw.ellipse(surface, (255, 200, 200), (int(self.x) + 5, int(self.y) + 5, self.width - 10, 10))
            # Spots
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x) + 6, int(self.y) + 8), 3)
            pygame.draw.circle(surface, (255, 255, 255), (int(self.x) + 19, int(self.y) + 8), 3)
        else:  # flower
            # Flower petals
            pygame.draw.circle(surface, COLOR_FLOWER, (int(self.x) + 12, int(self.y) + 5), 8)
            pygame.draw.circle(surface, COLOR_FLOWER, (int(self.x) + 5, int(self.y) + 12), 8)
            pygame.draw.circle(surface, COLOR_FLOWER, (int(self.x) + 19, int(self.y) + 12), 8)
            pygame.draw.circle(surface, COLOR_FLOWER, (int(self.x) + 12, int(self.y) + 19), 8)
            # Center
            pygame.draw.circle(surface, (255, 255, 0), (int(self.x) + 12, int(self.y) + 12), 5)


class Block:
    def __init__(self, x, y, block_type="brick", content=None):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE
        self.block_type = block_type  # "brick", "block", "ground"
        self.content = content  # "mushroom", "flower", or None
        self.used = False
        self.hit_offset = 0

    def hit(self):
        if self.block_type == "brick":
            self.hit_offset = -5
            return True
        elif self.block_type == "block" and not self.used:
            self.used = True
            self.hit_offset = -5
            return self.content
        return None

    def update(self):
        if self.hit_offset < 0:
            self.hit_offset += 1

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y) + self.hit_offset, self.width, self.height)

    def draw(self, surface):
        draw_y = int(self.y) + self.hit_offset

        if self.block_type == "ground":
            pygame.draw.rect(surface, COLOR_GROUND, (int(self.x), draw_y, self.width, self.height))
        elif self.block_type == "brick":
            color = COLOR_BRICK
            pygame.draw.rect(surface, color, (int(self.x), draw_y, self.width, self.height))
            # Brick pattern
            pygame.draw.rect(surface, (150, 60, 60), (int(self.x) + 2, draw_y + 2, self.width - 4, self.height - 4), 2)
            pygame.draw.line(surface, (150, 60, 60), (int(self.x), draw_y + self.height // 2),
                           (int(self.x) + self.width, draw_y + self.height // 2), 2)
        else:  # block
            color = (180, 180, 50) if self.used else COLOR_BLOCK
            pygame.draw.rect(surface, color, (int(self.x), draw_y, self.width, self.height))
            pygame.draw.rect(surface, (200, 200, 100), (int(self.x), draw_y, self.width, self.height), 2)
            if not self.used:
                # Question mark
                font = pygame.font.Font(None, 28)
                text = font.render("?", True, (180, 140, 0))
                surface.blit(text, (int(self.x) + 14, draw_y + 8))


class Barrier:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE * 3
        self.broken = False
        self.debris = []

    def break_barrier(self):
        self.broken = True
        # Create debris
        for i in range(4):
            self.debris.append({
                'x': self.x + (i % 2) * (self.width // 2),
                'y': self.y + (i // 2) * (self.height // 2),
                'vel_x': (i % 2 - 0.5) * 4,
                'vel_y': -5 - (i // 2) * 2
            })

    def update(self):
        if self.broken:
            for debris in self.debris:
                debris['y'] += debris['vel_y']
                debris['x'] += debris['vel_x']
                debris['vel_y'] += GRAVITY

    def get_hitbox(self):
        if self.broken:
            return pygame.Rect(0, 0, 0, 0)
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface):
        if self.broken:
            for debris in self.debris:
                if debris['y'] < SCREEN_HEIGHT:
                    pygame.draw.rect(surface, COLOR_BARRIER,
                                   (int(debris['x']), int(debris['y']), 15, 15))
        else:
            pygame.draw.rect(surface, COLOR_BARRIER, (int(self.x), int(self.y), self.width, self.height))
            # Lock icon
            pygame.draw.rect(surface, (150, 150, 150), (int(self.x) + 10, int(self.y) + 10, 20, 20))


class ExitGate:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = TILE_SIZE
        self.height = TILE_SIZE * 4

    def get_hitbox(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)

    def draw(self, surface):
        # Gate frame
        pygame.draw.rect(surface, (0, 200, 0), (int(self.x), int(self.y), self.width, self.height), 3)
        # Inner glow
        pygame.draw.rect(surface, (0, 255, 0, 100), (int(self.x) + 5, int(self.y) + 5, self.width - 10, self.height - 10))
        # Flag
        pygame.draw.polygon(surface, (255, 0, 0), [
            (int(self.x) + self.width // 2, int(self.y) + 10),
            (int(self.x) + self.width - 5, int(self.y) + 25),
            (int(self.x) + self.width // 2, int(self.y) + 40)
        ])


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros Power Up Logic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        self.player = Player(100, SCREEN_HEIGHT - TILE_SIZE - 40)
        self.platforms = []
        self.blocks = []
        self.barriers = []
        self.enemies = []
        self.powerups = []
        self.fireballs = []
        self.exit_gate = None
        self.score = 0
        self.game_over = False
        self.won = False
        self.shoot_cooldown = 0

        self.create_level()

    def create_level(self):
        # Ground
        for x in range(0, SCREEN_WIDTH, TILE_SIZE):
            if x < SCREEN_WIDTH - 200:  # Gap before exit
                self.blocks.append(Block(x, SCREEN_HEIGHT - TILE_SIZE, "ground"))

        # Floating platforms
        for i in range(3):
            self.blocks.append(Block(200 + i * TILE_SIZE, SCREEN_HEIGHT - 120, "brick"))
        for i in range(3):
            self.blocks.append(Block(450 + i * TILE_SIZE, SCREEN_HEIGHT - 200, "brick"))
        for i in range(4):
            self.blocks.append(Block(100 + i * TILE_SIZE, SCREEN_HEIGHT - 280, "brick"))

        # Question blocks with power-ups
        self.blocks.append(Block(220, SCREEN_HEIGHT - 160, "block", "mushroom"))
        self.blocks.append(Block(470, SCREEN_HEIGHT - 240, "block", "flower"))
        self.blocks.append(Block(120, SCREEN_HEIGHT - 320, "block", "mushroom"))

        # Target bricks (for Super Mario to break)
        self.blocks.append(Block(500, SCREEN_HEIGHT - 280, "brick"))
        self.blocks.append(Block(540, SCREEN_HEIGHT - 280, "brick"))

        # Barrier (requires Super/Fire Mario)
        self.barriers.append(Barrier(650, SCREEN_HEIGHT - TILE_SIZE * 4))

        # Exit gate (behind barrier)
        self.exit_gate = ExitGate(SCREEN_WIDTH - 80, SCREEN_HEIGHT - TILE_SIZE * 5)

        # Enemies
        self.enemies.append(Enemy(300, SCREEN_HEIGHT - TILE_SIZE - 30))
        self.enemies.append(Enemy(500, SCREEN_HEIGHT - TILE_SIZE - 30))
        self.enemies.append(Enemy(200, SCREEN_HEIGHT - 120 - 30))

    def handle_block_collision(self, rect, vel_y):
        for block in self.blocks:
            if rect.colliderect(block.get_hitbox()):
                # Hit from below
                if vel_y < 0 and rect.y >= block.y + block.height - 10:
                    content = block.hit()
                    if content:
                        self.powerups.append(PowerUp(block.x, block.y, content))
                    return True
        return False

    def update(self):
        if self.game_over or self.won:
            return

        keys = pygame.key.get_pressed()
        self.player.update(keys, self.blocks, self.barriers)

        # Check block collision from below
        player_rect = self.player.get_hitbox()
        if self.player.vel_y < 0:
            self.handle_block_collision(player_rect, self.player.vel_y)

        # Update blocks
        for block in self.blocks:
            block.update()

        # Update barriers
        for barrier in self.barriers:
            barrier.update()

        # Update enemies
        for enemy in self.enemies[:]:
            enemy.update()

            # Player collision
            if enemy.active and player_rect.colliderect(enemy.get_hitbox()):
                # Stomp from above
                if self.player.vel_y > 0 and self.player.y + self.player.height < enemy.y + 20:
                    self.enemies.remove(enemy)
                    self.player.vel_y = -8
                    self.score += 50
                else:
                    # Take damage
                    if self.player.damage():
                        self.game_over = True
                    else:
                        # Knockback
                        self.player.x += -30 if self.player.x > enemy.x else 30

        # Update power-ups
        for powerup in self.powerups[:]:
            powerup.update(self.blocks)
            if player_rect.colliderect(powerup.get_hitbox()):
                if not powerup.emerging:
                    self.player.power_up(powerup.power_type)
                    if powerup.power_type == "mushroom":
                        self.score += 100
                    else:
                        self.score += 200
                    self.powerups.remove(powerup)
            elif powerup.y > SCREEN_HEIGHT:
                self.powerups.remove(powerup)

        # Update fireballs
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1

        for fireball in self.fireballs[:]:
            fireball.update(self.blocks)
            if not fireball.active:
                self.fireballs.remove(fireball)
                continue

            # Check enemy collision
            fireball_rect = fireball.get_hitbox()
            for enemy in self.enemies[:]:
                if fireball_rect.colliderect(enemy.get_hitbox()):
                    self.enemies.remove(enemy)
                    self.score += 50
                    fireball.active = False
                    break

        # Check exit collision
        if self.exit_gate and player_rect.colliderect(self.exit_gate.get_hitbox()):
            self.won = True
            self.score += 1000

    def handle_shoot(self):
        if self.player.state == STATE_FIRE and self.shoot_cooldown == 0:
            direction = 1 if self.player.facing_right else -1
            fireball_x = self.player.x + (self.player.width if direction > 0 else -12)
            self.fireballs.append(Fireball(fireball_x, self.player.y + 15, direction))
            self.shoot_cooldown = 15

    def get_state(self):
        return {
            'player_state': self.player.state,
            'player_pos': (self.player.x, self.player.y),
            'enemies': [(e.x, e.y) for e in self.enemies],
            'powerups': [(p.x, p.y, p.power_type) for p in self.powerups]
        }

    def draw(self):
        self.screen.fill(COLOR_BG)

        # Draw exit gate
        if self.exit_gate:
            self.exit_gate.draw(self.screen)

        # Draw blocks
        for block in self.blocks:
            block.draw(self.screen)

        # Draw barriers
        for barrier in self.barriers:
            barrier.draw(self.screen)

        # Draw power-ups
        for powerup in self.powerups:
            powerup.draw(self.screen)

        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(self.screen)

        # Draw fireballs
        for fireball in self.fireballs:
            fireball.draw(self.screen)

        # Draw player
        self.player.draw(self.screen)

        # Draw HUD
        state_names = ["Small", "Super", "Fire"]
        state_text = self.small_font.render(f"State: {state_names[self.player.state]}", True, COLOR_TEXT)
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)

        # Draw background for HUD
        pygame.draw.rect(self.screen, (0, 0, 0, 150), (5, 5, 200, 60))
        self.screen.blit(state_text, (15, 10))
        self.screen.blit(score_text, (15, 35))

        # Controls hint
        if self.score < 100:
            hints = [
                "Arrow Keys: Move",
                "Space: Jump",
                "S: Shoot (Fire only)",
                "Get Mushroom -> Break Barrier"
            ]
            for i, hint in enumerate(hints):
                hint_text = self.small_font.render(hint, True, (255, 255, 0))
                self.screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 10, 10 + i * 22))

        # Game over overlay
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            game_over_text = self.font.render("GAME OVER", True, (255, 0, 0))
            restart_text = self.small_font.render("Press SPACE to restart", True, COLOR_TEXT)

            self.screen.blit(game_over_text,
                          (SCREEN_WIDTH // 2 - game_over_text.get_width() // 2, SCREEN_HEIGHT // 2 - 30))
            self.screen.blit(restart_text,
                          (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 20))

        # Win overlay
        if self.won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            win_text = self.font.render("LEVEL COMPLETE!", True, (0, 255, 0))
            score_final_text = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            restart_text = self.small_font.render("Press SPACE to play again", True, COLOR_TEXT)

            self.screen.blit(win_text,
                          (SCREEN_WIDTH // 2 - win_text.get_width() // 2, SCREEN_HEIGHT // 2 - 40))
            self.screen.blit(score_final_text,
                          (SCREEN_WIDTH // 2 - score_final_text.get_width() // 2, SCREEN_HEIGHT // 2))
            self.screen.blit(restart_text,
                          (SCREEN_WIDTH // 2 - restart_text.get_width() // 2, SCREEN_HEIGHT // 2 + 40))

        pygame.display.flip()

    def run(self):
        running = True

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_s:
                        self.handle_shoot()
                    elif event.key == pygame.K_SPACE and (self.game_over or self.won):
                        self.reset_game()

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
