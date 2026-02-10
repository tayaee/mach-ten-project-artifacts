"""Game state and logic for Vector Super Mario Bros Water Swim Avoid."""

from entities import Player, Blooper, CheepCheep, Obstacle, Vec2
import config


class Game:
    def __init__(self):
        self.width = config.SCREEN_WIDTH
        self.height = config.SCREEN_HEIGHT
        self.reset()

    def reset(self):
        self.player = Player(config.PLAYER_START_X, config.PLAYER_START_Y)
        self.score = 0
        self.game_over = False
        self.win = False
        self.time_elapsed = 0.0
        self.camera_x = 0.0
        self.prev_max_x = config.PLAYER_START_X

        # Create level with obstacles and enemies
        self.obstacles: list[Obstacle] = []
        self.bloopers: list[Blooper] = []
        self.cheeps: list[CheepCheep] = []
        self._create_level()

        # Goal flag position
        self.flag_x = config.LEVEL_LENGTH - 100
        self.flag_y = 300

    def _create_level(self):
        # Ceiling and floor boundaries
        self.obstacles.append(Obstacle(0, 0, config.LEVEL_LENGTH, 20, "ceiling"))
        self.obstacles.append(Obstacle(0, config.SCREEN_HEIGHT - 20, config.LEVEL_LENGTH, 20, "floor"))

        # Coral formations (static hazards)
        coral_positions = [
            (200, 500), (350, 520), (500, 480), (650, 510),
            (850, 490), (1000, 510), (1150, 480), (1300, 500),
            (1500, 490), (1700, 510), (1900, 480), (2100, 500),
            (2300, 510), (2500, 490), (2700, 480), (2900, 500),
            (3100, 510), (3300, 490), (3500, 480), (3700, 500),
        ]
        for x, y in coral_positions:
            self.obstacles.append(Obstacle(x, y, config.CORAL_SIZE, config.CORAL_SIZE, "coral"))

        # Hanging coral from ceiling
        hanging_coral = [
            (300, 20), (600, 20), (900, 20), (1200, 20),
            (1600, 20), (2000, 20), (2400, 20), (2800, 20),
            (3200, 20), (3600, 20),
        ]
        for x, y in hanging_coral:
            self.obstacles.append(Obstacle(x, y, config.CORAL_SIZE, config.CORAL_SIZE, "coral"))

        # Underwater pipes
        pipe_positions = [
            (400, 450), (750, 460), (1100, 440), (1400, 450),
            (1800, 460), (2200, 440), (2600, 450), (3000, 460),
            (3400, 440), (3800, 450),
        ]
        for x, y in pipe_positions:
            self.obstacles.append(Obstacle(x, y, config.PIPE_WIDTH, config.PIPE_HEIGHT, "pipe"))

        # Bloopers (vertical patrollers)
        blooper_positions = [
            (250, 300), (550, 300), (850, 300), (1150, 300),
            (1450, 300), (1750, 300), (2050, 300), (2350, 300),
            (2650, 300), (2950, 300), (3250, 300), (3550, 300),
        ]
        for x, y in blooper_positions:
            self.bloopers.append(Blooper(x, y))

        # Cheep Cheeps (horizontal swimmers)
        cheep_configs = [
            (150, 200, 1), (150, 450, 1),
            (500, 150, 1), (500, 400, 1),
            (900, 180, -1), (900, 420, -1),
            (1300, 160, 1), (1300, 440, 1),
            (1700, 190, -1), (1700, 410, -1),
            (2100, 170, 1), (2100, 430, 1),
            (2500, 180, -1), (2500, 420, -1),
            (2900, 160, 1), (2900, 440, 1),
            (3300, 190, -1), (3300, 410, -1),
            (3700, 170, 1), (3700, 430, 1),
        ]
        for x, y, dir in cheep_configs:
            self.cheeps.append(CheepCheep(x, y, dir))

    def update(self, dt: float, inputs: dict):
        if self.game_over:
            return

        self.time_elapsed += dt

        # Get obstacles in view
        visible_obstacles = [
            obs for obs in self.obstacles
            if obs.pos.x > self.camera_x - 100 and obs.pos.x < self.camera_x + self.width + 100
        ]

        # Update player
        self.player.update(dt, inputs, visible_obstacles)

        # Update camera (follow player, prevent backtracking)
        if self.player.pos.x > self.camera_x + self.width * 0.4:
            self.camera_x = self.player.pos.x - self.width * 0.4
        self.camera_x = max(0, min(self.camera_x, config.LEVEL_LENGTH - self.width))

        # Update score based on progress
        progress_score = int(self.player.max_x // 100) * config.SCORE_PER_100_PIXELS
        self.score = progress_score

        # Update enemies
        player_screen_x = self.player.pos.x - self.camera_x
        for blooper in self.bloopers:
            # Only update bloopers near the player
            if abs(blooper.pos.x - self.player.pos.x) < 300:
                blooper.update(dt, self.player.pos.x)

        for cheep in self.cheeps:
            if abs(cheep.pos.x - self.player.pos.x) < 300:
                cheep.update(dt)

        # Check collisions
        player_rect = self.player.get_rect()

        # Obstacle collision
        for obs in visible_obstacles:
            obs_rect = obs.get_rect()
            if self._rects_collide(player_rect, obs_rect):
                self.player.alive = False
                self.score += config.DEATH_PENALTY
                self.game_over = True

        # Blooper collision
        for blooper in self.bloopers:
            if abs(blooper.pos.x - self.player.pos.x) < 300:
                blooper_rect = blooper.get_rect()
                if self._rects_collide(player_rect, blooper_rect):
                    self.player.alive = False
                    self.score += config.DEATH_PENALTY
                    self.game_over = True

        # Cheep Cheep collision
        for cheep in self.cheeps:
            if abs(cheep.pos.x - self.player.pos.x) < 300:
                cheep_rect = cheep.get_rect()
                if self._rects_collide(player_rect, cheep_rect):
                    self.player.alive = False
                    self.score += config.DEATH_PENALTY
                    self.game_over = True

        # Check goal (reaching the flag)
        if self.player.pos.x + self.player.width >= self.flag_x:
            self.player.finished = True
            self.score += config.GOAL_REWARD
            self.win = True
            self.game_over = True

    def _rects_collide(self, r1, r2) -> bool:
        return (r1[0] < r2[0] + r2[2] and r1[0] + r1[2] > r2[0] and
                r1[1] < r2[1] + r2[3] and r1[1] + r1[3] > r2[1])

    def get_visible_entities(self):
        """Return entities that should be visible based on camera position."""
        visible_obstacles = [
            obs for obs in self.obstacles
            if obs.pos.x > self.camera_x - 100 and obs.pos.x < self.camera_x + self.width + 100
        ]

        visible_bloopers = [
            b for b in self.bloopers
            if b.pos.x > self.camera_x - 100 and b.pos.x < self.camera_x + self.width + 100
        ]

        visible_cheeps = [
            c for c in self.cheeps
            if c.pos.x > self.camera_x - 100 and c.pos.x < self.camera_x + self.width + 100
        ]

        return visible_obstacles, visible_bloopers, visible_cheeps
