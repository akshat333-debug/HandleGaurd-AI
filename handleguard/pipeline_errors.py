from __future__ import annotations


class HandleGuardError(Exception):
    """Base error for recoverable pipeline/API failures."""


class UnsupportedVideoError(HandleGuardError):
    def __init__(self, suffix: str):
        self.suffix = suffix
        super().__init__(f"Unsupported video type: {suffix}")


class EmptyDetectionsError(HandleGuardError):
    def __init__(self, video_id: str):
        self.video_id = video_id
        super().__init__(f"Video {video_id} produced no detections")


class CorruptVideoError(HandleGuardError):
    def __init__(self, path: str):
        self.path = path
        super().__init__(f"Corrupt or unreadable video: {path}")


def corrupt_video_error(path: str) -> CorruptVideoError:
    return CorruptVideoError(path)
