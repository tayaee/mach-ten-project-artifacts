"""Runtime analysis test script for Vector Frog Log Crossing Logic."""

import pygame
import sys
from game import GameState
from renderer import Renderer
import time

print('[TEST] Starting comprehensive runtime analysis...')
start_time = time.time()

pygame.init()
state = GameState()
renderer = Renderer(state)

test_results = []

# Test 1: Initialization
try:
    print('[TEST-1] Testing initialization...')
    assert state.width == 600, 'Screen width incorrect'
    assert state.height == 600, 'Screen height incorrect'
    assert state.grid_size == 60, 'Grid size incorrect'
    assert state.grid_cols == 10, 'Grid columns incorrect'
    assert state.grid_rows == 10, 'Grid rows incorrect'
    assert state.player.alive == True, 'Player should start alive'
    assert state.game_over == False, 'Game should not be over initially'
    assert state.win == False, 'Game should not be won initially'
    assert state.score == 0, 'Score should start at 0'
    assert len(state.logs) == 8, 'Should have 8 logs'
    print('[TEST-1] PASSED: Initialization')
    test_results.append(('Initialization', 'PASSED'))
except AssertionError as e:
    print(f'[TEST-1] FAILED: {e}')
    test_results.append(('Initialization', f'FAILED: {e}'))

# Test 2: Player movement
try:
    print('[TEST-2] Testing player movement...')
    initial_y = state.player.pos.y
    state.move('up')
    assert state.player.pos.y == initial_y - 60, 'Up movement failed'

    state.move('down')
    assert state.player.pos.y == initial_y, 'Down movement failed'

    initial_x = state.player.pos.x
    state.move('left')
    assert state.player.pos.x == initial_x - 60, 'Left movement failed'

    state.move('right')
    assert state.player.pos.x == initial_x, 'Right movement failed'
    print('[TEST-2] PASSED: Player movement')
    test_results.append(('Player movement', 'PASSED'))
except AssertionError as e:
    print(f'[TEST-2] FAILED: {e}')
    test_results.append(('Player movement', f'FAILED: {e}'))

# Test 3: Log movement
try:
    print('[TEST-3] Testing log movement...')
    dt = 1.0 / 30.0
    log_positions = [(log.pos.x, log.pos.y, log.speed) for log in state.logs]
    state.update(dt)

    logs_moving = False
    for i, log in enumerate(state.logs):
        if abs(log.pos.x - log_positions[i][0]) > 0:
            logs_moving = True
            break

    assert logs_moving, 'Logs should move over time'
    print('[TEST-3] PASSED: Log movement')
    test_results.append(('Log movement', 'PASSED'))
except AssertionError as e:
    print(f'[TEST-3] FAILED: {e}')
    test_results.append(('Log movement', f'FAILED: {e}'))

# Test 4: Log wrapping (cycling)
try:
    print('[TEST-4] Testing log wrapping...')
    dt = 1.0
    for _ in range(100):
        state.update(dt)

    for log in state.logs:
        assert -500 < log.pos.x < 1100, f'Log {log.pos.x} out of expected bounds'

    print('[TEST-4] PASSED: Log wrapping')
    test_results.append(('Log wrapping', 'PASSED'))
except AssertionError as e:
    print(f'[TEST-4] FAILED: {e}')
    test_results.append(('Log wrapping', f'FAILED: {e}'))

# Test 5: Water collision (player dies in water)
try:
    print('[TEST-5] Testing water collision...')
    state.reset()
    state.move('up')
    state.move('up')
    state.move('up')
    state.move('up')
    state.move('up')

    # Move to a position where there's no log
    state.player.pos.x = 10
    state.player.pos.y = 4 * 60
    state.update(1.0)

    assert state.game_over == True, 'Player should die when not on log'
    print('[TEST-5] PASSED: Water collision')
    test_results.append(('Water collision', 'PASSED'))
except AssertionError as e:
    print(f'[TEST-5] FAILED: {e}')
    test_results.append(('Water collision', f'FAILED: {e}'))

# Test 6: Goal reaching
try:
    print('[TEST-6] Testing goal reaching...')
    state.reset()
    state.move('up')
    state.move('up')
    state.move('up')
    state.move('up')
    state.move('up')

    # Find a log and position player on it
    for log in state.logs:
        if 4 * 60 <= log.pos.y < 5 * 60:
            state.player.pos.x = log.pos.x
            break

    state.update(0.1)
    state.move('up')
    state.move('up')
    state.move('up')
    state.move('up')

    assert state.win == True, 'Player should win when reaching goal'
    assert state.game_over == True, 'Game should be over after winning'
    assert state.score >= 100, 'Score should be at least 100 for reaching goal'
    print('[TEST-6] PASSED: Goal reaching')
    test_results.append(('Goal reaching', 'PASSED'))
except AssertionError as e:
    print(f'[TEST-6] FAILED: {e}')
    test_results.append(('Goal reaching', f'FAILED: {e}'))

# Test 7: Score calculation
try:
    print('[TEST-7] Testing score calculation...')
    state.reset()
    initial_score = state.score
    state.move('up')
    state.move('up')
    assert state.score == 0, 'Score should be 0 in safe zone'

    print('[TEST-7] PASSED: Score calculation')
    test_results.append(('Score calculation', 'PASSED'))
except AssertionError as e:
    print(f'[TEST-7] FAILED: {e}')
    test_results.append(('Score calculation', f'FAILED: {e}'))

# Test 8: Game state reset
try:
    print('[TEST-8] Testing game state reset...')
    state.score = 500
    state.game_over = True
    state.player.alive = False
    state.reset()

    assert state.score == 0, 'Score should reset to 0'
    assert state.game_over == False, 'Game should not be over after reset'
    assert state.player.alive == True, 'Player should be alive after reset'
    assert state.win == False, 'Win state should reset'
    print('[TEST-8] PASSED: Game state reset')
    test_results.append(('Game state reset', 'PASSED'))
except AssertionError as e:
    print(f'[TEST-8] FAILED: {e}')
    test_results.append(('Game state reset', f'FAILED: {e}'))

# Test 9: Boundary checking (off-screen death)
try:
    print('[TEST-9] Testing boundary checking...')
    state.reset()
    state.player.pos.x = -10
    state.update(0.1)

    assert state.game_over == True, 'Player should die when going off left screen'
    test_results.append(('Boundary checking (left)', 'PASSED'))

    state.reset()
    state.player.pos.x = state.width + 10
    state.update(0.1)

    assert state.game_over == True, 'Player should die when going off right screen'
    test_results.append(('Boundary checking (right)', 'PASSED'))

    print('[TEST-9] PASSED: Boundary checking')
except AssertionError as e:
    print(f'[TEST-9] FAILED: {e}')
    test_results.append(('Boundary checking', f'FAILED: {e}'))

# Test 10: Rendering
try:
    print('[TEST-10] Testing rendering...')
    renderer.render()
    print('[TEST-10] PASSED: Rendering')
    test_results.append(('Rendering', 'PASSED'))
except Exception as e:
    print(f'[TEST-10] FAILED: {e}')
    test_results.append(('Rendering', f'FAILED: {e}'))

# Test 11: Extended runtime (simulate gameplay)
try:
    print('[TEST-11] Testing extended runtime...')
    state.reset()
    frame_count = 0
    for _ in range(300):
        state.update(1.0/30.0)
        frame_count += 1

    assert frame_count == 300, 'Should have processed 300 frames'
    print('[TEST-11] PASSED: Extended runtime')
    test_results.append(('Extended runtime (10s)', 'PASSED'))
except Exception as e:
    print(f'[TEST-11] FAILED: {e}')
    test_results.append(('Extended runtime', f'FAILED: {e}'))

# Test 12: Player on log movement
try:
    print('[TEST-12] Testing player movement on log...')
    state.reset()

    for log in state.logs:
        if 4 * 60 <= log.pos.y < 5 * 60:
            state.player.pos.x = log.pos.x + 10
            state.player.pos.y = 4 * 60 + 10
            initial_x = state.player.pos.x
            state.update(1.0)

            expected_x = initial_x + log.speed * 1.0
            assert abs(state.player.pos.x - expected_x) < 1.0, f'Player should move with log: expected {expected_x}, got {state.player.pos.x}'
            break

    print('[TEST-12] PASSED: Player on log movement')
    test_results.append(('Player on log movement', 'PASSED'))
except AssertionError as e:
    print(f'[TEST-12] FAILED: {e}')
    test_results.append(('Player on log movement', f'FAILED: {e}'))

end_time = time.time()
duration = end_time - start_time

pygame.quit()

# Summary
print('')
print('=' * 50)
print('RUNTIME ANALYSIS SUMMARY')
print('=' * 50)
print(f'Total test duration: {duration:.2f} seconds')
print(f'Tests run: {len(test_results)}')
passed = sum(1 for _, result in test_results if result == 'PASSED')
failed = sum(1 for _, result in test_results if 'FAILED' in result)
print(f'Tests passed: {passed}')
print(f'Tests failed: {failed}')
print('')

for test_name, result in test_results:
    status = '[PASS]' if result == 'PASSED' else '[FAIL]'
    print(f'{status} {test_name}: {result}')

sys.exit(0 if failed == 0 else 1)
