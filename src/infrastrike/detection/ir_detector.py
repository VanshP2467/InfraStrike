"""
IRDetector – IR blob detection using OpenCV.

Contributor 2 owns this module.

Responsibilities
----------------
* Accept a BGR frame from the camera layer.
* Threshold the frame to isolate the bright IR blob produced by the gun LED.
* Locate the centroid of the blob and return its (x, y) screen coordinates.
* Reject noise by filtering on blob area (configurable via settings).

Algorithm overview
------------------
1. Convert BGR → grayscale.
2. Apply a binary threshold at ``IR_THRESHOLD_MIN``.
3. Find contours; select the largest contour inside the valid area range.
4. Compute the centroid with image moments.
5. Return a ``ShotPosition`` named-tuple, or ``None`` if no valid blob found.
"""

from __future__ import annotations

import logging
from typing import NamedTuple

import cv2
import numpy as np

from config.settings import IR_BLOB_MAX_AREA, IR_BLOB_MIN_AREA, IR_THRESHOLD_MIN

logger = logging.getLogger(__name__)


class ShotPosition(NamedTuple):
    """Screen coordinate of the detected IR shot."""

    x: int
    y: int


class IRDetector:
    """Detects the IR gun muzzle flash in a camera frame.

    Example usage::

        detector = IRDetector()
        pos = detector.detect(frame)   # frame is a BGR numpy array
        if pos:
            print(f"Shot at ({pos.x}, {pos.y})")
    """

    def __init__(
        self,
        threshold: int = IR_THRESHOLD_MIN,
        min_area: int = IR_BLOB_MIN_AREA,
        max_area: int = IR_BLOB_MAX_AREA,
    ) -> None:
        self.threshold = threshold
        self.min_area = min_area
        self.max_area = max_area

    def detect(self, frame: np.ndarray) -> ShotPosition | None:
        """Detect the IR blob in *frame* and return its centroid.

        Parameters
        ----------
        frame:
            BGR numpy array as returned by :class:`~infrastrike.camera.CameraManager`.

        Returns
        -------
        ShotPosition or None
            Pixel coordinates ``(x, y)`` of the blob centroid, or ``None``
            when no valid blob is found.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        _, binary = cv2.threshold(gray, self.threshold, 255, cv2.THRESH_BINARY)

        contours, _ = cv2.findContours(
            binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )

        best = self._pick_best_contour(contours)
        if best is None:
            return None

        moments = cv2.moments(best)
        if moments["m00"] == 0:
            return None

        cx = int(moments["m10"] / moments["m00"])
        cy = int(moments["m01"] / moments["m00"])
        logger.debug("IR blob detected at (%d, %d)", cx, cy)
        return ShotPosition(x=cx, y=cy)

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _pick_best_contour(self, contours: tuple[np.ndarray, ...]) -> np.ndarray | None:
        """Return the largest contour whose area is within the valid range."""
        valid = [
            c for c in contours if self.min_area <= cv2.contourArea(c) <= self.max_area
        ]
        if not valid:
            return None
        return max(valid, key=cv2.contourArea)
