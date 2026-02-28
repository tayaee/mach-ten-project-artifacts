"""Vector Frog Log Crossing Logic - Main entry point."""

import pygame
import sys

from game import GameState
from renderer import Renderer


def main():
    pygame.init()

    state = GameState()
    renderer = Renderer(state)
    clock = pygame.time.Clock()

    running = True
    while running:
        dt = clock.tick(30) / 1000.0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and state.game_over:
                    state.reset()
                elif event.key == pygame.K_UP and not state.game_over:
                    state.move('up')
                elif event.key == pygame.K_DOWN and not state.game_over:
                    state.move('down')
                elif event.key == pygame.K_LEFT and not state.game_over:
                    state.move('left')
                elif event.key == pygame.K_RIGHT and not state.game_over:
                    state.move('right')

        state.update(dt)
        renderer.render()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
