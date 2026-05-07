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
from infrastrike.game.game_engine import GameEngine, GamePhase
from infrastrike.ui.display import Display


def main() -> None:
    pygame.init()

    camera = CameraManager()
    detector = IRDetector()
    display = Display()
    engine = GameEngine()

    camera.start()
    display.show_start_screen()

    try:
        engine.start()
        running = True
        last_frame = None

        while running:
            state = engine.get_state()

            # Always handle window and key events.
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif state.phase == GamePhase.GAME_OVER and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_q:
                        running = False
                    else:
                        engine.start()

            if not running:
                break

            if state.phase == GamePhase.RUNNING:
                # 1. Grab the latest camera frame.
                frame = camera.get_frame()
                last_frame = frame

                # 2. Detect IR shot position in the frame.
                shot_position = detector.detect(frame)

                # 3. Update game state – the flash itself is the trigger.
                engine.update(
                    shot_position=shot_position, camera_frame_shape=frame.shape
                )

                # 4. Render the current frame + HUD.
                display.render(engine.get_state(), frame)
            elif state.phase == GamePhase.GAME_OVER:
                display.show_game_over_screen(state, last_frame)
    finally:
        camera.stop()
        display.quit()
        pygame.quit()
        sys.exit(0)


if __name__ == "__main__":
    main()
