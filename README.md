# Random Moving Squares (Pygame)

## Application Purpose
This project is a simple real-time graphics simulation built with Pygame. The application opens a window and displays 10 colored squares moving continuously on a 2D canvas.

The project is useful for learning:
- Basic game loop structure
- Object movement using velocity vectors
- Boundary collision and bounce behavior
- Controlled randomness for motion variation
- Organizing animation logic into small testable functions

## What the Application Does
When you run the app, it:
- Creates an 800x600 canvas.
- Spawns 10 squares at random positions.
- Assigns each square a random velocity and random color.
- Updates each square every frame.
- Makes squares bounce when they touch window edges.
- Adds slight random velocity drift over time to avoid predictable motion.
- Renders at 60 FPS for smooth animation.

## Core Behavior and Logic
The app is implemented in [main.py](main.py).

Key constants:
- `SCREEN_WIDTH`, `SCREEN_HEIGHT`: canvas size.
- `SQUARE_COUNT`: number of animated squares.
- `SPEED_MIN`, `SPEED_MAX`: initial velocity range.
- `DRIFT_CHANCE`: probability of random drift each frame.
- `DRIFT_DELTA`: max amount of drift added to velocity.
- `FPS`: target frames per second.

Main functions:
- `create_random_square()`:
  - Creates one square with random position, velocity, and color.
- `create_squares(count)`:
  - Creates a list of squares.
- `update_square(square)`:
  - Moves a square based on velocity.
  - Applies occasional random drift.
  - Applies boundary bounce logic.
- `update_squares(squares)`:
  - Updates all squares per frame.
- `draw_square(screen, square)`:
  - Draws one square.
- `draw_squares(screen, squares)`:
  - Draws all squares.
- `run()`:
  - Initializes Pygame and executes the game loop.

## Project Structure
- [main.py](main.py): application logic and game loop.
- [test_main.py](test_main.py): automated tests for behavior and integration.
- [REPORT.md](REPORT.md): lab/project report content.
- [JOURNAL.md](JOURNAL.md): interaction and change history.

## Requirements
- Python 3.10+ (project currently uses a virtual environment)
- Pygame
- Pytest (for running tests)

## Setup Instructions
The project already contains a virtual environment folder [.venv](.venv), but you can also create a fresh one.

### Option A: Use existing virtual environment
On Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies (if needed):

```powershell
python -m pip install --upgrade pip
python -m pip install pygame pytest
```

### Option B: Create a new virtual environment
On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install pygame pytest
```

## How To Run the Application
From the project root:

```powershell
python main.py
```

Expected result:
- A window titled "Random Moving Squares" appears.
- 10 squares move continuously, bounce at boundaries, and drift slightly over time.

To stop the app:
- Close the window using the window close button.

## How To Run Tests
Recommended command:

```powershell
python -m pytest -q
```

Verbose output:

```powershell
python -m pytest -v
```

Current test scope in [test_main.py](test_main.py):
- Data model validation
- Random square creation constraints
- Edge collision correctness
- Multi-square update behavior
- Draw-path execution
- Integration checks over repeated updates

## Troubleshooting
### `ModuleNotFoundError: No module named 'pygame'`
Cause:
- Pygame is not installed in the active environment.

Fix:

```powershell
python -m pip install pygame
```

### Tests fail because wrong Python interpreter is used
Cause:
- Command runs outside the project virtual environment.

Fix:
- Activate `.venv` first.
- Or run with explicit interpreter path:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

### App window opens and closes immediately
Cause:
- Running from an environment that exits instantly after launch or script errors before loop.

Fix:
- Run from terminal in project root.
- Check terminal output for traceback.

## Notes for Further Enhancement
You can extend this project by adding:
- Square-to-square collision logic
- Per-square speed limits
- Keyboard controls (pause/resume, reset)
- FPS and object count overlays
- User-configurable settings file
