from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class BehaviourEvent:
    behaviour: str
    start_s: float
    end_s: float
    actor_track: str | None
    object_track: str | None
    risk: str | None


@dataclass
class AnnotationRecord:
    video_id: str
    events: list[BehaviourEvent]


def parse_annotation(payload: dict[str, Any]) -> AnnotationRecord:
    events = [
        BehaviourEvent(
            behaviour=str(item["behaviour"]),
            start_s=float(item["start_s"]),
            end_s=float(item["end_s"]),
            actor_track=item.get("actor_track"),
            object_track=item.get("object_track"),
            risk=item.get("risk"),
        )
        for item in payload.get("events", [])
    ]
    return AnnotationRecord(video_id=str(payload["video_id"]), events=events)


def serialize_annotation(record: AnnotationRecord) -> dict[str, Any]:
    return {
        "video_id": record.video_id,
        "events": [asdict(event) for event in record.events],
    }
