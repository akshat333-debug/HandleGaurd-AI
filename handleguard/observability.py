from __future__ import annotations

from dataclasses import dataclass, field
from time import time

from handleguard.metrics.latency import summarize_latencies


@dataclass
class Observability:
    frames: int = 0
    incidents: int = 0
    errors: int = 0
    latencies_ms: list[float] = field(default_factory=list)
    started_at: float = field(default_factory=time)
    model_loaded: str = "stub-detector"
    queued_videos: int = 0

    def record_frame(self, latency_ms: float) -> None:
        self.frames += 1
        self.latencies_ms.append(float(latency_ms))

    def record_incident(self) -> None:
        self.incidents += 1

    def record_error(self) -> None:
        self.errors += 1


def snapshot(obs: Observability) -> dict[str, float | int | str]:
    elapsed = max(time() - obs.started_at, 1e-6)
    stats = summarize_latencies(obs.latencies_ms)
    return {
        "frames": obs.frames,
        "incidents": obs.incidents,
        "errors": obs.errors,
        "queued_videos": obs.queued_videos,
        "model_loaded": obs.model_loaded,
        "mean_latency_ms": stats.mean,
        "p50_latency_ms": stats.p50,
        "p95_latency_ms": stats.p95,
        "fps": round(obs.frames / elapsed, 3),
    }


OBS = Observability()
