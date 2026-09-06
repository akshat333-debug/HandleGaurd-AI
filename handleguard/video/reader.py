from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass
class VideoMetadata:
    path: str
    fps: float = 0.0
    width: int = 0
    height: int = 0
    frame_count: int = 0
    duration: float = 0.0


class VideoSource:
    """File-backed video reader. OpenCV is optional; tests use StubDetector timelines."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        self._opened = False
        self._index = 0
        self.metadata = VideoMetadata(path=str(self.path))

    def open(self) -> VideoMetadata:
        if not self.path.exists():
            raise FileNotFoundError(self.path)
        suffix = self.path.suffix.lower()
        if suffix not in {".mp4", ".avi", ".mov", ".mkv"}:
            raise ValueError(f"Unsupported video type: {suffix}")
        self._opened = True
        self._index = 0
        try:
            import cv2  # type: ignore

            capture = cv2.VideoCapture(str(self.path))
            fps = float(capture.get(cv2.CAP_PROP_FPS) or 0)
            width = int(capture.get(cv2.CAP_PROP_FRAME_WIDTH) or 0)
            height = int(capture.get(cv2.CAP_PROP_FRAME_HEIGHT) or 0)
            count = int(capture.get(cv2.CAP_PROP_FRAME_COUNT) or 0)
            capture.release()
            self.metadata = VideoMetadata(
                path=str(self.path),
                fps=fps,
                width=width,
                height=height,
                frame_count=count,
                duration=(count / fps) if fps else 0.0,
            )
        except ImportError:
            self.metadata = VideoMetadata(path=str(self.path), fps=8.0)
        return self.metadata

    def read(self):
        if not self._opened:
            raise RuntimeError("VideoSource is closed")
        return None

    def timestamp(self) -> float:
        fps = self.metadata.fps or 8.0
        return self._index / fps

    def close(self) -> None:
        self._opened = False
