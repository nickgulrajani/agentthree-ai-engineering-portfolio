import time


class Clock:
    """Injectable clock so tests and the demo can fast-forward past token expiry."""

    def __init__(self, start: float | None = None):
        self._offset = 0.0
        self._start = start

    def now(self) -> int:
        base = self._start if self._start is not None else time.time()
        return int(base + self._offset)

    def advance(self, seconds: float) -> None:
        self._offset += seconds
