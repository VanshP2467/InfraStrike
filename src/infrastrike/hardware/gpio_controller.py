"""
GPIOController – Raspberry Pi GPIO interface.

Contributor 5 owns this module.

Responsibilities
----------------
* Initialise BCM GPIO pins for the trigger button and status LED.
* Expose ``read_trigger()`` to poll the trigger button state each frame.
* Provide ``set_led(state)`` for a feedback LED.
* Clean up GPIO resources on shutdown via ``cleanup()``.

On non-Pi platforms (where RPi.GPIO is unavailable) the controller falls back
to keyboard simulation: the spacebar acts as the trigger, so the game can be
developed and tested on any machine.
"""

from __future__ import annotations

import logging

from config.settings import GPIO_LED_PIN, GPIO_TRIGGER_PIN

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO  # type: ignore[import-untyped]

    _GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    _GPIO_AVAILABLE = False


class GPIOController:
    """Manages GPIO pins for the trigger button and status LED.

    When running on a non-Pi machine the class operates in *keyboard mode*:
    call ``simulate_trigger_press()`` to emulate the button (useful in tests).

    Example usage::

        gpio = GPIOController()
        gpio.setup()
        if gpio.read_trigger():
            print("Trigger pulled!")
        gpio.cleanup()
    """

    def __init__(
        self,
        trigger_pin: int = GPIO_TRIGGER_PIN,
        led_pin: int = GPIO_LED_PIN,
    ) -> None:
        self._trigger_pin = trigger_pin
        self._led_pin = led_pin
        self._simulated_trigger = False
        self._ready = False

    # ── Lifecycle ─────────────────────────────────────────────────────────────

    def setup(self) -> None:
        """Initialise GPIO pins.

        On non-Pi hardware this is a no-op (keyboard simulation is used).
        """
        if not _GPIO_AVAILABLE:
            logger.warning(
                "RPi.GPIO not available – running in keyboard-simulation mode."
            )
            self._ready = True
            return

        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self._trigger_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self._led_pin, GPIO.OUT, initial=GPIO.LOW)
        self._ready = True
        logger.info(
            "GPIO ready – trigger pin %d, LED pin %d",
            self._trigger_pin,
            self._led_pin,
        )

    def cleanup(self) -> None:
        """Release GPIO resources."""
        if _GPIO_AVAILABLE and self._ready:
            GPIO.cleanup()
            logger.info("GPIO cleaned up.")
        self._ready = False

    # ── Input ─────────────────────────────────────────────────────────────────

    def read_trigger(self) -> bool:
        """Return ``True`` if the trigger button is currently pressed.

        In keyboard-simulation mode returns the value set by
        :meth:`simulate_trigger_press`.
        """
        if not _GPIO_AVAILABLE:
            pressed = self._simulated_trigger
            self._simulated_trigger = False  # auto-reset after one frame
            return pressed

        # Active-LOW: button connects pin to GND when pressed.
        return GPIO.input(self._trigger_pin) == GPIO.LOW

    # ── Output ────────────────────────────────────────────────────────────────

    def set_led(self, state: bool) -> None:
        """Turn the status LED on (``True``) or off (``False``)."""
        if not _GPIO_AVAILABLE:
            return
        GPIO.output(self._led_pin, GPIO.HIGH if state else GPIO.LOW)

    # ── Simulation helpers (for non-Pi development & testing) ─────────────────

    def simulate_trigger_press(self) -> None:
        """Simulate a single trigger press (consumed on next ``read_trigger()``)."""
        self._simulated_trigger = True

    # ── Properties ────────────────────────────────────────────────────────────

    @property
    def is_ready(self) -> bool:
        """``True`` after :meth:`setup` has been called successfully."""
        return self._ready
