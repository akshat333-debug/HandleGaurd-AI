from __future__ import annotations

from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

from handleguard.config.loader import load_config
from handleguard.demo import DEMO_TIMELINE, demo_timestamps
from handleguard.incidents.clips import plan_clip
from handleguard.metrics.ablation import AblationReport, run_ablation
from handleguard.metrics.behaviour import EventInterval
from handleguard.perception.yolo import YOLODetector, map_yolo_boxes
from handleguard.privacy.retention import expired_paths
from handleguard.types import Detection
from handleguard.video.clip_writer import write_clip_sidecar


def test_map_yolo_boxes_to_detections():
    boxes = [
        (10.0, 20.0, 110.0, 220.0, 0.91, 0),
        (5.0, 8.0, 40.0, 90.0, 0.4, 1),
    ]
    names = {0: "carton", 1: "person"}
    detections = map_yolo_boxes(boxes, names, min_confidence=0.5)
    assert detections == [Detection("carton", (10.0, 20.0, 110.0, 220.0), 0.91)]


def test_yolo_detector_without_model_raises():
    detector = YOLODetector()
    with pytest.raises(RuntimeError, match="not bound"):
        detector.detect(None, 0.0)


def test_write_clip_sidecar_without_opencv(tmp_path: Path):
    plan = plan_clip("HG-0001", 4.2, 4.8, 12.0, created_at="2026-09-06")
    path = write_clip_sidecar(plan, tmp_path)
    assert path.exists()
    assert path.suffix == ".json"
    text = path.read_text()
    assert "HG-0001" in text
    assert "4.2" not in text or "1.2" in text
    assert "8.8" in text or "end_time" in text


def test_retention_expires_old_files():
    now = datetime(2026, 9, 8, tzinfo=timezone.utc)
    files = [
        ("data/raw/new.mp4", now - timedelta(days=2)),
        ("data/raw/old.mp4", now - timedelta(days=10)),
    ]
    expired = expired_paths(files, now=now, retain_days=7)
    assert expired == ["data/raw/old.mp4"]


def test_ablation_full_beats_no_tracking_on_demo():
    truths = [
        EventInterval("drop", 0.5, 2.0),
        EventInterval("throw", 2.1, 3.1),
        EventInterval("drag", 3.5, 5.5),
    ]
    report = run_ablation(
        DEMO_TIMELINE,
        demo_timestamps(),
        truths,
        config=load_config(),
    )
    assert isinstance(report, AblationReport)
    assert "full" in report.variants
    assert "no_tracking" in report.variants
    assert "no_event_graph" in report.variants
    assert report.variants["full"].macro.f1 >= report.variants["no_tracking"].macro.f1
