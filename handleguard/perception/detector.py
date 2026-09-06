from __future__ import annotations

from typing import Protocol, Sequence

from handleguard.types import Detection


class Detector(Protocol):
    def detect(self, frame: object, timestamp: float) -> list[Detection]:
        ...


class StubDetector:
    """Deterministic detector for tests and CPU-only demos."""

    def __init__(self, timeline: Sequence[tuple[float, list[Detection]]] | None = None):
        self._timeline = list(timeline or [])

    def detect(self, frame: object, timestamp: float) -> list[Detection]:
        best: list[Detection] = []
        best_dt = float("inf")
        for ts, detections in self._timeline:
            dt = abs(ts - timestamp)
            if dt <= 1e-6:
                return list(detections)
            if dt < best_dt:
                best_dt = dt
                best = list(detections)
        if best_dt <= 0.2:
            return best
        return []
