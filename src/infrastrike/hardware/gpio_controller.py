"""
GPIOController – Raspberry Pi GPIO interface.

Contributor 5 owns this module.

Responsibilities
----------------
* Initialise BCM GPIO pin for the status LED.
* Provide ``set_led(state)`` for visual feedback.
* Clean up GPIO resources on shutdown via ``cleanup()``.

The gun trigger is not connected to GPIO; the IR flash captured by the
camera serves as the sole trigger.  On non-Pi platforms (where RPi.GPIO is
unavailable) the LED methods are silent no-ops.
"""

from __future__ import annotations

import logging

from config.settings import GPIO_LED_PIN

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO  # type: ignore[import-untyped]

    _GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    _GPIO_AVAILABLE = False


class GPIOController:
    """Manages the GPIO pin for the status LED.

    Example usage::

        gpio = GPIOController()
        gpio.setup()
        gpio.set_led(True)
        gpio.cleanup()
    """

    def __init__(self, led_pin: int = GPIO_LED_PIN) -> None:
        self._led_pin = led_pin
        self._ready = False

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def setup(self) -> None:
        """Initialise the LED GPIO pin.

        On non-Pi hardware this is a no-op.
        """
        if not _GPIO_AVAILABLE:
            logger.warning(
                "RPi.GPIO not available – LED control disabled."
            )
            self._ready = True
            return

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._led_pin, GPIO.OUT, initial=GPIO.LOW)
        self._ready = True
        logger.info("GPIO ready – LED pin %d", self._led_pin)

    def cleanup(self) -> None:
        """Release GPIO resources."""
        if _GPIO_AVAILABLE and self._ready:
            GPIO.cleanup()
            logger.info("GPIO cleaned up.")
        self._ready = False

    # ── Output ────────────────────────────────────────────────────────────────

    def set_led(self, state: bool) -> None:
        """Turn the status LED on (``True``) or off (``False``)."""
        if not _GPIO_AVAILABLE:
            return
        GPIO.output(self._led_pin, GPIO.HIGH if state else GPIO.LOW)

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def is_ready(self) -> bool:
        """``True`` after :meth:`setup` has been called successfully."""
        return self._ready

