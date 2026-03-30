"""Stubbed pygame app: 10 squares moving randomly on a canvas.

This file is intentionally scaffolded with TODOs so you can implement
the behavior step by step.
"""

from __future__ import annotations

import random
from dataclasses import dataclass

import pygame


# Canvas settings
SCREEN_WIDTH: int = 800
SCREEN_HEIGHT: int = 600
BG_COLOR: tuple[int, int, int] = (20, 20, 30)

# Square settings
SQUARE_COUNT: int = 10
SQUARE_SIZE: int = 30
SQUARE_COLOR: tuple[int, int, int] = (70, 200, 255)
SPEED_MIN: int = 1
SPEED_MAX: int = 4


@dataclass
class Square:
	"""Holds square position and velocity."""

	x: float
	y: float
	vx: float
	vy: float
	size: int = SQUARE_SIZE


def create_random_square() -> Square:
	"""Create one square at a random position with random velocity."""
	x = random.randint(0, SCREEN_WIDTH - SQUARE_SIZE)
	y = random.randint(0, SCREEN_HEIGHT - SQUARE_SIZE)
	vx = random.choice([-1, 1]) * random.randint(SPEED_MIN, SPEED_MAX)
	vy = random.choice([-1, 1]) * random.randint(SPEED_MIN, SPEED_MAX)
	return Square(x=x, y=y, vx=vx, vy=vy)


def create_squares(count: int) -> list[Square]:
	"""Create a list of squares.

	TODO: Try replacing this loop with your own approach and compare readability.
	"""
	squares: list[Square] = []
	for _ in range(count):
		squares.append(create_random_square())
	return squares


def update_square(square: Square) -> None:
	"""Update one square position.

	TODO 1: Move by velocity.
	TODO 2: Bounce when hitting screen edges.
	TODO 3 (optional): Add slight random direction changes over time.
	"""
	square.x += square.vx
	square.y += square.vy

	# TODO: Improve edge handling (for example, clamp position before reversing).
	if square.x <= 0 or square.x + square.size >= SCREEN_WIDTH:
		square.vx *= -1
	if square.y <= 0 or square.y + square.size >= SCREEN_HEIGHT:
		square.vy *= -1


def update_squares(squares: list[Square]) -> None:
	"""Update all squares each frame."""
	for square in squares:
		update_square(square)


def draw_square(screen: pygame.Surface, square: Square) -> None:
	"""Draw one square.

	TODO: Change color per-square if you want more visual feedback.
	"""
	rect = pygame.Rect(int(square.x), int(square.y), square.size, square.size)
	pygame.draw.rect(screen, SQUARE_COLOR, rect)


def draw_squares(screen: pygame.Surface, squares: list[Square]) -> None:
	"""Draw all squares to the screen."""
	for square in squares:
		draw_square(screen, square)


def run() -> None:
	"""Main game loop."""
	pygame.init()
	screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
	pygame.display.set_caption("Random Moving Squares (Stub)")
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

		# TODO: Experiment with FPS values and observe motion smoothness.
		clock.tick(60)

	pygame.quit()


if __name__ == "__main__":
	run()
