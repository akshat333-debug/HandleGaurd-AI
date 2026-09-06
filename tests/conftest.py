from __future__ import annotations

import pytest

from handleguard.config.loader import load_config
from handleguard.types import Detection, HistoryEntry, TrackState


@pytest.fixture(scope="session")
def config():
    return load_config()


def make_track(
    track_id: str,
    class_name: str,
    boxes: list[tuple[float, tuple[float, float, float, float]]],
    confidence: float = 0.9,
) -> TrackState:
    first_ts, first_box = boxes[0]
    track = TrackState(
        track_id=track_id,
        class_name=class_name,
        bbox=first_box,
        confidence=confidence,
        first_seen=first_ts,
        last_seen=first_ts,
    )
    for ts, box in boxes:
        x1, y1, x2, y2 = box
        track.history.append(
            HistoryEntry(
                timestamp=ts,
                bbox=box,
                center=((x1 + x2) / 2, (y1 + y2) / 2),
                width=x2 - x1,
                height=y2 - y1,
                confidence=confidence,
            )
        )
        track.bbox = box
        track.last_seen = ts
    if len(track.history) >= 2:
        from handleguard.features.kinematics import kinematics_from_history

        track.velocity, track.acceleration = kinematics_from_history(track.history)
    return track


def det(class_name: str, box: tuple[float, float, float, float], conf: float = 0.9) -> Detection:
    return Detection(class_name, box, conf)
