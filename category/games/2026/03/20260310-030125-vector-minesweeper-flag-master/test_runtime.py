"""Runtime analysis test script for Vector Minesweeper Flag Master."""

import sys
import os

# Mock pygame to allow headless testing
class MockPygame:
    class Vector2:
        def __init__(self, x, y):
            self.x = x
            self.y = y

    QUIT = 256
    KEYDOWN = 768
    MOUSEBUTTONDOWN = 1025
    K_ESCAPE = 27
    K_SPACE = 32

    @staticmethod
    def init():
        pass

    class Display:
        @staticmethod
        def set_mode(size):
            return MockPygame.Surface(size)

        @staticmethod
        def set_caption(title):
            pass

        @staticmethod
        def flip():
            pass

    display = Display()

    class Time:
        @staticmethod
        def Clock():
            class Clock:
                @staticmethod
                def tick(fps):
                    pass
            return Clock()

        @staticmethod
        def get_ticks():
            return 10000

    time = Time()

    class Font:
        @staticmethod
        def Font(name, size):
            class FontObj:
                def render(self, text, antialias, color):
                    class RenderedText:
                        def get_rect(self, **kwargs):
                            return MockPygame.Rect()
                    return RenderedText()

                def get_rect(self):
                    return MockPygame.Rect()
            return FontObj()

    font = Font()

    class Rect:
        def __init__(self):
            pass

    class Draw:
        @staticmethod
        def rect(surface, color, rect, width=0):
            pass

        @staticmethod
        def circle(surface, color, center, radius):
            pass

        @staticmethod
        def line(surface, color, start, end, width=1):
            pass

        @staticmethod
        def polygon(surface, color, points):
            pass

    draw = Draw()

    class Event:
        @staticmethod
        def get():
            return []

    event = Event()

    class Surface:
        def __init__(self, size):
            pass

        def set_alpha(self, alpha):
            pass

        def fill(self, color):
            pass

    @staticmethod
    def quit():
        pass

    class Mouse:
        @staticmethod
        def get_pos():
            return (200, 200)

    mouse = Mouse()


# Replace pygame with mock
sys.modules['pygame'] = MockPygame

# Import game modules after mocking
from game import Game, Cell
from config import (
    GRID_ROWS, GRID_COLS, MINE_COUNT, SCREEN_WIDTH,
    SCREEN_HEIGHT, CELL_SIZE, MARGIN, UI_HEIGHT
)


def test_cell_creation():
    """Test basic Cell creation."""
    cell = Cell(0, 0)
    assert cell.row == 0
    assert cell.col == 0
    assert cell.is_mine == False
    assert cell.is_covered == True
    assert cell.is_flagged == False
    assert cell.adjacent_mines == 0
    return "PASSED", "Cell creation works correctly"


def test_game_initialization():
    """Test Game initialization."""
    game = Game()
    assert game.grid is not None
    assert len(game.grid) == GRID_ROWS
    assert len(game.grid[0]) == GRID_COLS
    assert game.mines_placed == False
    assert game.game_over == False
    assert game.won == False
    assert game.start_time == None
    assert game.elapsed_time == 0
    assert game.flags_placed == 0
    assert game.cells_uncovered == 0
    return "PASSED", "Game initializes correctly with default state"


def test_mine_placement():
    """Test mine placement ensuring first click is safe."""
    game = Game()
    # Place mines with (0,0) as safe cell
    game.place_mines(0, 0)

    assert game.mines_placed == True

    # Count mines
    mine_count = sum(1 for row in game.grid for cell in row if cell.is_mine)
    assert mine_count == MINE_COUNT, f"Expected {MINE_COUNT} mines, got {mine_count}"

    # Verify safe cell and neighbors are safe
    assert not game.grid[0][0].is_mine, "First clicked cell should be safe"

    neighbors = game.get_neighbors(0, 0)
    for nr, nc in neighbors:
        assert not game.grid[nr][nc].is_mine, f"Neighbor ({nr},{nc}) should be safe"

    return "PASSED", f"Successfully placed {MINE_COUNT} mines avoiding first click area"


def test_adjacent_mines_calculation():
    """Test adjacent mine calculation."""
    game = Game()

    # Manually set up a simple grid
    game.reset_game()
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            game.grid[r][c].is_mine = False

    # Place mines at specific positions
    mine_positions = [(0, 0), (0, 1), (1, 0)]
    for r, c in mine_positions:
        game.grid[r][c].is_mine = True

    game.calculate_adjacent_mines()

    # Check cell (1,1) - should have 3 adjacent mines
    assert game.grid[1][1].adjacent_mines == 3, "Cell (1,1) should have 3 adjacent mines"

    # Check cell (2,2) - should have 0 adjacent mines
    assert game.grid[2][2].adjacent_mines == 0, "Cell (2,2) should have 0 adjacent mines"

    # Check cell (0,2) - should have 1 adjacent mine (only (0,1) is a neighbor)
    assert game.grid[0][2].adjacent_mines == 1, "Cell (0,2) should have 1 adjacent mine"

    return "PASSED", "Adjacent mine calculation works correctly"


def test_flag_toggle():
    """Test flag placement and removal."""
    game = Game()
    game.place_mines(5, 5)

    initial_flags = game.flags_placed

    # Place flag
    game.toggle_flag(0, 0)
    assert game.grid[0][0].is_flagged == True, "Cell should be flagged"
    assert game.flags_placed == initial_flags + 1, "Flag count should increase"

    # Remove flag
    game.toggle_flag(0, 0)
    assert game.grid[0][0].is_flagged == False, "Flag should be removed"
    assert game.flags_placed == initial_flags, "Flag count should decrease"

    # Try flagging uncovered cell (should do nothing)
    game.grid[0][0].is_covered = False
    game.toggle_flag(0, 0)
    assert game.grid[0][0].is_flagged == False, "Should not flag uncovered cell"

    return "PASSED", "Flag toggle functionality works correctly"


def test_uncover_cell():
    """Test cell uncovering including mine hitting and recursive uncover."""
    game = Game()

    # Manually set up a simple grid
    game.reset_game()
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            game.grid[r][c].is_mine = False
            game.grid[r][c].is_covered = True

    # Place one mine at (5, 5)
    game.grid[5][5].is_mine = True
    game.calculate_adjacent_mines()

    # Uncover safe cell
    game.uncover_cell(0, 0)
    assert game.grid[0][0].is_covered == False, "Cell should be uncovered"
    assert game.cells_uncovered > 0, "Cells uncovered counter should increase"

    # Try hitting a mine
    initial_uncovered = game.cells_uncovered
    game.uncover_cell(5, 5)
    assert game.game_over == True, "Game should be over after hitting mine"
    assert game.grid[5][5].is_covered == False, "Mine should be revealed"

    # Test recursion with zero-adjacent cell
    game.reset_game()
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            game.grid[r][c].is_mine = False
            game.grid[r][c].is_covered = True

    # Place mines far away to ensure zeros in corner
    for r in range(5, GRID_ROWS):
        for c in range(5, GRID_COLS):
            game.grid[r][c].is_mine = True

    game.calculate_adjacent_mines()
    initial_cells = game.cells_uncovered
    game.uncover_cell(0, 0)

    # Should recursively uncover multiple cells due to zero adjacent mines
    assert game.cells_uncovered > initial_cells, "Should recursively uncover zero-adjacent cells"

    return "PASSED", "Cell uncovering and recursion work correctly"


def test_win_condition():
    """Test win condition detection."""
    game = Game()

    # Set up a grid where all non-mine cells are uncovered
    game.reset_game()
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            game.grid[r][c].is_mine = False
            game.grid[r][c].is_covered = True

    # Place MINE_COUNT mines (as expected by check_win)
    mine_count = MINE_COUNT
    pos = 0
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if pos < mine_count:
                game.grid[r][c].is_mine = True
                pos += 1

    game.calculate_adjacent_mines()
    game.mines_placed = True  # Set this to allow uncovering

    # Uncover all non-mine cells
    for r in range(GRID_ROWS):
        for c in range(GRID_COLS):
            if not game.grid[r][c].is_mine:
                game.grid[r][c].is_covered = False
                game.cells_uncovered += 1

    game.check_win()  # Manually call check_win since we manually set cells

    safe_cells = GRID_ROWS * GRID_COLS - MINE_COUNT
    assert game.cells_uncovered == safe_cells, f"Should have {safe_cells} uncovered cells"
    assert game.game_over == True, "Game should be over"
    assert game.won == True, "Player should have won"

    return "PASSED", "Win condition detection works correctly"


def test_get_neighbors():
    """Test neighbor position calculation."""
    game = Game()

    # Corner cell (0,0)
    neighbors = game.get_neighbors(0, 0)
    assert len(neighbors) == 3, f"Corner cell should have 3 neighbors, got {len(neighbors)}"
    assert (0, 1) in neighbors, "Right neighbor should exist"
    assert (1, 0) in neighbors, "Bottom neighbor should exist"
    assert (1, 1) in neighbors, "Diagonal neighbor should exist"

    # Edge cell (0, 5)
    neighbors = game.get_neighbors(0, 5)
    assert len(neighbors) == 5, f"Edge cell should have 5 neighbors, got {len(neighbors)}"

    # Center cell (5, 5)
    neighbors = game.get_neighbors(5, 5)
    assert len(neighbors) == 8, f"Center cell should have 8 neighbors, got {len(neighbors)}"

    return "PASSED", "Neighbor calculation works correctly for all cell positions"


def test_get_cell_from_pos():
    """Test mouse position to cell coordinate conversion."""
    game = Game()
    grid_start_x = (SCREEN_WIDTH - GRID_COLS * CELL_SIZE) // 2
    grid_start_y = MARGIN + UI_HEIGHT

    # Test valid position (first cell)
    pos = (grid_start_x + CELL_SIZE // 2, grid_start_y + CELL_SIZE // 2)
    result = game.get_cell_from_pos(pos)
    assert result == (0, 0), f"Expected (0,0), got {result}"

    # Test invalid position (above grid)
    pos = (grid_start_x + 10, grid_start_y - 10)
    result = game.get_cell_from_pos(pos)
    assert result is None, "Should return None for position above grid"

    # Test invalid position (left of grid)
    pos = (grid_start_x - 10, grid_start_y + 10)
    result = game.get_cell_from_pos(pos)
    assert result is None, "Should return None for position left of grid"

    return "PASSED", "Mouse position to cell coordinate conversion works correctly"


def run_all_tests():
    """Run all runtime tests."""
    tests = [
        test_cell_creation,
        test_game_initialization,
        test_mine_placement,
        test_adjacent_mines_calculation,
        test_flag_toggle,
        test_uncover_cell,
        test_win_condition,
        test_get_neighbors,
        test_get_cell_from_pos,
    ]

    results = []

    for test in tests:
        try:
            status, message = test()
            results.append({
                "test_name": test.__name__,
                "status": status,
                "message": message
            })
            print(f"[{status}] {test.__name__}: {message}")
        except Exception as e:
            results.append({
                "test_name": test.__name__,
                "status": "FAILED",
                "message": str(e)
            })
            print(f"[FAILED] {test.__name__}: {str(e)}")

    passed = sum(1 for r in results if r["status"] == "PASSED")
    total = len(results)

    return {
        "test_results": results,
        "summary": {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{(passed / total * 100):.1f}%"
        }
    }


if __name__ == "__main__":
    print("=== Vector Minesweeper Flag Master - Runtime Analysis ===\n")
    analysis_result = run_all_tests()
    print(f"\n=== Summary ===")
    print(f"Total Tests: {analysis_result['summary']['total_tests']}")
    print(f"Passed: {analysis_result['summary']['passed']}")
    print(f"Failed: {analysis_result['summary']['failed']}")
    print(f"Pass Rate: {analysis_result['summary']['pass_rate']}")

    # Determine overall status
    overall_status = "PASSED" if analysis_result['summary']['failed'] == 0 else "FAILED"
    analysis_result['overall_status'] = overall_status
    print(f"\nOverall Status: {overall_status}")

    # Write to runtime_analysis.json
    import json
    with open("runtime_analysis.json", "w") as f:
        json.dump(analysis_result, f, indent=2)

    print(f"\nResults saved to runtime_analysis.json")
    sys.exit(0 if overall_status == "PASSED" else 1)
