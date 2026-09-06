from __future__ import annotations


def sample_timestamps(
    duration: float,
    source_fps: float,
    inference_fps: float = 8.0,
) -> list[float]:
    if duration <= 0 or inference_fps <= 0:
        return []
    fps = inference_fps if source_fps <= 0 else min(inference_fps, source_fps)
    step = 1.0 / fps
    stamps: list[float] = []
    t = 0.0
    while t < duration - 1e-9:
        stamps.append(round(t, 6))
        t += step
    return stamps
