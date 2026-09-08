from __future__ import annotations

from handleguard.features.geometry import bbox_center, bbox_size
from handleguard.types import Detection, HistoryEntry, TrackState


class FrameLocalTracker:
    """One new track per detection. Used as the no-tracking ablation."""

    def __init__(self) -> None:
        self._tracks: list[TrackState] = []
        self._seq = 0

    def tracks(self) -> list[TrackState]:
        return list(self._tracks)

    def update(self, detections: list[Detection], timestamp: float) -> list[TrackState]:
        self._tracks = []
        for det in detections:
            self._seq += 1
            width, height = bbox_size(det.bbox)
            track = TrackState(
                track_id=f"{det.class_name}_{self._seq}",
                class_name=det.class_name,
                bbox=det.bbox,
                confidence=det.confidence,
                first_seen=timestamp,
                last_seen=timestamp,
            )
            track.history.append(
                HistoryEntry(
                    timestamp=timestamp,
                    bbox=det.bbox,
                    center=bbox_center(det.bbox),
                    width=width,
                    height=height,
                    confidence=det.confidence,
                )
            )
            self._tracks.append(track)
        return self.tracks()
