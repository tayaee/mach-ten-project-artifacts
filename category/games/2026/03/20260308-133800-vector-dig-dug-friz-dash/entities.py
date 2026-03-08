"""Game entities for Dig Dug."""

import random
from enum import Enum
from typing import Optional, List
from config import *


class EntityType(Enum):
    PLAYER = "player"
    POOKA = "pooka"
    FYGAR = "fygar"


class Position:
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y

    def distance_to(self, other: 'Position') -> int:
        return abs(self.x - other.x) + abs(self.y - other.y)


class Player:
    def __init__(self, x: int, y: int):
        self.pos = Position(x, y)
        self.start_pos = Position(x, y)
        self.move_counter = 0
        self.pump_active = False
        self.pump_direction: Optional[str] = None
        self.pump_hit_pos: Optional[Position] = None
        self.facing = "right"

    def reset(self):
        self.pos.x = self.start_pos.x
        self.pos.y = self.start_pos.y
        self.move_counter = 0
        self.pump_active = False
        self.pump_direction = None
        self.pump_hit_pos = None
        self.facing = "right"

    def start_pump(self, direction: str):
        self.pump_active = True
        self.pump_direction = direction
        self.facing = direction

    def can_move(self) -> bool:
        return self.move_counter >= PLAYER_MOVE_DELAY

    def update(self):
        if self.move_counter < PLAYER_MOVE_DELAY:
            self.move_counter += 1


class Enemy:
    def __init__(self, x: int, y: int, entity_type: EntityType):
        self.pos = Position(x, y)
        self.entity_type = entity_type
        self.alive = True
        self.inflation = 0
        self.inflation_timer = 0
        self.move_counter = 0

    def inflate(self):
        self.inflation += 1
        self.inflation_timer = 0

    def deflate(self):
        if self.inflation > 0:
            self.inflation_timer += 1
            if self.inflation_timer >= INFLATION_DECAY_RATE:
                self.inflation -= 1
                self.inflation_timer = 0

    def can_move(self) -> bool:
        if self.inflation > 0:
            return False
        return self.move_counter >= ENEMY_MOVE_DELAY

    def reset_move_counter(self):
        self.move_counter = 0

    def update(self):
        if self.move_counter < ENEMY_MOVE_DELAY:
            self.move_counter += 1
        self.deflate()


class Pooka(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, EntityType.POOKA)
        self.ghost_mode = False


class Fygar(Enemy):
    def __init__(self, x: int, y: int):
        super().__init__(x, y, EntityType.FYGAR)
        self.facing_right = True
        self.breath_cooldown = 0

    def can_breathe_fire(self) -> bool:
        return self.breath_cooldown <= 0

    def breathe_fire(self):
        self.breath_cooldown = FYGAR_BREATH_COOLDOWN

    def update(self):
        super().update()
        if self.breath_cooldown > 0:
            self.breath_cooldown -= 1


class Rock:
    def __init__(self, x: int, y: int):
        self.pos = Position(x, y)
        self.alive = True
        self.state = "stable"  # stable, wobbling, falling
        self.wobble_timer = 0
        self.fall_progress = 0
        self.enemies_crushed: List[Enemy] = []

    def start_wobble(self):
        self.state = "wobbling"
        self.wobble_timer = 0

    def update(self):
        if self.state == "wobbling":
            self.wobble_timer += 1
            if self.wobble_timer >= ROCK_WOBBLE_TIME:
                self.state = "falling"
        elif self.state == "falling":
            self.fall_progress += 1


class Grid:
    def __init__(self, cols: int, rows: int):
        self.cols = cols
        self.rows = rows
        self.cells = [[0 for _ in range(rows)] for _ in range(cols)]  # 0 = soil, 1 = tunnel
        self.rocks: List[Rock] = []
        self._init_grid()

    def _init_grid(self):
        # Create center tunnel
        mid_x = self.cols // 2
        for y in range(1, self.rows - 1):
            self.cells[mid_x][y] = 1

        # Create horizontal tunnels
        mid_y = self.rows // 2
        for x in range(1, self.cols - 1):
            self.cells[x][mid_y] = 1

        # Spawn rocks
        rock_positions = [
            (2, 2), (self.cols - 3, 2), (2, self.rows - 3), (self.cols - 3, self.rows - 3),
            (mid_x + 3, mid_y - 3), (mid_x - 3, mid_y + 3)
        ]
        for rx, ry in rock_positions:
            if 0 < rx < self.cols - 1 and 0 < ry < self.rows - 1:
                self.rocks.append(Rock(rx, ry))

    def is_tunnel(self, x: int, y: int) -> bool:
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        return self.cells[x][y] == 1

    def is_soil(self, x: int, y: int) -> bool:
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        return self.cells[x][y] == 0

    def dig(self, x: int, y: int) -> bool:
        if not (0 <= x < self.cols and 0 <= y < self.rows):
            return False
        if self.cells[x][y] == 0:
            self.cells[x][y] = 1
            return True
        return False

    def get_rock_at(self, x: int, y: int) -> Optional[Rock]:
        for rock in self.rocks:
            if rock.alive and rock.pos.x == x and rock.pos.y == y:
                return rock
        return None

    def is_occupied_by_rock(self, x: int, y: int) -> bool:
        return self.get_rock_at(x, y) is not None
