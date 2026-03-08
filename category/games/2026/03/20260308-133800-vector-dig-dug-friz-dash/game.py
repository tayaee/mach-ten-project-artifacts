"""Main game logic for Dig Dug Friz Dash."""

import pygame
import sys
from typing import Optional, List, Dict, Any

from config import *
from entities import *


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Dig Dug Friz Dash")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)

        self.reset()

    def reset(self):
        """Reset the game to initial state."""
        self.grid = Grid(GRID_COLS, GRID_ROWS)
        self.player = Player(GRID_COLS // 2, GRID_ROWS // 2)
        self.enemies: List[Enemy] = []
        self._spawn_enemies()

        self.score = 0
        self.level = 1
        self.game_state = "playing"  # playing, game_over, level_clear
        self.state_timer = 0

    def _spawn_enemies(self):
        """Spawn enemies in tunnels."""
        mid_y = GRID_ROWS // 2
        mid_x = GRID_COLS // 2

        # Spawn Pookas
        pooka_positions = [
            (mid_x - 4, mid_y - 2), (mid_x + 4, mid_y + 2),
            (mid_x - 2, 2), (mid_x + 2, GRID_ROWS - 3)
        ]
        for px, py in pooka_positions:
            if 0 <= px < GRID_COLS and 0 <= py < GRID_ROWS:
                self.enemies.append(Pooka(px, py))

        # Spawn Fygars
        fygar_positions = [
            (mid_x, 2), (mid_x - 3, mid_y + 2)
        ]
        for fx, fy in fygar_positions:
            if 0 <= fx < GRID_COLS and 0 <= fy < GRID_ROWS:
                self.enemies.append(Fygar(fx, fy))

    def get_observation(self) -> Dict[str, Any]:
        """Get current game state for AI agents."""
        return {
            "grid": [[self.grid.cells[x][y] for y in range(GRID_ROWS)] for x in range(GRID_COLS)],
            "player_pos": (self.player.pos.x, self.player.pos.y),
            "player_pump_active": self.player.pump_active,
            "enemies": [
                {
                    "type": e.entity_type.value,
                    "pos": (e.pos.x, e.pos.y),
                    "inflation": e.inflation,
                    "alive": e.alive
                }
                for e in self.enemies
            ],
            "rocks": [
                {
                    "pos": (r.pos.x, r.pos.y),
                    "state": r.state,
                    "alive": r.alive
                }
                for r in self.grid.rocks
            ],
            "score": self.score,
            "game_state": self.game_state
        }

    def step_ai(self, action: int) -> tuple:
        """Execute AI action and return (observation, reward, done)."""
        prev_score = self.score
        prev_alive = sum(1 for e in self.enemies if e.alive)

        # Actions: 0=up, 1=down, 2=left, 3=right, 4=pump, 5=none
        if action == 0:
            self.move_player(0, -1)
            self.use_pump("UP")
        elif action == 1:
            self.move_player(0, 1)
            self.use_pump("DOWN")
        elif action == 2:
            self.move_player(-1, 0)
            self.use_pump("LEFT")
        elif action == 3:
            self.move_player(1, 0)
            self.use_pump("RIGHT")

        self.update()

        reward = (self.score - prev_score) / 100.0
        alive_now = sum(1 for e in self.enemies if e.alive)
        reward += (prev_alive - alive_now)

        done = self.game_state in ["game_over", "level_clear"]

        return self.get_observation(), reward, done

    def move_player(self, dx: int, dy: int) -> bool:
        """Move player in direction, returns True if moved."""
        if self.game_state != "playing":
            return False

        if not self.player.can_move():
            return False

        new_x = self.player.pos.x + dx
        new_y = self.player.pos.y + dy

        # Check bounds
        if not (0 <= new_x < GRID_COLS and 0 <= new_y < GRID_ROWS):
            return False

        # Check rock collision (can't move into stable rock)
        rock = self.grid.get_rock_at(new_x, new_y)
        if rock and rock.state == "stable":
            return False

        # Dig soil
        if self.grid.dig(new_x, new_y):
            self.score += SCORE_DIG_SOIL

        self.player.pos.x = new_x
        self.player.pos.y = new_y

        # Update facing direction
        if dx > 0:
            self.player.facing = "right"
        elif dx < 0:
            self.player.facing = "left"
        elif dy > 0:
            self.player.facing = "down"
        elif dy < 0:
            self.player.facing = "up"

        return True

    def use_pump(self, direction: str):
        """Use pump in direction."""
        if self.game_state != "playing":
            return

        self.player.start_pump(direction)

        # Calculate pump hit position
        dx, dy = 0, 0
        if direction == "UP":
            dy = -1
        elif direction == "DOWN":
            dy = 1
        elif direction == "LEFT":
            dx = -1
        elif direction == "RIGHT":
            dx = 1

        # Check for enemies in pump path
        for i in range(1, PUMP_RANGE + 1):
            check_x = self.player.pos.x + dx * i
            check_y = self.player.pos.y + dy * i

            for enemy in self.enemies:
                if enemy.alive and enemy.pos.x == check_x and enemy.pos.y == check_y:
                    enemy.inflate()
                    if enemy.inflation >= INFLATION_REQUIRED:
                        enemy.alive = False
                        self.score += SCORE_PUMP_KILL
                    self.player.pump_hit_pos = Position(check_x, check_y)
                    return

    def update_rocks(self):
        """Update rock physics."""
        for rock in self.grid.rocks:
            if not rock.alive:
                continue

            rock.update()

            # Check if rock should start wobbling
            if rock.state == "stable":
                below_y = rock.pos.y + 1
                if below_y < GRID_ROWS:
                    if self.grid.is_tunnel(rock.pos.x, below_y):
                        # Check if player is not directly under
                        if not (self.player.pos.x == rock.pos.x and
                                self.player.pos.y == below_y):
                            rock.start_wobble()

            # Check if rock should fall
            elif rock.state == "wobbling":
                below_y = rock.pos.y + 1
                if below_y >= GRID_ROWS or self.grid.is_soil(rock.pos.x, below_y):
                    rock.state = "stable"

            # Update falling
            elif rock.state == "falling":
                if rock.fall_progress >= ROCK_FALL_SPEED:
                    rock.fall_progress = 0
                    new_y = rock.pos.y + 1

                    # Check for entities below
                    if self.player.pos.x == rock.pos.x and self.player.pos.y == new_y:
                        self.game_state = "game_over"
                        rock.state = "stable"
                        continue

                    # Check for enemy crushing
                    for enemy in self.enemies:
                        if (enemy.alive and enemy.pos.x == rock.pos.x and
                                enemy.pos.y == new_y and enemy not in rock.enemies_crushed):
                            enemy.alive = False
                            rock.enemies_crushed.append(enemy)

                    # Move rock or stop
                    if new_y >= GRID_ROWS or self.grid.is_soil(rock.pos.x, new_y):
                        rock.state = "stable"
                        # Score for crushed enemies
                        if len(rock.enemies_crushed) == 1:
                            self.score += SCORE_ROCK_KILL
                        elif len(rock.enemies_crushed) >= 2:
                            self.score += SCORE_ROCK_KILL * 2
                    else:
                        rock.pos.y = new_y

    def update_enemies(self):
        """Update enemy AI."""
        for enemy in self.enemies:
            if not enemy.alive:
                continue

            enemy.update()

            # Inflated enemies can't move
            if enemy.inflation > 0:
                continue

            if not enemy.can_move():
                continue

            # Calculate distance to player
            distance = enemy.pos.distance_to(self.player.pos)

            # Chase AI
            dx = 0
            dy = 0

            if distance < CHASE_RADIUS:
                # Chase player
                if enemy.pos.x < self.player.pos.x:
                    dx = 1
                elif enemy.pos.x > self.player.pos.x:
                    dx = -1

                if enemy.pos.y < self.player.pos.y:
                    dy = 1
                elif enemy.pos.y > self.player.pos.y:
                    dy = -1

                # Prefer axis with larger distance
                if abs(self.player.pos.x - enemy.pos.x) > abs(self.player.pos.y - enemy.pos.y):
                    dy = 0
                else:
                    dx = 0
            else:
                # Random movement
                if random.random() < 0.02:
                    direction = random.choice([(0, 1), (0, -1), (1, 0), (-1, 0)])
                    dx, dy = direction

            new_x = enemy.pos.x + dx
            new_y = enemy.pos.y + dy

            # Check if can move
            can_move = False

            # Can move in tunnels
            if self.grid.is_tunnel(new_x, new_y):
                can_move = True
            # Pookas can move through soil in ghost mode
            elif isinstance(enemy, Pooka) and enemy.ghost_mode:
                can_move = True
                # Randomly exit ghost mode
                if random.random() < 0.02:
                    enemy.ghost_mode = False

            # Randomly enter ghost mode if stuck
            if not can_move and isinstance(enemy, Pooka) and not enemy.ghost_mode:
                if random.random() < 0.01:
                    enemy.ghost_mode = True
                    can_move = True

            # Check for rock collision
            if can_move and self.grid.get_rock_at(new_x, new_y):
                can_move = False

            if can_move:
                enemy.pos.x = new_x
                enemy.pos.y = new_y
                enemy.reset_move_counter()

                # Update facing direction for Fygar
                if isinstance(enemy, Fygar):
                    enemy.facing_right = dx > 0 or (dx == 0 and enemy.facing_right)

            # Fygar fire breath
            if isinstance(enemy, Fygar) and enemy.can_breathe_fire():
                if random.random() < 0.01:  # Low chance per frame when ready
                    enemy.breathe_fire()
                    direction = 1 if enemy.facing_right else -1
                    for i in range(1, FYGAR_BREATH_RANGE + 1):
                        breath_x = enemy.pos.x + direction * i
                        if breath_x == self.player.pos.x and enemy.pos.y == self.player.pos.y:
                            self.game_state = "game_over"
                            break
                        if not self.grid.is_tunnel(breath_x, enemy.pos.y):
                            break

    def check_level_clear(self):
        """Check if level is complete."""
        alive_enemies = sum(1 for e in self.enemies if e.alive)
        if alive_enemies == 0 and self.game_state == "playing":
            self.game_state = "level_clear"
            self.state_timer = 120

    def update(self):
        """Main game update loop."""
        self.player.update()

        if self.game_state == "playing":
            self.update_rocks()
            self.update_enemies()
            self.check_level_clear()

            # Check enemy collision with player
            for enemy in self.enemies:
                if enemy.alive and enemy.pos.x == self.player.pos.x and enemy.pos.y == self.player.pos.y:
                    self.game_state = "game_over"

        elif self.game_state == "level_clear":
            self.state_timer -= 1
            if self.state_timer <= 0:
                self.level += 1
                self.reset()

    def draw(self):
        """Render game."""
        self.screen.fill(COLOR_BG)

        # Draw grid
        for x in range(GRID_COLS):
            for y in range(GRID_ROWS):
                rect = pygame.Rect(
                    x * CELL_SIZE,
                    y * CELL_SIZE,
                    CELL_SIZE,
                    CELL_SIZE
                )

                if self.grid.cells[x][y] == 0:
                    # Soil
                    pygame.draw.rect(self.screen, COLOR_SOIL, rect)
                    pygame.draw.rect(self.screen, COLOR_SOIL_DARK, rect, 1)
                else:
                    # Tunnel
                    pygame.draw.rect(self.screen, COLOR_TUNNEL, rect)

        # Draw rocks
        for rock in self.grid.rocks:
            if not rock.alive:
                continue

            center_x = rock.pos.x * CELL_SIZE + CELL_SIZE // 2
            center_y = rock.pos.y * CELL_SIZE + CELL_SIZE // 2
            radius = CELL_SIZE // 2 - 4

            if rock.state == "wobbling":
                offset = (rock.wobble_timer % 6) - 3
                pygame.draw.circle(self.screen, COLOR_ROCK,
                                 (center_x + offset, center_y), radius)
            else:
                pygame.draw.circle(self.screen, COLOR_ROCK,
                                 (center_x, center_y), radius)

            # Rock highlight
            pygame.draw.circle(self.screen, (160, 160, 160),
                             (center_x - 4, center_y - 4), radius // 3)

        # Draw enemies
        for enemy in self.enemies:
            if not enemy.alive:
                continue

            center_x = enemy.pos.x * CELL_SIZE + CELL_SIZE // 2
            center_y = enemy.pos.y * CELL_SIZE + CELL_SIZE // 2
            size = CELL_SIZE // 2 - 2

            # Inflation effect
            inflation_scale = 1 + enemy.inflation * 0.2
            size = int(size * inflation_scale)

            if isinstance(enemy, Pooka):
                color = COLOR_POOKA
                if enemy.ghost_mode:
                    color = (200, 150, 100)
                pygame.draw.circle(self.screen, color, (center_x, center_y), size)
                # Goggles
                pygame.draw.circle(self.screen, (255, 255, 255),
                                 (center_x - 4, center_y - 2), 4)
                pygame.draw.circle(self.screen, (255, 255, 255),
                                 (center_x + 4, center_y - 2), 4)
            else:  # Fygar
                pygame.draw.rect(self.screen, COLOR_FYGAR,
                               (center_x - size, center_y - size, size * 2, size * 2))
                # Eyes
                pygame.draw.circle(self.screen, (255, 255, 255),
                                 (center_x - 4, center_y - 2), 3)
                pygame.draw.circle(self.screen, (255, 255, 255),
                                 (center_x + 4, center_y - 2), 3)

        # Draw player
        player_center_x = self.player.pos.x * CELL_SIZE + CELL_SIZE // 2
        player_center_y = self.player.pos.y * CELL_SIZE + CELL_SIZE // 2
        pygame.draw.circle(self.screen, COLOR_PLAYER,
                         (player_center_x, player_center_y), CELL_SIZE // 2 - 4)
        # Player face
        eye_offset_x = -4 if self.player.facing != "right" else 4
        pygame.draw.circle(self.screen, (50, 50, 50),
                         (player_center_x + eye_offset_x, player_center_y - 2), 4)
        pygame.draw.circle(self.screen, (50, 50, 50),
                         (player_center_x + eye_offset_x, player_center_y - 2), 2)

        # Draw pump wire
        if self.player.pump_active and self.player.pump_direction:
            dx, dy = 0, 0
            if self.player.pump_direction == "UP":
                dy = -1
            elif self.player.pump_direction == "DOWN":
                dy = 1
            elif self.player.pump_direction == "LEFT":
                dx = -1
            elif self.player.pump_direction == "RIGHT":
                dx = 1

            end_x = player_center_x + dx * PUMP_RANGE * CELL_SIZE
            end_y = player_center_y + dy * PUMP_RANGE * CELL_SIZE
            pygame.draw.line(self.screen, COLOR_PUMP,
                           (player_center_x, player_center_y),
                           (end_x, end_y), 3)

        # Draw HUD
        hud_height = 50
        pygame.draw.rect(self.screen, COLOR_HUD,
                        (0, WINDOW_HEIGHT - hud_height, WINDOW_WIDTH, hud_height))

        score_text = self.font.render(f"SCORE: {self.score}", True, COLOR_TEXT)
        level_text = self.font.render(f"LEVEL: {self.level}", True, COLOR_TEXT)
        enemies_text = self.small_font.render(
            f"ENEMIES: {sum(1 for e in self.enemies if e.alive)}", True, COLOR_TEXT)

        self.screen.blit(score_text, (20, WINDOW_HEIGHT - 40))
        self.screen.blit(level_text, (300, WINDOW_HEIGHT - 40))
        self.screen.blit(enemies_text, (550, WINDOW_HEIGHT - 35))

        # Instructions
        controls_text = self.small_font.render("ARROWS: Move/Dig | SPACE: Pump", True, (180, 180, 180))
        self.screen.blit(controls_text, (20, WINDOW_HEIGHT - 70))

        # Game over / level clear overlay
        if self.game_state == "game_over":
            overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))

            go_text = self.font.render("GAME OVER", True, (255, 50, 50))
            restart_text = self.small_font.render("Press R to restart or ESC to quit",
                                                 True, COLOR_TEXT)
            self.screen.blit(go_text,
                           (WINDOW_WIDTH // 2 - go_text.get_width() // 2,
                            WINDOW_HEIGHT // 2 - 50))
            self.screen.blit(restart_text,
                           (WINDOW_WIDTH // 2 - restart_text.get_width() // 2,
                            WINDOW_HEIGHT // 2 + 10))

        elif self.game_state == "level_clear":
            lc_text = self.font.render("LEVEL CLEAR!", True, (50, 255, 50))
            self.screen.blit(lc_text,
                           (WINDOW_WIDTH // 2 - lc_text.get_width() // 2,
                            WINDOW_HEIGHT // 2))

        pygame.display.flip()

    def run(self):
        """Main game loop."""
        running = True

        while running:
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False

                    elif self.game_state == "game_over":
                        if event.key == pygame.K_r:
                            self.reset()

                    elif self.game_state == "playing":
                        if event.key == pygame.K_UP:
                            self.move_player(0, -1)
                            self.use_pump("UP")
                        elif event.key == pygame.K_DOWN:
                            self.move_player(0, 1)
                            self.use_pump("DOWN")
                        elif event.key == pygame.K_LEFT:
                            self.move_player(-1, 0)
                            self.use_pump("LEFT")
                        elif event.key == pygame.K_RIGHT:
                            self.move_player(1, 0)
                            self.use_pump("RIGHT")
                        elif event.key == pygame.K_SPACE:
                            # Pump in last moved direction
                            if self.player.facing == "up":
                                self.use_pump("UP")
                            elif self.player.facing == "down":
                                self.use_pump("DOWN")
                            elif self.player.facing == "left":
                                self.use_pump("LEFT")
                            else:
                                self.use_pump("RIGHT")

            # Continuous movement with held keys
            if self.game_state == "playing":
                keys = pygame.key.get_pressed()
                if keys[pygame.K_UP]:
                    self.move_player(0, -1)
                elif keys[pygame.K_DOWN]:
                    self.move_player(0, 1)
                elif keys[pygame.K_LEFT]:
                    self.move_player(-1, 0)
                elif keys[pygame.K_RIGHT]:
                    self.move_player(1, 0)

            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
