"""Tests for IRDetector (Contributor 2)."""

import numpy as np

from infrastrike.detection.ir_detector import IRDetector, ShotPosition


def _blank_frame(width: int = 640, height: int = 480) -> np.ndarray:
    """Return a completely black BGR frame."""
    return np.zeros((height, width, 3), dtype=np.uint8)


def _frame_with_blob(
    cx: int, cy: int, radius: int = 10, width: int = 640, height: int = 480
) -> np.ndarray:
    """Return a BGR frame with a single bright white circle (IR blob)."""
    import cv2

    frame = _blank_frame(width, height)
    cv2.circle(frame, (cx, cy), radius, (255, 255, 255), -1)
    return frame


class TestIRDetector:
    def setup_method(self):
        self.detector = IRDetector(threshold=200, min_area=10, max_area=5000)

    def test_no_blob_returns_none(self):
        frame = _blank_frame()
        result = self.detector.detect(frame)
        assert result is None

    def test_blob_detection_returns_shot_position(self):
        frame = _frame_with_blob(cx=320, cy=240, radius=15)
        result = self.detector.detect(frame)
        assert result is not None
        assert isinstance(result, ShotPosition)

    def test_detected_centroid_approximately_correct(self):
        frame = _frame_with_blob(cx=200, cy=150, radius=12)
        result = self.detector.detect(frame)
        assert result is not None
        assert abs(result.x - 200) <= 5
        assert abs(result.y - 150) <= 5

    def test_blob_too_small_returns_none(self):
        # Use a tiny blob that falls below min_area
        detector = IRDetector(threshold=200, min_area=500, max_area=5000)
        frame = _frame_with_blob(cx=320, cy=240, radius=3)
        result = detector.detect(frame)
        assert result is None

    def test_blob_too_large_returns_none(self):
        # Fill nearly the whole frame → exceeds max_area
        detector = IRDetector(threshold=200, min_area=10, max_area=50)
        frame = _frame_with_blob(cx=320, cy=240, radius=100)
        result = detector.detect(frame)
        assert result is None
