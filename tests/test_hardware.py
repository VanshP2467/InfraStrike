"""Tests for GPIOController (Contributor 5)."""

from infrastrike.hardware.gpio_controller import GPIOController


class TestGPIOControllerLEDMode:
    """Tests for the LED-only GPIO controller on non-Pi hardware."""

    def setup_method(self):
        self.gpio = GPIOController(led_pin=27)
        self.gpio.setup()

    def teardown_method(self):
        self.gpio.cleanup()

    def test_setup_marks_ready(self):
        assert self.gpio.is_ready

    def test_cleanup_clears_ready(self):
        self.gpio.cleanup()
        assert not self.gpio.is_ready

    def test_set_led_does_not_raise_in_simulation(self):
        # Should be a no-op in simulation mode.
        self.gpio.set_led(True)
        self.gpio.set_led(False)
