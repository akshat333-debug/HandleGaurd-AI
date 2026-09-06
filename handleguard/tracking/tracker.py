from __future__ import annotations

from handleguard.features.geometry import bbox_center, bbox_size, distance, iou
from handleguard.features.kinematics import kinematics_from_history
from handleguard.types import Detection, HistoryEntry, TrackState


class IoUTracker:
    """Greedy IoU tracker with class-aware association and short occlusion memory."""

    def __init__(
        self,
        iou_threshold: float = 0.15,
        max_age: float = 1.25,
        max_center_distance: float = 160.0,
    ):
        self.iou_threshold = iou_threshold
        self.max_age = max_age
        self.max_center_distance = max_center_distance
        self._tracks: dict[str, TrackState] = {}
        self._next_id = 1
        self._class_counts: dict[str, int] = {}

    def tracks(self) -> list[TrackState]:
        return list(self._tracks.values())

    def update(self, detections: list[Detection], timestamp: float) -> list[TrackState]:
        unmatched = list(range(len(detections)))
        assignments: list[tuple[str, int]] = []

        candidates: list[tuple[float, str, int]] = []
        for track_id, track in self._tracks.items():
            for idx in unmatched:
                det = detections[idx]
                if det.class_name.lower() != track.class_name.lower():
                    continue
                overlap = iou(track.bbox, det.bbox)
                if overlap >= self.iou_threshold:
                    candidates.append((overlap + 1.0, track_id, idx))
                    continue
                dist = distance(bbox_center(track.bbox), bbox_center(det.bbox))
                if dist <= self.max_center_distance:
                    candidates.append((1.0 - dist / self.max_center_distance, track_id, idx))
        candidates.sort(reverse=True)

        used_tracks: set[str] = set()
        used_dets: set[int] = set()
        for score, track_id, idx in candidates:
            if track_id in used_tracks or idx in used_dets:
                continue
            assignments.append((track_id, idx))
            used_tracks.add(track_id)
            used_dets.add(idx)

        for track_id, idx in assignments:
            self._refresh(self._tracks[track_id], detections[idx], timestamp)

        for idx, det in enumerate(detections):
            if idx in used_dets:
                continue
            track_id = self._new_id(det.class_name)
            self._tracks[track_id] = self._create(det, timestamp, track_id)

        stale = [
            tid
            for tid, track in self._tracks.items()
            if timestamp - track.last_seen > self.max_age
        ]
        for tid in stale:
            del self._tracks[tid]

        return self.tracks()

    def _new_id(self, class_name: str) -> str:
        count = self._class_counts.get(class_name, 0) + 1
        self._class_counts[class_name] = count
        track_id = f"{class_name}_{count}"
        self._next_id += 1
        return track_id

    def _create(self, det: Detection, timestamp: float, track_id: str) -> TrackState:
        track = TrackState(
            track_id=track_id,
            class_name=det.class_name,
            bbox=det.bbox,
            confidence=det.confidence,
            first_seen=timestamp,
            last_seen=timestamp,
        )
        self._append_history(track, timestamp)
        return track

    def _refresh(self, track: TrackState, det: Detection, timestamp: float) -> None:
        track.bbox = det.bbox
        track.confidence = det.confidence
        track.last_seen = timestamp
        self._append_history(track, timestamp)
        vel, acc = kinematics_from_history(track.history)
        track.velocity = vel
        track.acceleration = acc

    def _append_history(self, track: TrackState, timestamp: float) -> None:
        width, height = bbox_size(track.bbox)
        entry = HistoryEntry(
            timestamp=timestamp,
            bbox=track.bbox,
            center=bbox_center(track.bbox),
            width=width,
            height=height,
            confidence=track.confidence,
            zone=track.zone,
        )
        track.history.append(entry)
        if len(track.history) > 64:
            track.history = track.history[-64:]
