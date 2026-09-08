from __future__ import annotations

from typing import Any, Mapping, Sequence

from handleguard.types import Detection


def map_yolo_boxes(
    boxes: Sequence[tuple[float, float, float, float, float, int]],
    names: Mapping[int, str],
    min_confidence: float = 0.5,
) -> list[Detection]:
    detections: list[Detection] = []
    for x1, y1, x2, y2, confidence, class_id in boxes:
        if confidence < min_confidence:
            continue
        class_name = names.get(int(class_id), str(class_id))
        detections.append(
            Detection(
                class_name=class_name,
                bbox=(float(x1), float(y1), float(x2), float(y2)),
                confidence=float(confidence),
            )
        )
    return detections


class YOLODetector:
    """Optional Ultralytics-style adapter. Tests never bind a real model."""

    def __init__(
        self,
        model: Any | None = None,
        names: Mapping[int, str] | None = None,
        min_confidence: float = 0.5,
    ):
        self.model = model
        self.names = dict(names or {})
        self.min_confidence = min_confidence

    def detect(self, frame: object, timestamp: float) -> list[Detection]:
        if self.model is None:
            raise RuntimeError("YOLO detector is not bound")
        result = self.model(frame)
        boxes = result if isinstance(result, list) else []
        return map_yolo_boxes(boxes, self.names, min_confidence=self.min_confidence)
