"""
Track and Field Dash - A rhythm-based 100m sprint game.

Run as fast as you can by alternating LEFT and RIGHT arrow keys.
Watch your stamina and don't press the same key twice or you'll stumble!
"""

import pygame
import sys
from game_state import State, GameState
from athlete import Athlete
from renderer import Renderer


def main():
    """Main game loop."""
    pygame.init()

    WIDTH, HEIGHT = 800, 400
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Track and Field Dash")

    clock = pygame.time.Clock()
    FPS = 60

    state = State()
    athlete = Athlete(state)
    renderer = Renderer(screen)

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0  # Delta time in seconds

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

                elif event.key == pygame.K_SPACE:
                    if state.state == GameState.MENU:
                        state.state = GameState.RUNNING
                    elif state.state == GameState.FINISHED:
                        state.reset()
                        state.state = GameState.RUNNING

                elif state.state == GameState.RUNNING:
                    athlete.handle_input(event.key)

        # Update game state
        athlete.update(dt)

        # Check if stumble is over
        if state.state == GameState.STUMBLE and not state.is_stumbling():
            state.state = GameState.RUNNING

        # Render
        renderer.draw_background()
        renderer.draw_finish_line(state.distance / state.TARGET_DISTANCE)

        if state.state in (GameState.RUNNING, GameState.STUMBLE):
            renderer.draw_athlete(state)
            renderer.draw_ui(state)
        elif state.state == GameState.MENU:
            renderer.draw_menu(state)
        elif state.state == GameState.FINISHED:
            renderer.draw_athlete(state)
            renderer.draw_finished(state)

        pygame.display.flip()

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
