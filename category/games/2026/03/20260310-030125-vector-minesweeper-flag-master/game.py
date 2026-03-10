"""Main game class for Vector Minesweeper Flag Master."""

import pygame
import sys
import random
from config import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    CELL_SIZE,
    GRID_ROWS,
    GRID_COLS,
    MINE_COUNT,
    MARGIN,
    UI_HEIGHT,
    COLORS,
    FONT_SIZE,
    TITLE_FONT_SIZE,
)


class Cell:
    """Represents a single cell in the minesweeper grid."""

    def __init__(self, row, col):
        self.row = row
        self.col = col
        self.is_mine = False
        self.is_covered = True
        self.is_flagged = False
        self.adjacent_mines = 0


class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Minesweeper Flag Master")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, FONT_SIZE)
        self.title_font = pygame.font.Font(None, TITLE_FONT_SIZE)
        self.reset_game()

    def reset_game(self):
        self.grid = [[Cell(r, c) for c in range(GRID_COLS)] for r in range(GRID_ROWS)]
        self.mines_placed = False
        self.game_over = False
        self.won = False
        self.start_time = None
        self.elapsed_time = 0
        self.flags_placed = 0
        self.cells_uncovered = 0

    def place_mines(self, safe_row, safe_col):
        """Place mines randomly, ensuring the first clicked cell is safe."""
        positions = [(r, c) for r in range(GRID_ROWS) for c in range(GRID_COLS)]
        # Remove the first clicked cell and its neighbors from mine positions
        safe_neighbors = self.get_neighbors(safe_row, safe_col)
        safe_neighbors.add((safe_row, safe_col))
        for pos in safe_neighbors:
            if pos in positions:
                positions.remove(pos)

        mine_positions = random.sample(positions, MINE_COUNT)
        for r, c in mine_positions:
            self.grid[r][c].is_mine = True

        self.calculate_adjacent_mines()
        self.mines_placed = True

    def get_neighbors(self, row, col):
        """Get all valid neighbor positions."""
        neighbors = set()
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue
                nr, nc = row + dr, col + dc
                if 0 <= nr < GRID_ROWS and 0 <= nc < GRID_COLS:
                    neighbors.add((nr, nc))
        return neighbors

    def calculate_adjacent_mines(self):
        """Calculate adjacent mine count for each cell."""
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c].is_mine:
                    continue
                neighbors = self.get_neighbors(r, c)
                count = sum(1 for nr, nc in neighbors if self.grid[nr][nc].is_mine)
                self.grid[r][c].adjacent_mines = count

    def uncover_cell(self, row, col):
        """Uncover a cell and recursively uncover adjacent cells if no mines nearby."""
        cell = self.grid[row][col]

        if not cell.is_covered or cell.is_flagged:
            return

        cell.is_covered = False
        self.cells_uncovered += 1

        if cell.is_mine:
            self.game_over = True
            self.reveal_all_mines()
            return

        if cell.adjacent_mines == 0:
            neighbors = self.get_neighbors(row, col)
            for nr, nc in neighbors:
                if self.grid[nr][nc].is_covered:
                    self.uncover_cell(nr, nc)

        self.check_win()

    def toggle_flag(self, row, col):
        """Toggle flag on a covered cell."""
        cell = self.grid[row][col]
        if not cell.is_covered:
            return
        cell.is_flagged = not cell.is_flagged
        self.flags_placed += 1 if cell.is_flagged else -1

    def reveal_all_mines(self):
        """Reveal all mines when game is lost."""
        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                if self.grid[r][c].is_mine:
                    self.grid[r][c].is_covered = False

    def check_win(self):
        """Check if all non-mine cells have been uncovered."""
        safe_cells = GRID_ROWS * GRID_COLS - MINE_COUNT
        if self.cells_uncovered == safe_cells:
            self.game_over = True
            self.won = True

    def get_cell_from_pos(self, pos):
        """Get cell coordinates from screen position."""
        x, y = pos
        grid_start_x = (SCREEN_WIDTH - GRID_COLS * CELL_SIZE) // 2
        grid_start_y = MARGIN + UI_HEIGHT

        if not (grid_start_x <= x < grid_start_x + GRID_COLS * CELL_SIZE):
            return None
        if not (grid_start_y <= y < grid_start_y + GRID_ROWS * CELL_SIZE):
            return None

        col = (x - grid_start_x) // CELL_SIZE
        row = (y - grid_start_y) // CELL_SIZE

        if 0 <= row < GRID_ROWS and 0 <= col < GRID_COLS:
            return row, col
        return None

    def handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                if self.game_over and event.key == pygame.K_SPACE:
                    self.reset_game()

            if event.type == pygame.MOUSEBUTTONDOWN and not self.game_over:
                cell_pos = self.get_cell_from_pos(event.pos)
                if cell_pos is None:
                    continue

                row, col = cell_pos

                if event.button == 1:  # Left click
                    if not self.mines_placed:
                        self.start_time = pygame.time.get_ticks()
                        self.place_mines(row, col)
                    self.uncover_cell(row, col)

                elif event.button == 3:  # Right click
                    if self.mines_placed:
                        self.toggle_flag(row, col)

    def update(self):
        if self.game_over:
            return

        if self.start_time:
            self.elapsed_time = (pygame.time.get_ticks() - self.start_time) // 1000

    def draw_cell(self, row, col, x, y):
        """Draw a single cell."""
        cell = self.grid[row][col]
        rect = (x, y, CELL_SIZE - 1, CELL_SIZE - 1)

        if cell.is_covered:
            pygame.draw.rect(self.screen, COLORS["cell_covered"], rect)
            pygame.draw.rect(self.screen, COLORS["grid_line"], rect, 1)
        else:
            pygame.draw.rect(self.screen, COLORS["cell_uncovered"], rect)
            pygame.draw.rect(self.screen, COLORS["grid_line"], rect, 1)

            if cell.is_mine:
                self.draw_mine(x, y)
            elif cell.adjacent_mines > 0:
                color = COLORS["numbers"].get(cell.adjacent_mines, (255, 255, 255))
                text = self.font.render(str(cell.adjacent_mines), True, color)
                text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
                self.screen.blit(text, text_rect)

        if cell.is_flagged:
            self.draw_flag(x, y)

    def draw_mine(self, x, y):
        """Draw a mine icon."""
        center_x = x + CELL_SIZE // 2
        center_y = y + CELL_SIZE // 2
        radius = CELL_SIZE // 4
        pygame.draw.circle(self.screen, COLORS["mine"], (center_x, center_y), radius)

    def draw_flag(self, x, y):
        """Draw a flag icon."""
        cx, cy = x + CELL_SIZE // 2, y + CELL_SIZE // 2
        flag_size = CELL_SIZE // 4
        # Flag triangle
        pygame.draw.polygon(
            self.screen,
            COLORS["flag"],
            [(cx, cy - flag_size), (cx + flag_size, cy - flag_size // 2), (cx, cy)]
        )
        # Flag pole
        pygame.draw.line(self.screen, COLORS["flag"], (cx, cy - flag_size), (cx, cy + flag_size), 2)

    def draw_ui(self):
        """Draw the UI header."""
        title = self.title_font.render("MINESWEEPER", True, COLORS["text"])
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, MARGIN // 2))
        self.screen.blit(title, title_rect)

        info_y = MARGIN + UI_HEIGHT // 2

        flags_text = self.font.render(f"Flags: {self.flags_placed}/{MINE_COUNT}", True, COLORS["text"])
        self.screen.blit(flags_text, (MARGIN, info_y))

        time_text = self.font.render(f"Time: {self.elapsed_time}s", True, COLORS["text"])
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, info_y))
        self.screen.blit(time_text, time_rect)

        progress = self.cells_uncovered * 100 // (GRID_ROWS * GRID_COLS - MINE_COUNT)
        progress_text = self.font.render(f"Progress: {progress}%", True, COLORS["text"])
        progress_rect = progress_text.get_rect(right=SCREEN_WIDTH - MARGIN, top=info_y)
        self.screen.blit(progress_text, progress_rect)

    def draw_grid(self):
        """Draw the game grid."""
        grid_start_x = (SCREEN_WIDTH - GRID_COLS * CELL_SIZE) // 2
        grid_start_y = MARGIN + UI_HEIGHT

        for r in range(GRID_ROWS):
            for c in range(GRID_COLS):
                x = grid_start_x + c * CELL_SIZE
                y = grid_start_y + r * CELL_SIZE
                self.draw_cell(r, c, x, y)

    def draw_game_over(self):
        """Draw game over overlay."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))

        if self.won:
            result_text = self.title_font.render("VICTORY!", True, (0, 255, 100))
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(result_text, result_rect)
        else:
            result_text = self.title_font.render("GAME OVER", True, (255, 100, 100))
            result_rect = result_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            self.screen.blit(result_text, result_rect)

        time_text = self.font.render(f"Time: {self.elapsed_time}s", True, COLORS["text"])
        time_rect = time_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.screen.blit(time_text, time_rect)

        restart_text = self.font.render("Press SPACE to restart", True, COLORS["text"])
        restart_rect = restart_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 50))
        self.screen.blit(restart_text, restart_rect)

    def draw(self):
        self.screen.fill(COLORS["background"])
        self.draw_ui()
        self.draw_grid()

        if self.game_over:
            self.draw_game_over()

        pygame.display.flip()

    def run(self):
        while True:
            self.handle_input()
            self.update()
            self.draw()
            self.clock.tick(60)
