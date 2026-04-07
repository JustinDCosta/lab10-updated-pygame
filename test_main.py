"""Tests for circle-based movement and magnetic repel behavior in main.py."""

from __future__ import annotations

import math
import os
import random
from collections.abc import Iterator

os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame
import pytest

import main as app
from main import (
    CIRCLE_COUNT,
    CIRCLE_MAX_RADIUS,
    CIRCLE_MIN_RADIUS,
    COLOR_MAX,
    COLOR_MIN,
    GLOBAL_MAX_SPEED,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    Circle,
    apply_magnetic_repel,
    create_circles,
    create_random_circle,
    draw_circle,
    draw_circles,
    update_circle,
    update_circles,
)


@pytest.fixture(scope="module", autouse=True)
def init_pygame() -> Iterator[None]:
    """Initialize pygame once for draw tests using a headless video driver."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture(autouse=True)
def disable_jitter_by_default(monkeypatch):
    """Keep updates deterministic unless a test explicitly enables jitter."""
    monkeypatch.setattr(app.random, "random", lambda: 1.0)


class TestCircleModel:
    def test_circle_creation(self):
        circle = Circle(x=10, y=20, vx=3, vy=-4, color=(10, 20, 30), radius=14, base_speed=5.0)
        assert circle.x == 10
        assert circle.y == 20
        assert circle.vx == 3
        assert circle.vy == -4
        assert circle.color == (10, 20, 30)
        assert circle.radius == 14
        assert circle.base_speed == 5.0
        assert circle.max_speed == GLOBAL_MAX_SPEED


class TestCreation:
    def test_create_random_circle_stays_in_bounds(self):
        for _ in range(40):
            circle = create_random_circle()
            assert circle.radius >= CIRCLE_MIN_RADIUS
            assert circle.radius <= CIRCLE_MAX_RADIUS
            assert circle.radius <= circle.x <= SCREEN_WIDTH - circle.radius
            assert circle.radius <= circle.y <= SCREEN_HEIGHT - circle.radius

    def test_create_random_circle_color_range(self):
        for _ in range(20):
            circle = create_random_circle()
            r, g, b = circle.color
            assert COLOR_MIN <= r <= COLOR_MAX
            assert COLOR_MIN <= g <= COLOR_MAX
            assert COLOR_MIN <= b <= COLOR_MAX

    def test_create_circles_count(self):
        circles = create_circles(CIRCLE_COUNT)
        assert len(circles) == CIRCLE_COUNT
        assert all(isinstance(circle, Circle) for circle in circles)


class TestUpdateSingleCircle:
    def test_update_circle_uses_dt(self):
        circle = Circle(x=100, y=100, vx=10, vy=-6, color=(255, 0, 0), radius=10, base_speed=11.66)
        update_circle(circle, dt=0.5)
        assert circle.x == pytest.approx(105.0)
        assert circle.y == pytest.approx(97.0)

    def test_bounce_left_boundary(self):
        circle = Circle(x=9, y=200, vx=-15, vy=0, color=(255, 0, 0), radius=10, base_speed=15)
        update_circle(circle, dt=1.0)
        assert circle.x == 10
        assert circle.vx > 0

    def test_bounce_right_boundary(self):
        circle = Circle(
            x=SCREEN_WIDTH - 11,
            y=200,
            vx=15,
            vy=0,
            color=(255, 0, 0),
            radius=10,
            base_speed=15,
        )
        update_circle(circle, dt=1.0)
        assert circle.x == SCREEN_WIDTH - 10
        assert circle.vx < 0

    def test_bounce_top_and_bottom_boundaries(self):
        top = Circle(x=200, y=9, vx=0, vy=-8, color=(255, 0, 0), radius=10, base_speed=8)
        bottom = Circle(
            x=200,
            y=SCREEN_HEIGHT - 9,
            vx=0,
            vy=8,
            color=(255, 0, 0),
            radius=10,
            base_speed=8,
        )

        update_circle(top, dt=1.0)
        update_circle(bottom, dt=1.0)

        assert top.y == 10
        assert top.vy > 0
        assert bottom.y == SCREEN_HEIGHT - 10
        assert bottom.vy < 0

    def test_jitter_rotates_velocity_without_speed_loss(self, monkeypatch):
        monkeypatch.setattr(app.random, "random", lambda: 0.0)
        monkeypatch.setattr(app.random, "uniform", lambda _a, _b: 0.2)

        circle = Circle(x=100, y=100, vx=3.0, vy=4.0, color=(0, 255, 0), radius=10, base_speed=5.0)
        before = math.hypot(circle.vx, circle.vy)

        update_circle(circle, dt=1.0)
        after = math.hypot(circle.vx, circle.vy)

        assert after == pytest.approx(before, rel=1e-6)


class TestMagneticRepel:
    def test_small_circle_flees_large_circle(self):
        small = Circle(x=180, y=100, vx=0, vy=0, color=(255, 0, 0), radius=10, base_speed=0, max_speed=100)
        large = Circle(x=120, y=100, vx=0, vy=0, color=(0, 255, 0), radius=24, base_speed=0, max_speed=100)

        apply_magnetic_repel([small, large], dt=1 / 60)

        assert small.vx > 0

    def test_large_circle_ignores_smaller_threat(self):
        small = Circle(x=180, y=100, vx=0, vy=0, color=(255, 0, 0), radius=10, base_speed=0, max_speed=100)
        large = Circle(x=120, y=100, vx=0, vy=0, color=(0, 255, 0), radius=24, base_speed=0, max_speed=100)

        apply_magnetic_repel([small, large], dt=1 / 60)

        assert large.vx == 0
        assert large.vy == 0

    def test_speed_is_clamped_after_repel(self):
        small = Circle(x=180, y=100, vx=49, vy=0, color=(255, 0, 0), radius=10, base_speed=0, max_speed=50)
        large = Circle(x=120, y=100, vx=0, vy=0, color=(0, 255, 0), radius=30, base_speed=0, max_speed=80)

        apply_magnetic_repel([small, large], dt=1.0)

        assert math.hypot(small.vx, small.vy) <= 50.0 + 1e-6


class TestOverlapSolver:
    def test_overlap_solver_separates_pair(self):
        a = Circle(x=100, y=100, vx=0, vy=0, color=(255, 0, 0), radius=20, base_speed=0)
        b = Circle(x=112, y=100, vx=0, vy=0, color=(0, 255, 0), radius=20, base_speed=0)

        changed = app._resolve_overlaps([a, b])

        distance = math.hypot(a.x - b.x, a.y - b.y)
        assert changed
        assert distance >= 40.0 - 1e-6


class TestUpdateIntegration:
    def test_update_circles_moves_items(self):
        circles = create_circles(6)
        before = [(circle.x, circle.y) for circle in circles]

        update_circles(circles, dt=1 / 60)

        after = [(circle.x, circle.y) for circle in circles]
        assert before != after

    def test_update_keeps_circles_in_bounds(self):
        random.seed(8)
        circles = create_circles(20)

        for _ in range(360):
            update_circles(circles, dt=1 / 60)
            for circle in circles:
                assert circle.radius <= circle.x <= SCREEN_WIDTH - circle.radius
                assert circle.radius <= circle.y <= SCREEN_HEIGHT - circle.radius

    def test_long_run_overlap_is_limited(self):
        random.seed(21)
        circles = create_circles(20)
        worst_overlap = 0.0

        for _ in range(360):
            update_circles(circles, dt=1 / 60)
            for i, a in enumerate(circles):
                for b in circles[i + 1 :]:
                    distance = math.hypot(a.x - b.x, a.y - b.y)
                    min_distance = a.radius + b.radius
                    if distance < min_distance:
                        worst_overlap = max(worst_overlap, min_distance - distance)

        assert worst_overlap <= 1e-3


class TestDrawing:
    def test_draw_circle_runs(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        circle = Circle(x=100, y=120, vx=0, vy=0, color=(120, 220, 180), radius=12, base_speed=0)
        draw_circle(screen, circle)

    def test_draw_circles_runs(self):
        screen = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        circles = create_circles(5)
        draw_circles(screen, circles)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
