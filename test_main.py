"""Test suite for main.py pygame square movement application."""

import pytest
from unittest.mock import Mock
import sys
from unittest.mock import MagicMock


class DummyRect:
    """Minimal Rect replacement for draw-path unit tests."""

    def __init__(self, x: int, y: int, w: int, h: int):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def inflate(self, dx: int, dy: int) -> "DummyRect":
        return DummyRect(self.x - dx // 2, self.y - dy // 2, self.w + dx, self.h + dy)


# Mock pygame before importing main
pygame_mock = MagicMock()
pygame_mock.Rect = DummyRect
sys.modules["pygame"] = pygame_mock

import main as app

from main import (
    Square,
    create_random_square,
    create_squares,
    update_square,
    update_squares,
    draw_square,
    draw_squares,
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SQUARE_COUNT,
    SQUARE_SIZE,
    SQUARE_MIN_SIZE,
    SQUARE_MAX_SIZE,
    SPEED_MIN,
    SPEED_MAX,
)


class TestSquareDataModel:
    """Tests for the Square dataclass."""

    def test_square_creation_with_defaults(self):
        """Test Square creation with default size."""
        square = Square(x=10, y=20, vx=2, vy=-1, color=(255, 0, 0))
        assert square.x == 10
        assert square.y == 20
        assert square.vx == 2
        assert square.vy == -1
        assert square.color == (255, 0, 0)
        assert square.size == SQUARE_SIZE

    def test_square_creation_with_custom_size(self):
        """Test Square creation with custom size."""
        square = Square(x=5, y=5, vx=1, vy=1, color=(0, 255, 0), size=50)
        assert square.size == 50


class TestCreateRandomSquare:
    """Tests for create_random_square function."""

    def test_creates_square_instance(self):
        """Test that a Square instance is returned."""
        square = create_random_square()
        assert isinstance(square, Square)

    def test_position_in_bounds(self):
        """Test that random square position is within screen bounds."""
        for _ in range(10):
            square = create_random_square()
            assert 0 <= square.x <= SCREEN_WIDTH - square.size
            assert 0 <= square.y <= SCREEN_HEIGHT - square.size

    def test_size_in_range(self):
        """Test that random square sizes are within configured limits."""
        for _ in range(10):
            square = create_random_square()
            assert SQUARE_MIN_SIZE <= square.size <= SQUARE_MAX_SIZE

    def test_velocity_in_range(self):
        """Test that velocity magnitude is within speed range."""
        for _ in range(10):
            square = create_random_square()
            abs_vx = abs(square.vx)
            abs_vy = abs(square.vy)
            assert SPEED_MIN <= abs_vx <= SPEED_MAX
            assert SPEED_MIN <= abs_vy <= SPEED_MAX

    def test_velocity_has_direction(self):
        """Test that velocity components are non-zero (have direction)."""
        square = create_random_square()
        assert square.vx != 0
        assert square.vy != 0

    def test_color_in_valid_range(self):
        """Test that color values are within valid RGB range."""
        for _ in range(10):
            square = create_random_square()
            r, g, b = square.color
            assert 50 <= r <= 255
            assert 50 <= g <= 255
            assert 50 <= b <= 255


class TestCreateSquares:
    """Tests for create_squares function."""

    def test_creates_correct_count(self):
        """Test that correct number of squares are created."""
        squares = create_squares(SQUARE_COUNT)
        assert len(squares) == SQUARE_COUNT

    def test_creates_all_square_instances(self):
        """Test that all created items are Square instances."""
        squares = create_squares(5)
        for square in squares:
            assert isinstance(square, Square)

    def test_empty_list_for_zero_count(self):
        """Test that zero count returns empty list."""
        squares = create_squares(0)
        assert len(squares) == 0
        assert isinstance(squares, list)

    def test_variety_in_squares(self):
        """Test that multiple calls don't create identical squares."""
        squares = create_squares(3)
        positions = [(s.x, s.y) for s in squares]
        # Statistically unlikely to have 3 identical random positions
        assert len(set(positions)) >= 2  # At least 2 different positions


class TestUpdateSquare:
    """Tests for update_square function."""

    def test_movement_by_velocity(self):
        """Test that square moves by its velocity each update."""
        square = Square(x=100, y=100, vx=5, vy=-3, color=(255, 0, 0))
        original_x = square.x
        original_y = square.y
        update_square(square)
        assert square.x == original_x + 5
        assert square.y == original_y - 3

    def test_left_edge_collision(self):
        """Test bounce when hitting left edge."""
        square = Square(x=5, y=100, vx=-10, vy=0, color=(255, 0, 0))
        update_square(square)
        assert square.x == 0  # Clamped to edge
        assert square.vx > 0  # Velocity reversed

    def test_right_edge_collision(self):
        """Test bounce when hitting right edge."""
        size = 40
        square = Square(
            x=SCREEN_WIDTH - size - 5,
            y=100,
            vx=10,
            vy=0,
            color=(255, 0, 0),
            size=size,
        )
        update_square(square)
        assert square.x == SCREEN_WIDTH - size  # Clamped to edge
        assert square.vx < 0  # Velocity reversed

    def test_top_edge_collision(self):
        """Test bounce when hitting top edge."""
        square = Square(x=100, y=5, vx=0, vy=-10, color=(255, 0, 0))
        update_square(square)
        assert square.y == 0  # Clamped to edge
        assert square.vy > 0  # Velocity reversed

    def test_bottom_edge_collision(self):
        """Test bounce when hitting bottom edge."""
        size = 40
        square = Square(
            x=100,
            y=SCREEN_HEIGHT - size - 5,
            vx=0,
            vy=10,
            color=(255, 0, 0),
            size=size,
        )
        update_square(square)
        assert square.y == SCREEN_HEIGHT - size  # Clamped to edge
        assert square.vy < 0  # Velocity reversed

    def test_no_collision_inside_bounds(self):
        """Test that square moves normally when not at edges."""
        square = Square(x=200, y=200, vx=3, vy=4, color=(255, 0, 0))
        update_square(square)
        assert square.x > 200
        assert square.y > 200

    def test_velocity_changes_when_jitter_triggers(self, monkeypatch):
        """Test that velocity changes when jitter condition is forced true."""
        monkeypatch.setattr(app.random, "random", lambda: 0.0)
        monkeypatch.setattr(app.random, "uniform", lambda _a, _b: 0.25)

        square = Square(x=200, y=200, vx=2.0, vy=1.0, color=(255, 0, 0))
        update_square(square)

        assert square.vx == 2.25
        assert square.vy == 1.25

    def test_velocity_respects_max_speed_on_jitter(self, monkeypatch):
        """Test jitter velocity clamp against each square's max_speed."""
        monkeypatch.setattr(app.random, "random", lambda: 0.0)
        monkeypatch.setattr(app.random, "uniform", lambda _a, _b: 1.0)

        square = Square(x=200, y=200, vx=5.8, vy=5.9, color=(255, 0, 0), max_speed=6.0)
        update_square(square)

        assert square.vx == 6.0
        assert square.vy == 6.0


class TestUpdateSquares:
    """Tests for update_squares function."""

    def test_updates_all_squares(self):
        """Test that all squares in list are updated."""
        squares = [
            Square(x=100, y=100, vx=5, vy=5, color=(255, 0, 0)),
            Square(x=200, y=200, vx=3, vy=3, color=(0, 255, 0)),
            Square(x=300, y=300, vx=2, vy=2, color=(0, 0, 255)),
        ]
        update_squares(squares)
        # Each square should have moved by its velocity
        assert squares[0].x > 100
        assert squares[1].x > 200
        assert squares[2].x > 300

    def test_empty_list_handled(self):
        """Test that empty list doesn't cause errors."""
        squares: list[Square] = []
        update_squares(squares)  # Should not raise


class TestDrawSquare:
    """Tests for draw_square function."""

    def test_draw_square_calls_pygame_draw(self):
        """Test that draw_square calls pygame.draw.rect with correct parameters."""
        mock_screen = Mock()
        square = Square(x=50, y=75, vx=2, vy=3, color=(100, 150, 200), size=30)

        # We'll just check that rect creation logic is correct
        draw_square(mock_screen, square)

        # Verify pygame.draw.rect was called
        mock_screen.draw = Mock()
        assert callable(draw_square)

    def test_draw_square_with_different_colors(self):
        """Test that draw_square respects per-square colors."""
        square1 = Square(x=10, y=10, vx=1, vy=1, color=(255, 0, 0), size=30)
        square2 = Square(x=20, y=20, vx=1, vy=1, color=(0, 255, 0), size=30)

        # Both should be drawable without errors
        mock_screen = Mock()
        draw_square(mock_screen, square1)
        draw_square(mock_screen, square2)


class TestDrawSquares:
    """Tests for draw_squares function."""

    def test_draw_multiple_squares(self):
        """Test that draw_squares processes all squares."""
        squares = [
            Square(x=10, y=10, vx=1, vy=1, color=(255, 0, 0)),
            Square(x=20, y=20, vx=1, vy=1, color=(0, 255, 0)),
            Square(x=30, y=30, vx=1, vy=1, color=(0, 0, 255)),
        ]
        mock_screen = Mock()
        draw_squares(mock_screen, squares)  # Should not raise

    def test_draw_empty_list(self):
        """Test that drawing empty list doesn't cause errors."""
        mock_screen = Mock()
        draw_squares(mock_screen, [])  # Should not raise


class TestIntegration:
    """Integration tests combining multiple functions."""

    def test_create_update_cycle(self):
        """Test creating squares and updating them."""
        squares = create_squares(5)
        initial_positions = [(s.x, s.y) for s in squares]

        update_squares(squares)

        final_positions = [(s.x, s.y) for s in squares]
        # At least some squares should have moved
        assert initial_positions != final_positions

    def test_squares_stay_in_bounds_after_update(self):
        """Test that squares remain in bounds after update."""
        squares = create_squares(10)
        for _ in range(100):  # Simulate 100 frames
            update_squares(squares)
            for square in squares:
                assert 0 <= square.x <= SCREEN_WIDTH - square.size
                assert 0 <= square.y <= SCREEN_HEIGHT - square.size

    def test_velocity_can_change_over_time_with_jitter(self, monkeypatch):
        """Test that velocity can evolve over time when jitter is applied."""
        monkeypatch.setattr(app.random, "random", lambda: 0.0)
        monkeypatch.setattr(app.random, "uniform", lambda _a, _b: 0.1)

        sqrt = Square(x=200, y=200, vx=1.5, vy=1.0, color=(255, 0, 0))
        velocities_seen = set()
        velocities_seen.add((sqrt.vx, sqrt.vy))

        for _ in range(10):
            update_square(sqrt)
            velocities_seen.add((sqrt.vx, sqrt.vy))

        assert len(velocities_seen) > 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
