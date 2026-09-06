from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class ClipPlan:
    incident_id: str
    start_time: float
    end_time: float
    filename: str


def plan_clip(
    incident_id: str,
    start_time: float,
    end_time: float,
    video_duration: float,
    created_at: str | datetime | None = None,
    pre_buffer: float = 3.0,
    post_buffer: float = 4.0,
) -> ClipPlan:
    clip_start = max(0.0, start_time - pre_buffer)
    clip_end = min(video_duration, end_time + post_buffer)
    if clip_end < clip_start:
        clip_end = clip_start
    if isinstance(created_at, datetime):
        stamp = created_at.strftime("%Y%m%d")
    elif isinstance(created_at, str) and created_at:
        stamp = created_at[:10].replace("-", "")
    else:
        stamp = datetime.utcnow().strftime("%Y%m%d")
    safe_id = incident_id.replace("/", "-")
    return ClipPlan(
        incident_id=incident_id,
        start_time=round(clip_start, 3),
        end_time=round(clip_end, 3),
        filename=f"incident_{stamp}_{safe_id}.mp4",
    )
