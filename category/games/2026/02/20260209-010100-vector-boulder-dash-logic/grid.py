"""Grid-based level and physics simulation for Boulder Dash."""

from config import *


class Grid:
    """Manages the game grid and physics simulation."""

    def __init__(self):
        self.grid = []
        self.width = GRID_COLS
        self.height = GRID_ROWS
        self.diamonds_collected = 0
        self.diamonds_total = 0
        self.exit_open = False
        self.enemies = []
        self.last_gravity_update = 0
        self.last_enemy_update = 0
        self.enemy_killed = False

    def load_level(self, level_data):
        """Load a level from a string representation."""
        self.grid = []
        self.enemies = []

        # Parse level data
        for row in level_data.strip().split('\n'):
            grid_row = []
            for char in row:
                if char == '#':
                    grid_row.append(TILE_WALL)
                elif char == '.':
                    grid_row.append(TILE_DIRT)
                elif char == ' ':
                    grid_row.append(TILE_EMPTY)
                elif char == 'O':
                    grid_row.append(TILE_ROCK)
                elif char == '$':
                    grid_row.append(TILE_DIAMOND)
                    self.diamonds_total += 1
                elif char == 'E':
                    grid_row.append(TILE_EMPTY)
                    self.enemies.append({'x': len(grid_row), 'y': len(self.grid)})
                elif char == 'X':
                    grid_row.append(TILE_EXIT)
                else:
                    grid_row.append(TILE_EMPTY)
            self.grid.append(grid_row)

        # Ensure grid has correct dimensions
        while len(self.grid) < self.height:
            self.grid.append([TILE_WALL] * self.width)

    def is_valid_pos(self, x, y):
        """Check if position is within grid bounds."""
        return 0 <= x < self.width and 0 <= y < self.height

    def get_tile(self, x, y):
        """Get tile at position."""
        if self.is_valid_pos(x, y):
            return self.grid[y][x]
        return TILE_WALL

    def set_tile(self, x, y, tile):
        """Set tile at position."""
        if self.is_valid_pos(x, y):
            self.grid[y][x] = tile

    def is_walkable(self, x, y):
        """Check if player can walk to position."""
        tile = self.get_tile(x, y)
        return tile in (TILE_EMPTY, TILE_DIRT, TILE_DIAMOND, TILE_EXIT, TILE_EXIT_OPEN)

    def dig(self, x, y):
        """Dig dirt at position, returns True if diamond collected."""
        tile = self.get_tile(x, y)
        if tile == TILE_DIRT:
            self.set_tile(x, y, TILE_EMPTY)
            return False
        elif tile == TILE_DIAMOND:
            self.set_tile(x, y, TILE_EMPTY)
            self.diamonds_collected += 1
            if self.diamonds_collected >= DIAMONDS_TO_OPEN_EXIT:
                self.exit_open = True
                self.open_exit()
            return True
        return False

    def open_exit(self):
        """Open the exit door."""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x] == TILE_EXIT:
                    self.grid[y][x] = TILE_EXIT_OPEN

    def can_fall_into(self, tile):
        """Check if an object can fall into this tile."""
        return tile in (TILE_EMPTY,)

    def can_roll_off(self, tile):
        """Check if a rounded object can roll off this tile."""
        return tile in (TILE_ROCK, TILE_DIAMOND)

    def is_rounded(self, tile):
        """Check if tile is a rounded object."""
        return tile in (TILE_ROCK, TILE_DIAMOND)

    def update_physics(self, current_time, player_x, player_y):
        """Update gravity and rock physics. Returns True if player was crushed."""
        if current_time - self.last_gravity_update < GRAVITY_UPDATE_INTERVAL:
            return False

        self.last_gravity_update = current_time
        player_crushed = False

        # Process from bottom to top, alternating left-right direction
        for y in range(self.height - 2, -1, -1):
            direction = 1 if (self.height - y) % 2 == 1 else -1
            x_range = range(self.width - 1, -1, -1) if direction == -1 else range(self.width)

            for x in x_range:
                tile = self.get_tile(x, y)

                if self.is_rounded(tile):
                    below = self.get_tile(x, y + 1)

                    # Fall straight down
                    if self.can_fall_into(below):
                        self.set_tile(x, y, TILE_EMPTY)
                        self.set_tile(x, y + 1, tile)

                        # Check if player is crushed
                        if x == player_x and y + 1 == player_y:
                            player_crushed = True

                    # Roll off rounded objects
                    elif self.can_roll_off(below):
                        # Try left
                        left = self.get_tile(x - 1, y)
                        left_below = self.get_tile(x - 1, y + 1)

                        if self.can_fall_into(left) and self.can_fall_into(left_below):
                            self.set_tile(x, y, TILE_EMPTY)
                            self.set_tile(x - 1, y + 1, tile)

                            if x - 1 == player_x and y + 1 == player_y:
                                player_crushed = True

                        # Try right
                        else:
                            right = self.get_tile(x + 1, y)
                            right_below = self.get_tile(x + 1, y + 1)

                            if self.can_fall_into(right) and self.can_fall_into(right_below):
                                self.set_tile(x, y, TILE_EMPTY)
                                self.set_tile(x + 1, y + 1, tile)

                                if x + 1 == player_x and y + 1 == player_y:
                                    player_crushed = True

                    # Roll off walls/dirt (with empty space below and to side)
                    elif below in (TILE_WALL, TILE_DIRT):
                        left = self.get_tile(x - 1, y)
                        left_below = self.get_tile(x - 1, y + 1)
                        right = self.get_tile(x + 1, y)
                        right_below = self.get_tile(x + 1, y + 1)

                        if self.can_fall_into(left) and self.can_fall_into(left_below):
                            self.set_tile(x, y, TILE_EMPTY)
                            self.set_tile(x - 1, y + 1, tile)

                            if x - 1 == player_x and y + 1 == player_y:
                                player_crushed = True

                        elif self.can_fall_into(right) and self.can_fall_into(right_below):
                            self.set_tile(x, y, TILE_EMPTY)
                            self.set_tile(x + 1, y + 1, tile)

                            if x + 1 == player_x and y + 1 == player_y:
                                player_crushed = True

        return player_crushed

    def update_enemies(self, current_time, player_x, player_y):
        """Update enemy positions. Returns True if player is caught."""
        if current_time - self.last_enemy_update < ENEMY_MOVE_INTERVAL:
            return False

        self.last_enemy_update = current_time
        self.enemy_killed = False

        for enemy in self.enemies[:]:
            ex, ey = enemy['x'], enemy['y']

            # Simple tracking AI - move toward player
            dx = player_x - ex
            dy = player_y - ey

            move_x = 0
            move_y = 0

            if abs(dx) > abs(dy):
                move_x = 1 if dx > 0 else -1
            else:
                move_y = 1 if dy > 0 else -1

            # Try primary direction
            new_x, new_y = ex + move_x, ey + move_y

            if self.is_walkable(new_x, new_y) and self.get_tile(new_x, new_y) != TILE_EXIT:
                enemy['x'] = new_x
                enemy['y'] = new_y
            else:
                # Try alternate direction
                if move_x != 0:
                    move_x = 0
                    move_y = 1 if dy >= 0 else -1
                else:
                    move_y = 0
                    move_x = 1 if dx >= 0 else -1

                new_x, new_y = ex + move_x, ey + move_y
                if self.is_walkable(new_x, new_y) and self.get_tile(new_x, new_y) != TILE_EXIT:
                    enemy['x'] = new_x
                    enemy['y'] = new_y

            # Check if enemy reached player
            if enemy['x'] == player_x and enemy['y'] == player_y:
                return True

        return False

    def check_enemy_crushed(self, x, y):
        """Check if an enemy was crushed by a falling rock."""
        for enemy in self.enemies[:]:
            if enemy['x'] == x and enemy['y'] == y:
                self.enemies.remove(enemy)
                self.enemy_killed = True
                return True
        return False

    def can_push_rock(self, x, y, dx):
        """Check if rock at x,y can be pushed in direction dx."""
        if dx == 0:
            return False

        target_x = x + dx
        if not self.is_valid_pos(target_x, y):
            return False

        target_tile = self.get_tile(target_x, y)

        # Can only push into empty space
        if target_tile == TILE_EMPTY:
            # Check nothing would fall on the rock after push
            for check_y in range(y - 1, -1, -1):
                check_tile = self.get_tile(x, check_y)
                if check_tile == TILE_WALL:
                    break
                if self.is_rounded(check_tile):
                    below = self.get_tile(x, check_y + 1)
                    if below in (TILE_EMPTY, TILE_DIRT):
                        return False

            return True

        return False

    def push_rock(self, x, y, dx):
        """Push a rock in direction dx."""
        if self.can_push_rock(x, y, dx):
            target_x = x + dx
            self.set_tile(target_x, y, TILE_ROCK)
            self.set_tile(x, y, TILE_EMPTY)
            return True
        return False

    def is_at_exit(self, x, y):
        """Check if position is at an open exit."""
        tile = self.get_tile(x, y)
        return tile == TILE_EXIT_OPEN
