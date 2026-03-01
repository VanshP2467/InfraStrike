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


class TestCameraManagerModule3NoIR:
    """Verify Camera Module 3 NoIR / CSI ribbon-cable configuration."""

    def teardown_method(self):
        if hasattr(self, "cam") and self.cam.is_running:
            self.cam.stop()

    def test_default_camera_num_is_csi_port_0(self):
        cam = CameraManager()
        assert cam.camera_num == 0

    def test_custom_camera_num_stored(self):
        cam = CameraManager(camera_num=1)
        assert cam.camera_num == 1

    def test_default_exposure_time_set(self):
        from config.settings import CAMERA_EXPOSURE_TIME_US
        cam = CameraManager()
        assert cam.exposure_time_us == CAMERA_EXPOSURE_TIME_US

    def test_custom_exposure_time_stored(self):
        cam = CameraManager(exposure_time_us=10_000)
        assert cam.exposure_time_us == 10_000

    def test_default_analogue_gain_set(self):
        from config.settings import CAMERA_ANALOGUE_GAIN
        cam = CameraManager()
        assert cam.analogue_gain == CAMERA_ANALOGUE_GAIN

    def test_custom_analogue_gain_stored(self):
        cam = CameraManager(analogue_gain=4.0)
        assert cam.analogue_gain == 4.0

    def test_dummy_mode_unaffected_by_camera_num(self):
        """camera_num has no effect in dummy mode – frame still returned."""
        self.cam = CameraManager(camera_num=0, resolution=(320, 240))
        self.cam.start()
        frame = self.cam.get_frame()
        assert frame.shape == (240, 320, 3)

