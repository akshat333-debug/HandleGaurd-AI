from __future__ import annotations

from pathlib import Path

from handleguard.incidents.clips import plan_clip
from handleguard.metrics.feedback import ReviewLabel, feedback_metrics
from handleguard.privacy.blur import blur_faces
from handleguard.video.clip_writer import write_clip_sidecar


def test_feedback_metrics_from_review_labels():
    labels = [
        ReviewLabel("HG-0001", "drop", "CONFIRMED"),
        ReviewLabel("HG-0002", "drop", "CONFIRMED"),
        ReviewLabel("HG-0003", "drop", "FALSE_POSITIVE"),
        ReviewLabel("HG-0004", "drag", "NEW"),
    ]
    report = feedback_metrics(labels)
    assert report.reviewed == 3
    assert report.confirmed == 2
    assert report.false_positives == 1
    assert abs(report.precision - 2 / 3) < 1e-9
    assert report.by_behaviour["drop"].false_positives == 1
    assert report.by_behaviour["drop"].confirmed == 2


def test_blur_faces_passthrough_without_opencv():
    frame = {"width": 64, "height": 64, "pixels": [0]}
    out = blur_faces(frame, enabled=True)
    assert out is frame


def test_blur_faces_disabled_returns_input():
    frame = object()
    assert blur_faces(frame, enabled=False) is frame


def test_write_clip_sidecar_on_process_directory(tmp_path: Path):
    plan = plan_clip("HG-0099", 1.0, 1.5, 10.0, created_at="2026-09-08")
    path = write_clip_sidecar(plan, tmp_path / "clips")
    assert path.parent.name == "clips"
    assert path.exists()
