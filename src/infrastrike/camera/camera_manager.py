"""
CameraManager – noIR camera capture layer.

Contributor 1 owns this module.

Responsibilities
----------------
* Initialise the Raspberry Pi noIR camera via picamera2.
* Expose a ``get_frame()`` method that returns the latest BGR numpy array
  (compatible with OpenCV) for the detection subsystem to process.
* Provide ``start()`` / ``stop()`` lifecycle helpers.

On non-Pi platforms a dummy frame (black image) is returned so that the
rest of the code can be developed and tested on any machine.
"""

from __future__ import annotations

import logging

import numpy as np

try:
    from picamera2 import Picamera2  # type: ignore[import-untyped]

    _PICAMERA2_AVAILABLE = True
except ImportError:
    _PICAMERA2_AVAILABLE = False

from config.settings import CAMERA_FRAMERATE, CAMERA_RESOLUTION

logger = logging.getLogger(__name__)


class CameraManager:
    """Manages frame capture from the Raspberry Pi noIR camera.

    Example usage::

        cam = CameraManager()
        cam.start()
        frame = cam.get_frame()  # numpy array, shape (H, W, 3), dtype uint8
        cam.stop()
    """

    def __init__(
        self,
        resolution: tuple[int, int] = CAMERA_RESOLUTION,
        framerate: int = CAMERA_FRAMERATE,
    ) -> None:
        self.resolution = resolution
        self.framerate = framerate
        self._camera: "Picamera2 | None" = None
        self._running = False

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Initialise and start the camera."""
        if not _PICAMERA2_AVAILABLE:
            logger.warning(
                "picamera2 not available – running in dummy (black-frame) mode."
            )
            self._running = True
            return

        self._camera = Picamera2()
        config = self._camera.create_video_configuration(
            main={"size": self.resolution, "format": "BGR888"},
            controls={"FrameRate": float(self.framerate)},
        )
        self._camera.configure(config)
        self._camera.start()
        self._running = True
        logger.info("Camera started at %s @ %d fps", self.resolution, self.framerate)

    def stop(self) -> None:
        """Stop and release the camera."""
        self._running = False
        if self._camera is not None:
            self._camera.stop()
            self._camera.close()
            self._camera = None
            logger.info("Camera stopped.")

    # ── Frame capture ─────────────────────────────────────────────────────────

    def get_frame(self) -> np.ndarray:
        """Return the latest camera frame as a BGR numpy array.

        Returns
        -------
        numpy.ndarray
            Shape ``(height, width, 3)``, dtype ``uint8``.
            Returns a black frame when running in dummy mode.
        """
        if not self._running:
            raise RuntimeError("Camera is not started. Call start() first.")

        if self._camera is None:
            # Dummy mode: return a black frame.
            height, width = self.resolution[1], self.resolution[0]
            return np.zeros((height, width, 3), dtype=np.uint8)

        return self._camera.capture_array("main")

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        """``True`` if the camera has been started."""
        return self._running
