"""Pygame app with circles that bounce, wander, and magnetically repel each other. Small circles flee large circles."""

from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Optional

import pygame

gfxdraw: Optional[Any]
try:
    import pygame.gfxdraw as gfxdraw
except ImportError:
    gfxdraw = None

SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
FPS: int = 60

CIRCLE_COUNT: int = 30  # Number of circles to simulate
CIRCLE_MIN_RADIUS: int = 8   
CIRCLE_MAX_RADIUS: int = 25  

# Drastically reduced speeds so it looks smooth and readable
SPEED_MIN: int = 15        
SPEED_MAX: int = 40
GLOBAL_MAX_SPEED: float = 180.0  

COLOR_MIN: int = 50
COLOR_MAX: int = 255
JITTER_CHANCE: float = 0.05
JITTER_ANGLE_MIN: float = -0.1
JITTER_ANGLE_MAX: float = 0.1

# Magnetic repel values
MAGNETIC_RADIUS: float = 180.0  # How far away they detect each other
MAGNETIC_FORCE: float = 800.0   # How hard they push away
OVERLAP_SOLVER_PASSES: int = 8


@dataclass(slots=True)
class Circle:
    """Circle center position, velocity, and render color."""
    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    radius: int
    base_speed: float  # Normal wandering speed
    lifespan: float    # random time before it dies
    max_speed: float = GLOBAL_MAX_SPEED
    age: float = 0.0   # keeps track of how long it's been alive


def create_random_circle() -> Circle:
    """Create one circle at a random position with random velocity."""
    radius = random.randint(CIRCLE_MIN_RADIUS, CIRCLE_MAX_RADIUS)

    # Make sure they spawn fully inside the screen
    x = random.randint(radius, SCREEN_WIDTH - radius)
    y = random.randint(radius, SCREEN_HEIGHT - radius)

    start_speed_x = random.randint(SPEED_MIN, SPEED_MAX)
    start_speed_y = random.randint(SPEED_MIN, SPEED_MAX)

    vx = random.choice([-1, 1]) * float(start_speed_x)
    vy = random.choice([-1, 1]) * float(start_speed_y)
    
    base_speed = math.hypot(vx, vy)
    
    # give it 30 to 180 secs to live
    lifespan = random.uniform(30.0, 180.0) 

    color = (
        random.randint(COLOR_MIN, COLOR_MAX),
        random.randint(COLOR_MIN, COLOR_MAX),
        random.randint(COLOR_MIN, COLOR_MAX),
    )
    
    return Circle(x=x, y=y, vx=vx, vy=vy, color=color, radius=radius, base_speed=base_speed, lifespan=lifespan)


def create_circles(count: int) -> list[Circle]:
    """Create a list of random circles."""
    circles = [create_random_circle() for _ in range(count)]
    return circles


def _build_spatial_grid(circles: list[Circle], cell_size: float) -> dict[tuple[int, int], list[Circle]]:
    """partitions circles into a grid for fast neighbor lookups."""
    grid: dict[tuple[int, int], list[Circle]] = {}
    for circle in circles:
        cell = (int(circle.x // cell_size), int(circle.y // cell_size))
        if cell not in grid:
            grid[cell] = []
        grid[cell].append(circle)
    return grid


def _apply_boundary(circle: Circle) -> None:
    # Use radius to bounce off the edges correctly
    if circle.x - circle.radius <= 0:
        circle.x = circle.radius
        circle.vx *= -1
    elif circle.x + circle.radius >= SCREEN_WIDTH:
        circle.x = SCREEN_WIDTH - circle.radius
        circle.vx *= -1

    if circle.y - circle.radius <= 0:
        circle.y = circle.radius
        circle.vy *= -1
    elif circle.y + circle.radius >= SCREEN_HEIGHT:
        circle.y = SCREEN_HEIGHT - circle.radius
        circle.vy *= -1


def _clamp_position(circle: Circle) -> None:
    """Clamp a circle to screen bounds without changing velocity."""
    if circle.x - circle.radius <= 0:
        circle.x = circle.radius
    elif circle.x + circle.radius >= SCREEN_WIDTH:
        circle.x = SCREEN_WIDTH - circle.radius

    if circle.y - circle.radius <= 0:
        circle.y = circle.radius
    elif circle.y + circle.radius >= SCREEN_HEIGHT:
        circle.y = SCREEN_HEIGHT - circle.radius


def _rotate_velocity(circle: Circle, angle_radians: float) -> None:
    """Rotate a velocity vector by a small angle to create a wandering path."""
    new_vx = circle.vx * math.cos(angle_radians) - circle.vy * math.sin(angle_radians)
    new_vy = circle.vx * math.sin(angle_radians) + circle.vy * math.cos(angle_radians)
    circle.vx = new_vx
    circle.vy = new_vy


def _clamp_speed(circle: Circle) -> None:
    """Ensure the circle never exceeds its absolute maximum sprint speed."""
    speed = math.hypot(circle.vx, circle.vy)
    if speed > circle.max_speed and speed > 0:
        scale = circle.max_speed / speed
        circle.vx *= scale
        circle.vy *= scale


def apply_random_trajectory_jitter(circle: Circle, dt: float) -> None:
    """Keep movement slightly random, scaled by delta time."""
    # scaling by dt * 60 keeps it consistent with a 60fps baseline
    if random.random() < JITTER_CHANCE * (dt * 60.0):
        angle = random.uniform(JITTER_ANGLE_MIN, JITTER_ANGLE_MAX)
        _rotate_velocity(circle, angle)


def _resolve_overlaps(circles: list[Circle]) -> bool:
    """Resolve circle overlap using a spatial grid."""
    separated_any = False
    
    # safe cell size is roughly 2x the max radius for overlaps
    cell_size = float(CIRCLE_MAX_RADIUS * 2)
    grid = _build_spatial_grid(circles, cell_size)

    def move_and_clamp(circle: Circle, dx: float, dy: float) -> None:
        circle.x += dx
        circle.y += dy
        _clamp_position(circle)

    def overlap_amount(a: Circle, b: Circle) -> float:
        distance = math.hypot(a.x - b.x, a.y - b.y)
        return (a.radius + b.radius) - distance

    for circle in circles:
        cx, cy = int(circle.x // cell_size), int(circle.y // cell_size)
        
        # check circle's cell and the 8 surrounding cells
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                neighbor_cell = (cx + dx, cy + dy)
                if neighbor_cell in grid:
                    for other in grid[neighbor_cell]:
                        # only check each pair once by comparing memory addresses
                        if id(circle) >= id(other):
                            continue

                        diff_x = circle.x - other.x
                        diff_y = circle.y - other.y
                        min_distance = circle.radius + other.radius
                        distance = math.hypot(diff_x, diff_y)

                        if distance >= min_distance:
                            continue

                        if distance <= 1e-6:
                            angle = random.uniform(0.0, math.tau)
                            dir_x = math.cos(angle)
                            dir_y = math.sin(angle)
                            overlap = min_distance
                        else:
                            dir_x = diff_x / distance
                            dir_y = diff_y / distance
                            overlap = min_distance - distance

                        if circle.radius > other.radius:
                            move_and_clamp(other, -dir_x * overlap, -dir_y * overlap)
                            remaining = overlap_amount(circle, other)
                            if remaining > 0:
                                move_and_clamp(circle, dir_x * remaining, dir_y * remaining)
                        elif circle.radius < other.radius:
                            move_and_clamp(circle, dir_x * overlap, dir_y * overlap)
                            remaining = overlap_amount(circle, other)
                            if remaining > 0:
                                move_and_clamp(other, -dir_x * remaining, -dir_y * remaining)
                        else:
                            half_overlap = overlap * 0.5
                            move_and_clamp(circle, dir_x * half_overlap, dir_y * half_overlap)
                            move_and_clamp(other, -dir_x * half_overlap, -dir_y * half_overlap)
                            remaining = overlap_amount(circle, other)
                            if remaining > 0:
                                correction = remaining * 0.5
                                move_and_clamp(circle, dir_x * correction, dir_y * correction)
                                move_and_clamp(other, -dir_x * correction, -dir_y * correction)

                        separated_any = True

    return separated_any


def _stabilize_positions(circles: list[Circle]) -> None:
    """Iteratively separate overlaps and re-clamp to the screen bounds."""
    for _ in range(OVERLAP_SOLVER_PASSES):
        changed = _resolve_overlaps(circles)
        for circle in circles:
            _apply_boundary(circle)
        if not changed:
            break


def apply_magnetic_repel(circles: list[Circle], dt: float) -> None:
    """Make smaller circles flee from larger ones using a spatial grid."""
    if len(circles) < 2:
        return

    grid = _build_spatial_grid(circles, MAGNETIC_RADIUS)
    check_radius_sq = MAGNETIC_RADIUS * MAGNETIC_RADIUS
    
    # Map circle id to accumulated force components
    force_x = {id(c): 0.0 for c in circles}
    force_y = {id(c): 0.0 for c in circles}
    is_repelled = {id(c): False for c in circles}

    for circle in circles:
        cx, cy = int(circle.x // MAGNETIC_RADIUS), int(circle.y // MAGNETIC_RADIUS)
        
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                neighbor_cell = (cx + dx, cy + dy)
                if neighbor_cell in grid:
                    for other in grid[neighbor_cell]:
                        if circle is other:
                            continue

                        diff_x = circle.x - other.x
                        diff_y = circle.y - other.y
                        distance_sq = diff_x * diff_x + diff_y * diff_y

                        if distance_sq > check_radius_sq or distance_sq <= 1e-12:
                            continue

                        distance = math.sqrt(distance_sq)
                        proximity = 1.0 - (distance / MAGNETIC_RADIUS)
                        if proximity <= 0:
                            continue

                        dir_x = diff_x / distance
                        dir_y = diff_y / distance
                        strength = (proximity ** 2) * MAGNETIC_FORCE

                        # Apply repel force based on size relationship
                        if circle.radius <= other.radius:
                            force_multiplier = 2.0 if circle.radius < other.radius else 1.0
                            force_x[id(circle)] += dir_x * strength * force_multiplier
                            force_y[id(circle)] += dir_y * strength * force_multiplier
                            is_repelled[id(circle)] = True

    for circle in circles:
        cid = id(circle)
        if is_repelled[cid]:
            circle.vx += force_x[cid] * dt
            circle.vy += force_y[cid] * dt
        else:
            current_speed = math.hypot(circle.vx, circle.vy)
            if current_speed > circle.base_speed:
                circle.vx *= 0.95
                circle.vy *= 0.95

        _clamp_speed(circle)


def lifecycle_system(circles: list[Circle], dt: float) -> None:
    """Handle aging and rebirth of circles."""
    for i in range(len(circles)):
        circles[i].age += dt
        if circles[i].age >= circles[i].lifespan:
            # Replace expired circle with a new one
            circles[i] = create_random_circle()


def force_system(circles: list[Circle], dt: float) -> None:
    """calculate and apply continuous forces like magnetism."""
    apply_magnetic_repel(circles, dt)


def motion_system(circles: list[Circle], dt: float) -> None:
    """integrate velocity, handle overlap physics, and enforce boundaries."""
    _stabilize_positions(circles)

    for circle in circles:
        circle.x += circle.vx * dt 
        circle.y += circle.vy * dt
        apply_random_trajectory_jitter(circle, dt)
        _apply_boundary(circle)

    _stabilize_positions(circles)


def update_circles(circles: list[Circle], dt: float) -> None:
    """orchestrate all systems per frame."""
    lifecycle_system(circles, dt)
    force_system(circles, dt)
    motion_system(circles, dt)


def draw_background(screen: pygame.Surface) -> None:
    """Render a plain black background."""
    screen.fill((0, 0, 0))


def draw_circle(screen: pygame.Surface, circle: Circle) -> None:
    """Draw one smooth anti-aliased colored circle."""
    x, y = int(circle.x), int(circle.y)
    if gfxdraw is None:
        pygame.draw.circle(screen, circle.color, (x, y), circle.radius)
        return

    gfxdraw.aacircle(screen, x, y, circle.radius, circle.color)
    gfxdraw.filled_circle(screen, x, y, circle.radius, circle.color)


def draw_circles(screen: pygame.Surface, circles: list[Circle]) -> None:
    """Draw all circles to the screen."""
    for circle in circles:
        draw_circle(screen, circle)


def run() -> None:
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hierarchical Magnetic Circles")
    clock = pygame.time.Clock()

    pygame.font.init()
    fps_font = pygame.font.SysFont("Arial", 24, bold=True)

    circles = create_circles(CIRCLE_COUNT)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        dt = clock.tick(FPS) / 1000.0

        update_circles(circles, dt)
        
        draw_background(screen)
        draw_circles(screen, circles)

        current_fps = clock.get_fps()
        fps_surface = fps_font.render(f"FPS: {int(current_fps)}", True, (0, 255, 0)) 
        screen.blit(fps_surface, (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()