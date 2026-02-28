"""Game state and tumbleweed physics logic for Vector Tumble Weed Dodge."""

from dataclasses import dataclass
from typing import List
import random
import time


@dataclass
class Vec2:
    x: float
    y: float


class Player:
    def __init__(self, x: float, y: float):
        self.pos = Vec2(x, y)
        self.width = 30
        self.height = 40
        self.speed = 300
        self.alive = True

    def move_up(self, dt: float, bounds_height: int):
        if self.alive:
            self.pos.y -= self.speed * dt
            self.pos.y = max(0, self.pos.y)

    def move_down(self, dt: float, bounds_height: int):
        if self.alive:
            self.pos.y += self.speed * dt
            self.pos.y = min(bounds_height - self.height, self.pos.y)

    def get_rect(self) -> tuple:
        return (self.pos.x, self.pos.y, self.width, self.height)


class Tumbleweed:
    def __init__(self, x: float, y: float, size: int, speed: float):
        self.pos = Vec2(x, y)
        self.size = size
        self.speed = speed
        self.rotation = 0
        self.rotation_speed = speed * 3
        self.dodged = False

    def update(self, dt: float):
        self.pos.x -= self.speed * dt
        self.rotation += self.rotation_speed * dt

    def get_rect(self) -> tuple:
        return (self.pos.x, self.pos.y, self.size, self.size)

    def is_off_screen(self, width: int) -> bool:
        return self.pos.x + self.size < 0


class GameState:
    def __init__(self):
        self.width = 800
        self.height = 400
        self.reset()

    def reset(self):
        start_x = 50
        start_y = self.height // 2 - 20
        self.player = Player(start_x, start_y)

        self.score = 0
        self.game_over = False

        self.tumbleweeds: List[Tumbleweed] = []

        self.spawn_timer = 0
        self.spawn_interval = 1.5

        self.game_time = 0
        self.last_time = time.time()
        self.score_timer = 0

        self.difficulty_level = 1

    def update(self, dt: float):
        if self.game_over:
            return

        current_time = time.time()
        elapsed = current_time - self.last_time
        self.last_time = current_time

        self.game_time += elapsed
        self.score_timer += elapsed

        # Difficulty scaling every 10 seconds
        self.difficulty_level = 1 + (self.game_time // 10)

        # Score for survival (1 point per second)
        if self.score_timer >= 1.0:
            self.score += 1
            self.score_timer = 0

        # Spawn tumbleweeds
        self.spawn_timer += dt
        spawn_threshold = max(0.4, self.spawn_interval - (self.difficulty_level - 1) * 0.15)

        if self.spawn_timer >= spawn_threshold:
            self.spawn_tumbleweed()
            self.spawn_timer = 0

        # Update tumbleweeds
        for tumbleweed in self.tumbleweeds[:]:
            tumbleweed.update(dt)

            # Score for dodging (when passing the left edge)
            if not tumbleweed.dodged and tumbleweed.is_off_screen(self.width):
                self.score += 10
                tumbleweed.dodged = True

            if tumbleweed.is_off_screen(self.width):
                self.tumbleweeds.remove(tumbleweed)

        # Check collisions
        player_rect = self.player.get_rect()
        for tumbleweed in self.tumbleweeds:
            if self._rects_collide(player_rect, tumbleweed.get_rect()):
                self.game_over = True
                self.player.alive = False
                return

    def spawn_tumbleweed(self):
        # Size varies between 20 and 50
        size = random.randint(20, 50)

        # Y position (ensure it's within bounds)
        y = random.randint(10, self.height - size - 10)

        # Speed increases with difficulty
        base_speed = 150 + (self.difficulty_level * 30)
        speed = base_speed + random.uniform(-20, 50)

        x = self.width + size
        self.tumbleweeds.append(Tumbleweed(x, y, size, speed))

    def _rects_collide(self, r1, r2) -> bool:
        return (r1[0] < r2[0] + r2[2] and
                r1[0] + r1[2] > r2[0] and
                r1[1] < r2[1] + r2[3] and
                r1[1] + r1[3] > r2[1])
