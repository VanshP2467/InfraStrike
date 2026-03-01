"""
Target – a single on-screen shooting target.

Contributor 3 owns this module (alongside game_engine and score_manager).

Responsibilities
----------------
* Store the position, size and remaining lifetime of a target.
* Provide a ``is_hit(x, y)`` method that returns ``True`` when a shot
  coordinate falls within the target's bounding circle.
* Track whether the target has already been hit or has expired.
"""

from __future__ import annotations

import time


class Target:
    """A circular target that appears on screen for a limited time.

    Parameters
    ----------
    x, y:
        Centre of the target in screen pixels.
    radius:
        Radius of the target in pixels.
    lifetime_ms:
        How long (milliseconds) the target stays alive before expiring.
    """

    def __init__(
        self,
        x: int,
        y: int,
        radius: int = 40,
        lifetime_ms: int = 3000,
    ) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.lifetime_ms = lifetime_ms
        self._spawned_at: float = time.monotonic()
        self._hit = False

    # ── State queries ─────────────────────────────────────────────────────────

    @property
    def is_hit(self) -> bool:
        """``True`` if this target was successfully shot."""
        return self._hit

    @property
    def is_expired(self) -> bool:
        """``True`` if the target has lived past its lifetime without being hit."""
        elapsed_ms = (time.monotonic() - self._spawned_at) * 1000
        return not self._hit and elapsed_ms >= self.lifetime_ms

    @property
    def is_active(self) -> bool:
        """``True`` if the target is still visible and hittable."""
        return not self._hit and not self.is_expired

    def time_remaining_ms(self) -> float:
        """Milliseconds of lifetime remaining (0 if expired)."""
        elapsed_ms = (time.monotonic() - self._spawned_at) * 1000
        return max(0.0, self.lifetime_ms - elapsed_ms)

    # ── Interaction ───────────────────────────────────────────────────────────

    def check_hit(self, x: int, y: int) -> bool:
        """Return ``True`` and mark this target as hit if ``(x, y)`` is inside it.

        Parameters
        ----------
        x, y:
            Shot coordinate in screen pixels.
        """
        if not self.is_active:
            return False
        distance_sq = (x - self.x) ** 2 + (y - self.y) ** 2
        if distance_sq <= self.radius**2:
            self._hit = True
            return True
        return False

    def __repr__(self) -> str:
        return (
            f"Target(x={self.x}, y={self.y}, radius={self.radius}, "
            f"active={self.is_active})"
        )
