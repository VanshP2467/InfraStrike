"""Tests for the Math Grid game engine."""

import time

from config.settings import GRID_COLS, GRID_MARGIN, GRID_ROWS, HUD_HEIGHT
from infrastrike.detection.ir_detector import ShotPosition
from infrastrike.game.game_engine import (
    GameEngine,
    GamePhase,
    GameState,
    _generate_grid,
)


class TestGameEngineLifecycle:
    def _make_engine(self, duration: int = 60) -> GameEngine:
        return GameEngine(
            round_duration=duration,
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
        engine.update(shot_position=None)
        assert engine.get_state().phase == GamePhase.GAME_OVER


class TestGenerateGrid:
    def test_grid_dimensions(self):
        grid = _generate_grid(answer=7)
        assert len(grid) == 4
        assert all(len(row) == 4 for row in grid)

    def test_answer_appears_exactly_once(self):
        for answer in [3, 7, 11, 14]:
            grid = _generate_grid(answer=answer)
            flat = [value for row in grid for value in row]
            assert flat.count(answer) == 1

    def test_all_cells_in_valid_range(self):
        grid = _generate_grid(answer=9)
        flat = [value for row in grid for value in row]
        assert all(1 <= value <= 20 for value in flat)

    def test_distractors_are_unique(self):
        grid = _generate_grid(answer=7)
        flat = [value for row in grid for value in row]
        assert len(flat) == len(set(flat))


class TestMathGrid:
    """Integration tests for Math Grid behavior."""

    def _make_engine(self) -> GameEngine:
        return GameEngine(
            round_duration=60,
            screen_width=1280,
            screen_height=720,
        )

    def _shot_at_cell(self, engine: GameEngine, row: int, col: int) -> ShotPosition:
        """Return a ShotPosition aimed at the center of the given grid cell."""
        grid_left = GRID_MARGIN
        grid_top = HUD_HEIGHT + GRID_MARGIN
        grid_width = engine._screen_width - 2 * GRID_MARGIN
        grid_height = engine._screen_height - HUD_HEIGHT - 2 * GRID_MARGIN

        cell_width = grid_width / GRID_COLS
        cell_height = grid_height / GRID_ROWS
        x = int(grid_left + (col + 0.5) * cell_width)
        y = int(grid_top + (row + 0.5) * cell_height)
        return ShotPosition(x, y)

    def _find_answer_cell(self, engine: GameEngine) -> tuple[int, int]:
        """Return the (row, col) of the cell whose value matches the current answer."""
        answer = engine._current_problem.answer
        for row_index, row in enumerate(engine._grid_numbers):
            for col_index, value in enumerate(row):
                if value == answer:
                    return row_index, col_index
        raise AssertionError("Answer not found in grid")

    def _find_wrong_cell(self, engine: GameEngine) -> tuple[int, int]:
        """Return any cell that does not match the current answer."""
        answer = engine._current_problem.answer
        for row_index, row in enumerate(engine._grid_numbers):
            for col_index, value in enumerate(row):
                if value != answer:
                    return row_index, col_index
        raise AssertionError("Expected at least one wrong cell")

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
        assert engine.get_state().score == 0

    def test_correct_hit_increments_score(self):
        engine = self._make_engine()
        engine.start()

        row, col = self._find_answer_cell(engine)
        shot = self._shot_at_cell(engine, row, col)
        engine.update(shot_position=shot)

        assert engine.get_state().score == 1

    def test_wrong_hit_does_not_increment_score(self):
        engine = self._make_engine()
        engine.start()

        row, col = self._find_wrong_cell(engine)
        shot = self._shot_at_cell(engine, row, col)
        engine.update(shot_position=shot)

        assert engine.get_state().score == 0

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

        row, col = self._find_wrong_cell(engine)
        shot = self._shot_at_cell(engine, row, col)
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
        engine = self._make_engine()
        engine.start()

        row, col = self._find_answer_cell(engine)
        shot = self._shot_at_cell(engine, row, col)

        engine.update(shot_position=shot)
        engine.update(shot_position=shot)

        assert engine.get_state().score == 1

    def test_shot_outside_grid_does_not_score(self):
        engine = self._make_engine()
        engine.start()

        shot = ShotPosition(x=640, y=10)
        engine.update(shot_position=shot)

        assert engine.get_state().score == 0

    def test_camera_coord_mapping(self):
        engine = self._make_engine()
        engine.start()

        row, col = self._find_answer_cell(engine)
        display_shot = self._shot_at_cell(engine, row, col)

        camera_shot = ShotPosition(x=display_shot.x // 2, y=display_shot.y // 2)
        frame_shape = (360, 640, 3)

        engine.update(shot_position=camera_shot, camera_frame_shape=frame_shape)

        assert engine.get_state().score == 1
