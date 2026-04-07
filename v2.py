"""Pygame app with configurable moving blocks, clock, and optional collisions."""

from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

SCREEN_WIDTH: int = 960
SCREEN_HEIGHT: int = 640
BG_TOP_COLOR: tuple[int, int, int] = (16, 24, 44)
BG_BOTTOM_COLOR: tuple[int, int, int] = (38, 58, 88)
FPS: int = 60

SQUARE_COUNT: int = 14
MIN_SQUARE_COUNT: int = 2
MAX_SQUARE_COUNT: int = 80

SQUARE_SIZE: int = 42
SQUARE_MIN_SIZE: int = 24
SQUARE_MAX_SIZE: int = 72
MAX_RENDER_SIZE: int = SQUARE_MAX_SIZE * 2
SQUARE_BORDER_COLOR: tuple[int, int, int] = (240, 246, 255)

SPEED_MIN: int = 1
SPEED_MAX: int = 4
VELOCITY_CAP: float = 8.0

SPEED_SCALE_MIN: float = 0.2
SPEED_SCALE_MAX: float = 3.0
SPEED_SCALE_STEP: float = 0.1

COLOR_MIN: int = 50
COLOR_MAX: int = 255

DRIFT_CHANCE: float = 0.05
DRIFT_DELTA: float = 0.5

SIZE_SCALE_MIN: float = 0.6
SIZE_SCALE_MAX: float = 2.0
SIZE_SCALE_STEP: float = 0.1

HUD_BG_COLOR: tuple[int, int, int, int] = (6, 10, 20, 190)
HUD_TEXT_COLOR: tuple[int, int, int] = (235, 242, 252)
HUD_SHADOW_COLOR: tuple[int, int, int] = (0, 0, 0)


@dataclass
class Square:
    """Square position, velocity, and render color."""

    x: float
    y: float
    vx: float
    vy: float
    color: tuple[int, int, int]
    size: int = SQUARE_SIZE
    base_size: int = 0

    def __post_init__(self) -> None:
        if self.base_size <= 0:
            self.base_size = self.size


@dataclass
class AppConfig:
    """Runtime controls that can be changed from keyboard input."""

    speed_multiplier: float = 1.0
    target_count: int = SQUARE_COUNT
    size_scale: float = 1.0
    collisions_enabled: bool = False
    show_overlay: bool = True
    paused: bool = False


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def _clamp_position(square: Square) -> None:
    square.x = _clamp(square.x, 0, SCREEN_WIDTH - square.size)
    square.y = _clamp(square.y, 0, SCREEN_HEIGHT - square.size)


def create_random_square() -> Square:
    """Create one square at a random position with random velocity."""
    size = random.randint(SQUARE_MIN_SIZE, SQUARE_MAX_SIZE)
    x = random.randint(0, SCREEN_WIDTH - size)
    y = random.randint(0, SCREEN_HEIGHT - size)
    vx = random.choice([-1, 1]) * random.randint(SPEED_MIN, SPEED_MAX)
    vy = random.choice([-1, 1]) * random.randint(SPEED_MIN, SPEED_MAX)
    color = (
        random.randint(COLOR_MIN, COLOR_MAX),
        random.randint(COLOR_MIN, COLOR_MAX),
        random.randint(COLOR_MIN, COLOR_MAX),
    )
    return Square(x=x, y=y, vx=vx, vy=vy, color=color, size=size, base_size=size)


def create_squares(count: int) -> list[Square]:
    """Create a list of random squares."""
    return [create_random_square() for _ in range(count)]


def sync_square_count(squares: list[Square], target_count: int) -> None:
    """Grow or shrink the square list to match the target count."""
    normalized_target = int(_clamp(target_count, MIN_SQUARE_COUNT, MAX_SQUARE_COUNT))
    while len(squares) < normalized_target:
        squares.append(create_random_square())
    while len(squares) > normalized_target:
        squares.pop()


def apply_size_scale(squares: list[Square], size_scale: float) -> None:
    """Resize squares based on the configured size scale."""
    scale = _clamp(size_scale, SIZE_SCALE_MIN, SIZE_SCALE_MAX)
    for square in squares:
        scaled_size = int(round(square.base_size * scale))
        square.size = int(_clamp(scaled_size, SQUARE_MIN_SIZE, MAX_RENDER_SIZE))
        _clamp_position(square)


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


def _squares_overlap(a: Square, b: Square) -> bool:
    return (
        a.x < b.x + b.size
        and a.x + a.size > b.x
        and a.y < b.y + b.size
        and a.y + a.size > b.y
    )


def _resolve_pair_collision(a: Square, b: Square) -> None:
    if not _squares_overlap(a, b):
        return

    overlap_x = min(a.x + a.size - b.x, b.x + b.size - a.x)
    overlap_y = min(a.y + a.size - b.y, b.y + b.size - a.y)
    if overlap_x <= 0 or overlap_y <= 0:
        return

    if overlap_x < overlap_y:
        separation = overlap_x / 2
        if a.x < b.x:
            a.x -= separation
            b.x += separation
        else:
            a.x += separation
            b.x -= separation
        a.vx, b.vx = b.vx, a.vx
    else:
        separation = overlap_y / 2
        if a.y < b.y:
            a.y -= separation
            b.y += separation
        else:
            a.y += separation
            b.y -= separation
        a.vy, b.vy = b.vy, a.vy

    _clamp_position(a)
    _clamp_position(b)


def resolve_collisions(squares: list[Square]) -> None:
    """Resolve collisions across all square pairs."""
    for i in range(len(squares) - 1):
        for j in range(i + 1, len(squares)):
            _resolve_pair_collision(squares[i], squares[j])


def update_square(square: Square, speed_multiplier: float = 1.0) -> None:
    """Advance one square by one frame."""
    speed = _clamp(speed_multiplier, SPEED_SCALE_MIN, SPEED_SCALE_MAX)
    square.x += square.vx * speed
    square.y += square.vy * speed

    if random.random() < DRIFT_CHANCE:
        square.vx += random.uniform(-DRIFT_DELTA, DRIFT_DELTA)
        square.vy += random.uniform(-DRIFT_DELTA, DRIFT_DELTA)
        square.vx = _clamp(square.vx, -VELOCITY_CAP, VELOCITY_CAP)
        square.vy = _clamp(square.vy, -VELOCITY_CAP, VELOCITY_CAP)

    _apply_boundary(square)


def update_squares(
    squares: list[Square],
    speed_multiplier: float = 1.0,
    collisions_enabled: bool = False,
) -> None:
    """Update all squares each frame."""
    for square in squares:
        update_square(square, speed_multiplier)

    if collisions_enabled:
        resolve_collisions(squares)


def build_gradient_surface() -> pygame.Surface:
    """Create a reusable vertical gradient background surface."""
    gradient = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    for y in range(SCREEN_HEIGHT):
        ratio = y / max(SCREEN_HEIGHT - 1, 1)
        color = (
            int(BG_TOP_COLOR[0] + (BG_BOTTOM_COLOR[0] - BG_TOP_COLOR[0]) * ratio),
            int(BG_TOP_COLOR[1] + (BG_BOTTOM_COLOR[1] - BG_TOP_COLOR[1]) * ratio),
            int(BG_TOP_COLOR[2] + (BG_BOTTOM_COLOR[2] - BG_TOP_COLOR[2]) * ratio),
        )
        pygame.draw.line(gradient, color, (0, y), (SCREEN_WIDTH, y))
    return gradient


def draw_background(screen: pygame.Surface, gradient: pygame.Surface) -> None:
    """Draw the precomputed gradient background."""
    screen.blit(gradient, (0, 0))


def draw_square(screen: pygame.Surface, square: Square) -> None:
    """Draw one square."""
    rect = pygame.Rect(int(square.x), int(square.y), square.size, square.size)
    shadow_rect = rect.move(4, 4)
    glow_rect = rect.inflate(8, 8)
    glow_color = (
        min(square.color[0] + 45, 255),
        min(square.color[1] + 45, 255),
        min(square.color[2] + 45, 255),
    )

    pygame.draw.rect(screen, (10, 14, 24), shadow_rect, border_radius=max(square.size // 5, 3))
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


def _format_elapsed_time(ms: int) -> str:
    total_seconds = ms // 1000
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes:02d}:{seconds:02d}"


def draw_clock(screen: pygame.Surface, font: pygame.font.Font, elapsed_ms: int) -> None:
    """Draw running clock in the upper-right corner."""
    label = font.render(f"Clock { _format_elapsed_time(elapsed_ms) }", True, HUD_TEXT_COLOR)
    shadow = font.render(f"Clock { _format_elapsed_time(elapsed_ms) }", True, HUD_SHADOW_COLOR)
    rect = label.get_rect(topright=(SCREEN_WIDTH - 16, 14))
    screen.blit(shadow, rect.move(2, 2))
    screen.blit(label, rect)


def draw_overlay(
    screen: pygame.Surface,
    font: pygame.font.Font,
    config: AppConfig,
    square_count: int,
) -> None:
    """Render the in-window configuration panel."""
    panel = pygame.Surface((460, 190), pygame.SRCALPHA)
    panel.fill(HUD_BG_COLOR)
    screen.blit(panel, (14, 14))

    collision_text = "ON" if config.collisions_enabled else "OFF"
    pause_text = "PAUSED" if config.paused else "RUNNING"
    lines = [
        "Configuration",
        f"Speed: Up/Down = {config.speed_multiplier:.1f}x",
        f"Blocks: Right/Left = {square_count}",
        f"Size Scale: ]/[ = {config.size_scale:.1f}x",
        f"Collisions: C = {collision_text}",
        f"Pause: Space = {pause_text}",
        "Reset: R   Hide Panel: H",
    ]

    line_y = 24
    for text in lines:
        rendered = font.render(text, True, HUD_TEXT_COLOR)
        screen.blit(rendered, (26, line_y))
        line_y += 24


def handle_keydown(key: int, config: AppConfig) -> None:
    """Apply keyboard controls to runtime configuration."""
    if key == pygame.K_UP:
        config.speed_multiplier = round(
            _clamp(config.speed_multiplier + SPEED_SCALE_STEP, SPEED_SCALE_MIN, SPEED_SCALE_MAX),
            1,
        )
    elif key == pygame.K_DOWN:
        config.speed_multiplier = round(
            _clamp(config.speed_multiplier - SPEED_SCALE_STEP, SPEED_SCALE_MIN, SPEED_SCALE_MAX),
            1,
        )
    elif key == pygame.K_RIGHT:
        config.target_count = int(_clamp(config.target_count + 1, MIN_SQUARE_COUNT, MAX_SQUARE_COUNT))
    elif key == pygame.K_LEFT:
        config.target_count = int(_clamp(config.target_count - 1, MIN_SQUARE_COUNT, MAX_SQUARE_COUNT))
    elif key in (pygame.K_RIGHTBRACKET, pygame.K_EQUALS, pygame.K_KP_PLUS):
        config.size_scale = round(
            _clamp(config.size_scale + SIZE_SCALE_STEP, SIZE_SCALE_MIN, SIZE_SCALE_MAX),
            1,
        )
    elif key in (pygame.K_LEFTBRACKET, pygame.K_MINUS, pygame.K_KP_MINUS):
        config.size_scale = round(
            _clamp(config.size_scale - SIZE_SCALE_STEP, SIZE_SCALE_MIN, SIZE_SCALE_MAX),
            1,
        )
    elif key == pygame.K_c:
        config.collisions_enabled = not config.collisions_enabled
    elif key == pygame.K_h:
        config.show_overlay = not config.show_overlay
    elif key == pygame.K_SPACE:
        config.paused = not config.paused
    elif key == pygame.K_r:
        config.speed_multiplier = 1.0
        config.target_count = SQUARE_COUNT
        config.size_scale = 1.0
        config.collisions_enabled = False
        config.paused = False


def run() -> None:
    """Main game loop."""
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Configurable Moving Blocks")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("consolas", 20)
    gradient = build_gradient_surface()

    config = AppConfig()
    squares = create_squares(config.target_count)
    start_ticks = pygame.time.get_ticks()

    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                handle_keydown(event.key, config)

        sync_square_count(squares, config.target_count)
        apply_size_scale(squares, config.size_scale)

        if not config.paused:
            update_squares(
                squares,
                speed_multiplier=config.speed_multiplier,
                collisions_enabled=config.collisions_enabled,
            )

        draw_background(screen, gradient)
        draw_squares(screen, squares)

        elapsed_ms = pygame.time.get_ticks() - start_ticks
        draw_clock(screen, font, elapsed_ms)
        if config.show_overlay:
            draw_overlay(screen, font, config, len(squares))

        pygame.display.flip()

        clock.tick(FPS)

    pygame.quit()


if __name__ == "__main__":
    run()
