"""Core game logic for Vector Karate Champ."""

import pygame
import sys
from typing import Optional, Tuple
import config as cfg
from entities import Fighter, AIFighter


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Karate Champ")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.running = True
        self.game_state = "playing"  # playing, round_end, match_end

        # Create fighters
        self.player = Fighter(150, is_player=True)
        self.opponent = AIFighter(cfg.SCREEN_WIDTH - 200)

        # Round state
        self.round_winner: Optional[Fighter] = None
        self.match_winner: Optional[Fighter] = None
        self.round_timer = 60  # frames before round reset
        self.message = ""
        self.message_timer = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()

        # Movement
        if keys[pygame.K_LEFT]:
            self.player.move(-1)
        elif keys[pygame.K_RIGHT]:
            self.player.move(1)
        else:
            self.player.stop_move()

        # Actions
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif self.game_state == "playing":
                    if event.key == pygame.K_a:
                        self.player.attack(cfg.ACTION_ATTACK_HIGH)
                    elif event.key == pygame.K_s:
                        self.player.attack(cfg.ACTION_ATTACK_LOW)
                    elif event.key == pygame.K_d:
                        self.player.block()

    def check_collision(self, rect1: Tuple[int, int, int, int], rect2: Tuple[int, int, int, int]) -> bool:
        x1, y1, w1, h1 = rect1
        x2, y2, w2, h2 = rect2
        return not (x1 + w1 < x2 or x2 + w2 < x1 or y1 + h1 < y2 or y2 + h2 < y1)

    def check_hits(self):
        # Check player hitting opponent
        if self.player.is_attacking():
            attack_hitbox = self.player.get_attack_hitbox()
            if attack_hitbox and self.opponent.state != cfg.STATE_BLOCKING:
                if self.check_collision(attack_hitbox, self.opponent.rect):
                    damage = self.opponent.take_hit(1)
                    self.player.score_point()
                    self.show_message("HIT!", 30)
                    self.check_round_end()
                    return

        # Check opponent hitting player
        if self.opponent.is_attacking():
            attack_hitbox = self.opponent.get_attack_hitbox()
            if attack_hitbox and self.player.state != cfg.STATE_BLOCKING:
                if self.check_collision(attack_hitbox, self.player.rect):
                    damage = self.player.take_hit(1)
                    self.opponent.score_point()
                    self.show_message("OUCH!", 30)
                    self.check_round_end()
                    return

    def check_round_end(self):
        if self.player.score >= cfg.POINTS_TO_WIN:
            self.player.win_round()
            self.round_winner = self.player
            self.game_state = "round_end"
            self.show_message("PLAYER WINS ROUND!", 90)
            self.check_match_end()
        elif self.opponent.score >= cfg.POINTS_TO_WIN:
            self.opponent.win_round()
            self.round_winner = self.opponent
            self.game_state = "round_end"
            self.show_message("OPPONENT WINS ROUND!", 90)
            self.check_match_end()

    def check_match_end(self):
        if self.player.wins >= 2:
            self.match_winner = self.player
            self.game_state = "match_end"
            self.show_message("YOU WIN THE MATCH!", 180)
        elif self.opponent.wins >= 2:
            self.match_winner = self.opponent
            self.game_state = "match_end"
            self.show_message("YOU LOSE THE MATCH!", 180)

    def show_message(self, text: str, duration: int):
        self.message = text
        self.message_timer = duration

    def update(self):
        if self.game_state == "playing":
            self.player.update()
            self.opponent.update()
            self.opponent.update_ai(self.player)
            self.check_hits()

        # Handle round reset
        if self.message_timer > 0:
            self.message_timer -= 1
            if self.message_timer == 0 and self.game_state == "round_end":
                if self.match_winner is None:
                    self.reset_round()
                else:
                    # Continue to show match end message
                    pass

        # Allow restart after match ends
        if self.game_state == "match_end" and self.message_timer == 0:
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE]:
                self.reset_match()

    def reset_round(self):
        self.player.reset_position(True)
        self.opponent.reset_position(False)
        self.player.facing_right = True
        self.opponent.facing_right = False
        self.game_state = "playing"
        self.round_winner = None
        self.show_message("FIGHT!", 60)

    def reset_match(self):
        self.player.reset_match()
        self.opponent.reset_match()
        self.player.reset_position(True)
        self.opponent.reset_position(False)
        self.player.facing_right = True
        self.opponent.facing_right = False
        self.game_state = "playing"
        self.match_winner = None
        self.show_message("NEW MATCH!", 60)

    def draw_fighter(self, fighter: Fighter, color):
        # Body
        body_rect = (fighter.x, fighter.y, fighter.width, fighter.height)
        pygame.draw.rect(self.screen, color, body_rect)

        # Head
        head_size = 20
        head_x = fighter.x + fighter.width // 2 - head_size // 2
        head_y = fighter.y - head_size - 5
        pygame.draw.rect(self.screen, color, (head_x, head_y, head_size, head_size))

        # Eyes (show direction)
        eye_color = (255, 255, 255)
        eye_size = 4
        if fighter.facing_right:
            pygame.draw.rect(self.screen, eye_color, (head_x + 12, head_y + 5, eye_size, eye_size))
        else:
            pygame.draw.rect(self.screen, eye_color, (head_x + 4, head_y + 5, eye_size, eye_size))

        # Attack visualization
        if fighter.is_attacking() and fighter.current_attack:
            attack_color = cfg.COLOR_ATTACK
            hitbox = fighter.get_attack_hitbox()
            if hitbox:
                pygame.draw.rect(self.screen, attack_color, hitbox, 2)

        # Block visualization
        if fighter.is_blocking():
            block_color = cfg.COLOR_BLOCK
            shield_rect = (
                fighter.x + (0 if fighter.facing_right else -20),
                fighter.y + 10,
                fighter.width + 20,
                fighter.height - 10
            )
            pygame.draw.rect(self.screen, block_color, shield_rect, 3)

        # Hit flash
        if fighter.state == cfg.STATE_HIT:
            pygame.draw.rect(self.screen, (255, 255, 255), body_rect, 3)

    def draw_ui(self):
        # Ground
        pygame.draw.rect(self.screen, cfg.COLOR_GROUND, (0, cfg.GROUND_Y, cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT - cfg.GROUND_Y))

        # Score panel
        panel_height = 60
        pygame.draw.rect(self.screen, cfg.COLOR_UI, (0, 0, cfg.SCREEN_WIDTH, panel_height))

        # Scores
        player_text = self.font.render(f"P1: {self.player.wins} | Score: {self.player.score}/{cfg.POINTS_TO_WIN}",
                                       True, cfg.COLOR_TEXT)
        opponent_text = self.font.render(f"CPU: {self.opponent.wins} | Score: {self.opponent.score}/{cfg.POINTS_TO_WIN}",
                                         True, cfg.COLOR_TEXT)

        self.screen.blit(player_text, (20, 15))
        self.screen.blit(opponent_text, (cfg.SCREEN_WIDTH - opponent_text.get_width() - 20, 15))

        # Controls hint
        controls = "Arrows: Move | A: High Attack | S: Low Attack | D: Block | ESC: Quit"
        controls_surf = self.small_font.render(controls, True, (150, 150, 150))
        self.screen.blit(controls_surf, (cfg.SCREEN_WIDTH // 2 - controls_surf.get_width() // 2, cfg.SCREEN_HEIGHT - 20))

        # Message
        if self.message:
            msg_surf = self.font.render(self.message, True, cfg.COLOR_ATTACK)
            self.screen.blit(msg_surf, (cfg.SCREEN_WIDTH // 2 - msg_surf.get_width() // 2, 100))

        # Match end restart prompt
        if self.game_state == "match_end" and self.message_timer == 0:
            restart_text = self.small_font.render("Press SPACE to restart", True, cfg.COLOR_TEXT)
            self.screen.blit(restart_text, (cfg.SCREEN_WIDTH // 2 - restart_text.get_width() // 2, 150))

    def draw(self):
        self.screen.fill(cfg.COLOR_BG)
        self.draw_ui()
        self.draw_fighter(self.player, cfg.COLOR_PLAYER)
        self.draw_fighter(self.opponent, cfg.COLOR_OPPONENT)
        pygame.display.flip()

    def run(self):
        self.show_message("FIGHT!", 60)
        while self.running:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(cfg.FPS)

        pygame.quit()
        sys.exit()


def main():
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
