"""
CameraManager – Camera Module 3 NoIR capture layer.

Contributor 1 owns this module.

Hardware
--------
Raspberry Pi Camera Module 3 NoIR (IMX708 sensor) connected to the
Raspberry Pi 4/5 via the CSI ribbon cable (CSI port 0).

The IMX708 has no IR-cut filter, so near-infrared light from the gun LED
passes straight through and produces a bright blob in the captured frame.

Responsibilities
----------------
* Initialise the CSI camera via picamera2, selecting port ``camera_num``
  (default 0 – the ribbon-cable connector).
* Disable automatic exposure and white balance so the IR flash always
  produces a consistent bright blob regardless of ambient lighting.
* Expose a ``get_frame()`` method that returns the latest BGR numpy array
  (compatible with OpenCV) for the detection subsystem to process.
* Provide ``start()`` / ``stop()`` lifecycle helpers.

On non-Pi platforms a dummy frame (black image) is returned so that the
rest of the code can be developed and tested on any machine.
"""

from __future__ import annotations

import logging

import numpy as np

import cv2

try:
    from picamera2 import Picamera2  # type: ignore[import-untyped]

    _PICAMERA2_AVAILABLE = True
except ImportError:
    _PICAMERA2_AVAILABLE = False

from config.settings import (
    CAMERA_ANALOGUE_GAIN,
    CAMERA_EXPOSURE_TIME_US,
    CAMERA_FRAMERATE,
    CAMERA_NUM,
    CAMERA_RESOLUTION,
)

logger = logging.getLogger(__name__)


class CameraManager:
    """Manages frame capture from the Raspberry Pi Camera Module 3 NoIR.

    The camera is assumed to be connected via the CSI ribbon cable.
    ``camera_num`` selects the CSI port (0 is the standard ribbon-cable
    connector on Raspberry Pi 4/5).

    Auto-exposure and auto-white-balance are disabled so the IMX708 sensor
    delivers a stable image suitable for IR blob detection.

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
        camera_num: int = CAMERA_NUM,
        exposure_time_us: int = CAMERA_EXPOSURE_TIME_US,
        analogue_gain: float = CAMERA_ANALOGUE_GAIN,
    ) -> None:
        self.resolution = resolution
        self.framerate = framerate
        self.camera_num = camera_num
        self.exposure_time_us = exposure_time_us
        self.analogue_gain = analogue_gain
        self._camera: "Picamera2 | None" = None
        self._running = False

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Initialise and start the Camera Module 3 NoIR via CSI."""
        if not _PICAMERA2_AVAILABLE:
            logger.warning(
                "picamera2 not available – running in dummy (black-frame) mode."
            )
            self._running = True
            return

        # Explicitly select the CSI port; camera_num=0 is the ribbon-cable
        # connector on Pi 4/5.  Change CAMERA_NUM in settings.py if you use
        # a different port (e.g. 1 on a Pi 5 with dual CSI).
        self._camera = Picamera2(camera_num=self.camera_num)
        config = self._camera.create_video_configuration(
            main={"size": self.resolution, "format": "BGR888"},
            controls={
                "FrameRate": float(self.framerate),
                # Disable automatic exposure so the IR flash always
                # saturates at the same brightness level.
                "AeEnable": False,
                "ExposureTime": self.exposure_time_us,
                "AnalogueGain": self.analogue_gain,
                # Disable auto-white-balance – not meaningful for IR sensing.
                "AwbEnable": False,
            },
        )
        self._camera.configure(config)
        self._camera.start()
        self._running = True
        logger.info(
            "Camera Module 3 NoIR started on CSI port %d at %s @ %d fps "
            "(exposure %d µs, gain %.1f)",
            self.camera_num,
            self.resolution,
            self.framerate,
            self.exposure_time_us,
            self.analogue_gain,
        )

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

        return cv2.flip(self._camera.capture_array("main"), 1)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def is_running(self) -> bool:
        """``True`` if the camera has been started."""
        return self._running
