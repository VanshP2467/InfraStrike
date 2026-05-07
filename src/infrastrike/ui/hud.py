"""HUD – Heads-Up Display overlay."""

from __future__ import annotations

import pygame

from config.settings import DISPLAY_HEIGHT, DISPLAY_WIDTH, HUD_HEIGHT
from infrastrike.game.game_engine import GamePhase, GameState
from infrastrike.ui.theme import (
    ACCENT_CYAN,
    ACCENT_YELLOW,
    GAME_OVER_OVERLAY,
    HUD_FONT_SIZE,
    HUD_LARGE_FONT_SIZE,
    PANEL_BLUE,
    PANEL_BORDER,
    SUCCESS_GREEN,
    TEXT_WHITE,
    WARNING_RED,
    load_pixel_font,
)


class HUD:
    """Renders all on-screen UI overlays on a pygame Surface."""

    def __init__(self, surface: pygame.Surface, font_size: int = 28) -> None:
        self._surface = surface
        _ = font_size
        self._font = load_pixel_font(HUD_FONT_SIZE, bold=True)
        self._large_font = load_pixel_font(HUD_LARGE_FONT_SIZE, bold=True)

    def draw(self, state: GameState) -> None:
        """Draw all HUD elements for the current *state*."""
        self._draw_hud_panel()
        self._draw_score(state)
        self._draw_timer(state)
        self._draw_problem(state)

        if state.last_shot_position is not None:
            self._draw_crosshair(state.last_shot_position.x, state.last_shot_position.y)
        if state.phase == GamePhase.GAME_OVER:
            self._draw_game_over(state)

    def _draw_hud_panel(self) -> None:
        panel_rect = pygame.Rect(8, 8, DISPLAY_WIDTH - 16, HUD_HEIGHT - 16)
        pygame.draw.rect(self._surface, PANEL_BLUE, panel_rect)
        pygame.draw.rect(self._surface, PANEL_BORDER, panel_rect, width=3)

    def _draw_score(self, state: GameState) -> None:
        text = self._font.render(f"SCORE  {state.score:>3}", True, ACCENT_YELLOW)
        self._surface.blit(text, (24, 24))

    def _draw_timer(self, state: GameState) -> None:
        seconds = int(state.time_remaining_seconds)
        colour = WARNING_RED if seconds <= 10 else TEXT_WHITE
        text = self._font.render(f"TIME   {seconds:>3}s", True, colour)
        self._surface.blit(text, (DISPLAY_WIDTH - text.get_width() - 24, 24))

    def _draw_problem(self, state: GameState) -> None:
        """Draw the current math problem text centered in the HUD."""
        problem_surf = self._font.render(state.current_problem, True, ACCENT_CYAN)
        cx = DISPLAY_WIDTH // 2
        self._surface.blit(problem_surf, problem_surf.get_rect(center=(cx, 32)))

    def _draw_crosshair(self, x: int, y: int, size: int = 20) -> None:
        colour = ACCENT_CYAN
        thickness = 2
        pygame.draw.line(self._surface, colour, (x - size, y), (x + size, y), thickness)
        pygame.draw.line(self._surface, colour, (x, y - size), (x, y + size), thickness)
        pygame.draw.circle(self._surface, colour, (x, y), size // 2, thickness)

    def _draw_game_over(self, state: GameState) -> None:
        overlay = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
        overlay.fill(GAME_OVER_OVERLAY)
        self._surface.blit(overlay, (0, 0))

        cx = DISPLAY_WIDTH // 2
        title = self._large_font.render("GAME OVER", True, WARNING_RED)
        self._surface.blit(title, title.get_rect(center=(cx, DISPLAY_HEIGHT // 2 - 80)))

        score_text = self._font.render(f"FINAL SCORE: {state.score}", True, ACCENT_YELLOW)
        self._surface.blit(
            score_text, score_text.get_rect(center=(cx, DISPLAY_HEIGHT // 2))
        )

        restart = self._font.render(
            "PRESS ENTER TO PLAY AGAIN  |  ESC TO QUIT", True, SUCCESS_GREEN
        )
        self._surface.blit(
            restart, restart.get_rect(center=(cx, DISPLAY_HEIGHT // 2 + 70))
        )
