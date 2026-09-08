from __future__ import annotations

import pytest

from handleguard.pipeline import HandleGuardPipeline
from handleguard.pipeline_errors import EmptyDetectionsError
from handleguard.video.camera import CameraGuidance, camera_guidance
from handleguard.video.stream import WebcamSource


def test_camera_guidance_lists_fixed_camera_rules():
    guide = camera_guidance()
    assert isinstance(guide, CameraGuidance)
    blob = " ".join(guide.rules).lower()
    assert "fixed" in blob
    assert "fisheye" in blob
    assert "720p" in blob
    assert "lighting" in blob


def test_empty_timeline_raises_empty_detections():
    pipeline = HandleGuardPipeline.from_stub([], video_id="empty-vid")
    with pytest.raises(EmptyDetectionsError, match="empty-vid"):
        pipeline.process_timeline([0.0, 0.125, 0.25], require_detections=True)


def test_webcam_source_is_not_opened_by_default():
    source = WebcamSource(device=0)
    assert source.opened is False
    meta = source.describe()
    assert meta["source_type"] == "webcam"
    assert meta["live"] is True
    with pytest.raises(RuntimeError, match="not bound"):
        source.read()
