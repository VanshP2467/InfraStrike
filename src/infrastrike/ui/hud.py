"""
HUD – Heads-Up Display overlay.

Contributor 4 owns this module (alongside display.py).

Responsibilities
----------------
* Draw the score, hit/miss counts, accuracy percentage and round timer on top
  of the game surface using pygame.
* Provide a cross-hair cursor at the last known shot position.
* Provide a round-end overlay showing final stats.
"""

from __future__ import annotations

import pygame

import sys

from config.settings import DISPLAY_HEIGHT, DISPLAY_WIDTH
from infrastrike.game.game_engine import GamePhase, GameState


# ── Colours ───────────────────────────────────────────────────────────────────
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
YELLOW = (255, 220, 0)
CYAN = (0, 220, 220)
DARK_OVERLAY = (0, 0, 0, 160)  # RGBA for semi-transparent surface


class HUD:
    """Renders all on-screen UI overlays on a pygame Surface.

    Parameters
    ----------
    surface:
        The pygame surface to draw on (typically the main display surface).
    font_size:
        Base font size for HUD text.
    """

    def __init__(self, surface: pygame.Surface, font_size: int = 28) -> None:
        self._surface = surface
        self._font = pygame.font.SysFont("monospace", font_size, bold=True)
        self._large_font = pygame.font.SysFont("monospace", font_size * 2, bold=True)

    # ── Public API ────────────────────────────────────────────────────────────

    def draw(self, state: GameState) -> None:
        """Draw all HUD elements for the current *state*.

        Call this once per frame after the game world has been rendered.
        """
        self._draw_score(state)
        self._draw_timer(state)
        self._draw_stats(state)
        if state.current_problem:
            self._draw_problem(state)
        if state.last_shot_position is not None:
            self._draw_crosshair(state.last_shot_position.x, state.last_shot_position.y)
        if state.phase == GamePhase.GAME_OVER:
            self._draw_game_over(state)

    # ── Private helpers ───────────────────────────────────────────────────────

    def _draw_score(self, state: GameState) -> None:
        text = self._font.render(f"SCORE  {state.score:>6}", True, YELLOW)
        self._surface.blit(text, (10, 10))

    def _draw_timer(self, state: GameState) -> None:
        seconds = int(state.time_remaining_seconds)
        colour = RED if seconds <= 10 else WHITE
        text = self._font.render(f"TIME   {seconds:>3}s", True, colour)
        self._surface.blit(text, (DISPLAY_WIDTH - text.get_width() - 10, 10))

    def _draw_stats(self, state: GameState) -> None:
        accuracy_pct = state.accuracy * 100
        lines = [
            f"HITS   {state.hits}",
            f"MISSES {state.misses}",
            f"ACC    {accuracy_pct:.0f}%",
        ]
        y = 50
        for line in lines:
            text = self._font.render(line, True, WHITE)
            self._surface.blit(text, (10, y))
            y += text.get_height() + 4

    def _draw_crosshair(self, x: int, y: int, size: int = 20) -> None:
        colour = CYAN
        thickness = 2
        pygame.draw.line(self._surface, colour, (x - size, y), (x + size, y), thickness)
        pygame.draw.line(self._surface, colour, (x, y - size), (x, y + size), thickness)
        pygame.draw.circle(self._surface, colour, (x, y), size // 2, thickness)

    def _draw_problem(self, state: GameState) -> None:
        """Draw the current math problem centered in the HUD, plus the math score."""
        # Problem text centered horizontally at the top of the HUD.
        problem_surf = self._font.render(state.current_problem, True, CYAN)
        cx = DISPLAY_WIDTH // 2
        self._surface.blit(problem_surf, problem_surf.get_rect(center=(cx, 20)))

        # Math score on the right side below the round timer.
        math_surf = self._font.render(f"MATH   {state.math_score}", True, GREEN)
        self._surface.blit(math_surf, (DISPLAY_WIDTH - math_surf.get_width() - 10, 50))

    def _draw_game_over(self, state: GameState) -> None:
        # Semi-transparent dark overlay.
        overlay = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT), pygame.SRCALPHA)
        overlay.fill(DARK_OVERLAY)
        self._surface.blit(overlay, (0, 0))

        cx = DISPLAY_WIDTH // 2

        title = self._large_font.render("GAME OVER", True, RED)
        self._surface.blit(title, title.get_rect(center=(cx, DISPLAY_HEIGHT // 2 - 80)))

        score_text = self._font.render(f"Final Score: {state.score}", True, YELLOW)
        self._surface.blit(
            score_text, score_text.get_rect(center=(cx, DISPLAY_HEIGHT // 2))
        )

        math_text = self._font.render(f"Math Score: {state.math_score}", True, CYAN)
        self._surface.blit(
            math_text, math_text.get_rect(center=(cx, DISPLAY_HEIGHT // 2 + 40))
        )

        acc_text = self._font.render(
            f"Accuracy: {state.accuracy * 100:.0f}%  Hits: {state.hits}  Misses: {state.misses}",
            True,
            WHITE,
        )
        self._surface.blit(
            acc_text, acc_text.get_rect(center=(cx, DISPLAY_HEIGHT // 2 + 90))
        )

        restart = self._font.render("Press ENTER to play again  |  ESC to quit", True, GREEN)
        self._surface.blit(
            restart, restart.get_rect(center=(cx, DISPLAY_HEIGHT // 2 + 140))
        )
