"""Tests for CameraManager (Contributor 1)."""

import numpy as np
import pytest

from infrastrike.camera.camera_manager import CameraManager


class TestCameraManagerDummyMode:
    """Tests that run on any machine (no Pi hardware required)."""

    def setup_method(self):
        self.cam = CameraManager(resolution=(640, 480), framerate=30)

    def teardown_method(self):
        if self.cam.is_running:
            self.cam.stop()

    def test_initial_state_not_running(self):
        assert not self.cam.is_running

    def test_start_sets_running(self):
        self.cam.start()
        assert self.cam.is_running

    def test_get_frame_before_start_raises(self):
        with pytest.raises(RuntimeError, match="not started"):
            self.cam.get_frame()

    def test_get_frame_returns_numpy_array(self):
        self.cam.start()
        frame = self.cam.get_frame()
        assert isinstance(frame, np.ndarray)

    def test_get_frame_correct_shape(self):
        self.cam.start()
        frame = self.cam.get_frame()
        # shape is (height, width, channels)
        assert frame.shape == (480, 640, 3)

    def test_get_frame_correct_dtype(self):
        self.cam.start()
        frame = self.cam.get_frame()
        assert frame.dtype == np.uint8

    def test_stop_clears_running(self):
        self.cam.start()
        self.cam.stop()
        assert not self.cam.is_running
