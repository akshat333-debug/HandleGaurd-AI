from __future__ import annotations

from typing import Any


class WebcamSource:
    """Optional live source. Tests never open a camera device."""

    def __init__(self, device: int = 0):
        self.device = device
        self.opened = False

    def describe(self) -> dict[str, Any]:
        return {"source_type": "webcam", "device": self.device, "live": True, "opened": self.opened}

    def open(self) -> None:
        raise RuntimeError("Webcam source is not bound")

    def read(self):
        if not self.opened:
            raise RuntimeError("Webcam source is not bound")
        return None

    def close(self) -> None:
        self.opened = False
