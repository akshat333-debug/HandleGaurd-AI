from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CameraGuidance:
    rules: list[str]


def camera_guidance() -> CameraGuidance:
    return CameraGuidance(
        rules=[
            "Prefer a fixed camera over handheld capture.",
            "Avoid extreme fisheye lenses.",
            "Keep the loading area, floor, and pallet boundaries visible.",
            "720p minimum preferred.",
            "Use a stable frame and adequate lighting.",
        ]
    )
