"""Vector Ice Block Pengo Logic - Game implementation."""

import sys
import random
import pygame
from config import *


class PengoGame:
    """Main Pengo game class."""

    def __init__(self):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Ice Block Pengo Logic")
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.Font(None, FONT_SIZE_LARGE)
        self.font_medium = pygame.font.Font(None, FONT_SIZE_MEDIUM)
        self.font_small = pygame.font.Font(None, FONT_SIZE_SMALL)

        self.reset_game()

    def reset_game(self):
        """Reset the game to initial state."""
        self.grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]
        self.player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]
        self.enemies = []
        self.lives = STARTING_LIVES
        self.score = 0
        self.level = 1
        self.game_over = False
        self.victory = False
        self.sliding_block = None
        self.block_slide_progress = 0
        self.block_start_pos = None
        self.block_end_pos = None
        self.block_direction = None
        self.enemies_to_crush = []
        self.last_enemy_move = pygame.time.get_ticks()
        self.message = ""
        self.message_timer = 0

        self._init_level()

    def _init_level(self):
        """Initialize level with walls, ice blocks, diamonds, and enemies."""
        self.grid = [[EMPTY for _ in range(GRID_SIZE)] for _ in range(GRID_SIZE)]

        # Place walls around the border (corners have no walls in classic Pengo)
        for i in range(1, GRID_SIZE - 1):
            self.grid[0][i] = WALL
            self.grid[GRID_SIZE - 1][i] = WALL
            self.grid[i][0] = WALL
            self.grid[i][GRID_SIZE - 1] = WALL

        # Place ice blocks in a pattern, leaving space for player
        block_positions = []
        for row in range(2, GRID_SIZE - 2):
            for col in range(2, GRID_SIZE - 2):
                # Skip center area for player
                if abs(row - GRID_SIZE // 2) <= 1 and abs(col - GRID_SIZE // 2) <= 1:
                    continue
                # Checkerboard-ish pattern
                if (row + col) % 3 == 0:
                    block_positions.append((row, col))

        # Place 3 diamond blocks among the ice blocks
        diamond_positions = random.sample(block_positions, min(3, len(block_positions)))
        for pos in diamond_positions:
            block_positions.remove(pos)
            self.grid[pos[0]][pos[1]] = DIAMOND_BLOCK

        # Place remaining ice blocks
        for pos in block_positions[:40]:  # Limit to 40 ice blocks
            self.grid[pos[0]][pos[1]] = ICE_BLOCK

        # Reset player position
        self.player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]

        # Place enemies
        self.enemies = []
        num_enemies = min(MAX_ENEMIES, 2 + self.level // 2)
        for _ in range(num_enemies):
            while True:
                row = random.randint(2, GRID_SIZE - 3)
                col = random.randint(2, GRID_SIZE - 3)
                if (self.grid[row][col] == EMPTY and
                        [row, col] != self.player_pos):
                    self.enemies.append({
                        'pos': [row, col],
                        'direction': random.choice(DIRECTIONS)
                    })
                    break

    def is_valid_pos(self, row, col):
        """Check if position is within grid bounds."""
        return 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE

    def get_cell(self, row, col):
        """Get cell content safely."""
        if self.is_valid_pos(row, col):
            return self.grid[row][col]
        return WALL

    def move_player(self, direction):
        """Move player in given direction."""
        if self.game_over or self.victory or self.sliding_block:
            return

        dx, dy = direction
        new_row = self.player_pos[0] + dy
        new_col = self.player_pos[1] + dx

        if not self.is_valid_pos(new_row, new_col):
            return

        cell = self.get_cell(new_row, new_col)

        if cell == EMPTY:
            self.player_pos = [new_row, new_col]
        elif cell in (ICE_BLOCK, DIAMOND_BLOCK):
            self._start_block_slide(new_row, new_col, direction)

    def _start_block_slide(self, row, col, direction):
        """Start sliding a block."""
        dx, dy = direction
        new_row = row + dy
        new_col = col + dx

        if not self.is_valid_pos(new_row, new_col):
            # Block is against wall - break it
            self.grid[row][col] = EMPTY
            self.score += SCORE_BREAK_BLOCK
            self._show_message("BLOCK BREAK!")
            return

        next_cell = self.get_cell(new_row, new_col)

        if next_cell != EMPTY:
            # Block can't move - break it
            self.grid[row][col] = EMPTY
            self.score += SCORE_BREAK_BLOCK
            self._show_message("BLOCK BREAK!")
            return

        # Block can slide
        self.sliding_block = {
            'row': row,
            'col': col,
            'type': self.grid[row][col]
        }
        self.block_start_pos = [row, col]
        self.block_direction = direction
        self.grid[row][col] = EMPTY

        # Find where block will stop
        end_row, end_col = row, col
        crushed_enemies = []

        while self.is_valid_pos(end_row + dy, end_col + dx):
            next_row = end_row + dy
            next_col = end_col + dx
            next_cell = self.get_cell(next_row, next_col)

            # Check for enemies in path
            for enemy in self.enemies:
                if enemy['pos'] == [next_row, next_col]:
                    crushed_enemies.append(enemy)
                    self.block_end_pos = [end_row, end_col]
                    break

            if next_cell != EMPTY or crushed_enemies:
                break

            end_row, end_col = next_row, next_col

        self.block_end_pos = [end_row, end_col]
        self.enemies_to_crush = crushed_enemies

    def _update_block_slide(self):
        """Update sliding block animation."""
        if not self.sliding_block:
            return

        self.block_slide_progress += SLIDE_SPEED

        dx, dy = self.block_direction
        total_distance = (
            abs(self.block_end_pos[0] - self.block_start_pos[0]) +
            abs(self.block_end_pos[1] - self.block_start_pos[1])
        ) * CELL_SIZE

        if self.block_slide_progress >= total_distance:
            # Slide complete
            block_type = self.sliding_block['type']
            self.grid[self.block_end_pos[0]][self.block_end_pos[1]] = block_type

            # Crush enemies
            for enemy in self.enemies_to_crush:
                if enemy in self.enemies:
                    self.enemies.remove(enemy)
                    self.score += SCORE_CRUSH_ENEMY
                    self._show_message("CRUSH!")

            # Check diamond alignment
            if self._check_diamond_alignment():
                self.score += SCORE_ALIGN_DIAMONDS
                self._show_message("DIAMOND BONUS!")

            self.sliding_block = None
            self.block_slide_progress = 0
            self.enemies_to_crush = []

            # Check victory
            if not self.enemies:
                self.victory = True
                self.score += SCORE_LEVEL_CLEAR

    def _check_diamond_alignment(self):
        """Check if 3 diamonds are aligned."""
        diamonds = []
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if self.grid[row][col] == DIAMOND_BLOCK:
                    diamonds.append((row, col))

        if len(diamonds) < 3:
            return False

        # Check horizontal alignment
        for row in range(GRID_SIZE):
            count = sum(1 for d in diamonds if d[0] == row)
            if count >= 3:
                cols = sorted([d[1] for d in diamonds if d[0] == row])
                for i in range(len(cols) - 2):
                    if cols[i + 2] - cols[i] == 2:
                        return True

        # Check vertical alignment
        for col in range(GRID_SIZE):
            count = sum(1 for d in diamonds if d[1] == col)
            if count >= 3:
                rows = sorted([d[0] for d in diamonds if d[1] == col])
                for i in range(len(rows) - 2):
                    if rows[i + 2] - rows[i] == 2:
                        return True

        return False

    def _move_enemies(self):
        """Move enemies toward player or randomly."""
        current_time = pygame.time.get_ticks()
        if current_time - self.last_enemy_move < ENEMY_MOVE_INTERVAL:
            return
        if self.sliding_block:
            return

        self.last_enemy_move = current_time

        for enemy in self.enemies:
            # 70% chance to move toward player, 30% random
            if random.random() < 0.7:
                dx = 0
                dy = 0
                if self.player_pos[0] > enemy['pos'][0]:
                    dy = 1
                elif self.player_pos[0] < enemy['pos'][0]:
                    dy = -1

                if self.player_pos[1] > enemy['pos'][1]:
                    dx = 1
                elif self.player_pos[1] < enemy['pos'][1]:
                    dx = -1

                # Prefer axis with greater distance
                if abs(self.player_pos[0] - enemy['pos'][0]) > abs(self.player_pos[1] - enemy['pos'][1]):
                    dx = 0
                else:
                    dy = 0

                if dx != 0 or dy != 0:
                    new_row = enemy['pos'][0] + dy
                    new_col = enemy['pos'][1] + dx
                    if (self.is_valid_pos(new_row, new_col) and
                            self.get_cell(new_row, new_col) == EMPTY and
                            [new_row, new_col] != self.player_pos):
                        enemy['pos'] = [new_row, new_col]
                        enemy['direction'] = (dx, dy)
                        continue

            # Random movement
            possible_moves = []
            for dx, dy in DIRECTIONS:
                new_row = enemy['pos'][0] + dy
                new_col = enemy['pos'][1] + dx
                if (self.is_valid_pos(new_row, new_col) and
                        self.get_cell(new_row, new_col) == EMPTY):
                    possible_moves.append((dx, dy))

            if possible_moves:
                dx, dy = random.choice(possible_moves)
                enemy['pos'] = [enemy['pos'][0] + dy, enemy['pos'][1] + dx]
                enemy['direction'] = (dx, dy)

        # Check collision with player
        for enemy in self.enemies:
            if enemy['pos'] == self.player_pos:
                self._player_hit()

    def _player_hit(self):
        """Handle player being hit by enemy."""
        self.lives -= 1
        if self.lives <= 0:
            self.game_over = True
        else:
            # Reset positions but keep grid
            self.player_pos = [GRID_SIZE // 2, GRID_SIZE // 2]
            for enemy in self.enemies:
                enemy['pos'] = [
                    random.randint(2, GRID_SIZE - 3),
                    random.randint(2, GRID_SIZE - 3)
                ]
            self._show_message("OUCH!")

    def _show_message(self, text):
        """Show temporary message."""
        self.message = text
        self.message_timer = pygame.time.get_ticks()

    def handle_event(self, event):
        """Handle pygame events."""
        if event.type == pygame.QUIT:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                return False
            if event.key == pygame.K_r:
                if self.game_over or self.victory:
                    self.reset_game()
                else:
                    self.score = 0
                    self.level = 1
                    self._init_level()

            if not self.sliding_block and not self.game_over and not self.victory:
                if event.key == pygame.K_UP:
                    self.move_player(UP)
                elif event.key == pygame.K_DOWN:
                    self.move_player(DOWN)
                elif event.key == pygame.K_LEFT:
                    self.move_player(LEFT)
                elif event.key == pygame.K_RIGHT:
                    self.move_player(RIGHT)
                elif event.key == pygame.K_SPACE:
                    # Push in facing direction or current movement direction
                    pass

        return True

    def update(self):
        """Update game state."""
        if not self.game_over and not self.victory:
            self._update_block_slide()
            self._move_enemies()

    def _draw_cell(self, row, col, x, y):
        """Draw a single grid cell."""
        cell = self.grid[row][col]

        if cell == WALL:
            pygame.draw.rect(self.screen, COLOR_WALL, (x, y, CELL_SIZE, CELL_SIZE))
            pygame.draw.rect(self.screen, COLOR_GRID, (x, y, CELL_SIZE, CELL_SIZE), 1)

        elif cell == ICE_BLOCK:
            pygame.draw.rect(self.screen, COLOR_ICE_BLOCK,
                           (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4))
            pygame.draw.rect(self.screen, COLOR_ICE_BLOCK_BORDER,
                           (x + 2, y + 2, CELL_SIZE - 4, CELL_SIZE - 4), 2)

        elif cell == DIAMOND_BLOCK:
            center_x = x + CELL_SIZE // 2
            center_y = y + CELL_SIZE // 2
            size = CELL_SIZE // 3
            points = [
                (center_x, center_y - size),
                (center_x + size, center_y),
                (center_x, center_y + size),
                (center_x - size, center_y)
            ]
            pygame.draw.polygon(self.screen, COLOR_DIAMOND_BLOCK, points)
            pygame.draw.polygon(self.screen, COLOR_DIAMOND_BORDER, points, 2)

    def draw(self):
        """Draw everything."""
        self.screen.fill(COLOR_BG)

        # Draw grid
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                x = GRID_OFFSET_X + col * CELL_SIZE
                y = GRID_OFFSET_Y + row * CELL_SIZE
                self._draw_cell(row, col, x, y)

        # Draw sliding block
        if self.sliding_block:
            start_x = GRID_OFFSET_X + self.block_start_pos[1] * CELL_SIZE
            start_y = GRID_OFFSET_Y + self.block_start_pos[0] * CELL_SIZE
            end_x = GRID_OFFSET_X + self.block_end_pos[1] * CELL_SIZE
            end_y = GRID_OFFSET_Y + self.block_end_pos[0] * CELL_SIZE

            dx, dy = self.block_direction
            progress = self.block_slide_progress / CELL_SIZE
            block_x = start_x + dx * self.block_slide_progress
            block_y = start_y + dy * self.block_slide_progress

            if self.sliding_block['type'] == ICE_BLOCK:
                pygame.draw.rect(self.screen, COLOR_ICE_BLOCK,
                               (block_x + 2, block_y + 2, CELL_SIZE - 4, CELL_SIZE - 4))
                pygame.draw.rect(self.screen, COLOR_ICE_BLOCK_BORDER,
                               (block_x + 2, block_y + 2, CELL_SIZE - 4, CELL_SIZE - 4), 2)
            else:
                center_x = block_x + CELL_SIZE // 2
                center_y = block_y + CELL_SIZE // 2
                size = CELL_SIZE // 3
                points = [
                    (center_x, center_y - size),
                    (center_x + size, center_y),
                    (center_x, center_y + size),
                    (center_x - size, center_y)
                ]
                pygame.draw.polygon(self.screen, COLOR_DIAMOND_BLOCK, points)
                pygame.draw.polygon(self.screen, COLOR_DIAMOND_BORDER, points, 2)

        # Draw enemies
        for enemy in self.enemies:
            ex = GRID_OFFSET_X + enemy['pos'][1] * CELL_SIZE
            ey = GRID_OFFSET_Y + enemy['pos'][0] * CELL_SIZE
            pygame.draw.circle(self.screen, COLOR_ENEMY,
                             (ex + CELL_SIZE // 2, ey + CELL_SIZE // 2),
                             CELL_SIZE // 2 - 3)
            pygame.draw.circle(self.screen, COLOR_ENEMY_BORDER,
                             (ex + CELL_SIZE // 2, ey + CELL_SIZE // 2),
                             CELL_SIZE // 2 - 3, 2)

        # Draw player
        px = GRID_OFFSET_X + self.player_pos[1] * CELL_SIZE
        py = GRID_OFFSET_Y + self.player_pos[0] * CELL_SIZE
        pygame.draw.circle(self.screen, COLOR_PLAYER,
                         (px + CELL_SIZE // 2, py + CELL_SIZE // 2),
                         CELL_SIZE // 2 - 3)
        pygame.draw.circle(self.screen, COLOR_PLAYER_BORDER,
                         (px + CELL_SIZE // 2, py + CELL_SIZE // 2),
                         CELL_SIZE // 2 - 3, 2)

        # Draw panel
        panel_y = GRID_OFFSET_Y + GRID_SIZE * CELL_SIZE + 10
        pygame.draw.rect(self.screen, COLOR_PANEL,
                        (0, panel_y, SCREEN_WIDTH, SCREEN_HEIGHT - panel_y))

        # Draw score and lives
        score_text = self.font_medium.render(f"SCORE: {self.score}", True, COLOR_TEXT)
        lives_text = self.font_medium.render(f"LIVES: {self.lives}", True, COLOR_TEXT)
        level_text = self.font_medium.render(f"LEVEL: {self.level}", True, COLOR_TEXT)
        enemies_text = self.font_medium.render(f"ENEMIES: {len(self.enemies)}", True, COLOR_TEXT)

        self.screen.blit(score_text, (20, panel_y + 10))
        self.screen.blit(lives_text, (200, panel_y + 10))
        self.screen.blit(level_text, (350, panel_y + 10))
        self.screen.blit(enemies_text, (500, panel_y + 10))

        # Draw message
        if pygame.time.get_ticks() - self.message_timer < 1500:
            msg_surface = self.font_large.render(self.message, True, COLOR_HIGHLIGHT)
            self.screen.blit(msg_surface,
                           (SCREEN_WIDTH // 2 - msg_surface.get_width() // 2, panel_y + 45))

        # Draw game over / victory
        if self.game_over:
            go_text = self.font_large.render("GAME OVER - Press R to restart", True, COLOR_ENEMY)
            self.screen.blit(go_text,
                           (SCREEN_WIDTH // 2 - go_text.get_width() // 2, panel_y + 45))
        elif self.victory:
            vic_text = self.font_large.render("VICTORY! Press R for next level", True, COLOR_PLAYER)
            self.screen.blit(vic_text,
                           (SCREEN_WIDTH // 2 - vic_text.get_width() // 2, panel_y + 45))

        # Draw controls hint
        hint_text = self.font_small.render("ARROWS: Move | R: Restart | ESC: Quit", True, (100, 100, 120))
        self.screen.blit(hint_text, (SCREEN_WIDTH - hint_text.get_width() - 10, SCREEN_HEIGHT - 20))

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True
        while running:
            for event in pygame.event.get():
                if not self.handle_event(event):
                    running = False

            self.update()
            self.draw()
            self.clock.tick(60)

        pygame.quit()
        sys.exit()


# Alias for consistency
Game = PengoGame
