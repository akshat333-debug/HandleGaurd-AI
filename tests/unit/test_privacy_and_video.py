from __future__ import annotations

from pathlib import Path

import pytest

from handleguard.config.loader import load_config
from handleguard.privacy.policy import load_privacy_policy
from handleguard.video.reader import VideoSource


def test_privacy_forbids_identity_storage():
    policy = load_privacy_policy(load_config())
    assert policy.store_worker_identity is False
    policy.assert_no_identity()


def test_video_source_rejects_missing_file(tmp_path: Path):
    src = VideoSource(tmp_path / "nope.mp4")
    with pytest.raises(FileNotFoundError):
        src.open()


def test_video_source_rejects_bad_suffix(tmp_path: Path):
    path = tmp_path / "notes.txt"
    path.write_text("x")
    src = VideoSource(path)
    with pytest.raises(ValueError):
        src.open()
