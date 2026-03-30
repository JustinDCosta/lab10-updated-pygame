"""Pygame app that renders 10 squares moving with random drift and edge bounce."""

from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
BG_COLOR: tuple[int, int, int] = (20, 20, 30)
FPS: int = 60

SQUARE_COUNT: int = 10
SQUARE_SIZE: int = 30
SQUARE_COLOR: tuple[int, int, int] = (70, 200, 255)
SPEED_MIN: int = 1
SPEED_MAX: int = 4
COLOR_MIN: int = 50
COLOR_MAX: int = 255
DRIFT_CHANCE: float = 0.05
DRIFT_DELTA: float = 0.5


@dataclass
class Square:
    """Square position, velocity, and render color."""

    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    size: int = SQUARE_SIZE


def create_random_square() -> Square:
    """Create one square at a random position with random velocity."""
    x = random.randint(0, SCREEN_WIDTH - SQUARE_SIZE)
    y = random.randint(0, SCREEN_HEIGHT - SQUARE_SIZE)
    vx = random.choice([-1, 1]) * random.randint(SPEED_MIN, SPEED_MAX)
    vy = random.choice([-1, 1]) * random.randint(SPEED_MIN, SPEED_MAX)
    color = (
        random.randint(COLOR_MIN, COLOR_MAX),
        random.randint(COLOR_MIN, COLOR_MAX),
        random.randint(COLOR_MIN, COLOR_MAX),
    )
    return Square(x=x, y=y, vx=vx, vy=vy, color=color)


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


def update_square(square: Square) -> None:
    """Advance one square by one frame."""
    square.x += square.vx
    square.y += square.vy

    if random.random() < DRIFT_CHANCE:
        square.vx += random.uniform(-DRIFT_DELTA, DRIFT_DELTA)
        square.vy += random.uniform(-DRIFT_DELTA, DRIFT_DELTA)

    _apply_boundary(square)


def update_squares(squares: list[Square]) -> None:
    """Update all squares each frame."""
    for square in squares:
        update_square(square)


def draw_square(screen: pygame.Surface, square: Square) -> None:
    """Draw one square."""
    rect = pygame.Rect(int(square.x), int(square.y), square.size, square.size)
    pygame.draw.rect(screen, square.color, rect)


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

    squares = create_squares(SQUARE_COUNT)
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Update
        update_squares(squares)

        # Draw
        screen.fill(BG_COLOR)
        draw_squares(screen, squares)
        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run()
