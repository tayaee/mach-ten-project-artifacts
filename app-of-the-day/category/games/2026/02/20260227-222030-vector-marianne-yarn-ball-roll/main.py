"""
Vector Marianne Yarn Ball Roll - Physics-based rolling platformer.
Guide a rolling yarn ball through obstacles to reach the kitten.
AI-friendly with clear state space for reinforcement learning.
"""

import os
import pygame
import sys
import math
from enum import Enum
from typing import List, Tuple, Optional, Dict, Set


class ActionType(Enum):
    LEFT = 0
    RIGHT = 1
    JUMP = 2
    NONE = 3


class ObstacleType(Enum):
    PLATFORM = 0
    ICE = 1
    NEEDLE = 2
    FAN = 3
    BUTTON = 4


class YarnBall:
    """The player's yarn ball with physics simulation."""

    def __init__(self, x: float, y: float, radius: int = 20):
        self.pos = [x, y]  # Position
        self.vel = [0.0, 0.0]  # Velocity
        self.radius = radius
        self.mass = 1.0
        self.on_ground = False
        self.facing_right = True

        # Physics constants
        self.gravity = 0.5
        self.acceleration = 0.4
        self.friction = 0.85
        self.ice_friction = 0.98
        self.jump_force = -12.0
        self.max_speed = 8.0
        self.air_control = 0.3

    def update(self, action: ActionType, on_ice: bool = False, fan_force: float = 0.0):
        """Update ball physics."""
        # Apply fan force (pushes ball horizontally)
        if fan_force != 0:
            self.vel[0] += fan_force

        # Apply input force
        if action == ActionType.LEFT:
            force = self.acceleration * (self.air_control if not self.on_ground else 1.0)
            self.vel[0] -= force
            self.facing_right = False
        elif action == ActionType.RIGHT:
            force = self.acceleration * (self.air_control if not self.on_ground else 1.0)
            self.vel[0] += force
            self.facing_right = True
        elif action == ActionType.JUMP and self.on_ground:
            self.vel[1] = self.jump_force
            self.on_ground = False

        # Apply gravity
        self.vel[1] += self.gravity

        # Apply friction
        current_friction = self.ice_friction if on_ice else self.friction
        self.vel[0] *= current_friction

        # Cap horizontal speed
        if abs(self.vel[0]) > self.max_speed:
            self.vel[0] = math.copysign(self.max_speed, self.vel[0])

        # Apply stop threshold
        if abs(self.vel[0]) < 0.05:
            self.vel[0] = 0

        # Update position
        self.pos[0] += self.vel[0]
        self.pos[1] += self.vel[1]

    def reset(self, x: float, y: float):
        """Reset ball to starting position."""
        self.pos = [x, y]
        self.vel = [0.0, 0.0]
        self.on_ground = False


class Platform:
    """Static platform for the ball to roll on."""

    def __init__(self, x: int, y: int, width: int, height: int, platform_type: ObstacleType = ObstacleType.PLATFORM):
        self.rect = pygame.Rect(x, y, width, height)
        self.type = platform_type
        self.fan_active = False
        self.fan_direction = 1  # 1 for right, -1 for left

    def draw(self, surface):
        """Draw the platform."""
        colors = {
            ObstacleType.PLATFORM: (100, 100, 120),
            ObstacleType.ICE: (150, 200, 255),
            ObstacleType.NEEDLE: (255, 50, 50),
            ObstacleType.FAN: (80, 150, 200),
            ObstacleType.BUTTON: (255, 200, 50)
        }
        color = colors.get(self.type, (100, 100, 120))
        pygame.draw.rect(surface, color, self.rect)

        # Draw fan blades or needle details
        if self.type == ObstacleType.NEEDLE:
            # Draw triangular needles
            for i in range(0, self.rect.width, 10):
                tip = (self.rect.x + i + 5, self.rect.y)
                base_left = (self.rect.x + i, self.rect.y + self.rect.height)
                base_right = (self.rect.x + i + 10, self.rect.y + self.rect.height)
                pygame.draw.polygon(surface, (200, 0, 0), [tip, base_left, base_right])
        elif self.type == ObstacleType.FAN:
            # Draw fan direction indicator
            center_x = self.rect.centerx
            center_y = self.rect.centery
            direction = ">>>" if self.fan_direction == 1 else "<<<"
            pygame.draw.circle(surface, (255, 255, 255), (center_x, center_y), 15, 2)


class Button:
    """Collectible button for bonus points."""

    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x - 8, y - 8, 16, 16)
        self.collected = False

    def draw(self, surface):
        """Draw the button."""
        if not self.collected:
            pygame.draw.circle(surface, (255, 200, 50), self.rect.center, 8)
            pygame.draw.circle(surface, (200, 150, 0), self.rect.center, 8, 2)
            # Draw button holes
            pygame.draw.circle(surface, (100, 100, 100), (self.rect.centerx - 3, self.rect.centery), 1)
            pygame.draw.circle(surface, (100, 100, 100), (self.rect.centerx + 3, self.rect.centery), 1)


class Kitten:
    """The goal target at the end of the level."""

    def __init__(self, x: int, y: int):
        self.pos = [x, y]
        self.radius = 25

    def draw(self, surface):
        """Draw the kitten (cat face)."""
        # Face
        pygame.draw.circle(surface, (255, 200, 150), self.pos, self.radius)
        pygame.draw.circle(surface, (200, 150, 100), self.pos, self.radius, 2)

        # Ears
        ear_offset = 15
        pygame.draw.polygon(surface, (255, 200, 150), [
            (self.pos[0] - ear_offset, self.pos[1] - 10),
            (self.pos[0] - ear_offset + 10, self.pos[1] - 30),
            (self.pos[0] - 5, self.pos[1] - 15)
        ])
        pygame.draw.polygon(surface, (255, 200, 150), [
            (self.pos[0] + ear_offset, self.pos[1] - 10),
            (self.pos[0] + ear_offset - 10, self.pos[1] - 30),
            (self.pos[0] + 5, self.pos[1] - 15)
        ])

        # Eyes
        eye_offset = 8
        eye_y = -3
        pygame.draw.circle(surface, (50, 50, 50), (self.pos[0] - eye_offset, self.pos[1] + eye_y), 4)
        pygame.draw.circle(surface, (50, 50, 50), (self.pos[0] + eye_offset, self.pos[1] + eye_y), 4)

        # Nose
        pygame.draw.circle(surface, (255, 150, 150), self.pos, 3)

        # Mouth (simple smile)
        pygame.draw.arc(surface, (50, 50, 50),
                       (self.pos[0] - 8, self.pos[1] + 2, 16, 10),
                       math.pi, 2 * math.pi, 2)

        # Whiskers
        for i in range(-1, 2):
            y_offset = i * 4
            pygame.draw.line(surface, (150, 150, 150),
                             (self.pos[0] - 18, self.pos[1] + y_offset),
                             (self.pos[0] - 8, self.pos[1] + y_offset - 2), 1)
            pygame.draw.line(surface, (150, 150, 150),
                             (self.pos[0] + 18, self.pos[1] + y_offset),
                             (self.pos[0] + 8, self.pos[1] + y_offset - 2), 1)


class YarnBallRollGame:
    """
    Physics-based rolling platformer game.

    Control a yarn ball with momentum and inertia through obstacle courses.
    Reach the kitten at the end of the level while avoiding falling off
    and hitting dangerous obstacles.

    Features:
    - Realistic momentum and inertia
    - Ice patches with reduced friction
    - Moving fans that push the ball
    - Sharp needles that are dangerous
    - Collectible buttons for bonus points

    State representation:
    - Player (x, y, vx, vy)
    - Kitten (x, y)
    - Obstacles (list of x, y, type)
    - Platform bounds

    Actions: 4 discrete (left, right, jump, none)

    Rewards:
    - +100: Reach the kitten (win)
    - +10: Collect a button
    - -50: Fall off the stage
    - -100: Hit a needle
    - -0.1: Each step (encourage speed)
    """

    WINDOW_WIDTH = 800
    WINDOW_HEIGHT = 600
    FPS = 60

    # Colors
    COLOR_BG = (20, 30, 50)
    COLOR_TEXT = (220, 220, 220)
    COLOR_HUD_BG = (30, 40, 60)
    COLOR_YARN = (200, 150, 220)
    COLOR_YARN_STITCH = (150, 100, 170)

    def __init__(self, render: bool = True):
        """Initialize the game."""
        self.render = render
        if self.render:
            pygame.init()
            pygame.display.set_caption("Yarn Ball Roll - Reach the Kitten!")
            self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
            self.clock = pygame.time.Clock()
            self.font = pygame.font.Font(None, 36)
            self.large_font = pygame.font.Font(None, 64)
        else:
            os.environ['SDL_VIDEODRIVER'] = 'dummy'
            pygame.init()
            pygame.display.set_mode((1, 1))

        self.ball = YarnBall(50, 450)
        self.reset()

    def reset(self) -> None:
        """Reset the game to initial state."""
        self.ball.reset(50, 450)
        self._build_level()

        # Game state
        self.score = 1000  # Starting score
        self.time_elapsed = 0
        self.fallen = False
        self.hit_needle = False
        self.game_over = False
        self.victory = False
        self.steps = 0

    def _build_level(self) -> None:
        """Build the level with platforms and obstacles."""
        self.platforms = []
        self.buttons = []

        # Starting platform
        self.platforms.append(Platform(0, 500, 200, 100))

        # Second platform with a gap (need to jump)
        self.platforms.append(Platform(220, 480, 120, 120))

        # Ice patch (slippery)
        self.platforms.append(Platform(350, 460, 100, 140, ObstacleType.ICE))

        # Gap with platform below (falling path)
        self.platforms.append(Platform(100, 350, 80, 20))
        self.platforms.append(Platform(250, 350, 80, 20))

        # Needle obstacle on platform
        self.platforms.append(Platform(400, 350, 150, 20))
        self.platforms.append(Platform(480, 330, 40, 20, ObstacleType.NEEDLE))  # Needle above

        # Fan pushing right
        fan = Platform(580, 300, 80, 40, ObstacleType.FAN)
        fan.fan_direction = 1
        self.platforms.append(fan)

        # Upper platforms
        self.platforms.append(Platform(100, 250, 100, 20))
        self.platforms.append(Platform(250, 220, 80, 20))

        # Ice ramp
        self.platforms.append(Platform(380, 200, 120, 20, ObstacleType.ICE))

        # Final section with narrow bridges
        self.platforms.append(Platform(550, 180, 50, 20))
        self.platforms.append(Platform(630, 180, 50, 20))
        self.platforms.append(Platform(710, 180, 90, 20))

        # Collectible buttons
        self.buttons.append(Button(280, 430))
        self.buttons.append(Button(130, 320))
        self.buttons.append(Button(440, 310))
        self.buttons.append(Button(290, 190))
        self.buttons.append(Button(575, 150))
        self.buttons.append(Button(655, 150))

        # Kitten (goal)
        self.kitten = Kitten(750, 155)

    def _get_fan_force(self) -> float:
        """Calculate fan force on the ball."""
        force = 0.0
        ball_rect = pygame.Rect(
            self.ball.pos[0] - self.ball.radius,
            self.ball.pos[1] - self.ball.radius,
            self.ball.radius * 2,
            self.ball.radius * 2
        )

        for platform in self.platforms:
            if platform.type == ObstacleType.FAN:
                # Check if ball is near the fan (within 50 pixels)
                if ball_rect.colliderect(
                    pygame.Rect(platform.rect.x - 50, platform.rect.y - 20,
                               platform.rect.width + 100, platform.rect.height + 40)
                ):
                    force = 0.3 * platform.fan_direction
        return force

    def _check_platform_collision(self) -> bool:
        """Check and resolve platform collisions."""
        ball_rect = pygame.Rect(
            self.ball.pos[0] - self.ball.radius,
            self.ball.pos[1] - self.ball.radius,
            self.ball.radius * 2,
            self.ball.radius * 2
        )

        self.ball.on_ground = False
        on_ice = False

        for platform in self.platforms:
            if platform.rect.colliderect(ball_rect):
                # Check if ball is hitting a needle
                if platform.type == ObstacleType.NEEDLE:
                    self.hit_needle = True
                    return False

                # Determine collision side
                overlap_left = (self.ball.pos[0] + self.ball.radius) - platform.rect.left
                overlap_right = platform.rect.right - (self.ball.pos[0] - self.ball.radius)
                overlap_top = (self.ball.pos[1] + self.ball.radius) - platform.rect.top
                overlap_bottom = platform.rect.bottom - (self.ball.pos[1] - self.ball.radius)

                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)

                if min_overlap == overlap_top and self.ball.vel[1] >= 0:
                    # Landing on top of platform
                    self.ball.pos[1] = platform.rect.top - self.ball.radius
                    self.ball.vel[1] = 0
                    self.ball.on_ground = True
                    if platform.type == ObstacleType.ICE:
                        on_ice = True
                elif min_overlap == overlap_bottom:
                    # Hitting bottom of platform
                    self.ball.pos[1] = platform.rect.bottom + self.ball.radius
                    self.ball.vel[1] = 0
                elif min_overlap == overlap_left and self.ball.vel[0] > 0:
                    # Hitting left side
                    self.ball.pos[0] = platform.rect.left - self.ball.radius
                    self.ball.vel[0] = -self.ball.vel[0] * 0.3
                elif min_overlap == overlap_right and self.ball.vel[0] < 0:
                    # Hitting right side
                    self.ball.pos[0] = platform.rect.right + self.ball.radius
                    self.ball.vel[0] = -self.ball.vel[0] * 0.3

        return on_ice

    def _check_button_collection(self) -> int:
        """Check if ball collects any buttons."""
        collected = 0
        for button in self.buttons:
            if not button.collected:
                dist = ((self.ball.pos[0] - button.rect.centerx) ** 2 +
                       (self.ball.pos[1] - button.rect.centery) ** 2) ** 0.5
                if dist < self.ball.radius + 8:
                    button.collected = True
                    collected += 1
        return collected

    def _check_kitten_reached(self) -> bool:
        """Check if ball reached the kitten."""
        dist = ((self.ball.pos[0] - self.kitten.pos[0]) ** 2 +
               (self.ball.pos[1] - self.kitten.pos[1]) ** 2) ** 0.5
        return dist < self.ball.radius + self.kitten.radius

    def step(self, action: ActionType) -> Tuple[float, bool, int]:
        """
        Execute one game step.

        Args:
            action: Action to take

        Returns:
            Tuple of (reward, done, score)
        """
        if self.game_over:
            return 0, True, self.score

        reward = 0
        self.steps += 1
        self.time_elapsed += 1

        # Score decay over time
        if self.steps % 60 == 0:  # Every second
            self.score = max(0, self.score - 1)

        # Get fan force
        fan_force = self._get_fan_force()

        # Update ball
        self.ball.update(action, fan_force=fan_force)

        # Check platform collisions
        on_ice = self._check_platform_collision()

        # Re-apply ice friction if needed
        if on_ice:
            self.ball.vel[0] *= self.ball.ice_friction

        # Check button collection
        buttons_collected = self._check_button_collection()
        if buttons_collected > 0:
            self.score += buttons_collected * 10
            reward += buttons_collected * 10

        # Check if fell off the stage
        if self.ball.pos[1] > self.WINDOW_HEIGHT + 50:
            self.fallen = True
            self.game_over = True
            self.score = max(0, self.score - 50)
            reward -= 50
            return reward, True, self.score

        # Check if hit a needle
        if self.hit_needle:
            self.game_over = True
            self.score = max(0, self.score - 100)
            reward -= 100
            return reward, True, self.score

        # Check if reached the kitten
        if self._check_kitten_reached():
            self.victory = True
            self.game_over = True
            self.score += 100
            reward += 100
            return reward, True, self.score

        # Small step penalty
        reward -= 0.1

        return reward, False, self.score

    def get_state(self) -> Dict:
        """Get current game state."""
        return {
            'player': {
                'x': self.ball.pos[0],
                'y': self.ball.pos[1],
                'vx': self.ball.vel[0],
                'vy': self.ball.vel[1],
                'on_ground': self.ball.on_ground
            },
            'kitten': {
                'x': self.kitten.pos[0],
                'y': self.kitten.pos[1]
            },
            'buttons': [
                {'x': b.rect.centerx, 'y': b.rect.centery, 'collected': b.collected}
                for b in self.buttons
            ],
            'platforms': [
                {'x': p.rect.x, 'y': p.rect.y, 'width': p.rect.width,
                 'height': p.rect.height, 'type': p.type.value}
                for p in self.platforms
            ],
            'score': self.score,
            'time_elapsed': self.time_elapsed,
            'game_over': self.game_over,
            'victory': self.victory,
            'steps': self.steps
        }

    def draw(self) -> None:
        """Render the game state."""
        if not self.render:
            return

        self.screen.fill(self.COLOR_BG)

        # Draw platforms
        for platform in self.platforms:
            platform.draw(self.screen)

        # Draw buttons
        for button in self.buttons:
            button.draw(self.screen)

        # Draw kitten
        self.kitten.draw(self.screen)

        # Draw yarn ball
        ball_x = int(self.ball.pos[0])
        ball_y = int(self.ball.pos[1])

        # Ball body (yarn texture)
        pygame.draw.circle(self.screen, self.COLOR_YARN, (ball_x, ball_y), self.ball.radius)

        # Yarn stitches (winding pattern)
        stitch_count = 8
        for i in range(stitch_count):
            angle = (i / stitch_count) * 2 * math.pi + (self.steps * 0.05)
            start_x = ball_x + math.cos(angle) * (self.ball.radius - 8)
            start_y = ball_y + math.sin(angle) * (self.ball.radius - 8)
            end_angle = angle + math.pi / stitch_count
            end_x = ball_x + math.cos(end_angle) * (self.ball.radius - 8)
            end_y = ball_y + math.sin(end_angle) * (self.ball.radius - 8)
            pygame.draw.line(self.screen, self.COLOR_YARN_STITCH, (start_x, start_y), (end_x, end_y), 2)

        # Ball outline
        pygame.draw.circle(self.screen, self.COLOR_YARN_STITCH, (ball_x, ball_y), self.ball.radius, 2)

        # Draw HUD
        hud_height = 50
        pygame.draw.rect(self.screen, self.COLOR_HUD_BG, (0, self.WINDOW_HEIGHT - hud_height,
                                                           self.WINDOW_WIDTH, hud_height))

        # Score
        score_text = self.font.render(f"Score: {self.score}", True, self.COLOR_TEXT)
        self.screen.blit(score_text, (20, self.WINDOW_HEIGHT - 40))

        # Time
        time_text = self.font.render(f"Time: {self.time_elapsed // 60}s", True, self.COLOR_TEXT)
        self.screen.blit(time_text, (200, self.WINDOW_HEIGHT - 40))

        # Instructions
        hint_text = self.font.render("Arrows: Move/Jump  |  R: Restart  |  ESC: Quit", True, (150, 150, 170))
        hint_rect = hint_text.get_rect(right=self.WINDOW_WIDTH - 20, y=self.WINDOW_HEIGHT - 40)
        self.screen.blit(hint_text, hint_rect)

        # Game over / Victory overlay
        if self.game_over:
            overlay = pygame.Surface((self.WINDOW_WIDTH, self.WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            if self.victory:
                msg = "YOU FOUND THE KITTEN!"
                color = (100, 255, 100)
            elif self.fallen:
                msg = "YOU FELL!"
                color = (255, 200, 100)
            else:
                msg = "OUCH! HIT A NEEDLE!"
                color = (255, 100, 100)

            text = self.large_font.render(msg, True, color)
            text_rect = text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 - 30))
            self.screen.blit(text, text_rect)

            final_score = self.font.render(f"Final Score: {self.score}", True, self.COLOR_TEXT)
            score_rect = final_score.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 20))
            self.screen.blit(final_score, score_rect)

            restart_text = self.font.render("Press R to restart, ESC to quit", True, (200, 200, 200))
            restart_rect = restart_text.get_rect(center=(self.WINDOW_WIDTH // 2, self.WINDOW_HEIGHT // 2 + 60))
            self.screen.blit(restart_text, restart_rect)

        pygame.display.flip()

    def handle_input(self) -> ActionType:
        """Handle keyboard input for human control."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                elif event.key == pygame.K_r and self.game_over:
                    self.reset()

        # Handle continuous input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            return ActionType.LEFT
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            return ActionType.RIGHT
        elif keys[pygame.K_UP] or keys[pygame.K_w]:
            return ActionType.JUMP
        else:
            return ActionType.NONE

    def run(self) -> None:
        """Main game loop for human play."""
        while True:
            action = self.handle_input()
            self.step(action)
            self.draw()
            self.clock.tick(self.FPS)


def main():
    """Entry point for running the game."""
    game = YarnBallRollGame(render=True)
    game.run()


if __name__ == "__main__":
    main()
