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

# Circle population and size tiers used by random spawning.
CIRCLE_COUNT: int = 20 
CIRCLE_SMALL_RADIUS: int = 8
CIRCLE_MEDIUM_RADIUS: int = (CIRCLE_SMALL_RADIUS * 2)
CIRCLE_BIG_RADIUS: int = (CIRCLE_SMALL_RADIUS * 3)
CIRCLE_SIZE_OPTIONS: tuple[int, int, int] = (
    CIRCLE_SMALL_RADIUS,
    CIRCLE_MEDIUM_RADIUS,
    CIRCLE_BIG_RADIUS,
)
CIRCLE_MAX_RADIUS: int = max(CIRCLE_SIZE_OPTIONS)

# Velocity and steering caps.
SPEED_MIN: int = 15        
SPEED_MAX: int = 40
GLOBAL_MAX_SPEED: float = 180.0  

COLOR_MIN: int = 50
COLOR_MAX: int = 255
JITTER_CHANCE: float = 0.05
JITTER_ANGLE_MIN: float = -0.1
JITTER_ANGLE_MAX: float = 0.1

# Interaction tuning for repulsion/collision settling.
MAGNETIC_RADIUS: float = 180.0  
MAGNETIC_FORCE: float = 800.0   
OVERLAP_SOLVER_PASSES: int = 8
BASE_DAMPING_PER_60FPS_FRAME: float = 0.95


@dataclass(slots=True)
class Circle:
    """Represents a simulated entity with physics properties and a lifecycle."""
    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    radius: int
    base_speed: float 
    lifespan: float   
    max_speed: float = GLOBAL_MAX_SPEED
    age: float = 0.0  


def create_random_circle() -> Circle:
    """Initialize a circle with randomized bounds, velocities, and lifespan."""
    # Pick one of the explicit default size tiers instead of an arbitrary radius.
    radius = random.choice(CIRCLE_SIZE_OPTIONS)

    # Spawn within screen bounds
    x = random.randint(radius, SCREEN_WIDTH - radius)
    y = random.randint(radius, SCREEN_HEIGHT - radius)

    start_speed_x = random.randint(SPEED_MIN, SPEED_MAX)
    start_speed_y = random.randint(SPEED_MIN, SPEED_MAX)

    vx = random.choice([-1, 1]) * float(start_speed_x)
    vy = random.choice([-1, 1]) * float(start_speed_y)
    
    base_speed = math.hypot(vx, vy)
    lifespan = random.uniform(30.0, 180.0) 

    color = (
        random.randint(COLOR_MIN, COLOR_MAX),
        random.randint(COLOR_MIN, COLOR_MAX),
        random.randint(COLOR_MIN, COLOR_MAX),
    )
    
    return Circle(x=x, y=y, vx=vx, vy=vy, color=color, radius=radius, base_speed=base_speed, lifespan=lifespan)


def create_circles(count: int) -> list[Circle]:
    """Generate the initial list of circle entities."""
    return [create_random_circle() for _ in range(count)]


def _build_spatial_grid(circles: list[Circle], cell_size: float) -> dict[tuple[int, int], list[Circle]]:
    """Partition circles into a spatial hash grid for O(1) local neighbor lookups."""
    grid: dict[tuple[int, int], list[Circle]] = {}
    for circle in circles:
        cell = (int(circle.x // cell_size), int(circle.y // cell_size))
        if cell not in grid:
            grid[cell] = []
        grid[cell].append(circle)
    return grid


def _apply_boundary(circle: Circle) -> None:
    """Clamp positions to screen edges and invert velocity only if heading out of bounds."""
    if circle.x - circle.radius <= 0:
        circle.x = circle.radius
        if circle.vx < 0:  
            circle.vx *= -1
    elif circle.x + circle.radius >= SCREEN_WIDTH:
        circle.x = SCREEN_WIDTH - circle.radius
        if circle.vx > 0:  
            circle.vx *= -1

    if circle.y - circle.radius <= 0:
        circle.y = circle.radius
        if circle.vy < 0:  
            circle.vy *= -1
    elif circle.y + circle.radius >= SCREEN_HEIGHT:
        circle.y = SCREEN_HEIGHT - circle.radius
        if circle.vy > 0:  
            circle.vy *= -1


def _clamp_position(circle: Circle) -> None:
    """Strictly constrain position to the screen without modifying momentum."""
    if circle.x - circle.radius <= 0:
        circle.x = circle.radius
    elif circle.x + circle.radius >= SCREEN_WIDTH:
        circle.x = SCREEN_WIDTH - circle.radius

    if circle.y - circle.radius <= 0:
        circle.y = circle.radius
    elif circle.y + circle.radius >= SCREEN_HEIGHT:
        circle.y = SCREEN_HEIGHT - circle.radius


def _rotate_velocity(circle: Circle, angle_radians: float) -> None:
    """Apply a rotation matrix to the velocity vector for wandering behavior."""
    new_vx = circle.vx * math.cos(angle_radians) - circle.vy * math.sin(angle_radians)
    new_vy = circle.vx * math.sin(angle_radians) + circle.vy * math.cos(angle_radians)
    circle.vx = new_vx
    circle.vy = new_vy


def _clamp_speed(circle: Circle) -> None:
    """Normalize and scale velocity if it exceeds the maximum allowed threshold."""
    speed = math.hypot(circle.vx, circle.vy)
    if speed > circle.max_speed and speed > 0:
        scale = circle.max_speed / speed
        circle.vx *= scale
        circle.vy *= scale


def apply_random_trajectory_jitter(circle: Circle, dt: float) -> None:
    """Introduce slight random angular deviations to paths."""
    if random.random() < JITTER_CHANCE * (dt * 60.0):
        angle = random.uniform(JITTER_ANGLE_MIN, JITTER_ANGLE_MAX)
        _rotate_velocity(circle, angle)


def _resolve_overlaps(circles: list[Circle]) -> bool:
    """Detect and resolve physical overlaps using a spatial grid and proportional displacement."""
    separated_any = False
    
    cell_size = float(CIRCLE_MAX_RADIUS * 2)
    grid = _build_spatial_grid(circles, cell_size)

    # Accumulate corrections first, then apply in one shot at the end of the pass.
    # This avoids mutating positions while we are still scanning neighbor pairs.
    accumulated_dx = {id(circle): 0.0 for circle in circles}
    accumulated_dy = {id(circle): 0.0 for circle in circles}
    index_by_id = {id(circle): i for i, circle in enumerate(circles)}

    for circle in circles:
        cx, cy = int(circle.x // cell_size), int(circle.y // cell_size)
        
        for dx in (-1, 0, 1):
            for dy in (-1, 0, 1):
                neighbor_cell = (cx + dx, cy + dy)
                if neighbor_cell in grid:
                    for other in grid[neighbor_cell]:
                        circle_id = id(circle)
                        other_id = id(other)
                        
                        # Prevent double-processing pairs
                        if index_by_id[circle_id] >= index_by_id[other_id]:
                            continue

                        diff_x = circle.x - other.x
                        diff_y = circle.y - other.y
                        
                        # Add a tiny buffer to prevent rendering artifacts on boundaries
                        min_distance = circle.radius + other.radius + 3.0
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

                        # Calculate proportional displacement based on circle radii
                        total_radius = circle.radius + other.radius
                        ratio_circle = other.radius / total_radius
                        ratio_other = circle.radius / total_radius

                        accumulated_dx[circle_id] += dir_x * overlap * ratio_circle
                        accumulated_dy[circle_id] += dir_y * overlap * ratio_circle
                        accumulated_dx[other_id] -= dir_x * overlap * ratio_other
                        accumulated_dy[other_id] -= dir_y * overlap * ratio_other

                        # Relative velocity projected onto collision normal.
                        rel_vx = circle.vx - other.vx
                        rel_vy = circle.vy - other.vy
                        
                        inward_speed = rel_vx * dir_x + rel_vy * dir_y

                        # Only apply bounce response when bodies are closing in.
                        if inward_speed < 0: 
                            # 2.0 gives a strong rebound feel for this visual simulation.
                            bounce_factor = 2.0
                            
                            circle.vx -= dir_x * inward_speed * ratio_circle * bounce_factor
                            circle.vy -= dir_y * inward_speed * ratio_circle * bounce_factor
                            other.vx += dir_x * inward_speed * ratio_other * bounce_factor
                            other.vy += dir_y * inward_speed * ratio_other * bounce_factor

                        separated_any = True

    # Apply positional corrections simultaneously
    for circle in circles:
        cid = id(circle)
        circle.x += accumulated_dx[cid]
        circle.y += accumulated_dy[cid]
        _clamp_position(circle)

    return separated_any


def _stabilize_positions(circles: list[Circle]) -> None:
    """Iteratively separate overlaps without modifying standard velocity."""
    # Multiple short passes are more stable than one large positional correction.
    for _ in range(OVERLAP_SOLVER_PASSES):
        changed = _resolve_overlaps(circles)
        for circle in circles:
            _clamp_position(circle)
        if not changed:
            break


def apply_magnetic_repel(circles: list[Circle], dt: float) -> None:
    """Apply continuous avoidance forces based on proximity and relative size."""
    if len(circles) < 2:
        return

    grid = _build_spatial_grid(circles, MAGNETIC_RADIUS)
    check_radius_sq = MAGNETIC_RADIUS * MAGNETIC_RADIUS
    
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
                        
                        # Hierarchical avoidance: ONLY smaller circles flee from bigger ones.
                        # Same-sized circles will ignore this and physically collide instead.
                        if circle.radius < other.radius:
                            strength = (proximity ** 2) * MAGNETIC_FORCE * 2.0
                            force_x[id(circle)] += dir_x * strength
                            force_y[id(circle)] += dir_y * strength
                            is_repelled[id(circle)] = True

    # Integrate forces to velocity; circles with no nearby threats drift back toward base speed.
    for circle in circles:
        cid = id(circle)
        if is_repelled[cid]:
            circle.vx += force_x[cid] * dt
            circle.vy += force_y[cid] * dt
        else:
            current_speed = math.hypot(circle.vx, circle.vy)
            if current_speed > circle.base_speed:
                damping = BASE_DAMPING_PER_60FPS_FRAME ** (dt * 60.0)
                circle.vx *= damping
                circle.vy *= damping

        _clamp_speed(circle)


def lifecycle_system(circles: list[Circle], dt: float) -> None:
    """Handle aging and respawning of entities."""
    for i in range(len(circles)):
        circles[i].age += dt
        if circles[i].age >= circles[i].lifespan:
            circles[i] = create_random_circle()


def force_system(circles: list[Circle], dt: float) -> None:
    """Calculate and apply continuous acceleration forces to entities."""
    apply_magnetic_repel(circles, dt)

    # Apply boundary repulsion to prevent corner trapping
    wall_margin = 50.0
    wall_force = 1200.0 

    for circle in circles:
        if circle.x < circle.radius + wall_margin:
            circle.vx += wall_force * dt
        elif circle.x > SCREEN_WIDTH - circle.radius - wall_margin:
            circle.vx -= wall_force * dt

        if circle.y < circle.radius + wall_margin:
            circle.vy += wall_force * dt
        elif circle.y > SCREEN_HEIGHT - circle.radius - wall_margin:
            circle.vy -= wall_force * dt


def motion_system(circles: list[Circle], dt: float) -> None:
    """Integrate velocity, handle physical collisions, and enforce boundaries."""
    # Pre-pass removes any overlaps introduced by spawn/respawn before moving this frame.
    _stabilize_positions(circles)

    for circle in circles:
        circle.x += circle.vx * dt 
        circle.y += circle.vy * dt
        apply_random_trajectory_jitter(circle, dt)
        _apply_boundary(circle)

    # Post-pass resolves overlaps introduced by movement this frame.
    _stabilize_positions(circles)


def update_circles(circles: list[Circle], dt: float) -> None:
    """Orchestrate all simulation systems per frame."""
    # Update order matters: lifecycle -> force accumulation -> motion/collision solve.
    lifecycle_system(circles, dt)
    force_system(circles, dt)
    motion_system(circles, dt)


def draw_background(screen: pygame.Surface) -> None:
    """Render the background."""
    screen.fill((0, 0, 0))


def draw_circle(screen: pygame.Surface, circle: Circle) -> None:
    """Draw a single entity to the screen."""
    x, y = int(circle.x), int(circle.y)
    if gfxdraw is None:
        pygame.draw.circle(screen, circle.color, (x, y), circle.radius)
        return

    gfxdraw.aacircle(screen, x, y, circle.radius, circle.color)
    gfxdraw.filled_circle(screen, x, y, circle.radius, circle.color)


def draw_circles(screen: pygame.Surface, circles: list[Circle]) -> None:
    """Batch render all entities."""
    for circle in circles:
        draw_circle(screen, circle)


def run() -> None:
    """Main execution loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Hierarchical Magnetic Circles")
    clock = pygame.time.Clock()

    pygame.font.init()
    fps_font = pygame.font.SysFont("Arial", 24, bold=True)

    circles = create_circles(CIRCLE_COUNT)
    running = True

    # Fixed-step render loop using frame delta for frame-rate independent motion.
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