"""Tests for game engine, score manager and target (Contributor 3)."""

import time

import pytest

from infrastrike.game.game_engine import (
    GameEngine,
    GamePhase,
    GameState,
    MathProblem,
    PROBLEM_BANK,
    _generate_grid,
)
from infrastrike.game.score_manager import ScoreManager
from infrastrike.game.target import Target


# ── Target ────────────────────────────────────────────────────────────────────

class TestTarget:
    def test_new_target_is_active(self):
        t = Target(x=100, y=100, radius=40, lifetime_ms=3000)
        assert t.is_active

    def test_hit_inside_radius_marks_hit(self):
        t = Target(x=100, y=100, radius=40)
        assert t.check_hit(100, 100) is True
        assert t.is_hit

    def test_miss_outside_radius(self):
        t = Target(x=100, y=100, radius=40)
        assert t.check_hit(200, 200) is False
        assert not t.is_hit

    def test_hit_target_no_longer_active(self):
        t = Target(x=100, y=100, radius=40)
        t.check_hit(100, 100)
        assert not t.is_active

    def test_expired_target_not_active(self):
        t = Target(x=100, y=100, radius=40, lifetime_ms=1)
        time.sleep(0.01)
        assert t.is_expired
        assert not t.is_active

    def test_time_remaining_decreases(self):
        t = Target(x=100, y=100, lifetime_ms=5000)
        remaining1 = t.time_remaining_ms()
        time.sleep(0.05)
        remaining2 = t.time_remaining_ms()
        assert remaining2 < remaining1

    def test_cannot_hit_already_expired_target(self):
        t = Target(x=100, y=100, radius=40, lifetime_ms=1)
        time.sleep(0.01)
        result = t.check_hit(100, 100)
        assert result is False


# ── ScoreManager ──────────────────────────────────────────────────────────────

class TestScoreManager:
    def test_initial_score_zero(self):
        sm = ScoreManager()
        assert sm.score == 0

    def test_hit_adds_points(self):
        sm = ScoreManager(points_per_hit=10, penalty_per_miss=5)
        sm.register_hit()
        assert sm.score == 10

    def test_miss_subtracts_points(self):
        sm = ScoreManager(points_per_hit=10, penalty_per_miss=5)
        sm.register_hit()
        sm.register_miss()
        assert sm.score == 5

    def test_score_never_negative(self):
        sm = ScoreManager(points_per_hit=10, penalty_per_miss=5)
        sm.register_miss()
        assert sm.score == 0

    def test_accuracy_with_no_shots(self):
        sm = ScoreManager()
        assert sm.accuracy == 0.0

    def test_accuracy_calculation(self):
        sm = ScoreManager()
        sm.register_hit()
        sm.register_hit()
        sm.register_miss()
        assert sm.accuracy == pytest.approx(2 / 3)

    def test_reset_clears_state(self):
        sm = ScoreManager(points_per_hit=10, penalty_per_miss=5)
        sm.register_hit()
        sm.reset()
        assert sm.score == 0
        assert sm.hits == 0
        assert sm.misses == 0


# ── GameEngine ────────────────────────────────────────────────────────────────

class TestGameEngine:
    def _make_engine(self, duration: int = 60) -> GameEngine:
        return GameEngine(
            round_duration=duration,
            spawn_interval_ms=500,
            target_lifetime_ms=3000,
            max_targets=5,
            screen_width=640,
            screen_height=480,
        )

    def test_initial_phase_idle(self):
        engine = self._make_engine()
        assert not engine.is_running()

    def test_start_sets_running(self):
        engine = self._make_engine()
        engine.start()
        assert engine.is_running()

    def test_stop_ends_running(self):
        engine = self._make_engine()
        engine.start()
        engine.stop()
        assert not engine.is_running()

    def test_get_state_returns_game_state(self):
        engine = self._make_engine()
        engine.start()
        state = engine.get_state()
        assert isinstance(state, GameState)

    def test_time_remaining_decreases(self):
        engine = self._make_engine(duration=60)
        engine.start()
        state1 = engine.get_state()
        time.sleep(0.05)
        state2 = engine.get_state()
        assert state2.time_remaining_seconds < state1.time_remaining_seconds

    def test_round_ends_when_time_expires(self):
        engine = self._make_engine(duration=1)
        engine.start()
        time.sleep(1.1)
        from infrastrike.detection.ir_detector import ShotPosition
        engine.update(shot_position=None)
        assert engine.get_state().phase == GamePhase.GAME_OVER

    def test_hit_increases_score(self):
        engine = self._make_engine()
        engine.start()
        # Force a target to be present at a known position.
        from infrastrike.game.target import Target
        engine._targets = [Target(x=300, y=200, radius=40, lifetime_ms=5000)]

        from infrastrike.detection.ir_detector import ShotPosition
        engine.update(shot_position=ShotPosition(300, 200))
        assert engine.get_state().score > 0


# ── Math Grid ─────────────────────────────────────────────────────────────────

class TestGenerateGrid:
    def test_grid_dimensions(self):
        grid = _generate_grid(answer=7)
        assert len(grid) == 4
        assert all(len(row) == 4 for row in grid)

    def test_answer_appears_exactly_once(self):
        for answer in [3, 7, 11, 14]:
            grid = _generate_grid(answer=answer)
            flat = [v for row in grid for v in row]
            assert flat.count(answer) == 1

    def test_no_answer_in_distractors(self):
        answer = 5
        grid = _generate_grid(answer=answer)
        flat = [v for row in grid for v in row]
        # Exactly one occurrence of the answer confirmed by prior test; all
        # values except that one must differ from answer.
        assert flat.count(answer) == 1

    def test_all_cells_in_valid_range(self):
        grid = _generate_grid(answer=9)
        flat = [v for row in grid for v in row]
        assert all(1 <= v <= 20 for v in flat)

    def test_distractors_are_unique(self):
        # With 16 cells and a pool of 19 numbers, all values should be distinct.
        grid = _generate_grid(answer=7)
        flat = [v for row in grid for v in row]
        assert len(flat) == len(set(flat))


class TestMathGrid:
    """Integration tests for the math-grid game mode inside GameEngine."""

    def _make_engine(self) -> GameEngine:
        return GameEngine(
            round_duration=60,
            spawn_interval_ms=99999,  # suppress target spawning
            target_lifetime_ms=3000,
            max_targets=0,
            screen_width=1280,
            screen_height=720,
        )

    def _shot_at_cell(self, engine: GameEngine, row: int, col: int):
        """Return a ShotPosition aimed at the center of the given grid cell."""
        from infrastrike.detection.ir_detector import ShotPosition
        from config.settings import GRID_MARGIN, HUD_HEIGHT, GRID_ROWS, GRID_COLS

        grid_left = GRID_MARGIN
        grid_top = HUD_HEIGHT + GRID_MARGIN
        grid_w = engine._screen_width - 2 * GRID_MARGIN
        grid_h = engine._screen_height - HUD_HEIGHT - 2 * GRID_MARGIN

        cell_w = grid_w / GRID_COLS
        cell_h = grid_h / GRID_ROWS
        x = int(grid_left + (col + 0.5) * cell_w)
        y = int(grid_top + (row + 0.5) * cell_h)
        return ShotPosition(x, y)

    def _find_answer_cell(self, engine: GameEngine) -> tuple[int, int]:
        """Return the (row, col) of the cell whose value matches the current answer."""
        answer = engine._current_problem.answer
        for r, row in enumerate(engine._grid_numbers):
            for c, val in enumerate(row):
                if val == answer:
                    return (r, c)
        raise AssertionError("Answer not found in grid")  # should never happen

    def test_initial_state_has_problem(self):
        engine = self._make_engine()
        engine.start()
        state = engine.get_state()
        assert state.current_problem != ""
        assert len(state.grid_numbers) == 4

    def test_no_shot_does_not_crash(self):
        engine = self._make_engine()
        engine.start()
        engine.update(shot_position=None)
        state = engine.get_state()
        assert state.math_score == 0

    def test_correct_hit_increments_math_score(self):
        engine = self._make_engine()
        engine.start()

        row, col = self._find_answer_cell(engine)
        shot = self._shot_at_cell(engine, row, col)

        engine.update(shot_position=shot)
        assert engine.get_state().math_score == 1

    def test_wrong_hit_does_not_increment_math_score(self):
        engine = self._make_engine()
        engine.start()

        answer = engine._current_problem.answer
        # Find a cell that does NOT contain the answer.
        wrong_row, wrong_col = None, None
        for r, row_vals in enumerate(engine._grid_numbers):
            for c, val in enumerate(row_vals):
                if val != answer:
                    wrong_row, wrong_col = r, c
                    break
            if wrong_row is not None:
                break

        shot = self._shot_at_cell(engine, wrong_row, wrong_col)
        engine.update(shot_position=shot)
        assert engine.get_state().math_score == 0

    def test_correct_hit_sets_correct_feedback(self):
        engine = self._make_engine()
        engine.start()

        row, col = self._find_answer_cell(engine)
        shot = self._shot_at_cell(engine, row, col)
        engine.update(shot_position=shot)
        assert engine.get_state().feedback == "correct"

    def test_wrong_hit_sets_wrong_feedback(self):
        engine = self._make_engine()
        engine.start()

        answer = engine._current_problem.answer
        wrong_row, wrong_col = None, None
        for r, row_vals in enumerate(engine._grid_numbers):
            for c, val in enumerate(row_vals):
                if val != answer:
                    wrong_row, wrong_col = r, c
                    break
            if wrong_row is not None:
                break

        shot = self._shot_at_cell(engine, wrong_row, wrong_col)
        engine.update(shot_position=shot)
        assert engine.get_state().feedback == "wrong"

    def test_correct_hit_advances_problem(self):
        engine = self._make_engine()
        engine.start()

        first_problem = engine.get_state().current_problem
        row, col = self._find_answer_cell(engine)
        shot = self._shot_at_cell(engine, row, col)
        engine.update(shot_position=shot)

        assert engine.get_state().current_problem != first_problem

    def test_debounce_prevents_double_count(self):
        """Rapid repeated shots (no cooldown gap) must count as one."""
        engine = self._make_engine()
        engine.start()

        row, col = self._find_answer_cell(engine)
        shot = self._shot_at_cell(engine, row, col)

        # First shot fires (rising edge: prev=None).
        engine.update(shot_position=shot)
        # Second shot immediately – same blob still visible, prev != None → skipped.
        engine.update(shot_position=shot)
        assert engine.get_state().math_score == 1

    def test_shot_outside_grid_does_not_score(self):
        from infrastrike.detection.ir_detector import ShotPosition

        engine = self._make_engine()
        engine.start()

        # Shoot in the HUD area (y=0 is well above the grid).
        shot = ShotPosition(x=640, y=10)
        engine.update(shot_position=shot)
        assert engine.get_state().math_score == 0

    def test_camera_coord_mapping(self):
        """Shot in camera-frame coords should be mapped correctly to display coords."""
        engine = self._make_engine()
        engine.start()

        row, col = self._find_answer_cell(engine)
        # Get the display-space shot for this cell.
        display_shot = self._shot_at_cell(engine, row, col)

        # Pretend camera is 640×360 (half of 1280×720 display).
        # Shot at camera (cx, cy) should map to display (cx*2, cy*2).
        from infrastrike.detection.ir_detector import ShotPosition
        camera_shot = ShotPosition(x=display_shot.x // 2, y=display_shot.y // 2)
        frame_shape = (360, 640, 3)  # (H, W, C)

        engine.update(shot_position=camera_shot, camera_frame_shape=frame_shape)
        assert engine.get_state().math_score == 1
