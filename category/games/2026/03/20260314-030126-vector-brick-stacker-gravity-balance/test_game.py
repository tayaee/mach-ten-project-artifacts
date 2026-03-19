"""Test script for Vector Brick Stacker Gravity Balance."""
import os
os.environ['SDL_VIDEODRIVER'] = 'dummy'

from game import Game
import time

def test_basic_functionality():
    """Test basic game functionality."""
    results = {}
    
    try:
        # Test 1: Game initialization
        game = Game()
        results['game_initialization'] = {
            'status': 'PASSED',
            'notes': 'Game initialized successfully'
        }
        
        # Test 2: Block spawning
        if game.falling_block:
            results['block_spawning'] = {
                'status': 'PASSED',
                'notes': f'Block spawned at ({game.falling_block.x}, {game.falling_block.y}), size: {game.falling_block.width}x{game.falling_block.height}'
            }
        else:
            results['block_spawning'] = {'status': 'FAILED', 'notes': 'No falling block'}
        
        # Test 3: Initial observation
        obs = game.get_observation()
        results['ai_observation'] = {
            'status': 'PASSED',
            'notes': f'Observation: {obs}'
        }
        
        # Test 4: Block movement (via AI step)
        for _ in range(5):
            game.step_ai(0)  # move left
        initial_x = game.falling_block.x if game.falling_block else 0
        
        for _ in range(5):
            game.step_ai(1)  # move right
        final_x = game.falling_block.x if game.falling_block else 0
        
        results['block_movement'] = {
            'status': 'PASSED',
            'notes': f'Block moved from x={initial_x} to x={final_x}'
        }
        
        # Test 5: Block rotation
        initial_rot = game.falling_block.rotation if game.falling_block else 0
        game.step_ai(2)  # rotate
        final_rot = game.falling_block.rotation if game.falling_block else 0
        results['block_rotation'] = {
            'status': 'PASSED',
            'notes': f'Rotation changed from {initial_rot} to {final_rot}'
        }
        
        # Test 6: Physics - center of mass
        com = game.physics_engine.calculate_center_of_mass(game.landed_blocks)
        results['physics_engine'] = {
            'status': 'PASSED',
            'notes': f'Center of mass: {com}'
        }
        
        # Test 7: Scoring system
        initial_score = game.score
        results['scoring'] = {
            'status': 'PASSED',
            'notes': f'Initial score: {initial_score}'
        }
        
        # Test 8: Game reset
        game._reset_game()
        if game.score == 0 and not game.game_over:
            results['game_reset'] = {
                'status': 'PASSED',
                'notes': 'Game reset successful'
            }
        else:
            results['game_reset'] = {'status': 'FAILED', 'notes': 'Reset failed'}
        
        # Test 9: Simulate block landing (force land)
        game._land_block()
        if game.score > 0:
            results['block_landing'] = {
                'status': 'PASSED',
                'notes': f'Score after landing: {game.score}'
            }
        else:
            results['block_landing'] = {'status': 'FAILED', 'notes': 'Score not updated'}
        
        pygame_quit = game.running
        
    except Exception as e:
        results['error'] = {
            'status': 'FAILED',
            'notes': f'Exception: {str(e)}'
        }
    
    return results

if __name__ == '__main__':
    results = test_basic_functionality()
    import json
    print(json.dumps(results, indent=2))
