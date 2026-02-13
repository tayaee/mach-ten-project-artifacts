"""
Snake Game - Classic arcade game where you control a growing snake.
AI-friendly: Simple state space, clear reward structure, deterministic controls.
"""

import os
import pygame
import random
import sys
from enum import Enum
from typing import List, Tuple, Optional


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)


class SnakeGame:
    """
    Snake game implementation optimized for both human play and AI training.

    State representation:
    - Grid-based: 20x20 cells
    - Snake: List of (x, y) coordinates
    - Food: Single (x, y) coordinate
    - Score: Current length - initial length

    Actions: 4 discrete moves (UP, DOWN, LEFT, RIGHT)

    Rewards:
    - +10: Eating food
    - -10: Collision (wall or self)
    - 0: Moving without eating

    Terminal states:
    - Collision with wall
    - Collision with self
    """

    # Game constants
    GRID_SIZE = 20
    CELL_SIZE = 25
    WINDOW_SIZE = GRID_SIZE * CELL_SIZE
    FPS = 10
    INITIAL_LENGTH = 3

    # Colors
    COLOR_BG = (15, 15, 20)
    COLOR_SNAKE_HEAD = (0, 200, 100)
    COLOR_SNAKE_BODY = (0, 150, 70)
    COLOR_FOOD = (220, 50, 50)
    COLOR_GRID = (30, 30, 40)
    COLOR_TEXT = (200, 200, 200)

    def __init__(self, render: bool = True):
        """
        Initialize the game.

        Args:
            render: If False, run in headless mode for AI training
        """
        self.render = render
        if self.render:
            pygame.init()
            pygame.display.set_caption("Snake")
            self.screen = pygame.display.set_mode((self.WINDOW_SIZE, self.WINDOW_SIZE))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 36)
        else:
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            pygame.init()
            pygame.display.set_mode((1, 1))

        self.reset()

    def reset(self) -> None:
        """Reset the game to initial state."""
        # Start snake in the middle
        mid = self.GRID_SIZE // 2
        self.snake: List[Tuple[int, int]] = [
            (mid, mid),
            (mid - 1, mid),
            (mid - 2, mid)
        ]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.score = 0
        self.steps_without_food = 0
        self.max_steps_without_food = self.GRID_SIZE * self.GRID_SIZE
        self._spawn_food()
        self.game_over = False

    def _spawn_food(self) -> None:
        """Place food at a random unoccupied cell."""
        while True:
            food = (
                random.randint(0, self.GRID_SIZE - 1),
                random.randint(0, self.GRID_SIZE - 1)
            )
            if food not in self.snake:
                self.food = food
                break

    def step(self, action: Optional[Direction] = None) -> Tuple[int, bool, int]:
        """
        Execute one game step.

        Args:
            action: Direction to move. If None, use current direction.

        Returns:
            Tuple of (reward, done, score)
            - reward: Immediate reward (+10, -10, or 0)
            - done: Whether the game is over
            - score: Current score
        """
        if self.game_over:
            return 0, True, self.score

        # Update direction if action provided
        if action is not None:
            # Prevent 180-degree turns
            if (action != Direction.UP or self.direction != Direction.DOWN) and \
               (action != Direction.DOWN or self.direction != Direction.UP) and \
               (action != Direction.LEFT or self.direction != Direction.RIGHT) and \
               (action != Direction.RIGHT or self.direction != Direction.LEFT):
                self.next_direction = action

        self.direction = self.next_direction

        # Calculate new head position
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)

        # Check wall collision
        if not (0 <= new_head[0] < self.GRID_SIZE and 0 <= new_head[1] < self.GRID_SIZE):
            self.game_over = True
            return -10, True, self.score

        # Check self collision
        if new_head in self.snake:
            self.game_over = True
            return -10, True, self.score

        # Move snake
        self.snake.insert(0, new_head)

        # Check food eaten
        if new_head == self.food:
            self.score += 10
            self.steps_without_food = 0
            self._spawn_food()
            reward = 10
        else:
            self.snake.pop()
            self.steps_without_food += 1
            reward = 0

        # Check starvation (too many steps without food)
        if self.steps_without_food >= self.max_steps_without_food:
            self.game_over = True
            return -10, True, self.score

        return reward, False, self.score

    def get_state(self) -> dict:
        """
        Get current game state as a dictionary.
        Useful for AI agents to observe the game.
        """
        return {
            'snake': self.snake.copy(),
            'food': self.food,
            'direction': self.direction,
            'score': self.score,
            'game_over': self.game_over
        }

    def get_grid_state(self) -> List[List[int]]:
        """
        Get game state as a 2D grid.
        Returns:
            2D array where:
            - 0: Empty cell
            - 1: Snake body
            - 2: Snake head
            - 3: Food
        """
        grid = [[0 for _ in range(self.GRID_SIZE)] for _ in range(self.GRID_SIZE)]

        for x, y in self.snake:
            grid[y][x] = 1

        if self.snake:
            head_x, head_y = self.snake[0]
            grid[head_y][head_x] = 2

        food_x, food_y = self.food
        grid[food_y][food_x] = 3

        return grid

    def draw(self) -> None:
        """Render the game state."""
        if not self.render:
            return

        self.screen.fill(self.COLOR_BG)

        # Draw grid
        for x in range(0, self.WINDOW_SIZE, self.CELL_SIZE):
            pygame.draw.line(self.screen, self.COLOR_GRID, (x, 0), (x, self.WINDOW_SIZE))
        for y in range(0, self.WINDOW_SIZE, self.CELL_SIZE):
            pygame.draw.line(self.screen, self.COLOR_GRID, (0, y), (self.WINDOW_SIZE, y))

        # Draw food
        food_rect = pygame.Rect(
            self.food[0] * self.CELL_SIZE + 2,
            self.food[1] * self.CELL_SIZE + 2,
            self.CELL_SIZE - 4,
            self.CELL_SIZE - 4
        )
        pygame.draw.ellipse(self.screen, self.COLOR_FOOD, food_rect)

        # Draw snake
        for i, (x, y) in enumerate(self.snake):
            color = self.COLOR_SNAKE_HEAD if i == 0 else self.COLOR_SNAKE_BODY
            rect = pygame.Rect(
                x * self.CELL_SIZE + 1,
                y * self.CELL_SIZE + 1,
                self.CELL_SIZE - 2,
                self.CELL_SIZE - 2
            )
            pygame.draw.rect(self.screen, color, rect, border_radius=3)

        # Draw score
        score_text = self.font.render(f"Score: {self.score}", True, self.COLOR_TEXT)
        self.screen.blit(score_text, (10, 10))

        if self.game_over:
            game_over_text = self.font.render("GAME OVER", True, (220, 50, 50))
            text_rect = game_over_text.get_rect(center=(self.WINDOW_SIZE // 2, self.WINDOW_SIZE // 2))
            self.screen.blit(game_over_text, text_rect)

        pygame.display.flip()

    def handle_input(self) -> Optional[Direction]:
        """
        Handle keyboard input for human control.
        Returns:
            Direction based on key press, or None if no relevant key pressed.
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    return Direction.UP
                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    return Direction.DOWN
                elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    return Direction.LEFT
                elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    return Direction.RIGHT
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
        return None

    def run(self) -> None:
        """Main game loop for human play."""
        while True:
            action = self.handle_input()
            self.step(action)
            self.draw()
            self.clock.tick(self.FPS)


def main():
    """Entry point for running the game."""
    game = SnakeGame(render=True)
    game.run()


if __name__ == "__main__":
    main()
