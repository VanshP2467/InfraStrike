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
CAMERA_EXPOSURE_TIME_US: int = 5000   # shutter time in microseconds (5 ms)
CAMERA_ANALOGUE_GAIN: float = 8.0     # sensor gain – raise if blobs are faint

# ── IR Detection ──────────────────────────────────────────────────────────────
# HSV range that isolates the bright IR blob in grayscale space.
IR_THRESHOLD_MIN: int = 200   # minimum pixel brightness (0-255)
IR_BLOB_MIN_AREA: int = 20    # minimum blob area in pixels to be considered a shot
IR_BLOB_MAX_AREA: int = 2000  # maximum blob area in pixels

# ── Display ───────────────────────────────────────────────────────────────────
DISPLAY_WIDTH: int = 1280
DISPLAY_HEIGHT: int = 720
DISPLAY_FPS: int = 60
DISPLAY_TITLE: str = "InfraStrike"
DISPLAY_FULLSCREEN: bool = False

# ── Game ──────────────────────────────────────────────────────────────────────
GAME_ROUND_DURATION_SECONDS: int = 60
TARGET_SPAWN_INTERVAL_MS: int = 1500   # milliseconds between new target spawns
TARGET_LIFETIME_MS: int = 3000         # milliseconds before a target disappears
MAX_TARGETS_ON_SCREEN: int = 5
POINTS_PER_HIT: int = 10
PENALTY_PER_MISS: int = 5

# ── Hardware / GPIO ───────────────────────────────────────────────────────────
GPIO_TRIGGER_PIN: int = 17   # BCM pin number for trigger button
GPIO_LED_PIN: int = 27       # BCM pin number for status LED
