"""Centralized visual theme for InfraStrike's arcade UI."""

from __future__ import annotations

import logging

import pygame

from infrastrike.path_utils import asset_path

logger = logging.getLogger(__name__)

# Font assets
PIXEL_FONT_FILE = ("fonts", "PressStart2P-Regular.ttf")

# Pixel-friendly integer sizes
HUD_FONT_SIZE = 18
HUD_LARGE_FONT_SIZE = 36
GRID_NUMBER_FONT_SIZE = 34
TITLE_FONT_SIZE = 72

# Arcade palette
BG_NAVY = (7, 12, 38)
BG_NAVY_LIGHT = (12, 25, 76)
PANEL_BLUE = (20, 40, 120)
PANEL_BORDER = (166, 203, 255)
ACCENT_YELLOW = (255, 219, 58)
ACCENT_CYAN = (74, 232, 255)
TEXT_WHITE = (241, 248, 255)
WARNING_RED = (255, 71, 87)
SUCCESS_GREEN = (73, 242, 124)
GRID_LINE = (112, 188, 255)
GRID_CELL_BG = (14, 25, 70)
GRID_SELECTION = (255, 219, 58, 90)
GRID_CORRECT = (73, 242, 124, 110)
GRID_WRONG = (255, 71, 87, 110)

# Overlays/effects
CAMERA_DIM_OVERLAY = (6, 12, 36, 90)
HUD_OVERLAY = (0, 0, 0, 140)
GAME_OVER_OVERLAY = (0, 0, 0, 180)
SCANLINE_COLOUR = (0, 0, 0, 35)
SCANLINE_STEP = 4


def load_pixel_font(size: int, *, bold: bool = False) -> pygame.font.Font:
    """Load the embedded pixel font with a robust fallback to default pygame font."""
    try:
        font_path = asset_path(*PIXEL_FONT_FILE)
        return pygame.font.Font(str(font_path), size)
    except Exception as exc:  # pragma: no cover - fallback path
        logger.warning("Pixel font not loaded, using fallback font: %s", exc)
        return pygame.font.SysFont("monospace", size, bold=bold)
