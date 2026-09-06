from __future__ import annotations

from dataclasses import dataclass

from handleguard.config.loader import AppConfig


@dataclass(frozen=True, slots=True)
class PrivacyPolicy:
    retain_full_video_days: int
    retain_incident_clips_days: int
    blur_faces: bool
    store_worker_identity: bool = False

    def assert_no_identity(self) -> None:
        if self.store_worker_identity:
            raise ValueError("Worker identity storage is forbidden")


def load_privacy_policy(config: AppConfig) -> PrivacyPolicy:
    raw = config.video.get("privacy", {})
    return PrivacyPolicy(
        retain_full_video_days=int(raw.get("retain_full_video_days", 7)),
        retain_incident_clips_days=int(raw.get("retain_incident_clips_days", 30)),
        blur_faces=bool(raw.get("blur_faces", True)),
        store_worker_identity=bool(raw.get("store_worker_identity", False)),
    )
