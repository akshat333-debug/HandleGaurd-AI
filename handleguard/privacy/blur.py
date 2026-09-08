from __future__ import annotations

from typing import Any


def blur_faces(frame: Any, enabled: bool = True) -> Any:
    if not enabled:
        return frame
    try:
        import cv2  # type: ignore
    except ImportError:
        return frame
    if frame is None:
        return frame
    return frame
