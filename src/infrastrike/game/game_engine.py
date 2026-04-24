"""
GameEngine – central game-state machine.

Contributor 3 owns this module.

Responsibilities
----------------
* Manage the overall game lifecycle: IDLE → RUNNING → GAME_OVER.
* Spawn targets on a configurable interval.
* Process shot positions from the detection layer and update scores.
* Expose a snapshot ``GameState`` dataclass for the UI to render.
* Drive the Math Grid game mode: present math problems on a 4×4 grid,
  accept IR shots mapped to display coordinates, and score correct answers.
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
    GRID_COLS,
    GRID_MARGIN,
    GRID_ROWS,
    HUD_HEIGHT,
    MAX_TARGETS_ON_SCREEN,
    TARGET_LIFETIME_MS,
    TARGET_SPAWN_INTERVAL_MS,
)
from infrastrike.detection.ir_detector import ShotPosition
from infrastrike.game.score_manager import ScoreManager
from infrastrike.game.target import Target

# ── Math-grid constants ───────────────────────────────────────────────────────

_DEBOUNCE_COOLDOWN_S: float = 0.3   # minimum seconds between counted shots
_FEEDBACK_DURATION_S: float = 0.8   # seconds to display correct/wrong feedback


@dataclass(frozen=True)
class MathProblem:
    """A single math question paired with its expected integer answer."""

    text: str
    answer: int


#: Pre-made problem bank (addition / subtraction; answers in 3–16).
PROBLEM_BANK: list[MathProblem] = [
    MathProblem("3 + 4 = ?", 7),
    MathProblem("8 - 3 = ?", 5),
    MathProblem("6 + 5 = ?", 11),
    MathProblem("12 - 4 = ?", 8),
    MathProblem("7 + 5 = ?", 12),
    MathProblem("9 - 6 = ?", 3),
    MathProblem("4 + 9 = ?", 13),
    MathProblem("6 + 8 = ?", 14),
    MathProblem("11 - 5 = ?", 6),
    MathProblem("7 + 2 = ?", 9),
    MathProblem("15 - 5 = ?", 10),
    MathProblem("8 + 8 = ?", 16),
]


def _generate_grid(answer: int, rows: int = GRID_ROWS, cols: int = GRID_COLS) -> list[list[int]]:
    """Return a *rows* × *cols* grid containing exactly one cell equal to *answer*.

    All other cells are unique distractor numbers drawn from 1–20 (excluding
    the answer so the correct cell is unambiguous).
    """
    total = rows * cols
    pool = [n for n in range(1, 21) if n != answer]
    distractors = random.sample(pool, total - 1)
    numbers = distractors + [answer]
    random.shuffle(numbers)
    return [numbers[i * cols : (i + 1) * cols] for i in range(rows)]


# ── Game phases ───────────────────────────────────────────────────────────────


class GamePhase(Enum):
    IDLE = auto()
    RUNNING = auto()
    GAME_OVER = auto()


# ── GameState snapshot ────────────────────────────────────────────────────────


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
    # ── Math grid ────────────────────────────────────────────────────────────
    math_score: int = 0
    current_problem: str = ""
    grid_numbers: list[list[int]] = field(default_factory=list)
    last_selected_cell: tuple[int, int] | None = None
    feedback: str = ""  # "correct" | "wrong" | ""


# ── GameEngine ────────────────────────────────────────────────────────────────


class GameEngine:
    """Drives the core game loop logic.

    Example usage::

        engine = GameEngine()
        engine.start()
        while engine.is_running():
            engine.update(shot_position=pos, camera_frame_shape=frame.shape)
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

        # Math-grid internal state (initialised in start()).
        self._math_score: int = 0
        self._problem_idx: int = 0
        self._current_problem: MathProblem = PROBLEM_BANK[0]
        self._grid_numbers: list[list[int]] = []
        self._last_selected_cell: tuple[int, int] | None = None
        self._feedback: str = ""
        self._feedback_until: float = 0.0
        self._prev_shot_was_none: bool = True
        self._last_shot_time: float = 0.0

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Begin a new game round."""
        self._phase = GamePhase.RUNNING
        self._score_manager.reset()
        self._targets.clear()
        self._round_start = time.monotonic()
        self._last_spawn = self._round_start
        self._last_shot = None

        # Reset math-grid state.
        self._math_score = 0
        self._problem_idx = 0
        self._current_problem = PROBLEM_BANK[0]
        self._grid_numbers = _generate_grid(self._current_problem.answer)
        self._last_selected_cell = None
        self._feedback = ""
        self._feedback_until = 0.0
        self._prev_shot_was_none = True
        self._last_shot_time = 0.0

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
        camera_frame_shape: tuple[int, int, int] | None = None,
    ) -> None:
        """Advance game state by one frame.

        Parameters
        ----------
        shot_position:
            IR blob centroid from the detector (camera-frame pixel coords), or
            ``None`` if no flash seen.
        camera_frame_shape:
            ``frame.shape`` from the camera layer – used to map camera coords
            to display coords.  When ``None`` the coordinates are assumed to
            already be in display space (safe when both resolutions are equal).
        """
        if self._phase != GamePhase.RUNNING:
            # Still track edge even when not running so first update is clean.
            self._prev_shot_was_none = shot_position is None
            return

        now = time.monotonic()

        # ── Clear expired feedback ───────────────────────────────────────────
        if self._feedback and now >= self._feedback_until:
            self._feedback = ""

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
        if shot_position is not None:
            self._last_shot = shot_position

            # Target-shooting: every detected blob fires at targets.
            hit_any = False
            for target in self._targets:
                if target.check_hit(shot_position.x, shot_position.y):
                    self._score_manager.register_hit()
                    hit_any = True
                    break
            if not hit_any:
                self._score_manager.register_miss()
            self._targets = [t for t in self._targets if t.is_active]

            # Math-grid: fire only on rising edge (None → detected) + cooldown.
            if self._prev_shot_was_none and (now - self._last_shot_time) >= _DEBOUNCE_COOLDOWN_S:
                self._last_shot_time = now
                self._process_math_shot(shot_position, camera_frame_shape)

        self._prev_shot_was_none = shot_position is None

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
            math_score=self._math_score,
            current_problem=self._current_problem.text,
            grid_numbers=[row[:] for row in self._grid_numbers],
            last_selected_cell=self._last_selected_cell,
            feedback=self._feedback,
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

    def _process_math_shot(
        self,
        shot: ShotPosition,
        frame_shape: tuple[int, int, int] | None,
    ) -> None:
        """Map shot coordinates to display space, determine hit cell, update math score."""
        # Convert camera-frame coords → display coords.
        if frame_shape is not None:
            frame_h, frame_w = frame_shape[:2]
            disp_x = int(shot.x * self._screen_width / frame_w)
            disp_y = int(shot.y * self._screen_height / frame_h)
        else:
            disp_x, disp_y = shot.x, shot.y

        # Determine which grid cell was hit (if any) using pure arithmetic.
        cell = self._map_to_cell(disp_x, disp_y)
        self._last_selected_cell = cell

        if cell is None:
            return

        row, col = cell
        value = self._grid_numbers[row][col]
        now = time.monotonic()
        if value == self._current_problem.answer:
            self._math_score += 1
            self._feedback = "correct"
            self._feedback_until = now + _FEEDBACK_DURATION_S
            self._advance_problem()
        else:
            self._feedback = "wrong"
            self._feedback_until = now + _FEEDBACK_DURATION_S

    def _map_to_cell(self, disp_x: int, disp_y: int) -> tuple[int, int] | None:
        """Map a display-space point to a (row, col) cell index, or ``None`` if outside."""
        grid_left = GRID_MARGIN
        grid_top = HUD_HEIGHT + GRID_MARGIN
        grid_w = self._screen_width - 2 * GRID_MARGIN
        grid_h = self._screen_height - HUD_HEIGHT - 2 * GRID_MARGIN

        if not (grid_left <= disp_x < grid_left + grid_w and grid_top <= disp_y < grid_top + grid_h):
            return None

        col = int((disp_x - grid_left) * GRID_COLS / grid_w)
        row = int((disp_y - grid_top) * GRID_ROWS / grid_h)
        col = max(0, min(GRID_COLS - 1, col))
        row = max(0, min(GRID_ROWS - 1, row))
        return (row, col)

    def _advance_problem(self) -> None:
        """Move to the next problem in the bank and regenerate the grid."""
        self._problem_idx = (self._problem_idx + 1) % len(PROBLEM_BANK)
        self._current_problem = PROBLEM_BANK[self._problem_idx]
        self._grid_numbers = _generate_grid(self._current_problem.answer)
        self._last_selected_cell = None
