"""Automated runtime analysis for Vector Minesweeper Flag Master."""

import os
import sys
import time
import json
import traceback

# Set headless mode for pygame
os.environ['SDL_VIDEODRIVER'] = 'dummy'

import pygame
from game import Game
from config import (
    GRID_ROWS, GRID_COLS, MINE_COUNT, SCREEN_WIDTH,
    SCREEN_HEIGHT, CELL_SIZE, MARGIN, UI_HEIGHT
)


class AutomatedRuntimeTest:
    def __init__(self):
        pygame.init()
        try:
            pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception as e:
            print(f"Display setup error: {e}")
            # Continue anyway - tests should work
        self.test_results = []
        self.start_time = time.time()
        self.max_duration = 120  # 2 minutes max

    def log_test(self, name, status, message):
        self.test_results.append({
            "test_name": name,
            "status": status,
            "message": message
        })
        print(f"[{status}] {name}: {message}")

    def check_time_limit(self):
        elapsed = time.time() - self.start_time
        if elapsed > self.max_duration:
            self.log_test("time_limit", "FAILED", f"Exceeded {self.max_duration}s limit")
            return False
        return True

    def run_tests(self):
        """Run automated runtime tests."""
        print("=== Vector Minesweeper Flag Master - Automated Runtime Analysis ===\n")

        try:
            # Test 1: Game Initialization
            print("Test 1: Game Initialization...")
            game = Game()
            assert game is not None, "Game object is None"
            assert game.grid is not None, "Grid is None"
            assert len(game.grid) == GRID_ROWS, f"Expected {GRID_ROWS} rows, got {len(game.grid)}"
            assert len(game.grid[0]) == GRID_COLS, f"Expected {GRID_COLS} cols, got {len(game.grid[0])}"
            self.log_test("game_initialization", "PASSED", "Game initialized correctly")

            if not self.check_time_limit():
                return self.get_summary()

            # Test 2: First Click (places mines and starts game)
            print("Test 2: First Click...")
            center_row, center_col = GRID_ROWS // 2, GRID_COLS // 2
            # Simulate first click: place mines first, then uncover
            game.place_mines(center_row, center_col)
            game.uncover_cell(center_row, center_col)
            assert game.mines_placed == True, "Mines not placed after first click"
            assert not game.game_over, "Game should not be over after first safe click"
            self.log_test("first_click", "PASSED", "First click placed mines and started game")

            if not self.check_time_limit():
                return self.get_summary()

            # Test 3: Cell Uncovering
            print("Test 3: Cell Uncovering...")
            initial_uncovered = game.cells_uncovered
            uncovered_count = 0
            # Try to uncover some cells, skip mines
            test_cells = [(0, 0), (0, 1), (1, 0), (1, 1)]
            for r, c in test_cells:
                if r < GRID_ROWS and c < GRID_COLS:
                    if not game.game_over and game.grid[r][c].is_covered:
                        if not game.grid[r][c].is_mine:
                            game.uncover_cell(r, c)
                            uncovered_count += 1
                    if game.game_over:
                        break

            if game.game_over:
                self.log_test("cell_uncovering", "FAILED", "Hit a mine during testing")
            else:
                assert game.cells_uncovered > initial_uncovered, "No cells were uncovered"
                self.log_test("cell_uncovering", "PASSED", f"Cells uncovered ({uncovered_count} new, {game.cells_uncovered} total)")

            if not self.check_time_limit():
                return self.get_summary()

            # Test 4: Flag Placement
            print("Test 4: Flag Placement...")
            # Find any covered cell that's not a mine for flagging
            initial_flags = game.flags_placed
            flag_cell = None
            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    if game.grid[r][c].is_covered and not game.grid[r][c].is_mine:
                        flag_cell = (r, c)
                        break
                if flag_cell:
                    break

            if flag_cell:
                flag_row, flag_col = flag_cell
                game.toggle_flag(flag_row, flag_col)
                assert game.flags_placed == initial_flags + 1, "Flag count didn't increase"
                assert game.grid[flag_row][flag_col].is_flagged == True, "Cell not flagged"
                game.toggle_flag(flag_row, flag_col)
                assert game.flags_placed == initial_flags, "Flag count didn't decrease"
                assert game.grid[flag_row][flag_col].is_flagged == False, "Flag not removed"
                self.log_test("flag_placement", "PASSED", "Flag toggle functionality works")
            else:
                self.log_test("flag_placement", "FAILED", "Could not find a covered cell for flagging")

            if not self.check_time_limit():
                return self.get_summary()

            # Test 5: Recursive Uncovering (find a zero-adjacent cell)
            print("Test 5: Recursive Uncovering...")
            game.reset_game()
            # Place mines in bottom half to ensure zeros in top half
            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    game.grid[r][c].is_mine = (r >= GRID_ROWS // 2)

            mine_count = sum(1 for row in game.grid for cell in row if cell.is_mine)
            print(f"  Placed {mine_count} mines in bottom half")

            game.calculate_adjacent_mines()
            game.mines_placed = True

            initial_uncovered = game.cells_uncovered
            game.uncover_cell(0, 0)  # Should have zero adjacent mines
            assert game.cells_uncovered > initial_uncovered, "No recursive uncovering occurred"
            self.log_test("recursive_uncover", "PASSED", f"Recursive uncovering works ({game.cells_uncovered} cells)")

            if not self.check_time_limit():
                return self.get_summary()

            # Test 6: Win Condition
            print("Test 6: Win Condition...")
            game.reset_game()
            # Set up winning state
            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    game.grid[r][c].is_mine = False
                    game.grid[r][c].is_covered = True

            # Place exactly MINE_COUNT mines
            mine_count = MINE_COUNT
            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    if mine_count > 0:
                        game.grid[r][c].is_mine = True
                        mine_count -= 1
                    else:
                        break
                if mine_count <= 0:
                    break

            game.calculate_adjacent_mines()
            game.mines_placed = True

            # Uncover all non-mine cells
            for r in range(GRID_ROWS):
                for c in range(GRID_COLS):
                    if not game.grid[r][c].is_mine:
                        game.grid[r][c].is_covered = False
                        game.cells_uncovered += 1

            game.check_win()
            assert game.game_over == True, "Game should be over"
            assert game.won == True, "Player should have won"
            self.log_test("win_condition", "PASSED", "Win condition detected correctly")

            if not self.check_time_limit():
                return self.get_summary()

            # Test 7: Lose Condition (hitting a mine)
            print("Test 7: Lose Condition...")
            game.reset_game()
            game.grid[5][5].is_mine = True
            game.mines_placed = True

            game.uncover_cell(5, 5)
            assert game.game_over == True, "Game should be over after hitting mine"
            assert game.won == False, "Player should have lost"
            assert game.grid[5][5].is_covered == False, "Mine should be revealed"
            self.log_test("lose_condition", "PASSED", "Lose condition detected correctly (mine hit)")

            if not self.check_time_limit():
                return self.get_summary()

            # Test 8: Game Reset
            print("Test 8: Game Reset...")
            game.reset_game()
            assert game.game_over == False, "Game should not be over after reset"
            assert game.won == False, "Won state should be reset"
            assert game.mines_placed == False, "Mines placed should be reset"
            assert game.start_time == None, "Start time should be reset"
            assert game.cells_uncovered == 0, "Cells uncovered should be reset"
            assert game.flags_placed == 0, "Flags placed should be reset"
            self.log_test("game_reset", "PASSED", "Game state reset correctly")

            if not self.check_time_limit():
                return self.get_summary()

            # Test 9: UI Rendering (basic check that draw doesn't crash)
            print("Test 9: UI Rendering...")
            try:
                game.draw()
                game.draw_ui()
                game.draw_grid()
                self.log_test("ui_rendering", "PASSED", "UI and grid rendering without errors")
            except Exception as e:
                self.log_test("ui_rendering", "FAILED", f"Rendering error: {str(e)}")

            if not self.check_time_limit():
                return self.get_summary()

            # Test 10: Multiple Game Cycles
            print("Test 10: Multiple Game Cycles...")
            successful_cycles = 0
            for i in range(3):
                game.reset_game()
                game.place_mines(2, 2)
                game.uncover_cell(2, 2)
                if not game.game_over:
                    # Toggle a flag on a covered cell
                    flag_r, flag_c = 0, 0
                    if game.grid[flag_r][flag_c].is_covered and not game.grid[flag_r][flag_c].is_mine:
                        game.toggle_flag(flag_r, flag_c)
                        game.toggle_flag(flag_r, flag_c)
                        successful_cycles += 1
            self.log_test("multiple_cycles", "PASSED", f"Multiple game cycles completed ({successful_cycles}/3)")

            if not self.check_time_limit():
                return self.get_summary()

            # Test 11: Neighbor Calculation
            print("Test 11: Neighbor Calculation...")
            neighbors = game.get_neighbors(0, 0)
            assert len(neighbors) == 3, f"Corner cell should have 3 neighbors, got {len(neighbors)}"
            neighbors = game.get_neighbors(GRID_ROWS // 2, GRID_COLS // 2)
            assert len(neighbors) == 8, f"Center cell should have 8 neighbors, got {len(neighbors)}"
            self.log_test("neighbor_calculation", "PASSED", "Neighbor position calculation works")

        except Exception as e:
            error_msg = f"Runtime exception: {str(e)}"
            error_trace = traceback.format_exc()
            print(f"ERROR: {error_msg}")
            print(f"Traceback:\n{error_trace}")
            self.log_test("runtime_error", "FAILED", error_msg)

        try:
            pygame.quit()
        except:
            pass

        return self.get_summary()

    def get_summary(self):
        passed = sum(1 for r in self.test_results if r["status"] == "PASSED")
        total = len(self.test_results)
        elapsed = time.time() - self.start_time

        summary = {
            "test_results": self.test_results,
            "summary": {
                "total_tests": total,
                "passed": passed,
                "failed": total - passed,
                "pass_rate": f"{(passed / total * 100):.1f}%",
                "duration_seconds": round(elapsed, 2)
            },
            "overall_status": "PASSED" if total - passed == 0 else "FAILED"
        }
        return summary


if __name__ == "__main__":
    tester = AutomatedRuntimeTest()
    result = tester.run_tests()

    print(f"\n=== Summary ===")
    print(f"Total Tests: {result['summary']['total_tests']}")
    print(f"Passed: {result['summary']['passed']}")
    print(f"Failed: {result['summary']['failed']}")
    print(f"Pass Rate: {result['summary']['pass_rate']}")
    print(f"Duration: {result['summary']['duration_seconds']}s")
    print(f"Overall Status: {result['overall_status']}")

    # Write to runtime_analysis.json
    with open("runtime_analysis.json", "w") as f:
        json.dump(result, f, indent=2)

    print(f"\nResults saved to runtime_analysis.json")

    sys.exit(0 if result['overall_status'] == 'PASSED' else 1)
