# InfraStrike 🎯

An IR light-gun shooting game built with Python, pygame and a Raspberry Pi 4 + noIR camera.

Point a high-powered IR LED gun at the screen, pull the trigger, and blast targets before they disappear!

---

## Table of Contents

- [How It Works](#how-it-works)
- [Hardware Requirements](#hardware-requirements)
- [Project Structure](#project-structure)
- [Quick Start (uv)](#quick-start-uv)
- [Running the Game](#running-the-game)
- [Configuration](#configuration)
- [Running Tests](#running-tests)
- [Contributor Guide](#contributor-guide)

---

## How It Works

```
IR LED Gun ──trigger──► GPIO pin 17
        │
        └── IR flash ──► noIR Camera ──► OpenCV blob detection
                                                │
                                        (x, y) shot coords
                                                │
                                        Game Engine checks hit/miss
                                                │
                                        pygame renders targets + HUD
```

1. The **noIR camera** captures a live feed. IR light passes through the noIR filter.
2. **OpenCV** thresholds the frame to find the bright IR blob produced when the gun fires.
3. The **game engine** checks whether the blob centroid overlaps any active target.
4. **pygame** renders the camera feed, targets, cross-hair and HUD in real time.
5. The physical **trigger button** is read from GPIO; on a desktop the spacebar acts as
   the trigger for development.

---

## Hardware Requirements

| Component | Notes |
|-----------|-------|
| Raspberry Pi 4 | Any RAM variant |
| Pi Camera Module (noIR) | V2 or HQ recommended |
| High-powered IR LED | ~850 nm, driven through a transistor |
| Momentary push button | Connected to GPIO 17 (BCM) + GND |
| Optional status LED | Connected to GPIO 27 (BCM) |
| HDMI monitor / TV | For the pygame display |

---

## Project Structure

```
InfraStrike/
├── pyproject.toml              # uv / hatch project metadata & dependencies
├── .python-version             # Python version pin (3.11)
├── config/
│   └── settings.py             # All tunable constants (resolution, thresholds, …)
├── src/
│   └── infrastrike/
│       ├── main.py             # Entry point – wires all subsystems together
│       ├── camera/             # Contributor 1 – noIR camera capture
│       │   └── camera_manager.py
│       ├── detection/          # Contributor 2 – IR blob detection (OpenCV)
│       │   └── ir_detector.py
│       ├── game/               # Contributor 3 – game state, targets, scoring
│       │   ├── game_engine.py
│       │   ├── score_manager.py
│       │   └── target.py
│       ├── ui/                 # Contributor 4 – pygame display & HUD
│       │   ├── display.py
│       │   └── hud.py
│       └── hardware/           # Contributor 5 – GPIO / IR LED / trigger
│           └── gpio_controller.py
└── tests/
    ├── test_camera.py
    ├── test_detection.py
    ├── test_game.py
    └── test_hardware.py
```

### Module ownership

| Module | Owner | Responsibility |
|--------|-------|----------------|
| `camera/` | Contributor 1 | picamera2 capture, dummy mode for dev |
| `detection/` | Contributor 2 | OpenCV IR blob detection & centroid |
| `game/` | Contributor 3 | GameEngine, Target, ScoreManager |
| `ui/` | Contributor 4 | pygame window, target rendering, HUD |
| `hardware/` | Contributor 5 | GPIO trigger, status LED, simulation mode |

---

## Quick Start (uv)

[uv](https://github.com/astral-sh/uv) is a fast Python package manager that
handles virtual environments automatically.

```bash
# 1. Install uv (once per machine)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. Clone the repo
git clone https://github.com/VanshP2467/InfraStrike.git
cd InfraStrike

# 3. Create the virtual environment and install core dependencies
uv venv --system-site-packages
uv sync

# 4a. On Raspberry Pi – also install Pi-specific packages
uv sync --extra pi

# 4b. Install dev tools (pytest, coverage)
uv sync --extra dev
```

The virtual environment is created at `.venv/` inside the project directory.
All subsequent commands automatically use it when run via `uv run`.

---

## Running the Game

```bash
# Via the installed script
uv run infrastrike

# Or directly
uv run python -m infrastrike.main
```

On a **desktop** (no Pi hardware):
- Camera → black frame (dummy mode)
- Trigger → **spacebar** simulates a trigger press
- The game is fully playable for UI/logic development

---

## Configuration

All tunable values live in `config/settings.py`:

```python
CAMERA_RESOLUTION      = (1280, 720)
CAMERA_FRAMERATE       = 60
IR_THRESHOLD_MIN       = 200   # blob brightness threshold
IR_BLOB_MIN_AREA       = 20    # min blob size (pixels)
GAME_ROUND_DURATION_SECONDS = 60
TARGET_SPAWN_INTERVAL_MS    = 1500
POINTS_PER_HIT         = 10
PENALTY_PER_MISS       = 5
GPIO_TRIGGER_PIN       = 17    # BCM pin
GPIO_LED_PIN           = 27    # BCM pin
```

Edit `config/settings.py` to tune sensitivity, scoring, and display without
touching module code.

---

## Running Tests

```bash
uv run pytest
```

All tests are hardware-independent and run on any machine. Pi-specific paths
(picamera2, RPi.GPIO) are mocked/skipped automatically when not available.

---

## Contributor Guide

1. **Fork & branch**: `git checkout -b feature/<your-module>-<description>`
2. **Own your module**: Each contributor should primarily edit their assigned
   module directory (see table above). Cross-module changes need PR review.
3. **Shared constants**: Add new config values to `config/settings.py` and
   import them in your module.
4. **Tests**: Add tests to the corresponding `tests/test_<module>.py` file.
5. **No Pi required**: Use dummy/simulation modes during development; hardware
   integration is tested on the Pi only.
6. **PR**: Open a pull request against `main`; at least one other contributor
   must review before merging.

