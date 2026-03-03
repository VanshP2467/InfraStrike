"""Tests for game engine, score manager and target (Contributor 3)."""

import time

import pytest

from infrastrike.game.game_engine import GameEngine, GamePhase, GameState
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
