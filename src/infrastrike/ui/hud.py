"""HUD – Heads-Up Display overlay."""

from __future__ import annotations

import pygame

from config.settings import DISPLAY_HEIGHT, DISPLAY_WIDTH
from infrastrike.game.game_engine import GamePhase, GameState

WHITE = (255, 255, 255)
RED = (220, 50, 50)
GREEN = (50, 220, 50)
YELLOW = (255, 220, 0)
CYAN = (0, 220, 220)
DARK_OVERLAY = (0, 0, 0, 160)


class HUD:
    """Renders all on-screen UI overlays on a pygame Surface."""

    def __init__(self, surface: pygame.Surface, font_size: int = 28) -> None:
        self._surface = surface
        self._font = pygame.font.SysFont("monospace", font_size, bold=True)
        self._large_font = pygame.font.SysFont("monospace", font_size * 2, bold=True)

    def draw(self, state: GameState) -> None:
        """Draw all HUD elements for the current *state*."""
        self._draw_score(state)
        self._draw_timer(state)
        self._draw_problem(state)

        if state.last_shot_position is not None:
            self._draw_crosshair(state.last_shot_position.x, state.last_shot_position.y)
        if state.phase == GamePhase.GAME_OVER:
            self._draw_game_over(state)

    def _draw_score(self, state: GameState) -> None:
        text = self._font.render(f"SCORE  {state.score:>3}", True, YELLOW)
        self._surface.blit(text, (10, 10))

    def _draw_timer(self, state: GameState) -> None:
        seconds = int(state.time_remaining_seconds)
        colour = RED if seconds <= 10 else WHITE
        text = self._font.render(f"TIME   {seconds:>3}s", True, colour)
        self._surface.blit(text, (DISPLAY_WIDTH - text.get_width() - 10, 10))

    def _draw_problem(self, state: GameState) -> None:
        """Draw the current math problem text centered in the HUD."""
        problem_surf = self._font.render(state.current_problem, True, CYAN)
        cx = DISPLAY_WIDTH // 2
        self._surface.blit(problem_surf, problem_surf.get_rect(center=(cx, 20)))

    def _draw_crosshair(self, x: int, y: int, size: int = 20) -> None:
        colour = CYAN
        thickness = 2
        pygame.draw.line(self._surface, colour, (x - size, y), (x + size, y), thickness)
        pygame.draw.line(self._surface, colour, (x, y - size), (x, y + size), thickness)
        pygame.draw.circle(self._surface, colour, (x, y), size // 2, thickness)

    def _draw_game_over(self, state: GameState) -> None:
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

        restart = self._font.render(
            "Press ENTER to play again  |  ESC to quit", True, GREEN
        )
        self._surface.blit(
            restart, restart.get_rect(center=(cx, DISPLAY_HEIGHT // 2 + 70))
        )
