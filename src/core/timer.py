"""Timer riutilizzabile basato su tempo reale (monotonic).

Non richiede update() per frame: il tempo trascorso e calcolato al
volo ogni volta che viene interrogato. La pausa e esplicita.

Uso tipico:
    t = Timer(duration=180.0)
    ...
    if t.is_expired():
        game_over()
    ...
    t.pause()      # entra in pausa
    t.resume()     # esce dalla pausa
    t.reset()      # ricomincia da capo
    t.reset(90.0)  # ricomincia con nuova durata

Il clock e iniettabile per testabilita:
    t = Timer(10.0, clock=lambda: 0.0)   # sempre a t=0
"""

from __future__ import annotations

import time
from typing import Callable


class Timer:
    """Timer with countdown, pausa e reset.

    Attributes:
        duration: total duration in seconds.
        elapsed: seconds elapsed (0 to duration).
        remaining: seconds remaining (Never negative).
        progress: fraction from 0.0 to 1.0.
        is_running: True if the timer is running.
        is_expired: True if elapsed >= duration.
    """

    def __init__(
        self,
        duration: float,
        *,
        auto_start: bool = True,
        clock: Callable[[], float] = time.monotonic,
    ) -> None:
        """Create a timer.

        Args:
            duration: total duration in seconds (>= 0).
            auto_start: if True (default), the timer starts immediately.
            If False, it starts upon the first `start()` or `resume()` call.
            clock: time source. Default is `time.monotonic`.
            Injectable for testing purposes.
        """
        if duration < 0:
            raise ValueError(
                f"duration must be >= 0, got {duration}"
            )
        self.duration: float = float(duration)
        self._clock = clock
        self._elapsed: float = 0.0
        self._started_at: float | None = clock() if auto_start else None

    # ==================================================================
    #   Query
    # ==================================================================
    @property
    def elapsed(self) -> float:
        """Seconds elapsed (excluding pause)."""
        if self._started_at is None:
            return self._elapsed
        return self._elapsed + (self._clock() - self._started_at)

    @property
    def remaining(self) -> float:
        """Seconds remaining. Never negative.."""
        return max(0.0, self.duration - self.elapsed)

    @property
    def progress(self) -> float:
        """Fraction [0.0, 1.0] of the elapsed time."""
        if self.duration <= 0.0:
            return 1.0
        return min(1.0, self.elapsed / self.duration)

    @property
    def is_running(self) -> bool:
        return self._started_at is not None

    @property
    def is_expired(self) -> bool:
        return self.elapsed >= self.duration

    # ==================================================================
    #   Controllo
    # ==================================================================
    def start(self) -> None:
        """Start the timer if it is not running."""
        if self._started_at is None:
            self._started_at = self._clock()

    def pause(self) -> None:
        """Freezes the timer. Idempotent."""
        if self._started_at is not None:
            self._elapsed += self._clock() - self._started_at
            self._started_at = None

    def resume(self) -> None:
        """The timer resumes. Idempotent."""
        if self._started_at is None:
            self._started_at = self._clock()

    def reset(self, duration: float | None = None) -> None:
        """Resets the timer to zero and starts it.

        Args:
            duration: new duration. If None, reuses the current one.
        """
        if duration is not None:
            if duration < 0:
                raise ValueError(
                    f"duration must be >= 0, got {duration}"
                )
            self.duration = float(duration)
        self._elapsed = 0.0
        self._started_at = self._clock()
