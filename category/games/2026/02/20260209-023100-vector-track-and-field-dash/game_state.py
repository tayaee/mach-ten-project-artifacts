"""
Game state management for Track and Field Dash.
"""

from enum import Enum
from dataclasses import dataclass
import time


class GameState(Enum):
    MENU = "menu"
    RUNNING = "running"
    FINISHED = "finished"
    STUMBLE = "stumble"


@dataclass
class State:
    """Core game state."""
    distance: float = 0.0
    velocity: float = 0.0
    stamina: float = 100.0
    max_stamina: float = 100.0
    last_key: str = None
    time_elapsed: float = 0.0
    finish_time: float = None
    state: GameState = GameState.MENU
    stumble_start: float = 0.0
    stumble_duration: float = 1.5

    TARGET_DISTANCE = 100.0
    MAX_VELOCITY = 12.0
    VELOCITY_INCREMENT = 0.8
    FRICTION = 0.02
    STUMBLE_VELOCITY_PENALTY = 3.0
    STAMINA_DRAIN_RATE = 15.0
    STAMINA_RECOVERY_RATE = 8.0
    STAMINA_THRESHOLD = 0.9

    def is_stumbling(self) -> bool:
        return (self.state == GameState.STUMBLE and
                time.time() - self.stumble_start < self.stumble_duration)

    def trigger_stumble(self):
        self.state = GameState.STUMBLE
        self.stumble_start = time.time()
        self.velocity = max(0, self.velocity - self.STUMBLE_VELOCITY_PENALTY)

    def reset(self):
        self.distance = 0.0
        self.velocity = 0.0
        self.stamina = self.max_stamina
        self.last_key = None
        self.time_elapsed = 0.0
        self.finish_time = None
        self.state = GameState.MENU

    def calculate_score(self) -> int:
        if self.finish_time is None or self.finish_time <= 0:
            return 0
        return int(10000 / self.finish_time)

    def get_max_speed_cap(self) -> float:
        if self.stamina <= 0:
            return self.MAX_VELOCITY * 0.5
        return self.MAX_VELOCITY

    def is_sprinting(self) -> bool:
        return self.velocity >= self.MAX_VELOCITY * self.STAMINA_THRESHOLD
