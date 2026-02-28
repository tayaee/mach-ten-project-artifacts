import pygame
import random
import sys

GRID_SIZE = 10
CELL_SIZE = 60
SCREEN_WIDTH = GRID_SIZE * CELL_SIZE
SCREEN_HEIGHT = GRID_SIZE * CELL_SIZE
FPS = 60

COLOR_BG = (40, 40, 40)
COLOR_GRID = (60, 60, 60)
COLOR_SAFE = (80, 80, 80)
COLOR_GOAL = (120, 120, 120)
COLOR_WATER = (30, 30, 30)
COLOR_LOG = (200, 200, 200)
COLOR_FROG = (255, 255, 255)
COLOR_TEXT = (255, 255, 255)

TIME_LIMIT = 60

class Log:
    def __init__(self, length, speed, direction):
        self.length = length
        self.speed = speed * direction
        self.x = random.randint(0, GRID_SIZE - length)

    def update(self):
        self.x += self.speed
        if self.speed > 0 and self.x > GRID_SIZE:
            self.x = -self.length
        elif self.speed < 0 and self.x + self.length < 0:
            self.x = GRID_SIZE

    def contains(self, col):
        return self.x <= col < self.x + self.length

class RiverRow:
    def __init__(self, row, speed, direction, log_length, num_logs):
        self.row = row
        self.logs = [Log(log_length, speed, direction) for _ in range(num_logs)]
        self.offset = 0

    def update(self):
        self.offset = 0
        for log in self.logs:
            log.update()

    def get_log_at(self, col):
        for log in self.logs:
            if log.contains(col):
                return log
        return None

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Frog River Log Logic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 28)
        self.reset_game()

    def reset_game(self):
        self.frog_col = GRID_SIZE // 2
        self.frog_row = 0
        self.score = 0
        self.highest_row = 0
        self.game_over = False
        self.won = False
        self.time_left = TIME_LIMIT
        self.start_ticks = pygame.time.get_ticks()
        self.river_rows = self.create_river_rows()

    def create_river_rows(self):
        rows = []
        for row in range(1, 9):
            speed = random.choice([0.01, 0.015, 0.02, 0.025])
            direction = random.choice([-1, 1])
            log_length = random.randint(1, 3)
            num_logs = random.randint(2, 4)
            rows.append(RiverRow(row, speed, direction, log_length, num_logs))
        return rows

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
                    if event.key == pygame.K_UP:
                        self.move_frog(0, 1)
                    elif event.key == pygame.K_DOWN:
                        self.move_frog(0, -1)
                    elif event.key == pygame.K_LEFT:
                        self.move_frog(-1, 0)
                    elif event.key == pygame.K_RIGHT:
                        self.move_frog(1, 0)
                    elif event.key == pygame.K_ESCAPE:
                        return False
        return True

    def move_frog(self, dx, dy):
        new_col = self.frog_col + dx
        new_row = self.frog_row + dy

        if 0 <= new_col < GRID_SIZE:
            self.frog_col = new_col
        if 0 <= new_row < GRID_SIZE:
            self.frog_row = new_row

        if self.frog_row > self.highest_row:
            self.highest_row = self.frog_row
            self.score += 10

    def update(self):
        if self.game_over or self.won:
            return

        current_time = pygame.time.get_ticks()
        elapsed = (current_time - self.start_ticks) / 1000
        self.time_left = max(0, TIME_LIMIT - elapsed)

        if self.time_left <= 0:
            self.game_over = True
            return

        for river_row in self.river_rows:
            river_row.update()

        if self.frog_row == 9:
            self.won = True
            self.score += 100
            return

        if 1 <= self.frog_row <= 8:
            river_row = self.river_rows[self.frog_row - 1]
            log = river_row.get_log_at(self.frog_col)

            if log is None:
                self.game_over = True
                return

            self.frog_col += log.speed

            if self.frog_col < 0 or self.frog_col >= GRID_SIZE:
                self.game_over = True
                return

    def draw(self):
        self.screen.fill(COLOR_BG)

        for row in range(GRID_SIZE):
            y = (GRID_SIZE - 1 - row) * CELL_SIZE

            if row == 0:
                pygame.draw.rect(self.screen, COLOR_SAFE, (0, y, SCREEN_WIDTH, CELL_SIZE))
                pygame.draw.rect(self.screen, COLOR_GRID, (0, y, SCREEN_WIDTH, CELL_SIZE), 1)
            elif row == 9:
                pygame.draw.rect(self.screen, COLOR_GOAL, (0, y, SCREEN_WIDTH, CELL_SIZE))
                pygame.draw.rect(self.screen, COLOR_GRID, (0, y, SCREEN_WIDTH, CELL_SIZE), 1)
                goal_text = self.small_font.render("GOAL", True, COLOR_TEXT)
                text_rect = goal_text.get_rect(center=(SCREEN_WIDTH // 2, y + CELL_SIZE // 2))
                self.screen.blit(goal_text, text_rect)
            else:
                pygame.draw.rect(self.screen, COLOR_WATER, (0, y, SCREEN_WIDTH, CELL_SIZE))
                pygame.draw.rect(self.screen, COLOR_GRID, (0, y, SCREEN_WIDTH, CELL_SIZE), 1)

                river_row = self.river_rows[row - 1]
                for log in river_row.logs:
                    log_x = log.x * CELL_SIZE
                    log_width = log.length * CELL_SIZE
                    if log_x + log_width > 0 and log_x < SCREEN_WIDTH:
                        draw_x = max(0, log_x)
                        draw_width = min(log_width, SCREEN_WIDTH - draw_x)
                        pygame.draw.rect(self.screen, COLOR_LOG,
                                       (draw_x + 2, y + 2, draw_width - 4, CELL_SIZE - 4))

        frog_x = self.frog_col * CELL_SIZE
        frog_y = (GRID_SIZE - 1 - self.frog_row) * CELL_SIZE
        pygame.draw.rect(self.screen, COLOR_FROG,
                        (frog_x + 8, frog_y + 8, CELL_SIZE - 16, CELL_SIZE - 16))
        pygame.draw.rect(self.screen, COLOR_BG,
                        (frog_x + 15, frog_y + 15, CELL_SIZE - 30, CELL_SIZE - 30))

        score_text = self.small_font.render(f"Score: {self.score}", True, COLOR_TEXT)
        time_text = self.small_font.render(f"Time: {int(self.time_left)}", True, COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(time_text, (10, 35))

        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            msg_text = self.font.render("GAME OVER", True, COLOR_TEXT)
            score_msg = self.small_font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            retry_msg = self.small_font.render("Press SPACE to retry or ESC to quit", True, COLOR_TEXT)

            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            score_rect = score_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            retry_rect = retry_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))

            self.screen.blit(msg_text, msg_rect)
            self.screen.blit(score_msg, score_rect)
            self.screen.blit(retry_msg, retry_rect)
        elif self.won:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            self.screen.blit(overlay, (0, 0))

            msg_text = self.font.render("GOAL REACHED!", True, COLOR_TEXT)
            score_msg = self.small_font.render(f"Final Score: {self.score}", True, COLOR_TEXT)
            retry_msg = self.small_font.render("Press SPACE to play again or ESC to quit", True, COLOR_TEXT)

            msg_rect = msg_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
            score_rect = score_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
            retry_rect = retry_msg.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40))

            self.screen.blit(msg_text, msg_rect)
            self.screen.blit(score_msg, score_rect)
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
