from __future__ import annotations

from dataclasses import dataclass


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
