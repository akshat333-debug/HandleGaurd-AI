from __future__ import annotations

import pytest

from handleguard.behaviours.cards import behaviour_card
from handleguard.behaviours.registry import build_detectors
from handleguard.video.stream import RtspSource, WebcamSource


def test_every_registered_behaviour_has_a_specific_card():
    names = [detector.name for detector in build_detectors()]
    assert len(names) == 12
    for name in names:
        card = behaviour_card(name)
        assert card.name == name
        assert card.detects
        assert card.does_not_detect
        generic = f"Configured {name.replace('_', ' ')} pattern from YAML thresholds."
        assert card.detects != generic
        assert card.calibration_status in {"image-space", "uncalibrated"}


def test_rtsp_source_is_not_opened_by_default():
    source = RtspSource("rtsp://camera.local/stream")
    assert source.opened is False
    meta = source.describe()
    assert meta["source_type"] == "rtsp"
    assert meta["live"] is True
    assert "rtsp://" in meta["url"]
    with pytest.raises(RuntimeError, match="not bound"):
        source.read()


def test_webcam_and_rtsp_are_distinct_sources():
    assert WebcamSource().describe()["source_type"] != RtspSource("rtsp://x").describe()["source_type"]
