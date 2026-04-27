"""
InfraStrike – entry point.

Wires together all subsystems and starts the main game loop.

Run directly:
    python -m infrastrike.main

Or via the installed script:
    infrastrike
"""

import sys

import pygame

from infrastrike.camera.camera_manager import CameraManager
from infrastrike.detection.ir_detector import IRDetector
from infrastrike.game.game_engine import GameEngine
from infrastrike.hardware.gpio_controller import GPIOController
from infrastrike.ui.display import Display


def main() -> None:
    pygame.init()

    camera = CameraManager()
    detector = IRDetector()
    gpio = GPIOController()
    display = Display()
    engine = GameEngine()

    camera.start()
    gpio.setup()
    display.show_start_screen()

    try:
        engine.start()
        while engine.is_running():
            # 1. Grab the latest camera frame.
            frame = camera.get_frame()

            # 2. Detect IR shot position in the frame.
            shot_position = detector.detect(frame)

            # 3. Update game state – the flash itself is the trigger.
            engine.update(shot_position=shot_position, camera_frame_shape=frame.shape)

            # 4. Render the current frame + HUD.
            display.render(engine.get_state(), frame)

            # 5. Handle pygame quit events.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    engine.stop()
    finally:
        camera.stop()
        gpio.cleanup()
        display.quit()
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
