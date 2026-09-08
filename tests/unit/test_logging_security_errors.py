from __future__ import annotations

import json

import pytest

from handleguard.logging import log_event
from handleguard.observability import Observability, snapshot
from handleguard.pipeline_errors import (
    EmptyDetectionsError,
    HandleGuardError,
    UnsupportedVideoError,
    corrupt_video_error,
)
from handleguard.security.uploads import UploadRejected, validate_upload


def test_log_event_is_json_with_required_fields(capsys):
    log_event(
        level="INFO",
        module="pipeline",
        event="frame_processed",
        video_id="vid-1",
        latency_ms=12.5,
    )
    payload = json.loads(capsys.readouterr().out.strip())
    assert payload["level"] == "INFO"
    assert payload["module"] == "pipeline"
    assert payload["event"] == "frame_processed"
    assert payload["video_id"] == "vid-1"
    assert payload["latency_ms"] == 12.5
    assert "timestamp" in payload
    assert payload.get("error") in (None, "")


def test_validate_upload_accepts_mp4():
    result = validate_upload("shift.mp4", size_bytes=1024, max_mb=200)
    assert result.ok is True
    assert result.safe_name.endswith(".mp4")
    assert "/" not in result.safe_name
    assert ".." not in result.safe_name


def test_validate_upload_rejects_bad_type():
    with pytest.raises(UploadRejected, match="Unsupported"):
        validate_upload("notes.exe", size_bytes=10, max_mb=200)


def test_validate_upload_rejects_oversize():
    with pytest.raises(UploadRejected, match="too large"):
        validate_upload("big.mp4", size_bytes=201 * 1024 * 1024, max_mb=200)


def test_validate_upload_sanitizes_path_traversal():
    result = validate_upload("../etc/passwd.mp4", size_bytes=100, max_mb=200)
    assert result.safe_name == "passwd.mp4"


def test_unsupported_video_error_is_handleguard_error():
    err = UnsupportedVideoError(".txt")
    assert isinstance(err, HandleGuardError)
    assert "Unsupported" in str(err)


def test_empty_detections_error_message():
    err = EmptyDetectionsError("vid-1")
    assert err.video_id == "vid-1"
    assert "no detections" in str(err).lower()


def test_corrupt_video_error():
    err = corrupt_video_error("broken.mp4")
    assert isinstance(err, HandleGuardError)
    assert "corrupt" in str(err).lower()


def test_observability_snapshot_counts():
    obs = Observability()
    obs.record_frame(latency_ms=10)
    obs.record_frame(latency_ms=20)
    obs.record_incident()
    obs.record_error()
    data = snapshot(obs)
    assert data["frames"] == 2
    assert data["incidents"] == 1
    assert data["errors"] == 1
    assert data["mean_latency_ms"] == 15.0
    assert "fps" in data
