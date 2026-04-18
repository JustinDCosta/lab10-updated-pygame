# Hierarchical Magnetic Circles (Pygame)

## Overview
This project is a real-time Pygame simulation where circles move across an 800x600 canvas, jitter slightly over time, and repel each other with size-aware behavior.

Key behavior:
- Random spawn position, radius, color, and starting velocity.
- Frame-independent movement using delta time.
- Magnetic repel force inside a configurable radius.
- Size hierarchy:
  - Smaller circles react more strongly to larger circles.
  - Equal-size circles repel each other symmetrically.
- Iterative overlap stabilization to reduce circle penetration.
- Boundary bounce at all screen edges.

## Current Configuration
Main settings are defined in [main.py](main.py):

- `SCREEN_WIDTH = 800`
- `SCREEN_HEIGHT = 600`
- `FPS = 60`
- `CIRCLE_COUNT = 30`
- `CIRCLE_MIN_RADIUS = 8`
- `CIRCLE_MAX_RADIUS = 25`
- `SPEED_MIN = 15`
- `SPEED_MAX = 40`
- `GLOBAL_MAX_SPEED = 180.0`
- `MAGNETIC_RADIUS = 180.0`
- `MAGNETIC_FORCE = 800.0`
- `OVERLAP_SOLVER_PASSES = 8`

## Motion and Repel Model
For each frame:
1. Stabilize existing overlap with iterative separation.
2. Apply magnetic repel acceleration to each circle.
3. Move circles with `x += vx * dt` and `y += vy * dt`.
4. Apply jitter by rotating velocity with a small random angle.
5. Stabilize positions again and enforce screen bounds.

Jitter uses velocity rotation:

$$
v_x' = v_x \cos(\theta) - v_y \sin(\theta)
$$

$$
v_y' = v_x \sin(\theta) + v_y \cos(\theta)
$$

This changes direction while mostly preserving speed magnitude.

## Rendering
- Background: solid black.
- Circle rendering:
  - Uses anti-aliased `pygame.gfxdraw` when available.
  - Falls back to `pygame.draw.circle` if `gfxdraw` is unavailable.
- FPS counter is shown at the top-left of the window.

## Project Files
- [main.py](main.py): simulation logic, physics, rendering, game loop.
- [REPORT.md](REPORT.md): project development report and AI workflow analysis.
- [JOURNAL.md](JOURNAL.md): interaction and change log.

## Requirements
- Python 3.10+
- pygame-ce
- pytest

## Setup
Use existing virtual environment (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pygame-ce pytest
```

Create a new virtual environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pygame-ce pytest
```

## Run the App
From the project root:

```powershell
python main.py
```

Expected result:
- Window title: "Hierarchical Magnetic Circles".
- 30 colored circles moving with smooth dt-based motion.
- Small random trajectory jitter.
- Repel interactions with size-based behavior.
- Visible FPS counter.

## Run Tests
Quick run:

```powershell
python -m pytest -q
```

Verbose run:

```powershell
python -m pytest -v
```

Direct module run:

```powershell
python test_main.py
```

Current suite validates:
- Circle creation and bounds.
- Boundary bounce behavior.
- Jitter behavior.
- Repel force and speed clamping.
- Overlap solver behavior.
- Integration behavior across many frames.
- Rendering path safety.

## Troubleshooting
### ModuleNotFoundError for pygame
Install dependencies in the active environment:

```powershell
python -m pip install pygame-ce pytest
```

### Wrong interpreter is being used
Run commands with the venv Python explicitly:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe main.py
```

### Behavior changed after physics edits
If you modify repel or overlap logic, update [test_main.py](test_main.py) so tests match the intended behavior.
