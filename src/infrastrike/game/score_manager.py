"""
ScoreManager – track and persist the player's score for one round.

Contributor 3 owns this module.

Responsibilities
----------------
* Add points for hits and apply penalties for misses/expired targets.
* Expose the current score, hit count and miss count.
* Provide a ``reset()`` method for starting a new round.
"""

from __future__ import annotations

from config.settings import PENALTY_PER_MISS, POINTS_PER_HIT


class ScoreManager:
    """Records the score for a single game round.

    Example usage::

        sm = ScoreManager()
        sm.register_hit()
        sm.register_miss()
        print(sm.score)   # 10 - 5 = 5
    """

    def __init__(
        self,
        points_per_hit: int = POINTS_PER_HIT,
        penalty_per_miss: int = PENALTY_PER_MISS,
    ) -> None:
        self._points_per_hit = points_per_hit
        self._penalty_per_miss = penalty_per_miss
        self.reset()

    # ── Mutators ──────────────────────────────────────────────────────────────

    def register_hit(self) -> None:
        """Record a successful hit and add points."""
        self._hits += 1
        self._score += self._points_per_hit

    def register_miss(self) -> None:
        """Record a miss or expired target and apply the penalty."""
        self._misses += 1
        self._score = max(0, self._score - self._penalty_per_miss)

    def reset(self) -> None:
        """Reset score, hits and misses to zero."""
        self._score: int = 0
        self._hits: int = 0
        self._misses: int = 0

    # ── Accessors ─────────────────────────────────────────────────────────────

    @property
    def score(self) -> int:
        """Current score (never negative)."""
        return self._score

    @property
    def hits(self) -> int:
        """Total hits this round."""
        return self._hits

    @property
    def misses(self) -> int:
        """Total misses/expired targets this round."""
        return self._misses

    @property
    def accuracy(self) -> float:
        """Hit accuracy as a fraction 0.0–1.0 (0.0 if no shots fired)."""
        total = self._hits + self._misses
        return self._hits / total if total > 0 else 0.0

    def __repr__(self) -> str:
        return (
            f"ScoreManager(score={self._score}, hits={self._hits}, "
            f"misses={self._misses})"
        )
