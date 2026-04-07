"""Pygame app that renders 100 squares with subtle jitter and edge bounce."""

from __future__ import annotations

import random
from dataclasses import dataclass

import pygame
import math

SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
BG_TOP_COLOR: tuple[int, int, int] = (18, 22, 38)
BG_BOTTOM_COLOR: tuple[int, int, int] = (34, 48, 72)
FPS: int = 60

SQUARE_COUNT: int = 100  # Number of squares to draw
SQUARE_SIZE: int = 30
SQUARE_MIN_SIZE: int = 18  # Smallest square size
SQUARE_MAX_SIZE: int = 54  # Largest square size
SQUARE_BORDER_COLOR: tuple[int, int, int] = (240, 246, 255)
SPEED_MIN: int = 60
SPEED_MAX: int = 240
GLOBAL_MAX_SPEED: float = 360.0
COLOR_MIN: int = 50
COLOR_MAX: int = 255
JITTER_CHANCE: float = 0.05
JITTER_ANGLE_MIN: float = -0.1
JITTER_ANGLE_MAX: float = 0.1

# Flee behavior scaffold values
FLEE_CHECK_RADIUS: float = 140.0
FLEE_ACCELERATION: float = 120.0


@dataclass
class Square:
    """Square position, velocity, and render color."""

    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    size: int = SQUARE_SIZE
    max_speed: float = GLOBAL_MAX_SPEED  # Maximum speed for this square


def create_random_square() -> Square:
    """Create one square at a random position with random velocity."""
    size = random.randint(SQUARE_MIN_SIZE, SQUARE_MAX_SIZE)

    # Larger squares move slower.
    # size_factor is in the 0-1 range, where 1 means the smallest square.
    size_factor = (SQUARE_MAX_SIZE - size) / max(1, (SQUARE_MAX_SIZE - SQUARE_MIN_SIZE))

    # Scale speed from 60.0 up to GLOBAL_MAX_SPEED.
    max_speed = 60.0 + (GLOBAL_MAX_SPEED - 60.0) * size_factor
    max_speed = min(max_speed, GLOBAL_MAX_SPEED)  # Keep within the global limit

    x = random.randint(0, SCREEN_WIDTH - size)
    y = random.randint(0, SCREEN_HEIGHT - size)

    # Limit starting speed to this square's max speed.
    start_speed_x = min(random.randint(SPEED_MIN, SPEED_MAX), max_speed)
    start_speed_y = min(random.randint(SPEED_MIN, SPEED_MAX), max_speed)

    vx = random.choice([-1, 1]) * start_speed_x
    vy = random.choice([-1, 1]) * start_speed_y

    color = (
        random.randint(COLOR_MIN, COLOR_MAX),
        random.randint(COLOR_MIN, COLOR_MAX),
        random.randint(COLOR_MIN, COLOR_MAX),
    )
    return Square(x=x, y=y, vx=vx, vy=vy, color=color, size=size, max_speed=max_speed)


def create_squares(count: int) -> list[Square]:
    """Create a list of random squares."""
    return [create_random_square() for _ in range(count)]


def _apply_boundary(square: Square) -> None:
    if square.x <= 0:
        square.x = 0
        square.vx *= -1
    elif square.x + square.size >= SCREEN_WIDTH:
        square.x = SCREEN_WIDTH - square.size
        square.vx *= -1

    if square.y <= 0:
        square.y = 0
        square.vy *= -1
    elif square.y + square.size >= SCREEN_HEIGHT:
        square.y = SCREEN_HEIGHT - square.size
        square.vy *= -1


def _rotate_velocity(square: Square, angle_radians: float) -> None:
    """Rotate a velocity vector by a small angle."""
    new_vx = square.vx * math.cos(angle_radians) - square.vy * math.sin(angle_radians)
    new_vy = square.vx * math.sin(angle_radians) + square.vy * math.cos(angle_radians)
    square.vx = new_vx
    square.vy = new_vy


def apply_random_trajectory_jitter(square: Square) -> None:
    """Keep movement slightly random by rotating velocity sometimes."""
    if random.random() < JITTER_CHANCE:
        angle = random.uniform(JITTER_ANGLE_MIN, JITTER_ANGLE_MAX)
        _rotate_velocity(square, angle)


def apply_flee_from_larger_squares(squares: list[Square], dt: float) -> None:
    """Stub: steer smaller squares away from nearby larger squares.

    TODO 1: For each square, look for larger squares within FLEE_CHECK_RADIUS.
    TODO 2: Build a flee direction vector from the larger square to the smaller one.
    TODO 3: Weight flee strength by size difference and distance.
    TODO 4: Add flee acceleration to velocity using dt.
    TODO 5: Clamp velocity to each square.max_speed after applying flee force.
    """
    # TODO: Implement flee steering and velocity updates.
    for square in squares:
        flee_accel_x = 0.0
        flee_accel_y = 0.0
        
        for other_square in squares:
            if other_square.size > square.size:
                diff_x = square.x - other_square.x
                diff_y = square.y - other_square.y
                
                distance = math.sqrt(diff_x * diff_x + diff_y * diff_y)
                
                if distance < FLEE_CHECK_RADIUS and distance > 0:
                    dir_x = diff_x / distance
                    dir_y = diff_y / distance
                    
                    size_diff = other_square.size - square.size
                    weight = size_diff / distance
                    
                    flee_accel_x += dir_x * weight * FLEE_ACCELERATION
                    flee_accel_y += dir_y * weight * FLEE_ACCELERATION
        
        square.vx += flee_accel_x * dt
        square.vy += flee_accel_y * dt
        
        current_speed = math.sqrt(square.vx * square.vx + square.vy * square.vy)
        if current_speed > square.max_speed:
            square.vx = (square.vx / current_speed) * square.max_speed
            square.vy = (square.vy / current_speed) * square.max_speed


def update_square(square: Square, dt: float) -> None:
    """Advance one square by one frame."""
    square.x += square.vx * dt  # Use delta time for frame-independent movement
    square.y += square.vy * dt

    apply_random_trajectory_jitter(square)

    _apply_boundary(square)


def update_squares(squares: list[Square], dt: float) -> None:
    """Update all squares each frame."""
    for square in squares:
        update_square(square, dt)

    # TODO: Enable interaction by applying flee logic after base movement.
    apply_flee_from_larger_squares(squares, dt)


def draw_background(screen: pygame.Surface) -> None:
    """Render a vertical color gradient background."""
    for y in range(SCREEN_HEIGHT):
        ratio = y / max(SCREEN_HEIGHT - 1, 1)
        color = (
            int(BG_TOP_COLOR[0] + (BG_BOTTOM_COLOR[0] - BG_TOP_COLOR[0]) * ratio),
            int(BG_TOP_COLOR[1] + (BG_BOTTOM_COLOR[1] - BG_TOP_COLOR[1]) * ratio),
            int(BG_TOP_COLOR[2] + (BG_BOTTOM_COLOR[2] - BG_TOP_COLOR[2]) * ratio),
        )
        pygame.draw.line(screen, color, (0, y), (SCREEN_WIDTH, y))


def draw_square(screen: pygame.Surface, square: Square) -> None:
    """Draw one square."""
    rect = pygame.Rect(int(square.x), int(square.y), square.size, square.size)
    glow_rect = rect.inflate(8, 8)
    glow_color = (
        min(square.color[0] + 45, 255),
        min(square.color[1] + 45, 255),
        min(square.color[2] + 45, 255),
    )

    pygame.draw.rect(screen, glow_color, glow_rect, border_radius=max(square.size // 4, 4))
    pygame.draw.rect(screen, square.color, rect, border_radius=max(square.size // 5, 3))
    pygame.draw.rect(
        screen,
        SQUARE_BORDER_COLOR,
        rect,
        width=max(square.size // 12, 1),
        border_radius=max(square.size // 5, 3),
    )

    shine = pygame.Rect(rect.x + rect.w // 6, rect.y + rect.h // 8, rect.w // 3, max(rect.h // 8, 2))
    pygame.draw.rect(
        screen,
        (255, 255, 255),
        shine,
        border_radius=max(square.size // 10, 2),
    )


def draw_squares(screen: pygame.Surface, squares: list[Square]) -> None:
    """Draw all squares to the screen."""
    for square in squares:
        draw_square(screen, square)


def run() -> None:
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Random Moving Squares")
    clock = pygame.time.Clock()

    #the font for the FPS counter
    pygame.font.init()
    fps_font = pygame.font.SysFont("Arial", 24, bold=True)

    squares = create_squares(SQUARE_COUNT)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        dt = clock.tick(FPS) / 1000.0

        update_squares(squares, dt)
        draw_background(screen)
        draw_squares(screen, squares)

        #calculate and render the FPS
        current_fps = clock.get_fps()
        # Render the text surface (Text, Antialias, Color)
        fps_surface = fps_font.render(f"FPS: {int(current_fps)}", True, (0, 255, 0)) 
        #putting the text surface to the top-left corner of the screen
        screen.blit(fps_surface, (10, 10))

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()