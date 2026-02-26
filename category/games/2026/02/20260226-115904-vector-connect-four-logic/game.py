"""Main game logic for Vector Connect Four Logic."""

import pygame
import sys
import random
from typing import Optional, Tuple, List

from config import (
    SCREEN_WIDTH, SCREEN_HEIGHT, GRID_COLS, GRID_ROWS, CELL_SIZE,
    MARGIN_X, MARGIN_Y, BACKGROUND_COLOR, GRID_COLOR, TEXT_COLOR,
    PLAYER1_COLOR, PLAYER2_COLOR, EMPTY_COLOR, COLUMN_HIGHLIGHT,
    WIN_COLOR, FPS, WIN_SCORE, DRAW_SCORE, ANIMATION_SPEED,
    EMPTY, PLAYER1, PLAYER2
)


class Game:
    """Main game class for Connect Four."""

    def __init__(self, ai_enabled: bool = True):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Vector Connect Four Logic")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.large_font = pygame.font.Font(None, 72)

        # Game state
        self.board = [[EMPTY for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.current_player = PLAYER1
        self.game_state = "playing"  # playing, win, draw, ai_thinking
        self.winner = None
        self.win_line = []
        self.player1_score = 0
        self.player2_score = 0
        self.ai_enabled = ai_enabled

        # Animation state
        self.animating = False
        self.anim_col = -1
        self.anim_row = -1
        self.anim_player = EMPTY
        self.anim_y = -1

    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            dt = self.clock.tick(FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    self.handle_keydown(event)
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.handle_mouse_down(event)
                elif event.type == pygame.MOUSEMOTION:
                    self.handle_mouse_motion(event)

            self.update(dt)
            self.draw()
            pygame.display.flip()

        pygame.quit()
        sys.exit()

    def handle_keydown(self, event: pygame.event.Event) -> None:
        """Handle keyboard input."""
        if event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        elif event.key == pygame.K_r:
            self.reset_game()
        elif event.key == pygame.K_a:
            self.ai_enabled = not self.ai_enabled

    def handle_mouse_down(self, event: pygame.event.Event) -> None:
        """Handle mouse button press."""
        if self.game_state != "playing":
            self.reset_game()
            return

        col = self.screen_to_column(event.pos[0])
        if col is not None and self.can_drop(col):
            self.drop_piece(col, self.current_player)

    def handle_mouse_motion(self, event: pygame.event.Event) -> None:
        """Handle mouse motion for column highlighting."""
        pass

    def screen_to_column(self, x: int) -> Optional[int]:
        """Convert screen x coordinate to column index."""
        if MARGIN_X <= x < MARGIN_X + GRID_COLS * CELL_SIZE:
            return (x - MARGIN_X) // CELL_SIZE
        return None

    def can_drop(self, col: int) -> bool:
        """Check if a piece can be dropped in the given column."""
        return self.board[0][col] == EMPTY

    def get_drop_row(self, col: int) -> Optional[int]:
        """Get the row where a piece will land in the given column."""
        for row in range(GRID_ROWS - 1, -1, -1):
            if self.board[row][col] == EMPTY:
                return row
        return None

    def drop_piece(self, col: int, player: int) -> None:
        """Drop a piece in the given column."""
        row = self.get_drop_row(col)
        if row is None:
            return

        self.animating = True
        self.anim_col = col
        self.anim_row = row
        self.anim_player = player
        self.anim_y = MARGIN_Y - CELL_SIZE

    def update(self, dt: float) -> None:
        """Update game state."""
        if self.animating:
            # Animate piece falling
            target_y = MARGIN_Y + self.anim_row * CELL_SIZE
            self.anim_y += ANIMATION_SPEED
            if self.anim_y >= target_y:
                self.anim_y = target_y
                self.board[self.anim_row][self.anim_col] = self.anim_player
                self.animating = False

                # Check for win or draw
                if self.check_win(self.anim_player):
                    self.game_state = "win"
                    self.winner = self.anim_player
                    if self.anim_player == PLAYER1:
                        self.player1_score += WIN_SCORE
                    else:
                        self.player2_score += WIN_SCORE
                elif self.is_board_full():
                    self.game_state = "draw"
                    self.player1_score += DRAW_SCORE
                    self.player2_score += DRAW_SCORE
                else:
                    # Switch player
                    self.current_player = PLAYER2 if self.current_player == PLAYER1 else PLAYER1

                    # AI move
                    if self.ai_enabled and self.current_player == PLAYER2:
                        self.game_state = "ai_thinking"

        elif self.game_state == "ai_thinking":
            # AI makes a move
            col = self.ai_move()
            if col is not None:
                self.game_state = "playing"
                self.drop_piece(col, PLAYER2)

    def ai_move(self) -> Optional[int]:
        """AI selects a column using minimax."""
        valid_cols = [c for c in range(GRID_COLS) if self.can_drop(c)]
        if not valid_cols:
            return None

        # First, try to win
        for col in valid_cols:
            if self.simulate_win(col, PLAYER2):
                return col

        # Second, block opponent from winning
        for col in valid_cols:
            if self.simulate_win(col, PLAYER1):
                return col

        # Prefer center column
        center_col = GRID_COLS // 2
        if center_col in valid_cols:
            valid_cols.remove(center_col)
            valid_cols.insert(0, center_col)

        # Random choice from valid columns
        return random.choice(valid_cols)

    def simulate_win(self, col: int, player: int) -> bool:
        """Simulate dropping a piece and check if it wins."""
        row = self.get_drop_row(col)
        if row is None:
            return False

        # Temporarily place piece
        self.board[row][col] = player
        won = self._check_lines(player)
        self.board[row][col] = EMPTY
        return won

    def check_win(self, player: int) -> bool:
        """Check if the given player has won."""
        if self._check_lines(player):
            self.win_line = self._find_win_line(player)
            return True
        return False

    def _check_lines(self, player: int) -> bool:
        """Check all lines for four in a row."""
        # Check horizontal
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 3):
                if all(self.board[row][col + i] == player for i in range(4)):
                    return True

        # Check vertical
        for row in range(GRID_ROWS - 3):
            for col in range(GRID_COLS):
                if all(self.board[row + i][col] == player for i in range(4)):
                    return True

        # Check diagonal (down-right)
        for row in range(GRID_ROWS - 3):
            for col in range(GRID_COLS - 3):
                if all(self.board[row + i][col + i] == player for i in range(4)):
                    return True

        # Check diagonal (up-right)
        for row in range(3, GRID_ROWS):
            for col in range(GRID_COLS - 3):
                if all(self.board[row - i][col + i] == player for i in range(4)):
                    return True

        return False

    def _find_win_line(self, player: int) -> List[Tuple[int, int]]:
        """Find the winning line of four connected pieces."""
        # Check horizontal
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS - 3):
                if all(self.board[row][col + i] == player for i in range(4)):
                    return [(row, col + i) for i in range(4)]

        # Check vertical
        for row in range(GRID_ROWS - 3):
            for col in range(GRID_COLS):
                if all(self.board[row + i][col] == player for i in range(4)):
                    return [(row + i, col) for i in range(4)]

        # Check diagonal (down-right)
        for row in range(GRID_ROWS - 3):
            for col in range(GRID_COLS - 3):
                if all(self.board[row + i][col + i] == player for i in range(4)):
                    return [(row + i, col + i) for i in range(4)]

        # Check diagonal (up-right)
        for row in range(3, GRID_ROWS):
            for col in range(GRID_COLS - 3):
                if all(self.board[row - i][col + i] == player for i in range(4)):
                    return [(row - i, col + i) for i in range(4)]

        return []

    def is_board_full(self) -> bool:
        """Check if the board is full."""
        return all(self.board[0][col] != EMPTY for col in range(GRID_COLS))

    def reset_game(self) -> None:
        """Reset the game to initial state."""
        self.board = [[EMPTY for _ in range(GRID_COLS)] for _ in range(GRID_ROWS)]
        self.current_player = PLAYER1
        self.game_state = "playing"
        self.winner = None
        self.win_line = []
        self.animating = False

    def draw(self) -> None:
        """Render the game."""
        self.screen.fill(BACKGROUND_COLOR)

        # Draw header
        self.draw_header()

        # Draw column highlights
        self.draw_column_highlight()

        # Draw grid
        self.draw_grid()

        # Draw pieces
        self.draw_pieces()

        # Draw win line
        if self.win_line:
            self.draw_win_line()

        # Draw overlay for game over
        if self.game_state in ["win", "draw"]:
            self.draw_overlay()

    def draw_header(self) -> None:
        """Draw the header with scores and info."""
        player1_text = self.font.render(f"Player 1: {self.player1_score}", True, PLAYER1_COLOR)
        player2_text = self.font.render(f"Player 2: {self.player2_score}", True, PLAYER2_COLOR)
        turn_text_str = "Turn: Player 1" if self.current_player == PLAYER1 else "Turn: Player 2"
        turn_text = self.font.render(turn_text_str, True, TEXT_COLOR)
        ai_text = self.font.render(f"AI: {'ON' if self.ai_enabled else 'OFF'}", True,
                                   (100, 255, 100) if self.ai_enabled else (255, 100, 100))

        self.screen.blit(player1_text, (20, 20))
        self.screen.blit(player2_text, (SCREEN_WIDTH - player2_text.get_width() - 20, 20))
        self.screen.blit(turn_text, (SCREEN_WIDTH // 2 - turn_text.get_width() // 2, 20))
        self.screen.blit(ai_text, (SCREEN_WIDTH // 2 - ai_text.get_width() // 2, 60))

        # Instructions
        if self.game_state == "playing":
            inst_text = self.font.render("Click column or press 0-6 | R: Reset | A: Toggle AI", True, (150, 150, 150))
            self.screen.blit(inst_text, (SCREEN_WIDTH // 2 - inst_text.get_width() // 2, SCREEN_HEIGHT - 30))

    def draw_column_highlight(self) -> None:
        """Draw highlight for the column under mouse."""
        mouse_x, _ = pygame.mouse.get_pos()
        col = self.screen_to_column(mouse_x)
        if col is not None and self.can_drop(col) and self.game_state == "playing":
            x = MARGIN_X + col * CELL_SIZE
            pygame.draw.rect(self.screen, COLUMN_HIGHLIGHT,
                            (x, MARGIN_Y - CELL_SIZE, CELL_SIZE, CELL_SIZE), 0)

    def draw_grid(self) -> None:
        """Draw the game grid."""
        grid_width = GRID_COLS * CELL_SIZE
        grid_height = GRID_ROWS * CELL_SIZE

        # Draw grid background
        pygame.draw.rect(self.screen, EMPTY_COLOR, (MARGIN_X, MARGIN_Y, grid_width, grid_height))

        # Draw grid cells
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                x = MARGIN_X + col * CELL_SIZE
                y = MARGIN_Y + row * CELL_SIZE
                pygame.draw.rect(self.screen, GRID_COLOR, (x, y, CELL_SIZE, CELL_SIZE), 2)

    def draw_pieces(self) -> None:
        """Draw all pieces on the board."""
        for row in range(GRID_ROWS):
            for col in range(GRID_COLS):
                player = self.board[row][col]
                if player != EMPTY:
                    self.draw_piece(row, col, player)

        # Draw animating piece
        if self.animating:
            self.draw_piece_at(self.anim_y, self.anim_col, self.anim_player)

    def draw_piece(self, row: int, col: int, player: int) -> None:
        """Draw a piece at the given grid position."""
        x = MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2
        y = MARGIN_Y + row * CELL_SIZE + CELL_SIZE // 2
        color = PLAYER1_COLOR if player == PLAYER1 else PLAYER2_COLOR
        radius = CELL_SIZE // 2 - 10
        pygame.draw.circle(self.screen, color, (x, y), radius)
        pygame.draw.circle(self.screen, (200, 150, 20) if player == PLAYER1 else (80, 140, 200), (x, y), radius, 3)

    def draw_piece_at(self, y: int, col: int, player: int) -> None:
        """Draw a piece at the given y position and column."""
        x = MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2
        color = PLAYER1_COLOR if player == PLAYER1 else PLAYER2_COLOR
        radius = CELL_SIZE // 2 - 10
        pygame.draw.circle(self.screen, color, (x, int(y) + CELL_SIZE // 2), radius)
        pygame.draw.circle(self.screen, (200, 150, 20) if player == PLAYER1 else (80, 140, 200),
                          (x, int(y) + CELL_SIZE // 2), radius, 3)

    def draw_win_line(self) -> None:
        """Draw a line through the winning pieces."""
        if len(self.win_line) < 2:
            return

        points = []
        for row, col in self.win_line:
            x = MARGIN_X + col * CELL_SIZE + CELL_SIZE // 2
            y = MARGIN_Y + row * CELL_SIZE + CELL_SIZE // 2
            points.append((x, y))

        pygame.draw.lines(self.screen, WIN_COLOR, False, points, 8)

    def draw_overlay(self) -> None:
        """Draw overlay for win or draw states."""
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))

        if self.game_state == "win":
            winner_name = "Player 1" if self.winner == PLAYER1 else "Player 2"
            text = self.large_font.render(f"{winner_name} WINS!", True, WIN_COLOR)
            color = PLAYER1_COLOR if self.winner == PLAYER1 else PLAYER2_COLOR
            pygame.draw.rect(self.screen, color, (SCREEN_WIDTH // 2 - text.get_width() // 2 - 20, SCREEN_HEIGHT // 2 - 70,
                          text.get_width() + 40, 80), 3)
        else:
            text = self.large_font.render("DRAW!", True, (200, 200, 200))

        text_x = SCREEN_WIDTH // 2 - text.get_width() // 2
        text_y = SCREEN_HEIGHT // 2 - 50
        self.screen.blit(text, (text_x, text_y))

        sub_text = self.font.render("Click or press R to play again", True, TEXT_COLOR)
        sub_x = SCREEN_WIDTH // 2 - sub_text.get_width() // 2
        self.screen.blit(sub_text, (sub_x, text_y + 70))

    # AI/RL Interface
    def get_observation(self) -> dict:
        """Get current game state for AI agents."""
        return {
            "board": [row[:] for row in self.board],
            "grid_cols": GRID_COLS,
            "grid_rows": GRID_ROWS,
            "current_player": self.current_player,
            "game_state": self.game_state,
            "player1_score": self.player1_score,
            "player2_score": self.player2_score
        }

    def get_valid_actions(self) -> List[int]:
        """Get list of valid columns to drop a piece."""
        return [c for c in range(GRID_COLS) if self.can_drop(c)]

    def step(self, col: int) -> dict:
        """Execute an action and return the new state."""
        if not self.can_drop(col):
            return {"done": False, "reward": -10, "observation": self.get_observation()}

        player = self.current_player
        self.drop_piece(col, player)

        reward = 0
        done = False

        if self.game_state == "win" and self.winner == player:
            reward = WIN_SCORE
            done = True
        elif self.game_state == "draw":
            reward = DRAW_SCORE
            done = True
        elif self.game_state == "win" and self.winner != player:
            reward = -WIN_SCORE
            done = True

        return {
            "done": done,
            "reward": reward,
            "observation": self.get_observation()
        }
