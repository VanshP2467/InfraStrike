"""game package – game engine, targets, and scoring (Contributor 3)."""

from .game_engine import GameEngine, GameState
from .score_manager import ScoreManager
from .target import Target

__all__ = ["GameEngine", "GameState", "ScoreManager", "Target"]
