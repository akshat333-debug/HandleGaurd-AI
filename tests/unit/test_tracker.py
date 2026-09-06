from __future__ import annotations

from handleguard.tracking.tracker import IoUTracker
from handleguard.types import Detection


def test_tracker_keeps_stable_id_across_frames():
    tracker = IoUTracker()
    d1 = Detection("carton", (10, 10, 50, 50), 0.9)
    d2 = Detection("carton", (12, 12, 52, 52), 0.91)
    first = tracker.update([d1], 0.0)
    second = tracker.update([d2], 0.125)
    assert len(first) == 1
    assert first[0].track_id == second[0].track_id
    assert first[0].track_id == "carton_1"


def test_tracker_creates_new_id_for_second_object():
    tracker = IoUTracker()
    a = Detection("carton", (0, 0, 20, 20), 0.9)
    b = Detection("carton", (80, 80, 100, 100), 0.9)
    tracks = tracker.update([a, b], 0.0)
    ids = {t.track_id for t in tracks}
    assert ids == {"carton_1", "carton_2"}


def test_tracker_does_not_associate_different_classes():
    tracker = IoUTracker()
    tracker.update([Detection("carton", (0, 0, 20, 20), 0.9)], 0.0)
    tracks = tracker.update([Detection("person", (0, 0, 20, 20), 0.9)], 0.1)
    assert {t.class_name for t in tracks} == {"carton", "person"}
