"""Fighter entity with state machine."""

from dataclasses import dataclass
from typing import Optional, Tuple
import config as cfg


@dataclass
class AttackInfo:
    attack_type: str
    hitbox: Tuple[int, int, int, int]  # x, y, width, height
    damage: int
    priority: int


class Fighter:
    def __init__(self, x: int, is_player: bool = True):
        self.x = x
        self.y = cfg.GROUND_Y - cfg.FIGHTER_HEIGHT
        self.width = cfg.FIGHTER_WIDTH
        self.height = cfg.FIGHTER_HEIGHT
        self.is_player = is_player

        # State
        self.state = cfg.STATE_IDLE
        self.facing_right = not is_player  # Player faces right, AI faces left
        self.velocity = 0

        # Action timers
        self.action_timer = 0
        self.cooldown_timer = 0
        self.stun_timer = 0

        # Attack info
        self.current_attack: Optional[AttackInfo] = None

        # Score
        self.score = 0
        self.wins = 0

        # AI state
        self.ai_decision_timer = 0
        self.ai_cooldown = 0
        self.last_action = cfg.ACTION_IDLE

    @property
    def center_x(self) -> int:
        return self.x + self.width // 2

    @property
    def rect(self) -> Tuple[int, int, int, int]:
        return (self.x, self.y, self.width, self.height)

    def can_act(self) -> bool:
        return (
            self.state not in (cfg.STATE_STUNNED, cfg.STATE_HIT, cfg.STATE_VICTORY, cfg.STATE_DEFEAT)
            and self.cooldown_timer == 0
            and self.action_timer == 0
        )

    def is_attacking(self) -> bool:
        return self.state == cfg.STATE_ATTACKING

    def is_blocking(self) -> bool:
        return self.state == cfg.STATE_BLOCKING

    def get_attack_hitbox(self) -> Optional[Tuple[int, int, int, int]]:
        if not self.is_attacking() or not self.current_attack:
            return None

        hx, hy, hw, hh = self.current_attack.hitbox
        if self.facing_right:
            return (self.x + self.width, self.y + hy, hw, hh)
        else:
            return (self.x - hw, self.y + hy, hw, hh)

    def update(self):
        if self.stun_timer > 0:
            self.stun_timer -= 1
            if self.stun_timer == 0:
                self.state = cfg.STATE_IDLE
            return

        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

        if self.action_timer > 0:
            self.action_timer -= 1
            if self.action_timer == 0:
                self.current_attack = None
                self.state = cfg.STATE_IDLE

        # Apply movement
        if self.state == cfg.STATE_MOVING:
            self.x += self.velocity

            # Boundary check
            min_x = 50
            max_x = cfg.SCREEN_WIDTH - 50 - self.width
            self.x = max(min_x, min(max_x, self.x))

    def move(self, direction: int):
        if not self.can_act():
            return

        self.state = cfg.STATE_MOVING
        self.velocity = direction * cfg.MOVE_SPEED

        # Update facing direction
        if direction < 0:
            self.facing_right = False
        elif direction > 0:
            self.facing_right = True

    def stop_move(self):
        if self.state == cfg.STATE_MOVING:
            self.state = cfg.STATE_IDLE
            self.velocity = 0

    def attack(self, attack_type: str):
        if not self.can_act():
            return

        self.state = cfg.STATE_ATTACKING
        self.action_timer = cfg.ATTACK_DURATION
        self.cooldown_timer = cfg.COOLDOWN_FRAMES

        if attack_type == cfg.ACTION_ATTACK_HIGH:
            hitbox = (0, 10, *cfg.HIGH_ATTACK_HITBOX)
            priority = 1
            damage = cfg.HIGH_ATTACK_DAMAGE
        else:  # ACTION_ATTACK_LOW
            hitbox = (0, 60, *cfg.LOW_ATTACK_HITBOX)
            priority = 2
            damage = cfg.LOW_ATTACK_DAMAGE

        self.current_attack = AttackInfo(attack_type, hitbox, damage, priority)

    def block(self):
        if not self.can_act():
            return

        self.state = cfg.STATE_BLOCKING
        self.action_timer = cfg.BLOCK_DURATION
        self.cooldown_timer = cfg.COOLDOWN_FRAMES

    def take_hit(self, damage: int):
        self.state = cfg.STATE_HIT
        self.stun_timer = 15
        self.current_attack = None
        self.action_timer = 0
        return damage

    def score_point(self):
        self.score += 1

    def win_round(self):
        self.wins += 1
        self.score = 0

    def reset_position(self, is_left_side: bool):
        target_x = 150 if is_left_side else cfg.SCREEN_WIDTH - 200
        self.x = target_x
        self.y = cfg.GROUND_Y - cfg.FIGHTER_HEIGHT
        self.state = cfg.STATE_IDLE
        self.velocity = 0
        self.action_timer = 0
        self.cooldown_timer = 0
        self.stun_timer = 0
        self.current_attack = None

    def reset_match(self):
        self.score = 0
        self.wins = 0
        self.state = cfg.STATE_IDLE
        self.velocity = 0
        self.action_timer = 0
        self.cooldown_timer = 0
        self.stun_timer = 0
        self.current_attack = None


class AIFighter(Fighter):
    def __init__(self, x: int):
        super().__init__(x, is_player=False)
        self.reaction_timer = 0

    def update_ai(self, opponent: 'Fighter'):
        if not self.can_act():
            return

        self.reaction_timer += 1
        if self.reaction_timer < cfg.AIReactionTime:
            return

        distance = abs(self.center_x - opponent.center_x)
        opponent_to_left = opponent.center_x < self.center_x

        # React to opponent attack
        if opponent.is_attacking() and distance < 120:
            if self.ai_cooldown == 0:
                self.block()
                self.ai_cooldown = 30
                self.reaction_timer = 0
                return

        # Decision making
        import random
        roll = random.random()

        if distance > 200:
            # Close distance
            if opponent_to_left:
                self.move(-1)
            else:
                self.move(1)
        elif distance < 80:
            # Too close, maybe back up
            if roll < 0.3:
                if opponent_to_left:
                    self.move(1)
                else:
                    self.move(-1)
            elif roll < cfg.AIAttackChance + 0.3:
                attack_type = cfg.ACTION_ATTACK_HIGH if roll < 0.4 else cfg.ACTION_ATTACK_LOW
                self.attack(attack_type)
                self.reaction_timer = 0
            else:
                self.stop_move()
        else:
            # Attack range
            if roll < cfg.AIAttackChance:
                attack_type = cfg.ACTION_ATTACK_HIGH if roll < cfg.AIAttackChance / 2 else cfg.ACTION_ATTACK_LOW
                self.attack(attack_type)
                self.reaction_timer = 0
            elif roll < cfg.AIAttackChance + cfg.AIBlockChance:
                self.block()
                self.reaction_timer = 0
            else:
                # Slight movement
                if roll < 0.55:
                    if opponent_to_left:
                        self.move(-1)
                    else:
                        self.move(1)
                else:
                    self.stop_move()

        if self.ai_cooldown > 0:
            self.ai_cooldown -= 1
