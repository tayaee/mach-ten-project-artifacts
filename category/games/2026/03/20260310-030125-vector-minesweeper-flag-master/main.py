"""Entry point for Vector Minesweeper Flag Master."""

import pygame
from game import Game


def main():
    pygame.init()
    game = Game()
    game.run()


if __name__ == "__main__":
    main()
