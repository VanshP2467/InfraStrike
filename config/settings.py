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
