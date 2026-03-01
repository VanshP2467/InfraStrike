"""
GameEngine – central game-state machine.

Contributor 3 owns this module.

Responsibilities
----------------
* Manage the overall game lifecycle: IDLE → RUNNING → GAME_OVER.
* Spawn targets on a configurable interval.
* Process shot positions from the detection layer and update scores.
* Expose a snapshot ``GameState`` dataclass for the UI to render.
"""

from __future__ import annotations

import random
import time
from dataclasses import dataclass, field
from enum import Enum, auto

from config.settings import (
    DISPLAY_HEIGHT,
    DISPLAY_WIDTH,
    GAME_ROUND_DURATION_SECONDS,
    MAX_TARGETS_ON_SCREEN,
    TARGET_LIFETIME_MS,
    TARGET_SPAWN_INTERVAL_MS,
)
from infrastrike.detection.ir_detector import ShotPosition
from infrastrike.game.score_manager import ScoreManager
from infrastrike.game.target import Target


class GamePhase(Enum):
    IDLE = auto()
    RUNNING = auto()
    GAME_OVER = auto()


@dataclass
class GameState:
    """Immutable snapshot of the game world passed to the UI each frame."""

    phase: GamePhase
    targets: list[Target]
    score: int
    hits: int
    misses: int
    accuracy: float
    time_remaining_seconds: float
    last_shot_position: ShotPosition | None = None


class GameEngine:
    """Drives the core game loop logic.

    Example usage::

        engine = GameEngine()
        engine.start()
        while engine.is_running():
            engine.update(shot_position=pos, trigger_pressed=True)
            state = engine.get_state()
    """

    def __init__(
        self,
        round_duration: int = GAME_ROUND_DURATION_SECONDS,
        spawn_interval_ms: int = TARGET_SPAWN_INTERVAL_MS,
        target_lifetime_ms: int = TARGET_LIFETIME_MS,
        max_targets: int = MAX_TARGETS_ON_SCREEN,
        screen_width: int = DISPLAY_WIDTH,
        screen_height: int = DISPLAY_HEIGHT,
    ) -> None:
        self._round_duration = round_duration
        self._spawn_interval_ms = spawn_interval_ms
        self._target_lifetime_ms = target_lifetime_ms
        self._max_targets = max_targets
        self._screen_width = screen_width
        self._screen_height = screen_height

        self._phase = GamePhase.IDLE
        self._score_manager = ScoreManager()
        self._targets: list[Target] = []
        self._round_start: float = 0.0
        self._last_spawn: float = 0.0
        self._last_shot: ShotPosition | None = None

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Begin a new game round."""
        self._phase = GamePhase.RUNNING
        self._score_manager.reset()
        self._targets.clear()
        self._round_start = time.monotonic()
        self._last_spawn = self._round_start
        self._last_shot = None

    def stop(self) -> None:
        """Force the round to end immediately."""
        self._phase = GamePhase.GAME_OVER

    def is_running(self) -> bool:
        """``True`` while the round is in progress."""
        return self._phase == GamePhase.RUNNING

    # ── Update ────────────────────────────────────────────────────────────────

    def update(
        self,
        shot_position: ShotPosition | None,
        trigger_pressed: bool,
    ) -> None:
        """Advance game state by one frame.

        Parameters
        ----------
        shot_position:
            IR blob centroid from the detector, or ``None`` if no shot seen.
        trigger_pressed:
            Whether the physical trigger button is currently held.
        """
        if self._phase != GamePhase.RUNNING:
            return

        now = time.monotonic()

        # ── Check round timer ────────────────────────────────────────────────
        elapsed = now - self._round_start
        if elapsed >= self._round_duration:
            self._phase = GamePhase.GAME_OVER
            return

        # ── Spawn new targets ────────────────────────────────────────────────
        elapsed_since_spawn_ms = (now - self._last_spawn) * 1000
        if (
            elapsed_since_spawn_ms >= self._spawn_interval_ms
            and len(self._targets) < self._max_targets
        ):
            self._spawn_target()
            self._last_spawn = now

        # ── Expire old targets ────────────────────────────────────────────────
        expired = [t for t in self._targets if t.is_expired]
        for t in expired:
            self._score_manager.register_miss()
        self._targets = [t for t in self._targets if t.is_active]

        # ── Process shot ─────────────────────────────────────────────────────
        if shot_position is not None and trigger_pressed:
            self._last_shot = shot_position
            hit_any = False
            for target in self._targets:
                if target.check_hit(shot_position.x, shot_position.y):
                    self._score_manager.register_hit()
                    hit_any = True
                    break
            if not hit_any:
                self._score_manager.register_miss()
            # Remove hit targets.
            self._targets = [t for t in self._targets if t.is_active]

    # ── State snapshot ────────────────────────────────────────────────────────

    def get_state(self) -> GameState:
        """Return an immutable snapshot of the current game state."""
        elapsed = time.monotonic() - self._round_start
        time_remaining = max(0.0, self._round_duration - elapsed)
        return GameState(
            phase=self._phase,
            targets=list(self._targets),
            score=self._score_manager.score,
            hits=self._score_manager.hits,
            misses=self._score_manager.misses,
            accuracy=self._score_manager.accuracy,
            time_remaining_seconds=time_remaining,
            last_shot_position=self._last_shot,
        )

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _spawn_target(self) -> None:
        """Create a new target at a random position within the safe margin."""
        margin = 60  # pixels from screen edge
        x = random.randint(margin, self._screen_width - margin)
        y = random.randint(margin, self._screen_height - margin)
        self._targets.append(
            Target(x=x, y=y, lifetime_ms=self._target_lifetime_ms)
        )
