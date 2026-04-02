# Random Moving Squares (Pygame)

## Overview
This project is a real-time Pygame simulation where 100 squares move around an 800x600 canvas.

Each square has:
- Random position
- Random size
- Random color
- Speed tied to size
- Subtle directional jitter over time

The app is useful for learning game-loop structure, frame-independent updates, and simple motion modeling.

## Latest Logic (Current Version)
The current implementation is in [main.py](main.py).

Main updates in the latest version:
- Uses delta time (`dt`) for frame-independent movement.
- Uses 100 squares by default (`SQUARE_COUNT = 100`).
- Ties max speed to square size (smaller squares can move faster).
- Uses trigonometric velocity rotation for jitter (instead of additive drift).
- Keeps edge bounce behavior and gradient background rendering.

### Movement Model
Per frame:
- Position update:
  - `x += vx * dt`
  - `y += vy * dt`
- Jitter chance:
  - With probability `JITTER_CHANCE`, velocity is rotated by a small random angle.
- Boundary behavior:
  - Squares bounce when touching screen edges.

### Jitter Model
Jitter uses a small angle `theta` (in radians) and rotates the velocity vector:

$$
v_x' = v_x \cos(\theta) - v_y \sin(\theta)
$$

$$
v_y' = v_x \sin(\theta) + v_y \cos(\theta)
$$

This changes direction smoothly while preserving speed magnitude.

## Key Constants
- `SCREEN_WIDTH`, `SCREEN_HEIGHT`: canvas size.
- `FPS`: target frame rate.
- `SQUARE_COUNT`: number of animated squares.
- `SQUARE_MIN_SIZE`, `SQUARE_MAX_SIZE`: random size range.
- `SPEED_MIN`, `SPEED_MAX`: initial speed range.
- `GLOBAL_MAX_SPEED`: upper speed cap used by size-based scaling.
- `JITTER_CHANCE`: probability of jitter per frame.

## Core Functions
- `create_random_square()`:
  - Creates one square with random size, color, and size-scaled max speed.
- `create_squares(count)`:
  - Creates a list of squares.
- `update_square(square, dt)`:
  - Advances one square using delta time and optional jitter rotation.
- `update_squares(squares, dt)`:
  - Updates all squares in one frame.
- `_apply_boundary(square)`:
  - Applies edge-bounce logic.
- `draw_background(screen)`:
  - Draws the gradient background.
- `draw_square(screen, square)`:
  - Draws one styled square.
- `draw_squares(screen, squares)`:
  - Draws all squares.
- `run()`:
  - Runs the app loop and computes `dt` each frame.

## Project Structure
- [main.py](main.py): application logic and rendering.
- [test_main.py](test_main.py): automated test suite.
- [REPORT.md](REPORT.md): project report.
- [JOURNAL.md](JOURNAL.md): interaction/change log.

## Requirements
- Python 3.10+
- Pygame
- Pytest

## Setup
The repository already contains [.venv](.venv), but you can create your own if needed.

Use existing environment (PowerShell):

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pygame pytest
```

Create new environment (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pygame pytest
```

## Run the App
From project root:

```powershell
python main.py
```

Expected result:
- A window titled "Random Moving Squares"
- 100 moving squares
- Smooth movement from `dt`
- Subtle direction jitter over time
- Edge bounce and gradient background

## Run Tests
Recommended:

```powershell
python -m pytest -q
```

Verbose:

```powershell
python -m pytest -v
```

Direct file execution:

```powershell
python test_main.py
```

Current test coverage in [test_main.py](test_main.py):
- Square creation and bounds
- Size and speed constraints
- Boundary collisions
- Jitter behavior
- `dt`-based movement updates
- Rendering path safety with pygame mocks
- Integration behavior over multiple frames

## Troubleshooting
### `ModuleNotFoundError: No module named 'pygame'`
Install pygame in the active environment:

```powershell
python -m pip install pygame
```

### Wrong interpreter / environment
Run tests and app with the venv interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe main.py
```

### Tests fail after logic changes
If you change function signatures or motion logic, update [test_main.py](test_main.py) so tests match the new API and behavior.
