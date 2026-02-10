"""Entity classes for Vector Super Mario Bros Water Swim Avoid."""

from dataclasses import dataclass
from typing import List, Tuple
import config


@dataclass
class Vec2:
    x: float
    y: float


class Player:
    def __init__(self, x: float, y: float):
        self.pos = Vec2(x, y)
        self.vel = Vec2(0.0, 0.0)
        self.width = config.PLAYER_WIDTH
        self.height = config.PLAYER_HEIGHT
        self.facing_right = True
        self.alive = True
        self.finished = False
        self.swim_frame = 0.0
        self.bubbles: List[List] = []
        self.max_x = x

    def update(self, dt: float, inputs: dict, obstacles: List):
        if not self.alive or self.finished:
            return

        # Horizontal movement
        if inputs['left']:
            self.vel.x = -config.HORIZONTAL_SPEED
            self.facing_right = False
        elif inputs['right']:
            self.vel.x = config.HORIZONTAL_SPEED
            self.facing_right = True
        else:
            self.vel.x *= config.DRAG

        # Swimming upward (buoyancy impulse)
        if inputs['swim']:
            self.vel.y += config.BUOYANCY_IMPULSE
            self.swim_frame += dt * 15
            # Add bubbles
            if len(self.bubbles) < 5 and int(self.swim_frame) % 3 == 0:
                self.bubbles.append([self.pos.x + 12, self.pos.y + 28, 0])
        else:
            self.swim_frame += dt * 5

        # Apply gravity
        self.vel.y += config.GRAVITY

        # Clamp fall speed
        self.vel.y = max(-config.MAX_FALL_SPEED * 2, min(config.MAX_FALL_SPEED, self.vel.y))

        # Update position
        self.pos.x += self.vel.x
        self.pos.y += self.vel.y

        # Track max progress
        if self.pos.x > self.max_x:
            self.max_x = self.pos.x

        # Update bubbles
        for bubble in self.bubbles:
            bubble[1] -= 40 * dt
            bubble[2] += dt

        # Remove old bubbles
        self.bubbles = [b for b in self.bubbles if b[2] < 1.0]

        # Screen bounds (vertical only - horizontal scrolling)
        self.pos.y = max(20, min(self.pos.y, config.SCREEN_HEIGHT - self.height - 20))
        self.pos.x = max(0, self.pos.x)

    def get_rect(self) -> Tuple[float, float, float, float]:
        return (self.pos.x, self.pos.y, self.width, self.height)


class Blooper:
    def __init__(self, x: float, y: float):
        self.pos = Vec2(x, y)
        self.start_y = y
        self.vel = Vec2(0.0, -config.BLOOPER_SPEED)
        self.width = config.BLOOPER_WIDTH
        self.height = config.BLOOPER_HEIGHT
        self.phase = 0.0
        self.alive = True

    def update(self, dt: float, player_x: float):
        if not self.alive:
            return

        self.phase += dt * 2

        # Wavy vertical movement pattern
        self.pos.y += self.vel.y
        if abs(self.pos.y - self.start_y) > 80:
            self.vel.y *= -1

        # Activate when player is near
        if abs(player_x - self.pos.x) < 200:
            # Slight horizontal drift toward player
            if player_x > self.pos.x:
                self.pos.x += config.BLOOPER_SPEED * 0.3 * dt * 60
            else:
                self.pos.x -= config.BLOOPER_SPEED * 0.3 * dt * 60

    def get_rect(self) -> Tuple[float, float, float, float]:
        return (self.pos.x, self.pos.y, self.width, self.height)


class CheepCheep:
    def __init__(self, x: float, y: float, direction: int):
        self.pos = Vec2(x, y)
        self.vel = Vec2(config.CHEEP_SPEED * direction, 0.0)
        self.width = config.CHEEP_WIDTH
        self.height = config.CHEEP_HEIGHT
        self.alive = True
        self.start_x = x
        self.patrol_range = 150

    def update(self, dt: float):
        if not self.alive:
            return

        self.pos.x += self.vel.x

        # Gentle wave motion
        self.pos.y += 0.3 * dt * 60

        # Patrol within range
        if abs(self.pos.x - self.start_x) > self.patrol_range:
            self.vel.x *= -1

    def get_rect(self) -> Tuple[float, float, float, float]:
        return (self.pos.x, self.pos.y, self.width, self.height)


class Obstacle:
    def __init__(self, x: float, y: float, width: float, height: float, obs_type: str):
        self.pos = Vec2(x, y)
        self.width = width
        self.height = height
        self.type = obs_type

    def get_rect(self) -> Tuple[float, float, float, float]:
        return (self.pos.x, self.pos.y, self.width, self.height)
