"""Display – pygame window management and scene rendering."""

from __future__ import annotations

import logging

import cv2
import numpy as np
import pygame

from config.settings import (
    DISPLAY_FPS,
    DISPLAY_FULLSCREEN,
    DISPLAY_HEIGHT,
    DISPLAY_SHOW_CAMERA_FEED,
    DISPLAY_TITLE,
    DISPLAY_WIDTH,
    GRID_COLS,
    GRID_MARGIN,
    GRID_ROWS,
    HUD_HEIGHT,
)
from infrastrike.game.game_engine import GameState
from infrastrike.path_utils import asset_path
from infrastrike.ui.grid import GridSpec, cell_rects
from infrastrike.ui.hud import HUD

logger = logging.getLogger(__name__)

WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (80, 220, 80)
DARK_BG = (20, 20, 30)
GRID_LINE_COLOUR = (0, 255, 0)
GRID_LINE_WIDTH = 2
CELL_CORRECT_COLOUR = (0, 200, 0, 120)
CELL_WRONG_COLOUR = (220, 50, 50, 120)
CELL_NEUTRAL_COLOUR = (255, 200, 0, 80)


class Display:
    """Manages the pygame window and all rendering."""

    def __init__(
        self,
        width: int = DISPLAY_WIDTH,
        height: int = DISPLAY_HEIGHT,
        fps: int = DISPLAY_FPS,
        title: str = DISPLAY_TITLE,
        fullscreen: bool = DISPLAY_FULLSCREEN,
    ) -> None:
        self._width = width
        self._height = height
        self._fps = fps
        self._title = title
        self._fullscreen = fullscreen

        self._grid_rect = pygame.Rect(
            GRID_MARGIN,
            HUD_HEIGHT + GRID_MARGIN,
            self._width - 2 * GRID_MARGIN,
            self._height - HUD_HEIGHT - 2 * GRID_MARGIN,
        )
        self._grid_spec = GridSpec(rect=self._grid_rect, rows=GRID_ROWS, cols=GRID_COLS)
        self._grid_cells = cell_rects(self._grid_spec)

        flags = pygame.FULLSCREEN if fullscreen else 0
        self._screen = pygame.display.set_mode((width, height), flags)
        pygame.display.set_caption(title)

        self._clock = pygame.time.Clock()
        self._hud = HUD(self._screen)
        self._font = pygame.font.SysFont("monospace", 36, bold=True)

        self._start_bg: pygame.Surface | None = None
        try:
            bg_path = asset_path("images", "infrastrike_bg.png")
            loaded = pygame.image.load(str(bg_path)).convert()
            self._start_bg = pygame.transform.smoothscale(
                loaded, (self._width, self._height)
            )
        except Exception as exc:  # pragma: no cover - fallback path
            logger.warning("Start background image not loaded: %s", exc)

    def show_start_screen(self) -> None:
        """Block until the player presses ENTER or SPACE to start."""
        if self._start_bg is not None:
            self._screen.blit(self._start_bg, (0, 0))
        else:
            self._screen.fill(DARK_BG)

        title_font = pygame.font.SysFont("monospace", 72, bold=True)
        title_surf = title_font.render("InfraStrike", True, (200, 80, 80))
        subtitle = self._font.render(
            "Point your IR gun and pull the trigger!", True, WHITE
        )
        prompt = self._font.render(
            "Press ENTER or SPACE to start", True, (100, 220, 100)
        )

        cx, cy = self._width // 2, self._height // 2
        self._screen.blit(title_surf, title_surf.get_rect(center=(cx, cy - 100)))
        self._screen.blit(subtitle, subtitle.get_rect(center=(cx, cy)))
        self._screen.blit(prompt, prompt.get_rect(center=(cx, cy + 70)))
        pygame.display.flip()

        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN and event.key in (
                    pygame.K_RETURN,
                    pygame.K_SPACE,
                ):
                    waiting = False

    def render(self, state: GameState, camera_frame: np.ndarray) -> None:
        """Render one frame: background → grid → numbers → HUD."""
        if DISPLAY_SHOW_CAMERA_FEED:
            self._blit_camera_frame(camera_frame)
        elif self._start_bg is not None:
            self._screen.blit(self._start_bg, (0, 0))
        else:
            self._screen.fill(DARK_BG)

        self._draw_grid_in_rect(
            self._grid_rect,
            cols=self._grid_spec.cols,
            rows=self._grid_spec.rows,
            colour=GRID_LINE_COLOUR,
            width=GRID_LINE_WIDTH,
        )

        if state.grid_numbers:
            self._draw_grid_numbers(state.grid_numbers)

        if state.last_selected_cell is not None:
            row, col = state.last_selected_cell
            if state.feedback == "correct":
                highlight_colour = CELL_CORRECT_COLOUR
            elif state.feedback == "wrong":
                highlight_colour = CELL_WRONG_COLOUR
            else:
                highlight_colour = CELL_NEUTRAL_COLOUR
            self._draw_cell_highlight(row, col, highlight_colour)

        self._hud.draw(state)

        if state.feedback:
            self._draw_feedback(state.feedback)

        pygame.display.flip()
        self._clock.tick(self._fps)

    def quit(self) -> None:
        """Destroy the pygame window."""
        pygame.display.quit()
        logger.info("Display closed.")

    def _blit_camera_frame(self, bgr_frame: np.ndarray) -> None:
        """Convert an OpenCV BGR frame to a pygame surface and blit it."""
        rgb_frame = cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB)
        if (rgb_frame.shape[1], rgb_frame.shape[0]) != (self._width, self._height):
            rgb_frame = cv2.resize(rgb_frame, (self._width, self._height))
        surf = pygame.surfarray.make_surface(rgb_frame.swapaxes(0, 1))
        self._screen.blit(surf, (0, 0))

    def _draw_grid_in_rect(
        self,
        rect: pygame.Rect,
        cols: int = 4,
        rows: int = 4,
        colour: tuple[int, int, int] = (0, 255, 0),
        width: int = 2,
    ) -> None:
        for col in range(cols + 1):
            x = rect.left + int(col * rect.width / cols)
            pygame.draw.line(
                self._screen, colour, (x, rect.top), (x, rect.bottom), width
            )

        for row in range(rows + 1):
            y = rect.top + int(row * rect.height / rows)
            pygame.draw.line(
                self._screen, colour, (rect.left, y), (rect.right, y), width
            )

    def _draw_grid_numbers(self, grid_numbers: list[list[int]]) -> None:
        """Draw each grid value centered inside its cell."""
        for row_index, row in enumerate(grid_numbers):
            for col_index, value in enumerate(row):
                cell = self._grid_cells[row_index][col_index]
                text_surf = self._font.render(str(value), True, WHITE)
                self._screen.blit(text_surf, text_surf.get_rect(center=cell.center))

    def _draw_cell_highlight(
        self,
        row: int,
        col: int,
        colour: tuple[int, int, int, int],
    ) -> None:
        """Draw a semi-transparent coloured rectangle over *cell* (row, col)."""
        cell = self._grid_cells[row][col]
        highlight = pygame.Surface((cell.width, cell.height), pygame.SRCALPHA)
        highlight.fill(colour)
        self._screen.blit(highlight, cell.topleft)

    def _draw_feedback(self, feedback: str) -> None:
        """Draw a brief CORRECT!/WRONG! banner near the top of the playfield."""
        if feedback == "correct":
            text_surf = self._font.render("CORRECT!", True, GREEN)
        elif feedback == "wrong":
            text_surf = self._font.render("WRONG!", True, RED)
        else:
            return

        rect = text_surf.get_rect(center=(self._width // 2, HUD_HEIGHT + 50))
        self._screen.blit(text_surf, rect)
