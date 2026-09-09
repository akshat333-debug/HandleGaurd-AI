from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class FrameSize:
    width: int
    height: int


def resize_frame(
    width: int,
    height: int,
    max_resolution: tuple[int, int] = (1280, 720),
) -> FrameSize:
    max_w, max_h = max_resolution
    if width <= 0 or height <= 0:
        return FrameSize(width=0, height=0)
    if width <= max_w and height <= max_h:
        return FrameSize(width=width, height=height)
    scale = min(max_w / width, max_h / height)
    return FrameSize(width=max(1, round(width * scale)), height=max(1, round(height * scale)))
