from __future__ import annotations

from dataclasses import dataclass

from handleguard.features.geometry import iou
from handleguard.types import BBox


@dataclass(frozen=True, slots=True)
class DetectionBox:
    class_name: str
    bbox: BBox
    confidence: float


@dataclass
class MAPResult:
    map50: float
    by_class: dict[str, float]


@dataclass(frozen=True, slots=True)
class ClassificationMetrics:
    precision: float
    recall: float
    f1: float
    tp: int = 0
    fp: int = 0
    fn: int = 0


def prf1(tp: int, fp: int, fn: int) -> ClassificationMetrics:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) else 0.0
    return ClassificationMetrics(
        precision=round(precision, 6),
        recall=round(recall, 6),
        f1=round(f1, 6),
        tp=tp,
        fp=fp,
        fn=fn,
    )


def confusion_counts(y_true: list[bool], y_pred: list[bool]) -> tuple[int, int, int]:
    tp = fp = fn = 0
    for truth, pred in zip(y_true, y_pred):
        if truth and pred:
            tp += 1
        elif pred and not truth:
            fp += 1
        elif truth and not pred:
            fn += 1
    return tp, fp, fn


def _average_precision(preds: list[DetectionBox], truths: list[DetectionBox], iou_threshold: float) -> float:
    if not truths and not preds:
        return 1.0
    if not truths or not preds:
        return 0.0
    ordered = sorted(preds, key=lambda box: box.confidence, reverse=True)
    used: set[int] = set()
    tp = 0
    fp = 0
    precisions: list[float] = []
    recalls: list[float] = []
    for pred in ordered:
        best_idx = None
        best_iou = iou_threshold
        for idx, truth in enumerate(truths):
            if idx in used:
                continue
            score = iou(pred.bbox, truth.bbox)
            if score >= best_iou:
                best_iou = score
                best_idx = idx
        if best_idx is None:
            fp += 1
        else:
            used.add(best_idx)
            tp += 1
        precisions.append(tp / (tp + fp))
        recalls.append(tp / len(truths))
    if tp == 0:
        return 0.0
    return round(precisions[-1] if recalls[-1] == 1.0 else precisions[-1] * recalls[-1], 6)


def mean_average_precision(
    predictions: list[DetectionBox],
    truths: list[DetectionBox],
    iou_threshold: float = 0.5,
) -> MAPResult:
    classes = sorted({box.class_name for box in predictions} | {box.class_name for box in truths})
    by_class: dict[str, float] = {}
    for name in classes:
        by_class[name] = _average_precision(
            [box for box in predictions if box.class_name == name],
            [box for box in truths if box.class_name == name],
            iou_threshold,
        )
    map50 = round(sum(by_class.values()) / len(by_class), 6) if by_class else 0.0
    return MAPResult(map50=map50, by_class=by_class)
