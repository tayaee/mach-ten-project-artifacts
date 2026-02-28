"""Game state and river log physics logic for Vector Frog Log Crossing Logic."""

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Vec2:
    x: float
    y: float


class Player:
    def __init__(self, x: float, y: float):
        self.pos = Vec2(x, y)
        self.alive = True
        self.on_log = False
        self.current_log: Optional['Log'] = None

    def update(self, dt: float):
        if self.on_log and self.current_log:
            self.pos.x += self.current_log.speed * dt


class Log:
    def __init__(self, x: float, y: float, width: int, speed: float):
        self.pos = Vec2(x, y)
        self.width = width
        self.height = 60
        self.speed = speed

    def update(self, dt: float):
        self.pos.x += self.speed * dt

    def get_rect(self):
        return (self.pos.x, self.pos.y, self.width, self.height)


class GameState:
    def __init__(self):
        self.width = 600
        self.height = 600
        self.grid_size = 60
        self.grid_cols = 10
        self.grid_rows = 10
        self.reset()

    def reset(self):
        start_x = (self.grid_cols // 2) * self.grid_size
        start_y = (self.grid_rows - 1) * self.grid_size
        self.player = Player(start_x, start_y)

        self.score = 0
        self.game_over = False
        self.win = False

        self.lanes_crossed = set()

        self.logs: List[Log] = []
        self._init_logs()

    def _init_logs(self):
        log_configs = [
            # (row, width, speed, count, spacing)
            # Lane 1: moves left (row 1)
            (1, 100, -40, 2, 280),
            # Lane 2: moves right (row 2)
            (2, 100, 50, 2, 280),
            # Lane 3: moves left (row 3)
            (3, 80, -60, 2, 280),
            # Lane 4: moves right (row 4)
            (4, 120, 35, 2, 280),
        ]

        for row, width, speed, count, spacing in log_configs:
            y = row * self.grid_size
            for i in range(count):
                x = i * spacing + (row * 27) % 80
                self.logs.append(Log(x, y, width, speed))

    def update(self, dt: float):
        if self.game_over:
            return

        for log in self.logs:
            log.update(dt)
            if log.speed > 0 and log.pos.x > self.width:
                log.pos.x = -log.width
            elif log.speed < 0 and log.pos.x + log.width < 0:
                log.pos.x = self.width

        self.player.update(dt)

        player_row = int(self.player.pos.y // self.grid_size)

        if player_row == 0:
            self.win = True
            self.game_over = True
            return

        if self.player.pos.x < 0 or self.player.pos.x + self.grid_size > self.width:
            self._lose()
            return

        if 1 <= player_row <= 4:
            frog_rect = (
                self.player.pos.x,
                self.player.pos.y,
                self.grid_size,
                self.grid_size
            )

            on_any_log = False
            for log in self.logs:
                log_rect = log.get_rect()
                if self._rects_collide(frog_rect, log_rect):
                    on_any_log = True
                    self.player.on_log = True
                    self.player.current_log = log
                    break

            if not on_any_log:
                self._lose()
                return
        else:
            self.player.on_log = False
            self.player.current_log = None

    def _lose(self):
        self.player.alive = False
        self.game_over = True

    def move(self, direction: str):
        if self.game_over:
            return

        grid_size = self.grid_size
        if direction == 'up':
            self.player.pos.y -= grid_size
        elif direction == 'down':
            self.player.pos.y += grid_size
        elif direction == 'left':
            self.player.pos.x -= grid_size
        elif direction == 'right':
            self.player.pos.x += grid_size

        self.player.on_log = False
        self.player.current_log = None

        player_row = int(self.player.pos.y // self.grid_size)

        if player_row not in self.lanes_crossed and 1 <= player_row <= 4:
            self.lanes_crossed.add(player_row)
            self.score += 10

        if player_row == 0:
            self.score += 100

    def _rects_collide(self, r1, r2) -> bool:
        return (r1[0] < r2[0] + r2[2] and
                r1[0] + r1[2] > r2[0] and
                r1[1] < r2[1] + r2[3] and
                r1[1] + r1[3] > r2[1])
