"""
Athlete physics and input handling.
"""

from pygame import K_LEFT, K_RIGHT
from game_state import State, GameState


class Athlete:
    """Handles athlete movement and input processing."""

    def __init__(self, state: State):
        self.state = state

    def handle_input(self, key):
        """Process keyboard input for acceleration."""
        if self.state.state not in (GameState.RUNNING, GameState.STUMBLE):
            return

        if self.state.is_stumbling():
            return

        current_key = "LEFT" if key == K_LEFT else "RIGHT"
        other_key = "RIGHT" if key == K_LEFT else "LEFT"

        if self.state.last_key == current_key:
            self.state.trigger_stumble()
            return

        if key in (K_LEFT, K_RIGHT):
            self.state.last_key = current_key
            self.accelerate()

    def accelerate(self):
        """Apply acceleration based on current speed cap."""
        max_cap = self.state.get_max_speed_cap()
        self.state.velocity = min(
            self.state.velocity + self.state.VELOCITY_INCREMENT,
            max_cap
        )

    def update(self, dt: float):
        """Update physics for one frame."""
        if self.state.state != GameState.RUNNING:
            return

        # Handle stumble recovery
        if self.state.is_stumbling():
            return

        # Apply friction
        self.state.velocity = max(0, self.state.velocity * (1 - self.state.FRICTION))

        # Update stamina
        if self.state.is_sprinting():
            self.state.stamina = max(0, self.state.stamina - self.state.STAMINA_DRAIN_RATE * dt)
        else:
            self.state.stamina = min(
                self.state.max_stamina,
                self.state.stamina + self.state.STAMINA_RECOVERY_RATE * dt
            )

        # Move athlete
        pixels_per_meter = 7.5
        self.state.distance += self.state.velocity * dt
        self.state.time_elapsed += dt

        # Check finish
        if self.state.distance >= self.state.TARGET_DISTANCE:
            self.state.state = GameState.FINISHED
            self.state.finish_time = self.state.time_elapsed
            self.state.distance = self.state.TARGET_DISTANCE
