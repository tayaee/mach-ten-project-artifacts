"""Game state and logic for Vector Kung Fu Master."""

import pygame
import random
from constants import *
from entities import Player, Enemy, Projectile


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Kung Fu Master")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset_game()

    def reset_game(self):
        """Reset all game state."""
        self.player = Player()
        self.enemies = []
        self.projectiles = []
        self.score = 0
        self.stage = 1
        self.time_remaining = TIME_LIMIT
        self.game_state = 'playing'  # 'playing', 'won', 'lost'
        self.last_enemy_spawn = 0
        self.last_knife_throw = 0
        self.stage_enemies_defeated = 0
        self.boss_spawned = False

    def spawn_enemy(self):
        """Spawn a new enemy based on current stage."""
        if self.stage == 5 and not self.boss_spawned:
            # Spawn boss on final stage
            boss = Enemy(SCREEN_WIDTH - 80, FLOOR_Y - 80, 50, 80, COLOR_ENEMY_BOSS, 'boss')
            boss.hp = 150
            boss.max_hp = 150
            self.enemies.append(boss)
            self.boss_spawned = True
            return

        if self.boss_spawned:
            return  # No more enemies after boss

        # Determine spawn side
        spawn_left = random.choice([True, False])

        if spawn_left:
            x = -40
            direction = 1
        else:
            x = SCREEN_WIDTH + 10
            direction = -1

        # Choose enemy type
        if self.stage >= 3 and random.random() < 0.3:
            enemy = Enemy(x, FLOOR_Y - 50, 30, 50, COLOR_ENEMY_KNIFE, 'knife')
        else:
            enemy = Enemy(x, FLOOR_Y - 50, 30, 50, COLOR_ENEMY_GRUNT, 'grunt')

        enemy.direction = direction
        self.enemies.append(enemy)

    def throw_knife(self):
        """Enemy throws a knife projectile."""
        throwers = [e for e in self.enemies if e.enemy_type == 'knife' and e.alive]
        if throwers:
            thrower = random.choice(throwers)
            direction = 1 if thrower.direction == 1 else -1
            projectile = Projectile(thrower.x, thrower.y + 20, direction)
            self.projectiles.append(projectile)

    def check_combat(self):
        """Check all combat interactions."""
        player_rect = self.player.get_rect()
        attack_rect = self.player.get_attack_rect()

        # Check player attacks against enemies
        if self.player.is_attacking and attack_rect:
            for enemy in self.enemies[:]:
                if enemy.alive and attack_rect.colliderect(enemy.get_rect()):
                    damage = PUNCH_DAMAGE if self.player.attack_type == 'punch' else KICK_DAMAGE
                    if enemy.enemy_type == 'boss':
                        damage = KICK_DAMAGE
                    enemy.hp -= damage
                    if enemy.hp <= 0:
                        enemy.alive = False
                        if enemy.enemy_type == 'boss':
                            self.score += SCORE_BOSS
                        else:
                            self.score += SCORE_GRUNT
                        self.stage_enemies_defeated += 1

        # Check enemy attacks against player
        for enemy in self.enemies:
            if not enemy.alive:
                continue

            if enemy.is_attacking() and player_rect.colliderect(enemy.get_rect()):
                damage = BOSS_DAMAGE if enemy.enemy_type == 'boss' else 15
                if self.player.take_damage(damage):
                    if self.player.hp <= 0:
                        self.game_state = 'lost'

        # Check projectiles against player
        for proj in self.projectiles[:]:
            if proj.alive and player_rect.colliderect(proj.get_rect()):
                if self.player.take_damage(10):
                    proj.alive = False
                    if self.player.hp <= 0:
                        self.game_state = 'lost'

        # Check player attacks against projectiles (deflect)
        if attack_rect:
            for proj in self.projectiles[:]:
                if proj.alive and attack_rect.colliderect(proj.get_rect()):
                    proj.alive = False
                    self.score += SCORE_KNIFE_DEFLECT

        # Remove dead entities
        self.enemies = [e for e in self.enemies if e.alive]
        self.projectiles = [p for p in self.projectiles if p.alive]

    def update(self, dt):
        """Update game state."""
        if self.game_state != 'playing':
            return

        # Update timer
        self.time_remaining -= dt / 1000
        if self.time_remaining <= 0:
            self.time_remaining = 0
            self.game_state = 'lost'

        # Update player
        self.player.update()

        # Update enemies
        for enemy in self.enemies:
            enemy.update(self.player.x)

        # Update projectiles
        for proj in self.projectiles:
            proj.update()

        # Spawn enemies
        now = pygame.time.get_ticks()
        spawn_rate = max(1000 - self.stage * 150, 400)
        if now - self.last_enemy_spawn > spawn_rate and len(self.enemies) < 3 + self.stage:
            self.spawn_enemy()
            self.last_enemy_spawn = now

        # Throw knives
        if any(e.enemy_type == 'knife' for e in self.enemies):
            if now - self.last_knife_throw > 2000:
                self.throw_knife()
                self.last_knife_throw = now

        # Check combat
        self.check_combat()

        # Check stage progression
        enemies_per_stage = 5 + self.stage * 2
        if self.stage_enemies_defeated >= enemies_per_stage and len(self.enemies) == 0:
            if self.stage >= 5:
                self.game_state = 'won'
                self.score += int(self.time_remaining * TIME_BONUS_MULTIPLIER)
            else:
                self.stage += 1
                self.stage_enemies_defeated = 0

    def handle_input(self):
        """Handle keyboard input."""
        keys = pygame.key.get_pressed()

        # Movement
        self.player.vx = 0
        if keys[pygame.K_LEFT]:
            self.player.vx = -PLAYER_SPEED
            self.player.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.player.vx = PLAYER_SPEED
            self.player.facing_right = True

        # Crouch
        self.player.is_crouching = keys[pygame.K_DOWN]

    def handle_events(self):
        """Handle pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False

                # Attacks
                if event.key == pygame.K_z:
                    self.player.attack('punch')
                elif event.key == pygame.K_x:
                    self.player.attack('kick')

                # Jump
                if event.key == pygame.K_UP and not self.player.is_jumping:
                    self.player.is_jumping = True
                    self.player.vy = JUMP_POWER

        return True

    def draw(self):
        """Draw the game."""
        self.screen.fill(COLOR_BG)

        # Draw floor
        pygame.draw.rect(self.screen, COLOR_FLOOR, (0, FLOOR_Y, SCREEN_WIDTH, SCREEN_HEIGHT - FLOOR_Y))

        # Draw entities
        self.player.draw(self.screen)
        for enemy in self.enemies:
            enemy.draw(self.screen)
        for proj in self.projectiles:
            proj.draw(self.screen)

        # Draw UI
        self.draw_ui()

        pygame.display.flip()

    def draw_ui(self):
        """Draw the user interface."""
        # Health bar
        pygame.draw.rect(self.screen, COLOR_HEALTH_BG, (10, 10, 200, 20))
        health_width = int(200 * (self.player.hp / MAX_HP))
        pygame.draw.rect(self.screen, COLOR_HEALTH_BAR, (10, 10, health_width, 20))

        # Text info
        score_text = self.font.render(f"Score: {self.score}", True, COLOR_TEXT)
        stage_text = self.font.render(f"Stage: {self.stage}/5", True, COLOR_TEXT)
        time_text = self.font.render(f"Time: {int(self.time_remaining)}", True, COLOR_TEXT)

        self.screen.blit(score_text, (10, 40))
        self.screen.blit(stage_text, (SCREEN_WIDTH // 2 - 50, 10))
        self.screen.blit(time_text, (SCREEN_WIDTH - 150, 10))

        # Game over / win screen
        if self.game_state != 'playing':
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            if self.game_state == 'won':
                msg = "VICTORY!"
                color = (0, 255, 0)
            else:
                msg = "GAME OVER"
                color = (255, 0, 0)

            title = self.font.render(msg, True, color)
            final_score = self.font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            restart = self.small_font.render("Press SPACE to restart or ESC to quit", True, COLOR_TEXT)

            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, 150))
            self.screen.blit(final_score, (SCREEN_WIDTH // 2 - final_score.get_width() // 2, 200))
            self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 260))

    def run(self):
        """Main game loop."""
        running = True

        while running:
            dt = self.clock.tick(60)

            running = self.handle_events()

            if self.game_state == 'playing':
                self.handle_input()

            # Handle restart
            if self.game_state != 'playing':
                keys = pygame.key.get_pressed()
                if keys[pygame.K_SPACE]:
                    self.reset_game()

            self.update(dt)
            self.draw()

        pygame.quit()
