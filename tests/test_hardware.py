"""Tests for GPIOController (Contributor 5)."""

import pytest

from infrastrike.hardware.gpio_controller import GPIOController


class TestGPIOControllerSimulationMode:
    """Tests that run on non-Pi hardware using keyboard simulation mode."""

    def setup_method(self):
        self.gpio = GPIOController(trigger_pin=17, led_pin=27)
        self.gpio.setup()

    def teardown_method(self):
        self.gpio.cleanup()

    def test_setup_marks_ready(self):
        assert self.gpio.is_ready

    def test_trigger_not_pressed_initially(self):
        assert self.gpio.read_trigger() is False

    def test_simulate_trigger_press(self):
        self.gpio.simulate_trigger_press()
        assert self.gpio.read_trigger() is True

    def test_simulated_trigger_auto_resets(self):
        self.gpio.simulate_trigger_press()
        self.gpio.read_trigger()  # consume
        assert self.gpio.read_trigger() is False  # now reset

    def test_cleanup_clears_ready(self):
        self.gpio.cleanup()
        assert not self.gpio.is_ready

    def test_set_led_does_not_raise_in_simulation(self):
        # Should be a no-op in simulation mode.
        self.gpio.set_led(True)
        self.gpio.set_led(False)
