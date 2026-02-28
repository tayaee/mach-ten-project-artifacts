"""Final runtime analysis test script."""

import pygame
import sys
from game import GameState
from renderer import Renderer
import time

print('[RUNTIME ANALYSIS] Starting comprehensive runtime analysis...')
start_time = time.time()

pygame.init()
state = GameState()
renderer = Renderer(state)

tests = []
all_passed = True

# Test 1: Application starts without errors
try:
    print('[TEST] Application initialization...')
    assert state.width == 600
    assert state.height == 600
    assert state.grid_size == 60
    print('[PASS] Application initializes correctly')
    tests.append({'name': 'Application initialization', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Application initialization: {e}')
    tests.append({'name': 'Application initialization', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

# Test 2: Player movement works
try:
    print('[TEST] Player movement...')
    initial_x = state.player.pos.x
    initial_y = state.player.pos.y
    state.move('right')
    assert state.player.pos.x == initial_x + 60
    state.move('left')
    assert state.player.pos.x == initial_x
    state.move('up')
    assert state.player.pos.y == initial_y - 60
    state.move('down')
    assert state.player.pos.y == initial_y
    print('[PASS] Player movement works in all directions')
    tests.append({'name': 'Player movement', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Player movement: {e}')
    tests.append({'name': 'Player movement', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

# Test 3: Log physics work
try:
    print('[TEST] Log physics...')
    dt = 0.1
    initial_log_x = state.logs[0].pos.x
    state.update(dt)
    assert state.logs[0].pos.x != initial_log_x
    print('[PASS] Logs move correctly')
    tests.append({'name': 'Log physics', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Log physics: {e}')
    tests.append({'name': 'Log physics', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

# Test 4: Player follows log when on it
try:
    print('[TEST] Player on log...')
    state.reset()
    log = state.logs[6]
    state.player.pos.x = log.pos.x + 10
    state.player.pos.y = 240 + 10
    state.player.on_log = True
    state.player.current_log = log
    initial_x = state.player.pos.x
    state.update(0.1)
    assert abs(state.player.pos.x - initial_x - log.speed * 0.1) < 1.0
    print('[PASS] Player moves with log when riding it')
    tests.append({'name': 'Player on log movement', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Player on log: {e}')
    tests.append({'name': 'Player on log movement', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

# Test 5: Water death
try:
    print('[TEST] Water collision/death...')
    state.reset()
    state.player.pos.x = 250
    state.player.pos.y = 250
    state.player.on_log = False
    state.update(0.1)
    assert state.game_over == True
    assert state.player.alive == False
    print('[PASS] Player dies when in water without log')
    tests.append({'name': 'Water collision/death', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Water collision: {e}')
    tests.append({'name': 'Water collision/death', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

# Test 6: Boundary death
try:
    print('[TEST] Boundary death...')
    state.reset()
    state.player.pos.x = -10
    state.update(0.1)
    assert state.game_over == True
    state.reset()
    state.player.pos.x = 610
    state.update(0.1)
    assert state.game_over == True
    print('[PASS] Player dies when going off-screen')
    tests.append({'name': 'Boundary death', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Boundary death: {e}')
    tests.append({'name': 'Boundary death', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

# Test 7: Goal reaching
try:
    print('[TEST] Goal reaching...')
    state.reset()
    for _ in range(9):
        state.move('up')
    state.update(0.1)
    assert state.win == True
    assert state.game_over == True
    assert state.score >= 100
    print('[PASS] Player wins when reaching top row')
    tests.append({'name': 'Goal reaching', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Goal reaching: {e}')
    tests.append({'name': 'Goal reaching', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

# Test 8: Game reset
try:
    print('[TEST] Game reset...')
    state.score = 999
    state.game_over = True
    state.win = True
    state.player.alive = False
    state.reset()
    assert state.score == 0
    assert state.game_over == False
    assert state.win == False
    assert state.player.alive == True
    print('[PASS] Game state resets correctly')
    tests.append({'name': 'Game reset', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Game reset: {e}')
    tests.append({'name': 'Game reset', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

# Test 9: Extended runtime
try:
    print('[TEST] Extended runtime (60 seconds simulation)...')
    state.reset()
    for i in range(1800):
        state.update(1.0/30.0)
    print('[PASS] Application runs for extended duration without crashing')
    tests.append({'name': 'Extended runtime', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Extended runtime: {e}')
    tests.append({'name': 'Extended runtime', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

# Test 10: Rendering works
try:
    print('[TEST] Rendering...')
    renderer.render()
    print('[PASS] Rendering executes without errors')
    tests.append({'name': 'Rendering', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Rendering: {e}')
    tests.append({'name': 'Rendering', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

# Test 11: Full game cycle simulation
try:
    print('[TEST] Full game cycle simulation...')
    state.reset()
    for _ in range(3):
        state.move('up')
        state.update(0.1)
    state.reset()
    assert state.score == 0
    assert state.game_over == False
    print('[PASS] Full game cycle completes successfully')
    tests.append({'name': 'Full game cycle', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Full game cycle: {e}')
    tests.append({'name': 'Full game cycle', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

# Test 12: Score tracking
try:
    print('[TEST] Score tracking...')
    state.reset()
    for _ in range(9):
        state.move('up')
    state.update(0.1)
    assert state.score >= 100
    print('[PASS] Score tracking works correctly')
    tests.append({'name': 'Score tracking', 'status': 'PASSED'})
except Exception as e:
    print(f'[FAIL] Score tracking: {e}')
    tests.append({'name': 'Score tracking', 'status': 'FAILED', 'error': str(e)})
    all_passed = False

end_time = time.time()
duration = end_time - start_time

pygame.quit()

# Summary
print('')
print('=' * 60)
print('RUNTIME ANALYSIS SUMMARY')
print('=' * 60)
print(f'Total duration: {duration:.2f} seconds')
print(f'Tests executed: {len(tests)}')
passed = sum(1 for t in tests if t['status'] == 'PASSED')
failed = sum(1 for t in tests if t['status'] == 'FAILED')
print(f'Tests passed: {passed}')
print(f'Tests failed: {failed}')
print('=' * 60)

sys.exit(0 if all_passed else 1)
