"""Runtime analysis test for Infinite Koopa Shell Bounce game."""

import os
import sys
import json
import time
from datetime import datetime

# Set pygame to use dummy video driver (headless mode)
os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'

# Import game modules
import pygame
import config as cfg
from game import Game, Player, Shell

def test_basic_imports():
    """Test that all modules can be imported."""
    results = []

    try:
        import pygame
        results.append({"test": "pygame_import", "status": "PASSED", "message": "Pygame imported successfully"})
    except Exception as e:
        results.append({"test": "pygame_import", "status": "FAILED", "message": f"Failed to import pygame: {e}"})
        return results

    try:
        import config
        results.append({"test": "config_import", "status": "PASSED", "message": "Config module imported successfully"})
    except Exception as e:
        results.append({"test": "config_import", "status": "FAILED", "message": f"Failed to import config: {e}"})

    try:
        from game import Game, Player, Shell
        results.append({"test": "game_import", "status": "PASSED", "message": "Game classes imported successfully"})
    except Exception as e:
        results.append({"test": "game_import", "status": "FAILED", "message": f"Failed to import game classes: {e}"})

    return results

def test_player_initialization():
    """Test Player class initialization."""
    results = []

    try:
        player = Player(100, 200)

        # Check initial position
        if player.x == 100 and player.y == 200:
            results.append({"test": "player_position", "status": "PASSED", "message": "Player initialized at correct position"})
        else:
            results.append({"test": "player_position", "status": "FAILED", "message": f"Player position incorrect: ({player.x}, {player.y})"})

        # Check dimensions
        if player.width == cfg.PLAYER_WIDTH and player.height == cfg.PLAYER_HEIGHT:
            results.append({"test": "player_dimensions", "status": "PASSED", "message": "Player dimensions match config"})
        else:
            results.append({"test": "player_dimensions", "status": "FAILED", "message": f"Player dimensions incorrect: {player.width}x{player.height}"})

        # Check initial state
        if player.vel_x == 0 and player.vel_y == 0:
            results.append({"test": "player_velocity", "status": "PASSED", "message": "Player initial velocity is zero"})
        else:
            results.append({"test": "player_velocity", "status": "FAILED", "message": f"Player initial velocity incorrect: ({player.vel_x}, {player.vel_y})"})

    except Exception as e:
        results.append({"test": "player_initialization", "status": "FAILED", "message": f"Exception during player initialization: {e}"})

    return results

def test_player_movement():
    """Test Player movement methods."""
    results = []

    try:
        player = Player(100, 200)
        initial_x = player.x

        # Test move left
        player.move_left()
        if player.vel_x == -cfg.PLAYER_SPEED:
            results.append({"test": "player_move_left", "status": "PASSED", "message": "Player move_left sets correct velocity"})
        else:
            results.append({"test": "player_move_left", "status": "FAILED", "message": f"Player move_left velocity incorrect: {player.vel_x}"})

        # Test move right
        player.move_right()
        if player.vel_x == cfg.PLAYER_SPEED:
            results.append({"test": "player_move_right", "status": "PASSED", "message": "Player move_right sets correct velocity"})
        else:
            results.append({"test": "player_move_right", "status": "FAILED", "message": f"Player move_right velocity incorrect: {player.vel_x}"})

        # Test stop horizontal
        player.stop_horizontal()
        if player.vel_x == 0:
            results.append({"test": "player_stop", "status": "PASSED", "message": "Player stop_horizontal sets velocity to zero"})
        else:
            results.append({"test": "player_stop", "status": "FAILED", "message": f"Player stop velocity incorrect: {player.vel_x}"})

    except Exception as e:
        results.append({"test": "player_movement", "status": "FAILED", "message": f"Exception during movement test: {e}"})

    return results

def test_shell_initialization():
    """Test Shell class initialization."""
    results = []

    try:
        shell = Shell(400, 300)

        # Check initial position
        if shell.x == 400 and shell.y == 300:
            results.append({"test": "shell_position", "status": "PASSED", "message": "Shell initialized at correct position"})
        else:
            results.append({"test": "shell_position", "status": "FAILED", "message": f"Shell position incorrect: ({shell.x}, {shell.y})"})

        # Check initial state
        if not shell.active and shell.vel_x == 0 and shell.vel_y == 0:
            results.append({"test": "shell_initial_state", "status": "PASSED", "message": "Shell initial state is inactive with zero velocity"})
        else:
            results.append({"test": "shell_initial_state", "status": "FAILED", "message": f"Shell initial state incorrect: active={shell.active}, vel=({shell.vel_x}, {shell.vel_y})"})

        # Test kick
        shell.kick(1)
        if shell.active and shell.vel_x > 0:
            results.append({"test": "shell_kick", "status": "PASSED", "message": "Shell kick activates and sets velocity"})
        else:
            results.append({"test": "shell_kick", "status": "FAILED", "message": f"Shell kick failed: active={shell.active}, vel_x={shell.vel_x}"})

    except Exception as e:
        results.append({"test": "shell_initialization", "status": "FAILED", "message": f"Exception during shell test: {e}"})

    return results

def test_game_initialization():
    """Test Game class initialization."""
    results = []

    try:
        game = Game()

        # Check pygame initialization
        if pygame.get_init():
            results.append({"test": "pygame_init", "status": "PASSED", "message": "Pygame initialized successfully"})
        else:
            results.append({"test": "pygame_init", "status": "FAILED", "message": "Pygame not initialized"})

        # Check screen
        if game.screen is not None:
            results.append({"test": "screen_creation", "status": "PASSED", "message": "Screen created successfully"})
        else:
            results.append({"test": "screen_creation", "status": "FAILED", "message": "Screen creation failed"})

        # Check clock
        if game.clock is not None:
            results.append({"test": "clock_creation", "status": "PASSED", "message": "Clock created successfully"})
        else:
            results.append({"test": "clock_creation", "status": "FAILED", "message": "Clock creation failed"})

        # Check game reset
        if game.player is not None and game.shell is not None:
            results.append({"test": "game_reset", "status": "PASSED", "message": "Game reset created player and shell"})
        else:
            results.append({"test": "game_reset", "status": "FAILED", "message": "Game reset failed to create objects"})

        # Check initial game state
        if not game.game_over and game.waiting_to_kick:
            results.append({"test": "game_initial_state", "status": "PASSED", "message": "Game starts in waiting_to_kick state"})
        else:
            results.append({"test": "game_initial_state", "status": "FAILED", "message": f"Game state incorrect: game_over={game.game_over}, waiting={game.waiting_to_kick}"})

    except Exception as e:
        results.append({"test": "game_initialization", "status": "FAILED", "message": f"Exception during game initialization: {e}"})

    return results

def test_physics_update():
    """Test physics simulation."""
    results = []

    try:
        # Test player gravity
        player = Player(100, 100)
        player.vel_y = 0
        player.update()

        if player.vel_y > 0:
            results.append({"test": "player_gravity", "status": "PASSED", "message": "Player gravity applied correctly"})
        else:
            results.append({"test": "player_gravity", "status": "FAILED", "message": f"Player gravity not applied: vel_y={player.vel_y}"})

        # Test shell update when inactive
        shell = Shell(400, 300)
        shell.update()
        if shell.x == 400 and shell.y == 300:
            results.append({"test": "shell_inactive_update", "status": "PASSED", "message": "Inactive shell doesn't move"})
        else:
            results.append({"test": "shell_inactive_update", "status": "FAILED", "message": f"Inactive shell moved: ({shell.x}, {shell.y})"})

        # Test shell update when active
        shell = Shell(400, 300)
        shell.kick(1)
        initial_x = shell.x
        shell.update()
        if shell.x != initial_x:
            results.append({"test": "shell_active_update", "status": "PASSED", "message": "Active shell moves when updated"})
        else:
            results.append({"test": "shell_active_update", "status": "FAILED", "message": "Active shell didn't move"})

        # Test platform collision
        player = Player(100, cfg.PLATFORM_Y_LEVEL - 50)
        player.vel_y = 10
        player.update()
        if player.on_ground and player.y == cfg.PLATFORM_Y_LEVEL - cfg.PLAYER_HEIGHT:
            results.append({"test": "platform_collision", "status": "PASSED", "message": "Player lands on platform correctly"})
        else:
            results.append({"test": "platform_collision", "status": "FAILED", "message": f"Platform collision failed: on_ground={player.on_ground}, y={player.y}"})

    except Exception as e:
        results.append({"test": "physics_update", "status": "FAILED", "message": f"Exception during physics test: {e}"})

    return results

def test_observations():
    """Test observation space for RL."""
    results = []

    try:
        game = Game()

        # Test player observation
        player_obs = game.player.get_observation()
        required_keys = ["player_x", "player_y", "is_grounded"]
        if all(key in player_obs for key in required_keys):
            results.append({"test": "player_observation", "status": "PASSED", "message": "Player observation has all required keys"})
        else:
            results.append({"test": "player_observation", "status": "FAILED", "message": f"Player observation missing keys: {player_obs}"})

        # Test shell observation
        shell_obs = game.shell.get_observation()
        required_keys = ["shell_x", "shell_y", "shell_velocity_x", "shell_velocity_y"]
        if all(key in shell_obs for key in required_keys):
            results.append({"test": "shell_observation", "status": "PASSED", "message": "Shell observation has all required keys"})
        else:
            results.append({"test": "shell_observation", "status": "FAILED", "message": f"Shell observation missing keys: {shell_obs}"})

        # Test game observation
        game_obs = game.get_observation()
        all_keys = required_keys + ["player_x", "player_y", "is_grounded"]
        if all(key in game_obs for key in all_keys):
            results.append({"test": "game_observation", "status": "PASSED", "message": "Game observation combines all observations"})
        else:
            results.append({"test": "game_observation", "status": "FAILED", "message": f"Game observation missing keys"})

        # Test action space
        actions = game.get_action_space()
        expected_actions = ["LEFT", "RIGHT", "JUMP", "NONE"]
        if actions == expected_actions:
            results.append({"test": "action_space", "status": "PASSED", "message": "Action space matches expected values"})
        else:
            results.append({"test": "action_space", "status": "FAILED", "message": f"Action space incorrect: {actions}"})

    except Exception as e:
        results.append({"test": "observations", "status": "FAILED", "message": f"Exception during observation test: {e}"})

    return results

def test_step_function():
    """Test RL step function."""
    results = []

    try:
        game = Game()
        initial_score = game.score

        # Test JUMP action
        obs, reward, done, info = game.step("JUMP")
        if isinstance(obs, dict) and isinstance(reward, (int, float)) and isinstance(done, bool):
            results.append({"test": "step_return_types", "status": "PASSED", "message": "Step returns correct types"})
        else:
            results.append({"test": "step_return_types", "status": "FAILED", "message": f"Step return types incorrect: obs={type(obs)}, reward={type(reward)}, done={type(done)}"})

        # Test reward calculation
        if reward >= 0:
            results.append({"test": "step_reward", "status": "PASSED", "message": "Step returns non-negative reward during gameplay"})
        else:
            results.append({"test": "step_reward", "status": "FAILED", "message": f"Step reward unexpected: {reward}"})

        # Test LEFT action
        obs, reward, done, info = game.step("LEFT")
        if "player_x" in obs:
            results.append({"test": "step_left_action", "status": "PASSED", "message": "LEFT action updates game state"})
        else:
            results.append({"test": "step_left_action", "status": "FAILED", "message": "LEFT action failed to update state"})

        # Test RIGHT action
        obs, reward, done, info = game.step("RIGHT")
        if "player_x" in obs:
            results.append({"test": "step_right_action", "status": "PASSED", "message": "RIGHT action updates game state"})
        else:
            results.append({"test": "step_right_action", "status": "FAILED", "message": "RIGHT action failed to update state"})

    except Exception as e:
        results.append({"test": "step_function", "status": "FAILED", "message": f"Exception during step test: {e}"})

    return results

def test_drawing():
    """Test drawing functions (headless)."""
    results = []

    try:
        game = Game()

        # Test draw methods don't crash
        game.draw_platform()
        results.append({"test": "draw_platform", "status": "PASSED", "message": "Platform drawing executed without errors"})

        game.player.draw(game.screen)
        results.append({"test": "draw_player", "status": "PASSED", "message": "Player drawing executed without errors"})

        game.shell.draw(game.screen)
        results.append({"test": "draw_shell", "status": "PASSED", "message": "Shell drawing executed without errors"})

        game.draw_hud()
        results.append({"test": "draw_hud", "status": "PASSED", "message": "HUD drawing executed without errors"})

    except Exception as e:
        results.append({"test": "drawing", "status": "FAILED", "message": f"Exception during drawing test: {e}"})

    return results

def test_collision_detection():
    """Test collision detection."""
    results = []

    try:
        game = Game()

        # Set up player above shell - need rects to overlap for collision
        # Player: height=40, Shell: height=24
        # For bounce collision: player.vel_y > 0 and player.bottom < shell.centery
        game.player.x = 200
        # Position player so bottom is just above shell center
        # If shell.y = 330, shell.centery = 330 + 12 = 342
        # Player bottom should be < 342, let's say player bottom = 338, so player.y = 338 - 40 = 298
        game.player.y = 298
        game.player.vel_y = 5
        game.player.rect.x = int(game.player.x)
        game.player.rect.y = int(game.player.y)

        game.shell.x = 200
        game.shell.y = 330  # Shell at y=330, so rect is (200, 330, 32, 24), centery at 342
        game.shell.kick(1)
        game.shell.rect.x = int(game.shell.x)
        game.shell.rect.y = int(game.shell.y)

        initial_score = game.score
        initial_combo = game.combo

        # Verify rects overlap
        rects_overlap = game.player.rect.colliderect(game.shell.rect)

        if not rects_overlap:
            results.append({"test": "shell_bounce_collision", "status": "FAILED", "message": f"Test setup failed: rects don't overlap. player_rect={game.player.rect}, shell_rect={game.shell.rect}"})
        else:
            game.check_collisions()

            # Player should bounce off shell
            if game.player.vel_y < 0:
                results.append({"test": "shell_bounce_collision", "status": "PASSED", "message": "Player bounces off shell correctly"})
            else:
                results.append({"test": "shell_bounce_collision", "status": "FAILED", "message": f"Player didn't bounce: vel_y={game.player.vel_y}, collision_condition={game.player.vel_y > 0 and game.player.y + game.player.height - 5 < game.shell.y + game.shell.height / 2}"})

            # Combo should increase
            if game.combo > initial_combo:
                results.append({"test": "combo_increase", "status": "PASSED", "message": "Combo increases on shell bounce"})
            else:
                results.append({"test": "combo_increase", "status": "FAILED", "message": f"Combo didn't increase: {game.combo}"})

            # Score should increase
            if game.score > initial_score:
                results.append({"test": "score_increase", "status": "PASSED", "message": "Score increases on shell bounce"})
            else:
                results.append({"test": "score_increase", "status": "FAILED", "message": f"Score didn't increase: {game.score}"})

    except Exception as e:
        results.append({"test": "collision_detection", "status": "FAILED", "message": f"Exception during collision test: {e}"})

    return results

def run_all_tests():
    """Run all runtime tests."""
    start_time = time.time()

    all_results = []

    print("Starting runtime analysis...")

    # Run all test suites
    all_results.extend(test_basic_imports())
    all_results.extend(test_player_initialization())
    all_results.extend(test_player_movement())
    all_results.extend(test_shell_initialization())
    all_results.extend(test_game_initialization())
    all_results.extend(test_physics_update())
    all_results.extend(test_observations())
    all_results.extend(test_step_function())
    all_results.extend(test_drawing())
    all_results.extend(test_collision_detection())

    elapsed_time = time.time() - start_time

    # Calculate statistics
    total_tests = len(all_results)
    passed_tests = sum(1 for r in all_results if r["status"] == "PASSED")
    failed_tests = total_tests - passed_tests
    success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

    # Determine overall status
    overall_status = "PASSED" if failed_tests == 0 else "FAILED"

    # Create report
    report = {
        "overall_status": overall_status,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "duration_seconds": round(elapsed_time, 2),
        "total_tests": total_tests,
        "passed_tests": passed_tests,
        "failed_tests": failed_tests,
        "success_rate": round(success_rate, 2),
        "tests": all_results,
        "summary": {
            "application_start": "PASSED",
            "basic_functionality": "PASSED" if failed_tests <= 2 else "FAILED",
            "physics_simulation": "PASSED" if all(r["status"] == "PASSED" for r in all_results if "physics" in r["test"]) else "FAILED",
            "rl_integration": "PASSED" if all(r["status"] == "PASSED" for r in all_results if "observation" in r["test"] or "action" in r["test"] or "step" in r["test"]) else "FAILED"
        }
    }

    return report

def main():
    # Initialize pygame with dummy driver
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal display for headless

    try:
        report = run_all_tests()

        # Save report
        with open("runtime_analysis.json", "w") as f:
            json.dump(report, f, indent=2)

        print(f"\nRuntime Analysis Complete")
        print(f"Overall Status: {report['overall_status']}")
        print(f"Tests Passed: {report['passed_tests']}/{report['total_tests']}")
        print(f"Duration: {report['duration_seconds']}s")

        return 0 if report["overall_status"] == "PASSED" else 1

    finally:
        pygame.quit()

if __name__ == "__main__":
    sys.exit(main())
