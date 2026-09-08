from __future__ import annotations

from dataclasses import dataclass

from handleguard.types import BBox


@dataclass(frozen=True, slots=True)
class OverlayBox:
    track_id: str
    class_name: str
    bbox: BBox
    behaviour: str | None = None


@dataclass(frozen=True, slots=True)
class OverlayPlan:
    timestamp: float
    boxes: list[OverlayBox]
    caption: str


def plan_overlay(
    timestamp: float,
    boxes: list[OverlayBox],
    risk_score: float,
    behaviour: str,
) -> OverlayPlan:
    caption = f"{behaviour} · risk {risk_score:.0f}/100"
    return OverlayPlan(timestamp=timestamp, boxes=list(boxes), caption=caption)
