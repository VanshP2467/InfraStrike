# InfraStrike 🎯

An IR light-gun math game built with Python, pygame and a Raspberry Pi 4 + noIR camera.

Point a high-powered IR LED gun at the screen, pull the trigger, and hit the right number on the 4×4 grid.

---

## Table of Contents

- [How It Works](#how-it-works)
- [Hardware Requirements](#hardware-requirements)
- [Project Structure](#project-structure)
- [Quick Start (uv)](#quick-start-uv)
- [Running the Game](#running-the-game)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Running Linting / Formatting](#running-linting--formatting)
- [Contributor Guide](#contributor-guide)


## Hardware Requirements

| Component | Notes                               |
|-----------|-------------------------------------|
| Raspberry Pi 4 | Any RAM variant                     |
| Pi Camera Module (noIR) | V2 or HQ recommended                |
| High-powered IR LED | ~940 nm, driven through a transistor |
          |
| HDMI monitor / TV | For the pygame display              |

---

## Quick Start (uv)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that
handles virtual environments automatically.

```bash
# 1. Clone the repo
git clone https://github.com/VanshP2467/InfraStrike.git
cd InfraStrike

# 2. Create the virtual environment and install core dependencies
uv venv --system-site-packages
uv sync

# 2a. On Raspberry Pi – also install Pi-specific packages
uv sync --extra pi

# 2b. Install dev tools (pytest, coverage, ruff)
uv sync --extra dev
```
---

## Running the Game

```bash
# Via the installed script
uv run infrastrike

# Or directly
uv run python -m infrastrike.main
```

On a **desktop** (no Pi hardware), camera runs in dummy mode and the game remains playable for UI/logic development.

---

## Configuration

All tunable values live in `config/settings.py`:

```python
"""
Shared configuration constants for InfraStrike.

Edit values here to tune camera, detection, game and display behaviour
without touching module code.
"""

# ── Camera ────────────────────────────────────────────────────────────────────
# Raspberry Pi Camera Module 3 NoIR (IMX708) connected via CSI ribbon cable.
CAMERA_RESOLUTION: tuple[int, int] = (1280, 720)
CAMERA_FRAMERATE: int = 60
# CSI port number: 0 for the ribbon-cable connector on Raspberry Pi 4/5.
CAMERA_NUM: int = 0
# Fixed exposure settings for consistent IR blob detection.
# Auto-exposure and auto-white-balance are disabled so the IMX708 sensor does
# not adjust away from the bright IR flash produced by the gun LED.
CAMERA_EXPOSURE_TIME_US: int = 5000  # shutter time in microseconds (5 ms)
CAMERA_ANALOGUE_GAIN: float = 8.0  # sensor gain – raise if blobs are faint

# ── IR Detection ──────────────────────────────────────────────────────────────
# HSV range that isolates the bright IR blob in grayscale space.
IR_THRESHOLD_MIN: int = 200  # minimum pixel brightness (0-255)
IR_BLOB_MIN_AREA: int = 20  # minimum blob area in pixels to be considered a shot
IR_BLOB_MAX_AREA: int = 2000  # maximum blob area in pixels

# ── Display ───────────────────────────────────────────────────────────────────
DISPLAY_WIDTH: int = 1280
DISPLAY_HEIGHT: int = 720
DISPLAY_FPS: int = 60
DISPLAY_TITLE: str = "InfraStrike"
DISPLAY_FULLSCREEN: bool = False

# HUD / grid layout (shared by display and game engine for hit-testing)
HUD_HEIGHT: int = 140  # pixels reserved at the top for the HUD overlay
GRID_MARGIN: int = 20  # pixel gap between grid and screen/HUD edges
GRID_ROWS: int = 4
GRID_COLS: int = 4

# ── Game ──────────────────────────────────────────────────────────────────────
GAME_ROUND_DURATION_SECONDS: int = 60

DISPLAY_SHOW_CAMERA_FEED = False

```

Edit `config/settings.py` to tune sensitivity, Math Grid layout, and display without
touching module code.

UI visuals are centralized in `src/infrastrike/ui/theme.py`, including the arcade
palette, HUD/grid colors, and pixel-friendly font sizes. The embedded pixel font
is `src/infrastrike/assets/fonts/PressStart2P-Regular.ttf` (licensed under SIL OFL
in `src/infrastrike/assets/fonts/LICENSE-PressStart2P.txt`), and `load_pixel_font()`
automatically falls back to a default pygame font if loading fails.

To customize the look, edit the color constants and font size values in
`ui/theme.py`; gameplay behavior is unchanged because these values only affect
rendering.

---

## Running Tests

```bash
uv run pytest
```

All tests are hardware-independent and run on any machine. Pi-specific paths
(picamera2, RPi.GPIO) are mocked/skipped automatically when not available.

---

## Running Linting / Formatting

```bash
uv run ruff check .
uv run ruff format .
```

---
