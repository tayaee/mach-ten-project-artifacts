import pygame
import sys
from entities import Player, Block, Coin, Platform
from config import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Super Mario Bros Jump Block Logic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 28)
        self.reset_game()

    def reset_game(self):
        self.player = Player(100, GROUND_Y - PLAYER_HEIGHT)
        self.blocks = []
        self.coins = []
        self.platforms = []
        self.score = 0
        self.mystery_blocks_hit = 0
        self.bricks_broken = 0
        self.coins_collected = 0
        self.game_over = False
        self.victory = False
        self.create_level()

    def create_level(self):
        self.blocks = []
        self.platforms = []

        self.platforms.append(Platform(0, GROUND_Y, SCREEN_WIDTH, 60))

        self.platforms.append(Platform(80, 450, 180, 20))
        self.platforms.append(Platform(350, 450, 180, 20))
        self.platforms.append(Platform(550, 450, 180, 20))

        self.platforms.append(Platform(180, 350, 200, 20))
        self.platforms.append(Platform(450, 350, 200, 20))

        self.platforms.append(Platform(100, 260, 150, 20))
        self.platforms.append(Platform(300, 260, 200, 20))
        self.platforms.append(Platform(550, 260, 150, 20))

        self.platforms.append(Platform(200, 180, 180, 20))
        self.platforms.append(Platform(450, 180, 180, 20))

        self.platforms.append(Platform(320, 120, 160, 20))

        for i in range(4):
            self.blocks.append(Block(100 + i * 45, 410, "mystery"))

        for i in range(4):
            self.blocks.append(Block(370 + i * 45, 410, "brick"))

        for i in range(4):
            self.blocks.append(Block(570 + i * 45, 410, "mystery"))

        for i in range(3):
            self.blocks.append(Block(200 + i * 50, 310, "brick" if i % 2 else "mystery"))

        for i in range(3):
            self.blocks.append(Block(470 + i * 50, 310, "mystery" if i % 2 else "brick"))

        for i in range(2):
            self.blocks.append(Block(120 + i * 50, 220, "mystery"))

        for i in range(3):
            self.blocks.append(Block(320 + i * 50, 220, "brick"))

        for i in range(2):
            self.blocks.append(Block(570 + i * 50, 220, "mystery"))

        for i in range(2):
            self.blocks.append(Block(220 + i * 55, 140, "mystery"))

        for i in range(2):
            self.blocks.append(Block(470 + i * 55, 140, "mystery"))

        self.blocks.append(Block(380, 80, "mystery"))
        self.blocks.append(Block(425, 80, "mystery"))

        self.blocks.append(Block(150, 500, "solid"))
        self.blocks.append(Block(650, 500, "solid"))

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if self.game_over or self.victory:
                    if event.key == pygame.K_SPACE or event.key == pygame.K_r:
                        self.reset_game()
                else:
                    if event.key == pygame.K_SPACE:
                        self.player.jump()

        if not self.game_over and not self.victory:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_LEFT]:
                self.player.move_left()
            elif keys[pygame.K_RIGHT]:
                self.player.move_right()
            else:
                self.player.stop_horizontal()

        return True

    def check_collisions(self):
        player_rect = self.player.get_rect()
        player_feet = self.player.get_feet_rect()
        player_head = self.player.get_head_rect()

        self.player.on_ground = False

        for platform in self.platforms:
            plat_rect = platform.get_rect()
            if player_feet.colliderect(plat_rect) and self.player.vel_y >= 0:
                if self.player.y + self.player.height <= platform.y + platform.height:
                    self.player.y = platform.y - self.player.height
                    self.player.vel_y = 0
                    self.player.on_ground = True

        if self.player.y + self.player.height >= GROUND_Y:
            self.player.y = GROUND_Y - self.player.height
            self.player.vel_y = 0
            self.player.on_ground = True

        for block in self.blocks[:]:
            if not block.alive:
                self.blocks.remove(block)
                continue

            block_rect = block.get_rect()

            if player_head.colliderect(block_rect) and self.player.vel_y < 0:
                hit_height = abs(self.player.y - block.y)
                if hit_height < 30:
                    result = block.hit()
                    if result == "coin":
                        self.score += REWARD_HIT_MYSTERY
                        self.mystery_blocks_hit += 1
                        self.coins.append(Coin(block.x + block.width // 2, block.y))
                    elif result == "bounce":
                        pass

                    self.player.vel_y = 0

            if player_feet.colliderect(block_rect) and self.player.vel_y >= 0:
                if self.player.y + self.player.height <= block.y + 15:
                    self.player.y = block.y - self.player.height
                    self.player.vel_y = 0
                    self.player.on_ground = True

            player_rect_current = self.player.get_rect()
            if player_rect_current.colliderect(block_rect):
                if self.player.vel_y < 0 and player_head.colliderect(block_rect):
                    pass
                elif self.player.vel_y > 0 and player_feet.colliderect(block_rect):
                    pass
                else:
                    if self.player.x < block.x:
                        self.player.x = block.x - self.player.width
                    else:
                        self.player.x = block.x + block.width

        for coin in self.coins[:]:
            if not coin.collected:
                coin_rect = coin.get_rect()
                if player_rect.colliderect(coin_rect):
                    coin.collected = True
                    self.coins.remove(coin)
                    self.score += REWARD_COLLECT_COIN
                    self.coins_collected += 1

    def check_victory(self):
        mystery_blocks = [b for b in self.blocks if b.block_type == "mystery" and b.has_reward]
        if len(mystery_blocks) == 0:
            self.victory = True

    def update(self):
        if self.game_over or self.victory:
            return

        self.player.update()

        for block in self.blocks:
            block.update()

        for coin in self.coins[:]:
            if not coin.update():
                if coin in self.coins:
                    self.coins.remove(coin)

        self.check_collisions()
        self.check_victory()

        if self.player.x < 0:
            self.player.x = 0
        elif self.player.x > SCREEN_WIDTH - self.player.width:
            self.player.x = SCREEN_WIDTH - self.player.width

    def draw(self):
        self.screen.fill(BACKGROUND_COLOR)

        for platform in self.platforms:
            platform.draw(self.screen)

        pygame.draw.line(self.screen, (200, 200, 200), (0, GROUND_Y), (SCREEN_WIDTH, GROUND_Y), 2)

        for block in self.blocks:
            block.draw(self.screen)

        for coin in self.coins:
            coin.draw(self.screen)

        self.player.draw(self.screen)

        score_text = self.font.render(f"Score: {self.score}", True, SCORE_COLOR)
        self.screen.blit(score_text, (15, 15))

        mystery_text = self.small_font.render(f"Mystery: {self.mystery_blocks_hit}", True, TEXT_COLOR)
        coins_text = self.small_font.render(f"Coins: {self.coins_collected}", True, TEXT_COLOR)
        self.screen.blit(mystery_text, (15, 55))
        self.screen.blit(coins_text, (200, 55))

        remaining = len([b for b in self.blocks if b.block_type == "mystery" and b.has_reward])
        remaining_text = self.small_font.render(f"Blocks: {remaining}", True, TEXT_COLOR)
        self.screen.blit(remaining_text, (350, 55))

        if self.victory:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((255, 255, 255, 200))
            self.screen.blit(overlay, (0, 0))

            victory_text = self.font.render("ALL BLOCKS CLEARED!", True, (0, 150, 0))
            final_score_text = self.font.render(f"Final Score: {self.score}", True, TEXT_COLOR)
            stats_text = self.small_font.render(
                f"Mystery Hit: {self.mystery_blocks_hit} | Coins: {self.coins_collected}",
                True, TEXT_COLOR
            )
            restart_text = self.small_font.render("Press SPACE or R to play again", True, (80, 80, 80))

            self.screen.blit(victory_text, (SCREEN_WIDTH // 2 - 170, SCREEN_HEIGHT // 2 - 60))
            self.screen.blit(final_score_text, (SCREEN_WIDTH // 2 - 100, SCREEN_HEIGHT // 2 - 15))
            self.screen.blit(stats_text, (SCREEN_WIDTH // 2 - 160, SCREEN_HEIGHT // 2 + 25))
            self.screen.blit(restart_text, (SCREEN_WIDTH // 2 - 150, SCREEN_HEIGHT // 2 + 70))

        pygame.display.flip()

    def run(self):
        running = True
        while running:
            running = self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(FPS)
